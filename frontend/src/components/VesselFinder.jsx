// VesselFinder.jsx
import Iframe from 'react-iframe';
import { useTranslation } from "react-i18next";

export default function VesselFinder() {
  const { t } = useTranslation();
  return (
    <div className="bg-white/5 border-b border-white/10">
      <Iframe
        url="https://www.vesselfinder.com/aismap?zoom=undefined&lat=undefined&lon=undefined&width=100%25&height=400&names=false&mmsi=244700620&track=true&fleet=false&fleet_name=false&fleet_hide_old_positions=false&clicktoact=false&store_pos=true&ra=http%3A%2F%2F127.0.0.1%3A5500%2Findex.html"
        title={t("Vessel Tracker")}
        height="380px"
        className="w-screen"
        display="block"
        position="relative"
      />
    </div>
  );
}
