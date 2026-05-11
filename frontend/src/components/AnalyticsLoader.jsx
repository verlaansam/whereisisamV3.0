import { useEffect } from "react";

const GA_ID = "G-Q78X0BQFTB";

function injectAnalytics() {
  const existingScript = document.querySelector(`script[src*="googletagmanager.com/gtag/js?id=${GA_ID}"]`);
  if (window.__whereIsSamAnalyticsLoaded || existingScript) {
    window.__whereIsSamAnalyticsLoaded = true;
    return;
  }
  window.__whereIsSamAnalyticsLoaded = true;
  window.dataLayer = window.dataLayer || [];
  window.gtag = window.gtag || function gtag() {
    window.dataLayer.push(arguments);
  };
  window.gtag("js", new Date());
  window.gtag("config", GA_ID);

  const script = document.createElement("script");
  script.async = true;
  script.src = `https://www.googletagmanager.com/gtag/js?id=${GA_ID}`;
  document.head.appendChild(script);
}

export default function AnalyticsLoader() {
  useEffect(() => {
    const run = () => injectAnalytics();

    if ("requestIdleCallback" in window) {
      const idleId = window.requestIdleCallback(run, { timeout: 3000 });
      return () => window.cancelIdleCallback(idleId);
    }

    const timeoutId = window.setTimeout(run, 2000);
    return () => window.clearTimeout(timeoutId);
  }, []);

  return null;
}
