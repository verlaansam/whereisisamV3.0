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
        <header className="fixed top-0 inset-x-0 z-40 bg-slate-900/90 backdrop-blur border-b border-white/10 text-white">
            <div className="mx-auto max-w-screen px-3 md:px-6 lg:px-8 flex flex-wrap items-center gap-3 md:gap-4 py-2 md:py-3 min-w-0">
                {/* Hamburger (Mobile) */}
                <button
                    aria-label="Toggle menu"
                    className="block md:hidden text-white"
                    onClick={() => setIsOpen(!isOpen)}
                >
                    {isOpen ? <X size={24} /> : <Menu size={24} />}
                </button>

                <Link to="/" className="text-lg font-semibold tracking-tight hover:text-cyan-200 transition min-w-0 max-w-[45%] truncate">
                    {t("Where is Sam")}
                </Link>

                <nav className="hidden md:flex items-center gap-1 ml-4 flex-wrap">
                    {[
                        { to: "/", label: t("Home") },
                        { to: "/login", label: t("Login") },
                        { to: "/register", label: t("Register") },
                        { to: "/posts", label: t("Blog") },
                        { to: "/albums", label: t("Foto's") },
                        { to: "/weather", label: t("Weer") },
                        { to: "/profiel", label: t("Profiel") },
                    ].map((item) => (
                        <Link
                            key={item.to}
                            to={item.to}
                            className="px-3 py-2 rounded-xl text-sm font-medium text-slate-100 hover:text-cyan-200 hover:bg-white/5 transition"
                        >
                            {item.label}
                        </Link>
                    ))}
                </nav>

                {/* Mobile dropdown */}
                <ul
                    className={`absolute left-1/2 top-14 w-[90%] max-w-md -translate-x-1/2 rounded-2xl bg-slate-800 text-white flex flex-col p-3 shadow-2xl transition-all duration-500 md:hidden ${
                        isOpen ? "opacity-100 translate-y-0" : "opacity-0 -translate-y-3 pointer-events-none"
                    }`}
                >
                    {[
                        { to: "/", label: t("Home") },
                        { to: "/login", label: t("Login") },
                        { to: "/register", label: t("Register") },
                        { to: "/posts", label: t("Blog") },
                        { to: "/albums", label: t("Foto's") },
                        { to: "/weather", label: t("Weer") },
                    ].map((item, idx) => (
                        <li key={item.to} className="transition-all duration-500" style={{ transitionDelay: `${50 * idx}ms` }}>
                            <Link
                                to={item.to}
                                className="block m-1 p-3 rounded-xl hover:bg-slate-700 hover:text-cyan-200"
                                onClick={() => setIsOpen(false)}
                            >
                                {item.label}
                            </Link>
                        </li>
                    ))}
                </ul>

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
            </div>
        </header>
    );
}
