import { useEffect, useMemo, useState } from "react";
import { AlertTriangle, CloudSun, Eye, Waves, Wind } from "lucide-react";
import BottomNav from "./BottomNav";
import TopNav from "./TopNav";
import { useTranslation } from "react-i18next";

//python manage.py fetch_weather_vlieland max 5keer per dag in prod

const API_URL = process.env.REACT_APP_API_URL;
if (!API_URL) {
  throw new Error("Missing REACT_APP_API_URL environment variable");
}
const endpoint = (path) => `${API_URL.replace(/\/$/, "")}/${path.replace(/^\//, "")}`;
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
  const { t } = useTranslation();
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
      updatedAt: weather.recorded_at,
    };
  }, [weather]);

  useEffect(() => {
    let cancelled = false;
    const fetchWeather = async () => {
      try {
        setLoadingWeather(true);
        setWeatherError("");
        const res = await fetch(endpoint("weather/?limit=1"));
        if (!res.ok) throw new Error(`Kon weerdata niet laden (${res.status})`);
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
    // Embed Windguru widget
    const widgetId = "wg_fwdg_500860_100_1765737296177";
    const container = document.getElementById(widgetId);
    if (container) container.innerHTML = "";

    // Avoid double-injecting in StrictMode/dev
    if (window.__windguruWidgetLoaded) {
      return undefined;
    }

    const script = document.createElement("script");
    script.id = `${widgetId}-script`;
    script.src =
      "https://www.windguru.cz/js/widget.php?" +
      [
        "s=500860",
        "m=100",
        `uid=${widgetId}`,
        "wj=knots",
        "tj=c",
        "waj=m",
        "tij=cm",
        "odh=0",
        "doh=24",
        "fhours=240",
        "hrsm=1",
        "vt=forecasts",
        "lng=nl",
        "idbs=1",
        "p=WINDSPD,GUST,SMER,TMPE,WCHILL,CDC,APCP1s,SLP",
      ].join("&");
    script.async = true;
    document.body.appendChild(script);
    window.__windguruWidgetLoaded = true;

    return () => {
      script.remove();
      const widgetContainer = document.getElementById(widgetId);
      if (widgetContainer) widgetContainer.innerHTML = "";
    };
  }, []);

  useEffect(() => {
    let cancelled = false;
    const fetchTides = async () => {
      try {
        setLoadingTides(true);
        setTideError("");
        const res = await fetch(endpoint(`tides/?location=${encodeURIComponent(tideLocation)}&limit=4`));
        if (!res.ok) throw new Error(`Kon getijden niet laden (${res.status})`);
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

      <main className="pt-16 pb-28 px-4 md:px-6 lg:px-8 max-w-6xl lg:max-w-7xl mx-auto space-y-6 min-w-0 w-full">
        <header className="rounded-3xl border border-white/10 bg-white/5 p-6 shadow-xl backdrop-blur">
          <p className="text-sm uppercase tracking-[0.2em] text-cyan-200/80 mb-2">
            Vlieland · Vliehorst
          </p>
          <h1 className="text-3xl md:text-4xl font-bold text-white">{t("Weer en getijden")}</h1>
          <p className="text-slate-200/80 mt-2">
            {t("Live weer op vlieland. Data van KNMI")}
          </p>
          <p className="text-xs text-slate-200/70 mt-3">
            {loadingWeather ? "" : `${t("Bijgewerkt")}: ${formatTimestamp(weatherMetrics.updatedAt)}`}
          </p>
        </header>

        <section className="grid gap-4 md:grid-cols-2 lg:grid-cols-[1.1fr,0.9fr]">
          <div className="space-y-3">
            <div className="rounded-2xl bg-white/5 border border-white/10 p-4 shadow-md">
              <div className="flex items-center gap-3 mb-2">
                <span className="rounded-xl bg-white/10 p-3 text-cyan-200">
                  <Wind className="h-6 w-6" />
                </span>
                <div>
                  <p className="text-sm uppercase tracking-wide text-slate-200/70">Windguru</p>
                  <p className="text-base text-slate-100">{t("5-daagse wind en golf verwachting")}</p>
                </div>
              </div>

            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <span className="rounded-full bg-cyan-500/15 p-3 text-cyan-200">
                  <CloudSun className="h-6 w-6" />
                </span>
                <div>
                  <p className="text-sm text-slate-200/70">Vlieland · Vliehorst</p>
                  <p className="text-xl font-semibold text-white">
                    {loadingWeather ? t("Data laden...") : t("Laatste meting")}
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
                label={t("Temperatuur")}
                value={
                  weatherMetrics.temperature !== undefined && weatherMetrics.temperature !== null
                    ? weatherMetrics.temperature
                    : null
                }
                unit="°C"
              />
              <Metric
                icon={Wind}
                label={t("Wind")}
                value={
                  weatherMetrics.windSpeed !== undefined && weatherMetrics.windSpeed !== null
                    ? weatherMetrics.windSpeed
                    : null
                }
                unit="kn"
              />
              <Metric
                icon={Wind}
                label={t("Windstoten")}
                value={
                  weatherMetrics.gusts !== undefined && weatherMetrics.gusts !== null
                    ? weatherMetrics.gusts
                    : null
                }
                unit="kn"
              />
              <Metric
                icon={Waves}
                label={t("Golfhoogte")}
                value={
                  weatherMetrics.waveHeight !== undefined && weatherMetrics.waveHeight !== null
                    ? weatherMetrics.waveHeight
                    : null
                }
                unit="m"
              />
              <Metric
                icon={Eye}
                label={t("zicht")}
                value={
                  weatherMetrics.sight !== undefined && weatherMetrics.sight !== null
                    ? weatherMetrics.sight
                    : null
                }
                unit="nm"
              />
            </div>

            <div className="rounded-2xl bg-white/5 border border-white/10 p-4 shadow-md">
              <div className="flex items-center gap-2 text-amber-200">
                <AlertTriangle className="h-5 w-5" />
                <p className="text-sm uppercase tracking-wide">{t("Weerwaarschuwingen")}</p>
              </div>
              <p className="mt-2 text-sm text-slate-100">
                {weatherMetrics.warnings || t("Geen actieve waarschuwingen bekend.")}
              </p>
            </div>

            <div className="rounded-2xl bg-white/5 border border-white/10 p-4 shadow-md">
              <div className="flex items-center gap-3">
                <span className="rounded-xl bg-white/10 p-3 text-cyan-200">
                  <CloudSun className="h-6 w-6" />
                </span>
                <div>
                  <p className="text-sm uppercase tracking-wide text-slate-200/70">{t("Verwachting")}</p>
                  <p className="text-base text-slate-100">
                    {weatherMetrics.expectation || t("Geen verwachting beschikbaar.")}
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
                  <p className="text-sm text-slate-200/70">{t("Getijden")}</p>
                  <p className="text-xl font-semibold text-white">{t("Kies station")}</p>
                </div>
              </div>
              {loadingTides && <span className="text-xs text-slate-200/70">{t("Data laden...")}</span>}
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
                <p className="text-sm text-slate-200/70">{t("Geen getijdedata beschikbaar voor deze locatie.")}</p>
              )}

              {tideEvents.slice(0, 4).map((event, idx) => (
                <div
                  key={`${event?.time || event?.timestamp || idx}-${idx}`}
                  className="flex items-center justify-between rounded-2xl border border-white/10 bg-white/5 px-4 py-3"
                >
                  <div>
                    <p className="text-sm uppercase tracking-wide text-slate-200/70">
                      {event.type || event.state || "Getij"}
                    </p>
                    <p className="text-sm text-slate-200/80">
                    {formatTimestamp(event.time || event.datetime || event.timestamp)}
                  </p>
                  </div>
                  <p className="text-lg font-semibold">
                      {event.height !== undefined && event.height !== null ? `${event.height} m` : "—"}
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
