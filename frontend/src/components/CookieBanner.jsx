import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";

const STORAGE_KEY = "whereissam-cookie-banner-dismissed";

export default function CookieBanner() {
  const { t } = useTranslation();
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    try {
      const dismissed = window.localStorage.getItem(STORAGE_KEY);
      setIsVisible(dismissed !== "true");
    } catch {
      setIsVisible(true);
    }
  }, []);

  const handleClose = () => {
    try {
      window.localStorage.setItem(STORAGE_KEY, "true");
    } catch {
      // Ignore storage failures and still close the banner for this session.
    }
    setIsVisible(false);
  };

  if (!isVisible) {
    return null;
  }

  return (
    <aside className="fixed inset-x-0 bottom-0 z-50 px-3 pb-3 md:px-6 md:pb-6">
      <div className="mx-auto flex max-w-4xl flex-col gap-3 rounded-2xl border border-white/10 bg-slate-950/95 p-4 text-sm text-slate-100 shadow-2xl backdrop-blur md:flex-row md:items-center md:justify-between">
        <p className="leading-relaxed text-slate-200">
          {t("Deze website gebruikt Google Analytics-cookies om verkeer te meten.")}
        </p>
        <button
          type="button"
          onClick={handleClose}
          className="shrink-0 rounded-full bg-cyan-300 px-4 py-2 text-sm font-semibold text-slate-950 transition hover:bg-cyan-200"
        >
          {t("Sluiten")}
        </button>
      </div>
    </aside>
  );
}
