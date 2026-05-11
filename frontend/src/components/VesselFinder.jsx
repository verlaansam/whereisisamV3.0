// VesselFinder.jsx
import { useEffect, useRef, useState } from "react";
import { useTranslation } from "react-i18next";

export default function VesselFinder() {
  const { t } = useTranslation();
  const containerRef = useRef(null);
  const [shouldLoadIframe, setShouldLoadIframe] = useState(false);

  useEffect(() => {
    const node = containerRef.current;
    if (!node || shouldLoadIframe) {
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
  }, [shouldLoadIframe]);

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
        <div className="flex h-[420px] sm:h-[26rem] md:h-[28rem] lg:h-[32rem] items-center justify-center bg-slate-900/40 text-slate-300">
          {t("Vessel Tracker")}
        </div>
      )}
    </div>
  );
}
