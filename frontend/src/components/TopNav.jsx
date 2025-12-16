// TopNav.jsx
import { useMemo, useState } from 'react';
import { Menu, X } from "lucide-react";
import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";

export default function TopNav() {
    const [isOpen, setIsOpen] = useState(false);
    const { t, i18n } = useTranslation();

    const currentLang = useMemo(() => (i18n.language || "").split("-")[0], [i18n.language]);
    const changeLanguage = (lng) => {
        i18n.changeLanguage(lng);
        setIsOpen(false);
    };

    const FlagNL = ({ active }) => (
        <svg
            viewBox="0 0 3 2"
            className={`${active ? "w-10 h-8" : "w-8 h-6"} transition-all rounded shadow border border-white/20`}
            aria-hidden="true"
        >
            <rect width="3" height="2" fill="#21468B" />
            <rect width="3" height="1.333" fill="#FFF" />
            <rect width="3" height="0.666" fill="#AE1C28" />
        </svg>
    );

    const FlagUK = ({ active }) => (
        <svg
            viewBox="0 0 60 30"
            className={`${active ? "w-10 h-8" : "w-8 h-6"} transition-all rounded shadow border border-white/20`}
            aria-hidden="true"
        >
            <clipPath id="uk-clip">
                <path d="M0 0h60v30H0z" />
            </clipPath>
            <g clipPath="url(#uk-clip)">
                <path d="M0 0h60v30H0z" fill="#012169" />
                <path d="M0 0l60 30M60 0L0 30" stroke="#FFF" strokeWidth="6" />
                <path d="M0 0l60 30M60 0L0 30" stroke="#C8102E" strokeWidth="4" />
                <path d="M30 0v30M0 15h60" stroke="#FFF" strokeWidth="10" />
                <path d="M30 0v30M0 15h60" stroke="#C8102E" strokeWidth="6" />
            </g>
        </svg>
    );

    const FlagDE = ({ active }) => (
        <svg
            viewBox="0 0 5 3"
            className={`${active ? "w-10 h-8" : "w-8 h-6"} transition-all rounded shadow border border-white/20`}
            aria-hidden="true"
        >
            <rect width="5" height="3" fill="#FFCE00" />
            <rect width="5" height="2" fill="#D00" />
            <rect width="5" height="1" fill="#000" />
        </svg>
    );

    return (
        <main className="fixed top-0 w-full bg-slate-900/90 backdrop-blur border-b border-white/10 p-2 z-40 flex text-white">
            {/* Hamburger (Mobile) */}
            <button
            aria-label="Toggle menu"
            className="block md:hidden text-white"
            onClick={() => setIsOpen(!isOpen)}
            >
            {isOpen ? <X size={24} /> : <Menu size={24} />}
            </button>
            {/* Menu */}
            <ul
            className={`absolute top-6 left-0 w-10/12 mx-8 rounded-xl bg-slate-800 text-white flex flex-col p-2 shadow-lg transition-all duration-500 ${
                isOpen ? "opacity-100 translate-y-0" : "opacity-0 -translate-y-5 pointer-events-none"
            }`}
            >
                <li className="transition-all duration-500 delay-100">
                    <Link
                    to="/"
                    className="block m-2 p-3 rounded-xl hover:bg-slate-700 hover:text-cyan-200"
                    onClick={() => setIsOpen(false)}
                    >
                    {t("Home")}
                    </Link>
                </li>
                <li className="transition-all duration-500 delay-200">
                    <Link
                    to="/login"
                    className="block m-2 p-3 rounded-xl hover:bg-slate-700 hover:text-cyan-200"
                    onClick={() => setIsOpen(false)}
                    >
                    {t("Login")}
                    </Link>
                </li>
                <li className="transition-all duration-500 delay-300">
                    <Link
                    to="/register"
                    className="block m-2 p-3 rounded-xl hover:bg-slate-700 hover:text-cyan-200"
                    onClick={() => setIsOpen(false)}
                    >
                    {t("Register")}
                    </Link>
                </li>
            </ul>
            <h1 className="text-white pl-4 font-semibold">{t("Where is Sam")}</h1>

            <div className="ml-auto flex items-center gap-2 pr-2">
                <button
                    type="button"
                    onClick={() => changeLanguage("nl")}
                    className="overflow-hidden"
                    aria-label="Nederlands"
                >
                    <FlagNL active={currentLang === "nl"} />
                </button>
                <button
                    type="button"
                    onClick={() => changeLanguage("en")}
                    className="overflow-hidden"
                    aria-label="English"
                >
                    <FlagUK active={currentLang === "en"} />
                </button>
                <button
                    type="button"
                    onClick={() => changeLanguage("de")}
                    className="overflow-hidden"
                    aria-label="Deutsch"
                >
                    <FlagDE active={currentLang === "de"} />
                </button>
            </div>
        </main>
    );
}
