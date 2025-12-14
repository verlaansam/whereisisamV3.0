import logging
import os
from pathlib import Path
from datetime import datetime

import json
from urllib import request, error
from django.core.management.base import BaseCommand
from django.utils import timezone

from core.models import WeatherVlieland, Location, Tides

logger = logging.getLogger(__name__)

LAT = 53.215
LONG = 4.954
TIDE_LOCATIONS = {
    "vlieland": {"name": "Vlieland", "lat": 53.296, "long": 4.955},
    "harlingen": {"name": "Harlingen", "lat": 53.1745, "long": 5.4225},
    "ameland": {"name": "Ameland", "lat": 53.439, "long": 5.754},
    "texel": {"name": "Texel", "lat": 53.055, "long": 4.799},
    "kornwerderzand": {"name": "Kornwerderzand", "lat": 53.0703, "long": 5.336},
    "terschelling": {"name": "Terschelling", "lat": 53.367, "long": 5.227},
}


def _first_payload(data):
    """
    The Meteoserver payload can vary; pick the first record from common containers.
    """
    if not data:
        return None
    if isinstance(data, list):
        return data[0] if data else None
    if isinstance(data, dict):
        for key in ("liveweer", "data", "result", "results", "weather", "weer"):
            if isinstance(data.get(key), list) and data[key]:
                return data[key][0]
        return data
    return None


def _coerce_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _pick(item, keys):
    for key in keys:
        if key in item and item[key] not in ("", None):
            return item[key]
    return None


def _parse_timestamp(raw):
    if not raw:
        return None
    if isinstance(raw, (int, float)):
        try:
            return datetime.fromtimestamp(raw, tz=timezone.utc)
        except (OSError, OverflowError, ValueError):
            return None
    if isinstance(raw, str):
        for parser in (datetime.fromisoformat,):
            try:
                dt = parser(raw.replace("Z", "+00:00"))
                return dt if timezone.is_aware(dt) else timezone.make_aware(dt, timezone.utc)
            except Exception:
                continue
    return None


class Command(BaseCommand):
    help = "Fetches Vlieland Vliehorst weather and tide data and stores it in the database."

    def handle(self, *args, **options):
        api_key = self._resolve_api_key()
        vlieland_payload = self._fetch_payload(LAT, LONG, api_key)
        weather = self._extract_weather(vlieland_payload)
        self._store_weather(weather)
        self.stdout.write(self.style.SUCCESS(f"Stored weather record at {weather['recorded_at']}"))

        self._fetch_and_store_tides(api_key, vlieland_payload)

    def _resolve_api_key(self):
        api_key = os.environ.get("METEOSERVER_API_KEY")
        if api_key:
            return api_key

        for candidate in [
            Path(__file__).resolve().parents[3] / ".env",
            Path(__file__).resolve().parents[2] / ".env",
            Path(__file__).resolve().parents[1] / ".env",
        ]:
            if candidate.exists():
                with candidate.open() as f:
                    for line in f:
                        if line.startswith("METEOSERVER_API_KEY="):
                            return line.strip().split("=", 1)[1]

        raise SystemExit("Missing METEOSERVER_API_KEY environment variable.")

    def _fetch_payload(self, lat, long, api_key):
        api_url = f"https://data.meteoserver.nl/api/zeeweer.php?lat={lat}&long={long}&key={api_key}"
        self.stdout.write(f"Fetching Meteoserver data from {api_url}")
        try:
            with request.urlopen(api_url, timeout=20) as resp:
                if resp.status != 200:
                    raise SystemExit(f"Unexpected status code {resp.status}")
                payload = json.loads(resp.read().decode("utf-8"))
        except (error.HTTPError, error.URLError, TimeoutError) as exc:
            logger.exception("Failed to fetch Meteoserver data")
            raise SystemExit(f"Error fetching Meteoserver data: {exc}")
        except json.JSONDecodeError as exc:
            logger.exception("Failed to decode Meteoserver response")
            raise SystemExit(f"Invalid JSON from Meteoserver: {exc}")
        return payload

    def _extract_weather(self, payload):
        record = _first_payload(payload)
        if not record:
            raise SystemExit("No weather payload found in Meteoserver response")

        recorded_at = _parse_timestamp(
            _pick(record, ["timestamp", "time", "datetime", "observation_time", "measure_time"])
        ) or timezone.now()

        return {
            "recorded_at": recorded_at,
            "wind_direction": _pick(record, ["wind_direction", "windr", "windrichting"]),
            "temperature": _coerce_float(_pick(record, ["temperature", "temp", "temp_c", "air_temperature"])),
            "wind_speed": _coerce_float(_pick(record, ["wind_speed", "windspeed", "windk", "wind_kmh"])),
            "wind_gusts": _coerce_float(_pick(record, ["wind_gusts", "windgust", "windstoten", "windgusts"])),
            "sea_temperature": _coerce_float(_pick(record, ["sea_temperature", "seatemp", "wtemp"])),
            "verwachting": _pick(record, ["verw", "verwachting", "forecast"]) or "",
            "wave_height": _coerce_float(_pick(record, ["golfsig", "wave_height"])),
            "sight": _pick(record, ["zicht", "visibility"]),
            "weather_warnings": _pick(record, ["weather_warnings", "warning", "warnings", "waarsch", "alert"]) or "",
        }

    def _store_weather(self, weather):
        WeatherVlieland.objects.all().delete()
        WeatherVlieland.objects.create(**weather)

    def _fetch_and_store_tides(self, api_key, vlieland_payload):
        payload_cache = {"vlieland": vlieland_payload}
        for slug, meta in TIDE_LOCATIONS.items():
            location_obj, _ = Location.objects.get_or_create(location=slug)

            # Remove past events to keep table lean
            self._prune_past_tides(location_obj)

            # Skip fetching if we already have enough upcoming events
            upcoming_count = (
                Tides.objects.filter(location=location_obj, timestamp__gte=timezone.now()).count()
            )
            if upcoming_count >= 4:
                self.stdout.write(self.style.NOTICE(f"Skipping {slug}: {upcoming_count} future tide events present"))
                continue

            if slug in payload_cache:
                payload = payload_cache[slug]
            else:
                payload = self._fetch_payload(meta["lat"], meta["long"], api_key)
                payload_cache[slug] = payload

            events = self._normalize_tide_events(payload)
            if not events:
                self.stdout.write(self.style.WARNING(f"No tide events found for {slug}"))
                continue

            created = 0
            for event in events:
                timestamp = event.get("time")
                if not timestamp:
                    continue
                tide_type = event.get("type") or ""
                defaults = {"waterheight": event.get("height")}
                _, made = Tides.objects.update_or_create(
                    location=location_obj,
                    tide_type=tide_type,
                    timestamp=timestamp,
                    defaults=defaults,
                )
                if made:
                    created += 1

            self.stdout.write(self.style.SUCCESS(f"Stored {created} tide events for {meta['name']}"))
        # Final cleanup pass to ensure no expired tides linger
        self._prune_past_tides()

    def _prune_past_tides(self, location=None):
        qs = Tides.objects.filter(timestamp__lt=timezone.now())
        if location:
            qs = qs.filter(location=location)
        deleted, _ = qs.delete()
        if deleted:
            self.stdout.write(self.style.WARNING(f"Removed {deleted} past tide entries"))

    def _normalize_tide_events(self, payload):
        """
        Meteoserver tides are in the same response as weather under the `getij` key.
        Example entry:
        {"datum":"14122025","uur":"10:08","getij":"LW","verschil":"-68","latniveau":"80"}
        """

        def _events_container(data):
            if isinstance(data, list):
                return data
            if isinstance(data, dict):
                for key in ("getij", "tides", "events", "result", "results", "data"):
                    value = data.get(key)
                    if isinstance(value, list):
                        return value
                    if isinstance(value, dict):
                        nested = _events_container(value)
                        if nested:
                            return nested
            return []

        raw_events = _events_container(payload)
        events = []
        for item in raw_events:
            if not isinstance(item, dict):
                continue

            tide_type = (_pick(item, ["getij", "type", "state", "code", "tide_type", "soort"]) or "").upper()

            date_str = _pick(item, ["datum", "date"])
            time_str = _pick(item, ["uur", "tijd", "time"])
            timestamp = None
            if date_str and time_str:
                dt = None
                # Typical format: datum=14122025 (ddmmyyyy), uur=10:08
                for fmt in ("%d%m%Y %H:%M", "%Y%m%d %H:%M", "%d-%m-%Y %H:%M"):
                    try:
                        dt = datetime.strptime(f"{date_str} {time_str}", fmt)
                        break
                    except ValueError:
                        continue
                if dt:
                    tz = timezone.get_default_timezone()
                    timestamp = timezone.make_aware(dt, tz) if timezone.is_naive(dt) else dt

            height_cm = _coerce_float(_pick(item, ["verschil", "latniveau", "hoogte", "height", "waterhoogte"]))
            height_m = height_cm / 100.0 if height_cm is not None else None

            events.append({"type": tide_type, "time": timestamp, "height": height_m})

        events = [e for e in events if e.get("time")]
        events.sort(key=lambda x: x["time"])
        return events
