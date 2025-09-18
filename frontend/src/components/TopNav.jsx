// TopNav.jsx
import { useState } from 'react';
import { Menu, X } from "lucide-react";
import { Link } from "react-router-dom";

export default function TopNav() {
    const [isOpen, setIsOpen] = useState(false);

    return (
        <main className="fixed top-0 w-full bg-slate-50 border-b  p-2 z-20 flex">
            {/* Hamburger (Mobile) */}
            <button
            aria-label="Toggle menu"
            className="block md:hidden text-slate-700"
            onClick={() => setIsOpen(!isOpen)}
            >
            {isOpen ? <X size={24} /> : <Menu size={24} />}
            </button>
            {/* Menu */}
            <ul
            className={`absolute top-6 left-0 w-10/12 mx-8 rounded-xl bg-slate-100 text-slate-700 flex flex-col p-2 shadow-lg transition-all duration-500 ${
                isOpen ? "opacity-100 translate-y-0" : "opacity-0 -translate-y-5 pointer-events-none"
            }`}
            >
                <li className="transition-all duration-500 delay-100">
                    <Link
                    to="/"
                    className="block m-2 p-3 rounded-xl hover:bg-slate-200 hover:text-cyan-800"
                    onClick={() => setIsOpen(false)}
                    >
                    Home
                    </Link>
                </li>
                <li className="transition-all duration-500 delay-200">
                    <Link
                    to="/login"
                    className="block m-2 p-3 rounded-xl hover:bg-slate-200 hover:text-cyan-800"
                    onClick={() => setIsOpen(false)}
                    >
                    Login
                    </Link>
                </li>
                <li className="transition-all duration-500 delay-300">
                    <Link
                    to="/register"
                    className="block m-2 p-3 rounded-xl hover:bg-slate-200 hover:text-cyan-800"
                    onClick={() => setIsOpen(false)}
                    >
                    Register
                    </Link>
                </li>
            </ul>
            <h1 className="text-slate-700 pl-4">Where is sam</h1>
        </main>
    );
}