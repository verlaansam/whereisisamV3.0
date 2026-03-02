import logging
import os
import re
import csv
import gzip
import io
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime, timedelta, timezone as dt_timezone

import json
from urllib import request, error
from urllib.parse import quote
from django.core.management.base import BaseCommand
from django.utils import timezone

from core.models import WeatherVlieland, Location, Tides

logger = logging.getLogger(__name__)

# Weather metrics source preferred by user: Brandaris area (West-Terschelling).
WEATHER_LAT = 53.359
WEATHER_LONG = 5.216

# Forecast district preference requested by user.
FORECAST_LOCATION_CANDIDATES = (
    ("texel", 53.055, 4.799),
    ("harlingen", 53.1745, 5.4225),
    ("brandaris", WEATHER_LAT, WEATHER_LONG),
)

# Legacy fallback (Vlieland).
LAT = 53.296
LONG = 4.955
TIDE_LOCATIONS = {
    "vlieland": {"name": "Vlieland", "lat": 53.296, "long": 4.955},
    "harlingen": {"name": "Harlingen", "lat": 53.1745, "long": 5.4225},
    "ameland": {"name": "Ameland", "lat": 53.439, "long": 5.754},
    "texel": {"name": "Texel", "lat": 53.055, "long": 4.799},
    "kornwerderzand": {"name": "Kornwerderzand", "lat": 53.0703, "long": 5.336},
    "terschelling": {"name": "Terschelling", "lat": 53.367, "long": 5.227},
}
RWS_WAARNEMINGEN_URL = "https://ddapi20-waterwebservices.rijkswaterstaat.nl/ONLINEWAARNEMINGENSERVICES/OphalenWaarnemingen"
RWS_TIDE_LOCATION_CODES = {
    "vlieland": ("vlieland.haven", "vlieland.west", "harlingen.waddenzee"),
    "harlingen": ("harlingen.waddenzee",),
    "ameland": ("ameland.nes", "ameland.noord", "harlingen.waddenzee"),
    "texel": ("texel.oudeschild", "texel.noordzee", "harlingen.waddenzee"),
    # No reliable tide series was returned for Kornwerderzand codes in ddapi20; fallback to nearby stations.
    "kornwerderzand": ("kornwerderzand.waddenzee", "harlingen.waddenzee", "texel.oudeschild"),
    "terschelling": ("terschelling.west", "terschelling.hoorn", "harlingen.waddenzee"),
}
KNMI_BASE_URL = "https://api.dataplatform.knmi.nl/open-data/v1"
KNMI_WARNINGS_DATASET = "waarschuwingen_nederland_48h"
KNMI_WARNINGS_VERSION = "1.0"
KNMI_DEFAULT_ANON_KEY = "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJkNWVkNTM3YTY0YmFjN2FkYjRiNWEzZmNmNDE4ZjU1YmY0OTQ4MDIwYTA1MzIzNjQxIiwiYXVkIjoiYW5vbm9ua2V5IiwiaWF0IjoxNzQ4NjkxODE2LCJleHAiOjE3NTEyODM4MTZ9.3M_2o9_TcPAhk7MphjUSOHNv3hRBMJaQXquI5S4_S4I"
KNMI_PREFERRED_STATION = 242  # Vlieland
KNMI_WEATHER_DATASET_CANDIDATES = (
    ("10-minute-in-situ-meteorological-observations", "1.0"),
    ("hourly-in-situ-meteorological-observations", "1.0"),
    ("hourly-in-situ-meteorological-observations-validated", "1.0"),
    # Backward-compatible fallbacks (deprecated/legacy names).
    ("actuele10mindata_knmi", "2.0"),
    ("actuele10mindata_knmi", "1.0"),
    ("uurgegevens_knmi", "1.0"),
)
ENV_FILE_CANDIDATES = tuple(parent / ".env" for parent in Path(__file__).resolve().parents)


def _first_payload(data):
    """
    The Meteoserver payload can vary; pick the dict that most likely contains weather fields.
    """

    def _iter_dicts(node):
        if isinstance(node, dict):
            yield node
            for value in node.values():
                yield from _iter_dicts(value)
        elif isinstance(node, list):
            for item in node:
                yield from _iter_dicts(item)

    def _weather_score(item):
        keys = {_normalize_key(key) for key in item.keys()}
        hints = {
            "temp",
            "temperature",
            "airtemperature",
            "luchttemp",
            "wind",
            "windk",
            "windspeed",
            "windrichting",
            "winddirection",
            "zicht",
            "visibility",
            "golfsig",
            "waveheight",
            "verw",
            "verwachting",
            "forecast",
            "warning",
            "warnings",
            "waarsch",
        }
        return sum(1 for hint in hints if any(hint in key for key in keys))

    best = None
    best_score = 0
    for candidate in _iter_dicts(data):
        score = _weather_score(candidate)
        if score > best_score:
            best = candidate
            best_score = score
    return best if best_score > 0 else None


def _coerce_float(value):
    if value in ("", None):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        text = str(value).strip().replace(",", ".")
        match = re.search(r"-?\d+(?:\.\d+)?", text)
        if not match:
            return None
        try:
            return float(match.group(0))
        except (TypeError, ValueError):
            return None


def _normalize_key(value):
    if value is None:
        return ""
    return re.sub(r"[^a-z0-9]", "", str(value).lower())


def _pick(item, keys):
    if not isinstance(item, dict):
        return None

    normalized = {}
    for key, value in item.items():
        if value not in ("", None):
            normalized[_normalize_key(key)] = value

    for key in keys:
        value = normalized.get(_normalize_key(key))
        if value not in ("", None):
            return value
    return None


def _pick_deep(data, keys):
    normalized_keys = {_normalize_key(key) for key in keys}
    queue = [data]
    seen = set()

    while queue:
        node = queue.pop(0)
        node_id = id(node)
        if node_id in seen:
            continue
        seen.add(node_id)

        if isinstance(node, dict):
            for key, value in node.items():
                nkey = _normalize_key(key)
                if nkey in normalized_keys and value not in ("", None) and not isinstance(value, (dict, list)):
                    return value
                if isinstance(value, (dict, list)):
                    queue.append(value)
        elif isinstance(node, list):
            for value in node:
                if isinstance(value, (dict, list)):
                    queue.append(value)
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
    help = "Fetches KNMI weather/warnings data and stores it in the database."

    def handle(self, *args, **options):
        knmi_weather = self._fetch_knmi_current_weather()
        weather = self._merge_weather(knmi_weather, {})
        weather["weather_warnings"] = self._merge_warnings(
            weather.get("weather_warnings"),
            self._fetch_knmi_warning_text(),
        )
        weather.setdefault("recorded_at", timezone.now())
        weather.setdefault("wind_direction", None)
        weather.setdefault("temperature", None)
        weather.setdefault("wind_speed", None)
        weather.setdefault("wind_gusts", None)
        weather.setdefault("sea_temperature", None)
        weather.setdefault("sight", None)
        weather.setdefault("wave_height", None)
        weather.setdefault("verwachting", "")
        self._store_weather(weather)
        self.stdout.write(self.style.SUCCESS(f"Stored weather record at {weather['recorded_at']}"))
        self._fetch_and_store_rws_tides()

    def _fetch_forecast_payload(self, api_key):
        for _, lat, lon in FORECAST_LOCATION_CANDIDATES:
            try:
                payload = self._fetch_payload(lat, lon, api_key)
                forecast = self._extract_weather(payload).get("verwachting", "")
                if self._is_preferred_forecast(forecast):
                    return payload
            except Exception:
                continue
        return {}

    def _is_preferred_forecast(self, text):
        normalized = _normalize_key(text)
        return ("distrtexel" in normalized) or ("harlingen" in normalized)

    def _pick_preferred_forecast_text(self, fallback, payloads):
        fallback = (fallback or "").strip()
        for payload in payloads:
            if not payload:
                continue
            candidate = self._extract_weather(payload).get("verwachting", "").strip()
            if self._is_preferred_forecast(candidate):
                return candidate
        if "distr. zierikzee" in fallback.lower():
            return fallback.replace("distr. Zierikzee", "distr. Texel/Harlingen")
        return fallback

    def _resolve_api_key(self):
        api_key = os.environ.get("METEOSERVER_API_KEY")
        if api_key:
            return api_key

        api_key = self._read_env_value("METEOSERVER_API_KEY")
        if api_key:
            return api_key

        raise SystemExit("Missing METEOSERVER_API_KEY environment variable.")

    def _resolve_knmi_api_key(self):
        api_key = (
            os.environ.get("KNMI_API_KEY")
            or os.environ.get("knmi_api_key")
            or os.environ.get("KNMI_OPEN_DATA_API_KEY")
            or os.environ.get("DEV_KNMI_OPEN_DATA_API_KEY")
        )
        if api_key:
            return api_key

        api_key = (
            self._read_env_value("KNMI_API_KEY")
            or self._read_env_value("knmi_api_key")
            or self._read_env_value("KNMI_OPEN_DATA_API_KEY")
            or self._read_env_value("DEV_KNMI_OPEN_DATA_API_KEY")
        )
        if api_key:
            return api_key
        return KNMI_DEFAULT_ANON_KEY

    def _read_env_value(self, key):
        for candidate in ENV_FILE_CANDIDATES:
            if not candidate.exists():
                continue
            with candidate.open() as f:
                for line in f:
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    env_key, env_val = line.split("=", 1)
                    if env_key.strip() != key:
                        continue
                    return env_val.strip().strip('"').strip("'")
        return None

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

    def _fetch_json_url(self, url, headers=None, method="GET", body=None):
        payload = None
        if body is not None:
            payload = json.dumps(body).encode("utf-8")
        req = request.Request(url, data=payload, headers=headers or {}, method=method)
        with request.urlopen(req, timeout=20) as resp:
            if resp.status != 200:
                raise SystemExit(f"Unexpected status code {resp.status} for {url}")
            return json.loads(resp.read().decode("utf-8"))

    def _fetch_text_url(self, url, headers=None):
        req = request.Request(url, headers=headers or {})
        with request.urlopen(req, timeout=20) as resp:
            if resp.status != 200:
                raise SystemExit(f"Unexpected status code {resp.status} for {url}")
            return resp.read().decode("utf-8", errors="replace")

    def _fetch_bytes_url(self, url, headers=None):
        req = request.Request(url, headers=headers or {})
        with request.urlopen(req, timeout=20) as resp:
            if resp.status != 200:
                raise SystemExit(f"Unexpected status code {resp.status} for {url}")
            return resp.read()

    def _merge_weather(self, primary, fallback):
        result = dict(fallback or {})
        for key, value in (primary or {}).items():
            if value not in (None, ""):
                result[key] = value
        return result

    def _fetch_knmi_current_weather(self):
        api_key = self._resolve_knmi_api_key()
        headers = {"Authorization": api_key}
        for dataset, version in KNMI_WEATHER_DATASET_CANDIDATES:
            try:
                weather = self._fetch_latest_knmi_observation(dataset, version, headers=headers)
                if not weather:
                    continue
                self.stdout.write(self.style.SUCCESS(f"Loaded KNMI weather from {dataset} v{version}"))
                return weather
            except (error.HTTPError, error.URLError, TimeoutError, json.JSONDecodeError, SystemExit, OSError) as exc:
                logger.warning("Could not fetch KNMI weather from %s v%s: %s", dataset, version, exc)
                self.stdout.write(self.style.WARNING(f"KNMI weer niet opgehaald uit {dataset} v{version}: {exc}"))
        return {}

    def _fetch_latest_knmi_observation(self, dataset, version, headers):
        list_url = (
            f"{KNMI_BASE_URL}/datasets/{dataset}/versions/{version}/files"
            "?maxKeys=25&sorting=desc&orderBy=created"
        )
        listing = self._fetch_json_url(list_url, headers=headers)
        files = listing.get("files") or []
        if not files:
            return None

        filename = self._pick_knmi_observation_file(files)
        if not filename:
            return None

        file_url = (
            f"{KNMI_BASE_URL}/datasets/{dataset}/versions/{version}"
            f"/files/{quote(filename, safe='')}/url"
        )
        signed = self._fetch_json_url(file_url, headers=headers)
        download_url = signed.get("temporaryDownloadUrl")
        if not download_url:
            return None

        blob = self._fetch_bytes_url(download_url)
        lower_name = filename.lower()
        if lower_name.endswith(".nc"):
            return self._build_weather_from_knmi_netcdf(blob)

        if filename.lower().endswith(".gz"):
            blob = gzip.decompress(blob)

        text = blob.decode("utf-8", errors="replace")
        rows = self._parse_knmi_table_rows(text)
        if not rows:
            return None

        best_row = None
        best_score = None
        for row in rows:
            ts = self._parse_knmi_row_timestamp(row)
            if not ts:
                continue
            stn = self._to_int(row.get("STN"))
            stn_score = 0 if stn == KNMI_PREFERRED_STATION else 1
            score = (stn_score, -int(ts.timestamp()))
            if best_score is None or score < best_score:
                best_score = score
                best_row = row
        if not best_row:
            return None
        return self._build_weather_from_knmi_row(best_row)

    def _pick_knmi_observation_file(self, files):
        candidates = []
        for item in files:
            name = item.get("filename") if isinstance(item, dict) else ""
            if not name:
                continue
            low = name.lower()
            score = 0
            if low.endswith(".csv.gz"):
                score += 5
            elif low.endswith(".csv"):
                score += 4
            elif low.endswith(".txt.gz"):
                score += 3
            elif low.endswith(".txt"):
                score += 2
            elif low.endswith(".nc"):
                score += 6
            else:
                continue
            if "10min" in low or "10_min" in low:
                score += 2
            if "uur" in low or "hour" in low:
                score += 1
            candidates.append((score, name))
        if not candidates:
            return ""
        candidates.sort(reverse=True)
        return candidates[0][1]

    def _build_weather_from_knmi_netcdf(self, blob):
        try:
            from netCDF4 import Dataset, num2date
        except ImportError as exc:
            raise SystemExit("NetCDF parsing requires netCDF4 (and numpy) in backend requirements.") from exc

        dataset = Dataset("inmemory", mode="r", memory=blob)
        try:
            station_idx = self._pick_knmi_netcdf_station_index(dataset)

            time_var = dataset.variables.get("time")
            recorded_at = timezone.now()
            if time_var is not None and len(time_var) > 0:
                raw_time = time_var[-1]
                converted = num2date(
                    raw_time,
                    units=getattr(time_var, "units", "seconds since 1970-01-01"),
                    calendar=getattr(time_var, "calendar", "standard"),
                )
                dt = None
                if isinstance(converted, datetime):
                    dt = converted.replace(tzinfo=None)
                elif hasattr(converted, "year") and hasattr(converted, "month"):
                    dt = datetime(
                        int(converted.year),
                        int(converted.month),
                        int(converted.day),
                        int(getattr(converted, "hour", 0)),
                        int(getattr(converted, "minute", 0)),
                        int(getattr(converted, "second", 0)),
                    )
                if dt is not None:
                    recorded_at = timezone.make_aware(dt, dt_timezone.utc)

            temperature = self._coerce_netcdf_number(self._read_netcdf_var(dataset, "ta", station_idx))
            if temperature is None:
                temperature = self._coerce_netcdf_number(self._read_netcdf_var(dataset, "t", station_idx))
            wind_speed = self._coerce_netcdf_number(self._read_netcdf_var(dataset, "ff", station_idx))
            wind_gusts = self._coerce_netcdf_number(self._read_netcdf_var(dataset, "fx", station_idx))
            sea_temperature = self._coerce_netcdf_number(self._read_netcdf_var(dataset, "tw", station_idx))
            if sea_temperature is None:
                sea_temperature = self._coerce_netcdf_number(self._read_netcdf_var(dataset, "tz", station_idx))
            wind_direction = self._read_netcdf_var(dataset, "dd", station_idx)
            visibility_m = self._coerce_netcdf_number(self._read_netcdf_var(dataset, "vv", station_idx))
            sight = None
            if visibility_m is not None:
                sight = str(round(visibility_m / 1000.0, 2))

            return {
                "recorded_at": recorded_at,
                "wind_direction": None if wind_direction in ("", None) else str(self._coerce_netcdf_number(wind_direction)),
                "temperature": temperature,
                "wind_speed": wind_speed,
                "wind_gusts": wind_gusts,
                "sea_temperature": sea_temperature,
                "sight": sight,
                "wave_height": None,
                "verwachting": "",
                "weather_warnings": "",
            }
        finally:
            dataset.close()

    def _pick_knmi_netcdf_station_index(self, dataset):
        station_var = dataset.variables.get("station")
        if station_var is None:
            return 0
        stations = station_var[:]
        preferred = str(KNMI_PREFERRED_STATION)
        for idx, raw in enumerate(stations):
            code = self._normalize_station_code(raw)
            if not code:
                continue
            if code == preferred or code.endswith(preferred.zfill(3)):
                return idx

        lat_var = dataset.variables.get("lat")
        lon_var = dataset.variables.get("lon")
        if lat_var is None or lon_var is None:
            return 0

        best_idx = 0
        best_dist = None
        for idx in range(min(len(stations), len(lat_var), len(lon_var))):
            lat = self._coerce_netcdf_number(lat_var[idx])
            lon = self._coerce_netcdf_number(lon_var[idx])
            if lat is None or lon is None:
                continue
            dist = (lat - LAT) ** 2 + (lon - LONG) ** 2
            if best_dist is None or dist < best_dist:
                best_dist = dist
                best_idx = idx
        return best_idx

    def _read_netcdf_var(self, dataset, name, station_idx):
        var = dataset.variables.get(name)
        if var is None:
            return None

        dims = getattr(var, "dimensions", ())
        if not dims:
            return var[...]

        index = []
        for dim_name in dims:
            if dim_name == "station":
                index.append(station_idx)
            elif dim_name == "time":
                index.append(-1)
            else:
                index.append(0)

        try:
            return var[tuple(index)]
        except Exception:
            return None

    def _normalize_station_code(self, value):
        if value in ("", None):
            return ""
        text = str(value).strip()
        digits = "".join(ch for ch in text if ch.isdigit())
        return digits or text

    def _coerce_netcdf_number(self, value):
        if value in ("", None):
            return None
        try:
            # Handle numpy scalars without importing numpy directly.
            if hasattr(value, "item"):
                value = value.item()
        except Exception:
            pass
        if str(value).strip() in {"--", "nan", "NaN"}:
            return None
        return _coerce_float(value)

    def _parse_knmi_table_rows(self, text):
        lines = [line for line in text.splitlines() if line.strip()]
        if not lines:
            return []

        header_line = None
        for line in lines:
            cleaned = line.lstrip("#").strip()
            if "STN" in cleaned and "," in cleaned:
                header_line = cleaned
                break
        if not header_line:
            return []

        headers = [part.strip() for part in header_line.split(",")]
        rows = []
        for line in lines:
            if line.startswith("#"):
                continue
            if "," not in line:
                continue
            parts = next(csv.reader([line], skipinitialspace=True), [])
            if len(parts) != len(headers):
                continue
            row = {headers[idx]: (parts[idx].strip() if idx < len(parts) else "") for idx in range(len(headers))}
            rows.append(row)
        return rows

    def _parse_knmi_row_timestamp(self, row):
        date_raw = row.get("YYYYMMDD")
        hour_raw = row.get("HH")
        minute_raw = row.get("MM") or "00"
        if not date_raw or not hour_raw:
            return None

        try:
            base = datetime.strptime(str(date_raw).strip(), "%Y%m%d")
            hour = int(str(hour_raw).strip())
            minute = int(str(minute_raw).strip())
            if hour == 24:
                base = base + timedelta(days=1)
                hour = 0
            dt = base.replace(hour=hour, minute=minute, second=0, microsecond=0)
            return timezone.make_aware(dt, timezone.get_default_timezone())
        except (ValueError, TypeError):
            return None

    def _to_int(self, value):
        try:
            return int(str(value).strip())
        except (ValueError, TypeError, AttributeError):
            return None

    def _knmi_pick(self, row, keys):
        for key in keys:
            val = row.get(key)
            if val not in ("", None):
                return val
        return None

    def _knmi_tenths(self, value):
        number = _coerce_float(value)
        if number is None:
            return None
        return round(number / 10.0, 2)

    def _build_weather_from_knmi_row(self, row):
        if not row:
            return {}
        timestamp = self._parse_knmi_row_timestamp(row) or timezone.now()
        direction = self._knmi_pick(row, ["DD", "DDVEC", "DDVEC10"])
        sight_value = self._knmi_tenths(self._knmi_pick(row, ["VV"]))

        return {
            "recorded_at": timestamp,
            "wind_direction": str(direction) if direction not in ("", None) else None,
            "temperature": self._knmi_tenths(self._knmi_pick(row, ["T", "TA", "TG"])),
            "wind_speed": self._knmi_tenths(self._knmi_pick(row, ["FF", "FH", "FHVEC"])),
            "wind_gusts": self._knmi_tenths(self._knmi_pick(row, ["FX", "FXH"])),
            "sea_temperature": self._knmi_tenths(self._knmi_pick(row, ["TZ", "TW", "WATERTEMP"])),
            "sight": str(sight_value) if sight_value is not None else None,
            "wave_height": None,
            "verwachting": "",
            "weather_warnings": "",
        }

    def _fetch_knmi_warning_text(self):
        api_key = self._resolve_knmi_api_key()
        headers = {"Authorization": api_key}
        list_url = (
            f"{KNMI_BASE_URL}/datasets/{KNMI_WARNINGS_DATASET}/versions/{KNMI_WARNINGS_VERSION}/files"
            "?maxKeys=25&sorting=desc&orderBy=created"
        )
        try:
            listing = self._fetch_json_url(list_url, headers=headers)
            files = listing.get("files") or []
            if not files:
                return ""
            filename = self._pick_knmi_warning_file(files)
            if not filename:
                return ""

            file_url = (
                f"{KNMI_BASE_URL}/datasets/{KNMI_WARNINGS_DATASET}/versions/{KNMI_WARNINGS_VERSION}"
                f"/files/{quote(filename, safe='')}/url"
            )
            signed = self._fetch_json_url(file_url, headers=headers)
            download_url = signed.get("temporaryDownloadUrl")
            if not download_url:
                return ""

            raw = self._fetch_text_url(download_url)
            parsed = self._parse_knmi_warning_payload(raw, filename)
            if parsed:
                self.stdout.write(self.style.SUCCESS("Loaded KNMI waarschuwingen"))
            return parsed
        except (error.HTTPError, error.URLError, TimeoutError, json.JSONDecodeError, ET.ParseError, SystemExit) as exc:
            logger.warning("Could not fetch KNMI warnings: %s", exc)
            self.stdout.write(self.style.WARNING(f"KNMI waarschuwingen niet opgehaald: {exc}"))
            return ""

    def _pick_knmi_warning_file(self, files):
        candidates = []
        for item in files:
            name = item.get("filename") if isinstance(item, dict) else ""
            if not name:
                continue
            low = name.lower()
            score = 0
            if "waarschuwingen" in low:
                score += 4
            if "nederland" in low:
                score += 3
            if low.endswith(".xml"):
                score += 2
            if low.endswith(".txt"):
                score += 1
            candidates.append((score, name))
        if not candidates:
            return ""
        candidates.sort(reverse=True)
        return candidates[0][1]

    def _parse_knmi_warning_payload(self, raw, filename):
        lowered = (filename or "").lower()
        if lowered.endswith(".json"):
            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                data = None
            if data:
                return self._render_knmi_warning_from_json(data)
        if lowered.endswith(".xml") or raw.lstrip().startswith("<"):
            xml_text = self._render_knmi_warning_from_xml(raw)
            if xml_text:
                return xml_text
        return self._render_knmi_warning_from_text(raw)

    def _render_knmi_warning_from_json(self, data):
        if isinstance(data, dict):
            direct = _pick_deep(data, ["headline", "description", "message", "event", "title", "warning"])
            if direct:
                return str(direct).strip()
        return ""

    def _render_knmi_warning_from_text(self, raw):
        lines = [line.strip() for line in (raw or "").splitlines() if line.strip()]
        if not lines:
            return ""
        return " | ".join(lines[:6])

    def _render_knmi_warning_from_xml(self, raw):
        root = ET.fromstring(raw)

        def local_name(tag):
            if "}" in tag:
                return tag.rsplit("}", 1)[1].lower()
            return tag.lower()

        messages = []
        for info in root.iter():
            if local_name(info.tag) != "info":
                continue
            parts = {}
            for child in info:
                key = local_name(child.tag)
                text = (child.text or "").strip()
                if key in {"event", "headline", "description", "areadesc", "severity"} and text:
                    parts[key] = text
            if not parts:
                continue
            msg_bits = [parts.get("event"), parts.get("severity"), parts.get("areadesc"), parts.get("headline")]
            msg = " - ".join([bit for bit in msg_bits if bit])
            if not msg:
                msg = parts.get("description", "")
            if msg:
                messages.append(msg)

        if not messages:
            return ""
        unique = []
        seen = set()
        for msg in messages:
            if msg in seen:
                continue
            seen.add(msg)
            unique.append(msg)
        return " | ".join(unique[:4])

    def _merge_warnings(self, meteoserver_warning, knmi_warning):
        left = (meteoserver_warning or "").strip()
        right = (knmi_warning or "").strip()
        if left and right:
            if right in left:
                return left
            return f"{left} | KNMI: {right}"
        if right:
            return f"KNMI: {right}"
        return left

    def _extract_weather(self, payload):
        record = _first_payload(payload)
        if not record:
            raise SystemExit("No weather payload found in Meteoserver response")

        def pick(keys):
            return _pick(record, keys) or _pick_deep(payload, keys)

        recorded_at = _parse_timestamp(
            pick(["timestamp", "time", "datetime", "observation_time", "measure_time", "observed_at", "updated_at"])
        ) or timezone.now()

        return {
            "recorded_at": recorded_at,
            "wind_direction": pick(
                ["wind_direction", "windr", "windrichting", "wind_dir", "winddirection", "windrichtinggr", "wdir"],
            ),
            "temperature": _coerce_float(
                pick(["temperature", "temp", "temp_c", "air_temperature", "luchttemp", "tempc", "tt", "tempair"])
            ),
            "wind_speed": _coerce_float(
                pick(
                    ["wind_speed", "windspeed", "windk", "wind_kmh", "wind_ms", "windsnelheid", "wind", "ff", "winds"]
                )
            ),
            "wind_gusts": _coerce_float(
                pick(["wind_gusts", "windgust", "windstoten", "windgusts", "gust", "gusts", "windvlaag", "fx"])
            ),
            "sea_temperature": _coerce_float(
                pick(["sea_temperature", "seatemp", "wtemp", "watertemp", "water_temperature", "zeetemp", "tempwater"])
            ),
            "verwachting": pick(["verw", "verwachting", "forecast", "expectation"]) or "",
            "wave_height": _coerce_float(
                pick(["golfsig", "wave_height", "waveheight", "golfhoogte", "wave_sig_height", "hs"])
            ),
            "sight": pick(["zicht", "visibility", "vis", "zichtkm"]),
            "weather_warnings": pick(
                ["weather_warnings", "warning", "warnings", "waarsch", "alert", "weerwaarschuwing", "waarschuwing"]
            )
            or "",
        }

    def _store_weather(self, weather):
        WeatherVlieland.objects.all().delete()
        WeatherVlieland.objects.create(**weather)

    def _fetch_and_store_rws_tides(self):
        now = timezone.now()
        for slug, meta in TIDE_LOCATIONS.items():
            location_obj, _ = Location.objects.get_or_create(location=slug)

            # Remove past events to keep table lean
            self._prune_past_tides(location_obj)

            rows = self._fetch_rws_waterlevels(slug)
            if not rows:
                self.stdout.write(self.style.WARNING(f"No Rijkswaterstaat waterlevels found for {slug}"))
                continue

            events = self._detect_tide_events_from_levels(rows)
            if not events:
                self.stdout.write(self.style.WARNING(f"No tide events derived from Rijkswaterstaat for {slug}"))
                continue

            next_events = [event for event in events if event.get("time") and event["time"] >= now][:4]
            if not next_events:
                self.stdout.write(self.style.WARNING(f"No upcoming tide events found for {slug}"))
                continue

            # Keep only the next 4 upcoming events per location.
            Tides.objects.filter(location=location_obj, timestamp__gte=now).delete()
            Tides.objects.bulk_create(
                [
                    Tides(
                        location=location_obj,
                        tide_type=event.get("type") or "",
                        waterheight=event.get("height"),
                        timestamp=event.get("time"),
                    )
                    for event in next_events
                ]
            )
            self.stdout.write(self.style.SUCCESS(f"Stored {len(next_events)} RWS tide events for {meta['name']}"))

        self._prune_past_tides()

    def _fetch_rws_waterlevels(self, slug):
        codes = RWS_TIDE_LOCATION_CODES.get(slug, ())
        now = timezone.now()
        begin = (now - timedelta(days=1)).astimezone(dt_timezone.utc).isoformat(timespec="milliseconds")
        end = (now + timedelta(days=2)).astimezone(dt_timezone.utc).isoformat(timespec="milliseconds")

        for code in codes:
            payload = {
                "Locatie": {"Code": code},
                "AquoPlusWaarnemingMetadata": {
                    "AquoMetadata": {"Compartiment": {"Code": "OW"}, "Grootheid": {"Code": "WATHTE"}}
                },
                "Periode": {"Begindatumtijd": begin, "Einddatumtijd": end},
            }

            try:
                data = self._fetch_json_url(
                    RWS_WAARNEMINGEN_URL,
                    headers={"Content-Type": "application/json"},
                    method="POST",
                    body=payload,
                )
            except (SystemExit, error.HTTPError, error.URLError, TimeoutError, json.JSONDecodeError):
                continue

            series = data.get("WaarnemingenLijst") or []
            if not series:
                continue

            best = max(series, key=lambda s: len((s or {}).get("MetingenLijst") or []))
            metingen = best.get("MetingenLijst") or []
            rows = []
            for item in metingen:
                raw_time = item.get("Tijdstip")
                raw_value = _pick_deep(item, ["Waarde_Numeriek", "waarde_numeriek"])
                ts = _parse_timestamp(raw_time)
                val = _coerce_float(raw_value)
                if not ts or val is None:
                    continue
                rows.append({"time": ts, "value_cm": val})
            if rows:
                rows.sort(key=lambda x: x["time"])
                self.stdout.write(self.style.SUCCESS(f"Loaded RWS waterlevels for {slug} via {code}"))
                return rows

        return []

    def _detect_tide_events_from_levels(self, rows):
        if len(rows) < 3:
            return []

        events = []
        for idx in range(1, len(rows) - 1):
            prev_val = rows[idx - 1]["value_cm"]
            cur_val = rows[idx]["value_cm"]
            next_val = rows[idx + 1]["value_cm"]

            if cur_val >= prev_val and cur_val > next_val:
                tide_type = "HW"
            elif cur_val <= prev_val and cur_val < next_val:
                tide_type = "LW"
            else:
                continue

            events.append(
                {
                    "type": tide_type,
                    "time": rows[idx]["time"],
                    "height": round(cur_val / 100.0, 3),  # cm to meters
                }
            )

        deduped = {}
        for event in events:
            deduped[(event["type"], event["time"])] = event
        ordered = list(deduped.values())
        ordered.sort(key=lambda x: x["time"])
        return ordered

    def _fetch_and_store_tides(self, api_key, vlieland_payload):
        payload_cache = {}
        now = timezone.now()
        for slug, meta in TIDE_LOCATIONS.items():
            location_obj, _ = Location.objects.get_or_create(location=slug)

            # Remove past events to keep table lean
            self._prune_past_tides(location_obj)

            if slug in payload_cache:
                payload = payload_cache[slug]
            else:
                payload = self._fetch_payload(meta["lat"], meta["long"], api_key)
                payload_cache[slug] = payload

            events = self._normalize_tide_events(payload)
            if not events:
                self.stdout.write(self.style.WARNING(f"No tide events found for {slug}"))
                continue

            next_events = [event for event in events if event.get("time") and event["time"] >= now][:4]
            if not next_events:
                self.stdout.write(self.style.WARNING(f"No upcoming tide events found for {slug}"))
                continue

            # Keep only the next 4 upcoming events per location.
            Tides.objects.filter(location=location_obj, timestamp__gte=now).delete()
            Tides.objects.bulk_create(
                [
                    Tides(
                        location=location_obj,
                        tide_type=event.get("type") or "",
                        waterheight=event.get("height"),
                        timestamp=event.get("time"),
                    )
                    for event in next_events
                ]
            )

            self.stdout.write(
                self.style.SUCCESS(f"Stored {len(next_events)} upcoming tide events for {meta['name']}")
            )
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

        def _normalize_tide_type(raw):
            if raw in ("", None):
                return ""
            text = str(raw).strip().upper()
            if text in {"HW", "LW"}:
                return text
            if text in {"H", "HIGH", "HOOG", "HOOGWATER"} or text.startswith("HW"):
                return "HW"
            if text in {"L", "LOW", "LAAG", "LAAGWATER"} or text.startswith("LW"):
                return "LW"
            return ""

        def _iter_dicts(node):
            if isinstance(node, dict):
                yield node
                for value in node.values():
                    yield from _iter_dicts(value)
            elif isinstance(node, list):
                for item in node:
                    yield from _iter_dicts(item)

        raw_events = list(_iter_dicts(payload))
        events = []
        for item in raw_events:
            if not isinstance(item, dict):
                continue

            tide_raw = _pick(item, ["getij", "type", "state", "code", "tide_type", "soort", "event"])
            if isinstance(tide_raw, (list, dict)):
                continue
            tide_type = _normalize_tide_type(tide_raw)

            timestamp = _parse_timestamp(_pick(item, ["timestamp", "datetime", "date_time"]))
            date_str = _pick(item, ["datum", "date"])
            time_str = _pick(item, ["uur", "tijd", "time"])
            if (not timestamp) and date_str and time_str:
                dt = None
                clean_time = str(time_str).strip()
                time_match = re.search(r"\d{1,2}:\d{2}(?::\d{2})?", clean_time)
                if time_match:
                    clean_time = time_match.group(0)
                elif re.fullmatch(r"\d{4,6}", clean_time):
                    clean_time = f"{clean_time[:2]}:{clean_time[2:4]}"
                # Typical format: datum=14122025 (ddmmyyyy), uur=10:08
                for fmt in (
                    "%d%m%Y %H:%M",
                    "%d%m%y %H:%M",
                    "%d%m%Y %H:%M:%S",
                    "%Y%m%d %H:%M",
                    "%Y%m%d %H:%M:%S",
                    "%d-%m-%Y %H:%M",
                    "%d-%m-%y %H:%M",
                    "%d-%m-%Y %H:%M:%S",
                    "%d/%m/%Y %H:%M",
                    "%d/%m/%y %H:%M",
                    "%d/%m/%Y %H:%M:%S",
                    "%d.%m.%Y %H:%M",
                    "%d.%m.%y %H:%M",
                    "%Y-%m-%d %H:%M",
                    "%Y-%m-%d %H:%M:%S",
                ):
                    try:
                        dt = datetime.strptime(f"{date_str} {clean_time}", fmt)
                        break
                    except ValueError:
                        continue
                if dt:
                    tz = timezone.get_default_timezone()
                    timestamp = timezone.make_aware(dt, tz) if timezone.is_naive(dt) else dt

            height_cm = _coerce_float(_pick(item, ["latniveau", "verschil", "hoogte", "height", "waterhoogte"]))
            height_m = height_cm / 100.0 if height_cm is not None else None

            if tide_type not in {"HW", "LW"} or not timestamp:
                continue
            events.append({"type": tide_type, "time": timestamp, "height": height_m})

        deduped = {}
        for event in events:
            key = (event["type"], event["time"])
            deduped[key] = event
        events = list(deduped.values())
        events.sort(key=lambda x: x["time"])
        return events
