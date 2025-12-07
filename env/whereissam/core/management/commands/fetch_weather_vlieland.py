import logging
import os
from pathlib import Path
from datetime import datetime

import json
from urllib import request, error
from django.core.management.base import BaseCommand
from django.utils import timezone

from core.models import WeatherVlieland

logger = logging.getLogger(__name__)

LAT = 53.215
LONG = 4.954


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
    help = "Fetches Vlieland Vliehorst weather from Meteoserver and stores it in WeatherVlieland."

    def handle(self, *args, **options):
        api_key = os.environ.get("METEOSERVER_API_KEY")
        if not api_key:
            # Fallback: try loading a .env file if present
            for candidate in [
                Path(__file__).resolve().parents[3] / ".env",
                Path(__file__).resolve().parents[2] / ".env",
                Path(__file__).resolve().parents[1] / ".env",
            ]:
                if candidate.exists():
                    with candidate.open() as f:
                        for line in f:
                            if line.startswith("METEOSERVER_API_KEY="):
                                api_key = line.strip().split("=", 1)[1]
                                break
                if api_key:
                    break

        if not api_key:
            raise SystemExit("Missing METEOSERVER_API_KEY environment variable.")

        api_url = f"https://data.meteoserver.nl/api/zeeweer.php?lat={LAT}&long={LONG}&key={api_key}"

        self.stdout.write(f"Fetching Meteoserver Vlieland Vliehorst from {api_url}")
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

        record = _first_payload(payload)
        if not record:
            raise SystemExit("No weather payload found in Meteoserver response")

        recorded_at = _parse_timestamp(
            _pick(record, ["timestamp", "time", "datetime", "observation_time", "measure_time"])
        ) or timezone.now()

        # Remove previous entries so table only holds the latest fetch.
        WeatherVlieland.objects.all().delete()

        weather = WeatherVlieland.objects.create(
            recorded_at=recorded_at,
            wind_direction=_pick(record, ["wind_direction", "windr", "windrichting"]),
            temperature=_coerce_float(_pick(record, ["temperature", "temp", "temp_c", "air_temperature"])),
            wind_speed=_coerce_float(_pick(record, ["wind_speed", "windspeed", "windk", "wind_kmh"])),
            #staat niet in api wind gust
            wind_gusts=_coerce_float(_pick(record, ["wind_gusts", "windgust", "windstoten", "windgusts"])),
            sea_temperature=_coerce_float(_pick(record, ["sea_temperature", "seatemp", "wtemp"])),
            verwachting=_pick(record, ["verw", "verwachting", "forecast"]) or "",
            wave_height=_coerce_float(_pick(record, ["golfsig", "wave_height"])),
            sight=_pick(record, ["zicht", "visibility"]),
            weather_warnings=_pick(
                record,
                ["weather_warnings", "warning", "warnings", "waarsch", "alert"]
            )
            or "",
        )

        self.stdout.write(self.style.SUCCESS(f"Stored weather record at {weather.recorded_at} (id={weather.id})"))
