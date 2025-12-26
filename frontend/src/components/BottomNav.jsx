import { Cloud, FileText, Image, User, House } from "lucide-react";
import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";

export default function BottomNav() {
  const { t } = useTranslation();
  return (
    <nav className="fixed bottom-0 inset-x-0 w-full bg-slate-900/90 backdrop-blur border-t border-white/10 p-2 flex justify-around z-40 text-white md:hidden">
      <Link to="/weather" className="flex flex-col items-center text-slate-200 hover:text-cyan-200">
        <Cloud className="w-8 h-8" />
        <span className="text-xs">{t("Weer")}</span>
      </Link>

      <Link to="/posts" className="flex flex-col items-center text-slate-200 hover:text-cyan-200">
        <FileText className="w-8 h-8" />
        <span className="text-xs">{t("Blog")}</span>
      </Link>

      <Link to="/" className="flex flex-col items-center text-slate-200 hover:text-cyan-200">
        <House className="w-8 h-8" />
        <span className="text-xs">{t("Home")}</span>
      </Link> 

      <Link to="/albums" className="flex flex-col items-center text-slate-200 hover:text-cyan-200">
        <Image className="w-8 h-8" />
        <span className="text-xs">{t("Foto's")}</span>
      </Link>

      <Link to="/profiel" className="flex flex-col items-center text-slate-200 hover:text-cyan-200">
        <User className="w-8 h-8" />
        <span className="text-xs">{t("Profiel")}</span>
      </Link>
    </nav>
  );
}
