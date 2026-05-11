// VesselFinder.jsx
import { useEffect, useRef, useState } from "react";
import { useTranslation } from "react-i18next";

export default function VesselFinder() {
  const { t } = useTranslation();
  const containerRef = useRef(null);
  const [shouldLoadIframe, setShouldLoadIframe] = useState(false);
  const [isMobileViewport, setIsMobileViewport] = useState(false);

  useEffect(() => {
    const mediaQuery = window.matchMedia("(max-width: 767px)");
    const applyMatch = () => setIsMobileViewport(mediaQuery.matches);

    applyMatch();
    if (mediaQuery.addEventListener) {
      mediaQuery.addEventListener("change", applyMatch);
      return () => mediaQuery.removeEventListener("change", applyMatch);
    }

    mediaQuery.addListener(applyMatch);
    return () => mediaQuery.removeListener(applyMatch);
  }, []);

  useEffect(() => {
    const node = containerRef.current;
    if (!node || shouldLoadIframe || isMobileViewport) {
      return undefined;
    }

    const observer = new IntersectionObserver(
      (entries) => {
        if (entries.some((entry) => entry.isIntersecting)) {
          setShouldLoadIframe(true);
          observer.disconnect();
        }
      },
      { rootMargin: "200px 0px" },
    );

    observer.observe(node);

    return () => observer.disconnect();
  }, [isMobileViewport, shouldLoadIframe]);

  return (
    <div ref={containerRef} className="bg-white/5 border-b border-white/10">
      {shouldLoadIframe ? (
        <iframe
          src="https://www.vesselfinder.com/aismap?zoom=undefined&lat=undefined&lon=undefined&width=100%25&height=400&names=false&mmsi=244700620&track=true&fleet=false&fleet_name=false&fleet_hide_old_positions=false&clicktoact=false&store_pos=true&ra=https%3A%2F%2Fwhereis.samverlaan.nl%2F"
          title={t("Vessel Tracker")}
          loading="lazy"
          referrerPolicy="no-referrer-when-downgrade"
          className="block w-full max-w-full h-[420px] sm:h-[26rem] md:h-[28rem] lg:h-[32rem]"
        />
      ) : (
        <div className="flex h-[420px] sm:h-[26rem] md:h-[28rem] lg:h-[32rem] flex-col items-center justify-center gap-4 bg-slate-900/40 px-6 text-center text-slate-300">
          <div className="space-y-2">
            <p className="text-lg font-medium text-white">{t("Vessel Tracker")}</p>
            <p className="text-sm text-slate-300">
              {isMobileViewport ? t("Laad de tracker op aanvraag om mobiel sneller te houden.") : t("Tracker wordt geladen zodra deze in beeld komt.")}
            </p>
          </div>
          {isMobileViewport && (
            <button
              type="button"
              onClick={() => setShouldLoadIframe(true)}
              className="rounded-full bg-cyan-300 px-5 py-2 text-sm font-semibold text-slate-950 transition hover:bg-cyan-200"
            >
              {t("Laad vessel tracker")}
            </button>
          )}
        </div>
      )}
    </div>
  );
}
