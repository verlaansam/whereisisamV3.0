import { useEffect, useMemo, useState } from "react";
import { AlertTriangle, CloudSun, Eye, Waves, Wind } from "lucide-react";
import BottomNav from "./BottomNav";
import TopNav from "./TopNav";

const API_URL = process.env.REACT_APP_API_URL;
if (!API_URL) {
  throw new Error("Missing REACT_APP_API_URL environment variable");
}
const WEATHER_LOCATION = "vlieland-vliehorst";
const TIDE_LOCATIONS = [
  { label: "Vlieland", value: "vlieland" },
  { label: "Harlingen", value: "harlingen" },
  { label: "Terschelling", value: "terschelling" },
  { label: "Kornwerderzand", value: "kornwerderzand" },
  { label: "Texel", value: "texel" },
  { label: "Ameland", value: "ameland" },
];

const normalizeFirst = (payload) => {
  if (!payload) return null;
  if (Array.isArray(payload)) return payload[0] ?? null;
  if (Array.isArray(payload?.results)) return payload.results[0] ?? null;
  return payload;
};

const normalizeEvents = (payload) => {
  if (!payload) return [];
  if (Array.isArray(payload?.events)) return payload.events;
  if (Array.isArray(payload?.results)) return payload.results;
  if (Array.isArray(payload)) return payload;
  return [];
};

const formatTimestamp = (value) => {
  if (!value) return "—";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "—";
  return date.toLocaleString("nl-NL", {
    hour: "2-digit",
    minute: "2-digit",
    day: "2-digit",
    month: "short",
  });
};

const Metric = ({ icon: Icon, label, value, unit }) => (
  <div className="flex items-center gap-3 rounded-2xl bg-white/5 border border-white/10 p-4 shadow-md">
    <div className="rounded-xl bg-white/10 p-3 text-cyan-200">
      <Icon className="h-6 w-6" />
    </div>
    <div>
      <p className="text-sm uppercase tracking-wide text-slate-200/70">{label}</p>
      <p className="text-2xl font-semibold text-white">
        {value ?? "—"}
        {value !== undefined && value !== null && unit ? ` ${unit}` : ""}
      </p>
    </div>
  </div>
);

export default function Weather() {
  const [weather, setWeather] = useState(null);
  const [weatherError, setWeatherError] = useState("");
  const [loadingWeather, setLoadingWeather] = useState(true);

  const [tideLocation, setTideLocation] = useState(TIDE_LOCATIONS[0].value);
  const [tideEvents, setTideEvents] = useState([]);
  const [tideError, setTideError] = useState("");
  const [loadingTides, setLoadingTides] = useState(false);

  const weatherMetrics = useMemo(() => {
    if (!weather) return {};
    return {
      temperature: weather.temperature ?? weather.temp ?? weather.air_temperature,
      windSpeed: weather.wind_speed ?? weather.wind ?? weather.wind_speed_10m,
      gusts: weather.wind_gust ?? weather.gusts ?? weather.wind_gusts,
      waveHeight: weather.wave_height ?? weather.waveheight,
      sight: weather.sight ?? weather.visibility ?? weather.zicht,
      expectation: weather.verwachting ?? weather.forecast ?? weather.expectation,
      warnings: weather.warnings ?? weather.warning ?? weather.weather_warnings,
      updatedAt: weather.observed_at ?? weather.timestamp ?? weather.created_at,
      windUnit: weather.wind_speed_unit ?? "m/s",
      gustUnit: weather.wind_gust_unit ?? weather.wind_speed_unit ?? "m/s",
    };
  }, [weather]);

  useEffect(() => {
    let cancelled = false;
    const fetchWeather = async () => {
      try {
        setLoadingWeather(true);
        setWeatherError("");
        const res = await fetch(`${API_URL}/weather/?location=${WEATHER_LOCATION}`);
        if (!res.ok) throw new Error("Kon weerdata niet laden");
        const data = await res.json();
        if (cancelled) return;
        setWeather(normalizeFirst(data));
      } catch (error) {
        if (!cancelled) setWeatherError(error.message || "Onbekende fout");
      } finally {
        if (!cancelled) setLoadingWeather(false);
      }
    };

    fetchWeather();
    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    let cancelled = false;
    const fetchTides = async () => {
      try {
        setLoadingTides(true);
        setTideError("");
        const res = await fetch(`${API_URL}/tides/?location=${tideLocation}`);
        if (!res.ok) throw new Error("Kon getijden niet laden");
        const data = await res.json();
        if (cancelled) return;
        setTideEvents(normalizeEvents(data));
      } catch (error) {
        if (!cancelled) setTideError(error.message || "Onbekende fout");
      } finally {
        if (!cancelled) setLoadingTides(false);
      }
    };

    fetchTides();
    return () => {
      cancelled = true;
    };
  }, [tideLocation]);

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-900 via-slate-900 to-slate-950 text-white">
      <TopNav />

      <main className="pt-16 pb-28 px-4 md:px-6 max-w-5xl mx-auto space-y-6">
        <header className="rounded-3xl border border-white/10 bg-white/5 p-6 shadow-xl backdrop-blur">
          <p className="text-sm uppercase tracking-[0.2em] text-cyan-200/80 mb-2">
            Vlieland · Vliehorst
          </p>
          <h1 className="text-3xl md:text-4xl font-bold text-white">Weer en getijden</h1>
          <p className="text-slate-200/80 mt-2">
            Live vanuit de Django database. Backend haalt max. 16× per dag op uit Meteoserver;
            deze pagina leest wanneer je wilt.
          </p>
          <p className="text-xs text-slate-200/70 mt-3">
            {loadingWeather ? "" : `Bijgewerkt: ${formatTimestamp(weatherMetrics.updatedAt)}`}
          </p>
        </header>

        <section className="grid gap-4 md:grid-cols-2">
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <span className="rounded-full bg-cyan-500/15 p-3 text-cyan-200">
                  <CloudSun className="h-6 w-6" />
                </span>
                <div>
                  <p className="text-sm text-slate-200/70">Vlieland · Vliehorst</p>
                  <p className="text-xl font-semibold text-white">
                    {loadingWeather ? "Data laden..." : "Laatste meting"}
                  </p>
                </div>
              </div>
            </div>

            {weatherError && (
              <p className="rounded-xl border border-rose-200/30 bg-rose-500/10 p-3 text-sm text-rose-100">
                {weatherError}
              </p>
            )}

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <Metric
                icon={CloudSun}
                label="Temperatuur"
                value={
                  weatherMetrics.temperature !== undefined && weatherMetrics.temperature !== null
                    ? weatherMetrics.temperature
                    : null
                }
                unit="°C"
              />
              <Metric
                icon={Wind}
                label="Wind"
                value={
                  weatherMetrics.windSpeed !== undefined && weatherMetrics.windSpeed !== null
                    ? weatherMetrics.windSpeed
                    : null
                }
                unit={weatherMetrics.windUnit}
              />
              <Metric
                icon={Wind}
                label="Windstoten"
                value={
                  weatherMetrics.gusts !== undefined && weatherMetrics.gusts !== null
                    ? weatherMetrics.gusts
                    : null
                }
                unit={weatherMetrics.gustUnit}
              />
              <Metric
                icon={Waves}
                label="Golfhoogte"
                value={
                  weatherMetrics.waveHeight !== undefined && weatherMetrics.waveHeight !== null
                    ? weatherMetrics.waveHeight
                    : null
                }
                unit="m"
              />
              <div className="rounded-2xl bg-white/5 border border-white/10 p-4 shadow-md">
                <div className="flex items-center gap-3">
                  <div className="rounded-xl bg-white/10 p-3 text-cyan-200">
                    <Eye className="h-6 w-6" />
                  </div>
                  <div className="flex-1">
                    <p className="text-sm uppercase tracking-wide text-slate-200/70">Zicht</p>
                    <p className="text-2xl font-semibold text-white">
                      {weatherMetrics.sight ?? "—"}
                    </p>
                  </div>
                </div>
              </div>
            </div>

            <div className="rounded-2xl bg-white/5 border border-white/10 p-4 shadow-md">
              <div className="flex items-center gap-2 text-amber-200">
                <AlertTriangle className="h-5 w-5" />
                <p className="text-sm uppercase tracking-wide">Weerwaarschuwingen</p>
              </div>
              <p className="mt-2 text-sm text-slate-100">
                {weatherMetrics.warnings || "Geen actieve waarschuwingen bekend."}
              </p>
            </div>

            <div className="rounded-2xl bg-white/5 border border-white/10 p-4 shadow-md">
              <div className="flex items-center gap-3">
                <span className="rounded-xl bg-white/10 p-3 text-cyan-200">
                  <CloudSun className="h-6 w-6" />
                </span>
                <div>
                  <p className="text-sm uppercase tracking-wide text-slate-200/70">Verwachting</p>
                  <p className="text-base text-slate-100">
                    {weatherMetrics.expectation || "Geen verwachting beschikbaar."}
                  </p>
                </div>
              </div>
            </div>
          </div>

          <div className="rounded-3xl border border-white/10 bg-white/5 p-5 shadow-xl backdrop-blur">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <span className="rounded-full bg-cyan-500/15 p-3 text-cyan-200">
                  <Waves className="h-6 w-6" />
                </span>
                <div>
                  <p className="text-sm text-slate-200/70">Getijden</p>
                  <p className="text-xl font-semibold text-white">Kies station</p>
                </div>
              </div>
              {loadingTides && <span className="text-xs text-slate-200/70">Data laden...</span>}
            </div>

            <div className="mt-3 grid grid-cols-2 gap-2 sm:grid-cols-3">
              {TIDE_LOCATIONS.map((loc) => (
                <button
                  key={loc.value}
                  type="button"
                  onClick={() => setTideLocation(loc.value)}
                  className={`rounded-xl border px-3 py-2 text-sm transition ${
                    tideLocation === loc.value
                      ? "border-cyan-400 bg-cyan-500/20 text-white shadow"
                      : "border-white/10 bg-white/5 text-slate-200 hover:border-cyan-300/50"
                  }`}
                >
                  {loc.label}
                </button>
              ))}
            </div>

            {tideError && (
              <p className="mt-3 rounded-xl border border-rose-200/30 bg-rose-500/10 p-3 text-sm text-rose-100">
                {tideError}
              </p>
            )}

            <div className="mt-4 space-y-3">
              {(!loadingTides && tideEvents.length === 0) && (
                <p className="text-sm text-slate-200/70">Geen getijdedata beschikbaar voor deze locatie.</p>
              )}

              {tideEvents.slice(0, 6).map((event, idx) => (
                <div
                  key={`${event?.time || event?.timestamp || idx}-${idx}`}
                  className="flex items-center justify-between rounded-2xl border border-white/10 bg-white/5 px-4 py-3"
                >
                  <div>
                    <p className="text-sm uppercase tracking-wide text-slate-200/70">
                      {event.type || event.state || "Getij"}
                    </p>
                    <p className="text-lg font-semibold">
                      {event.height !== undefined && event.height !== null ? `${event.height} m` : "—"}
                    </p>
                  </div>
                  <p className="text-sm text-slate-200/80">
                    {formatTimestamp(event.time || event.datetime || event.timestamp)}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </section>
      </main>

      <BottomNav />
    </div>
  );
}
