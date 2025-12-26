import { useState } from "react";
import TopNav from "./TopNav";
import BottomNav from "./BottomNav";
import { useTranslation } from "react-i18next";

const API_URL = process.env.REACT_APP_API_URL;
if (!API_URL) {
  throw new Error("Missing REACT_APP_API_URL environment variable");
}

export default function AuthForm() {
  const { t } = useTranslation();
  const [isLogin, setIsLogin] = useState(true); // true = login, false = register
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [email, setEmail] = useState("");
  const [message, setMessage] = useState("");

  // Validatiefunctie voor email
  const isValidEmail = (email) => {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    // Client-side validatie bij registratie
    if (!isLogin) {
      if (!isValidEmail(email)) {
        setMessage(t("Voer een geldig e-mailadres in."));
        return;
      }
      if (password.length < 6) {
        setMessage(t("Wachtwoord moet minimaal 6 tekens bevatten."));
        return;
      }
    }

    try {
      if (isLogin) {
        // Login via JWT
        const res = await fetch(`${API_URL}/token/`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ username, password }),
        });
        const data = await res.json();

        if (res.ok) {
          localStorage.setItem("accessToken", data.access);
          localStorage.setItem("refreshToken", data.refresh);
          setMessage(t("Succesvol ingelogd!"));
        } else {
          setMessage(data.detail || t("Fout bij login"));
        }
      } else {
        // Register via API
        const res = await fetch(`${API_URL}/register/`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ username, password, email }),
        });
        const data = await res.json();

        if (res.ok) {
          setMessage(t("Account aangemaakt! Je kunt nu inloggen."));
          setIsLogin(true);
          setEmail("");
          setPassword("");
        } else {
          setMessage(data.detail || t("Fout bij registreren"));
        }
      }
    } catch (error) {
      setMessage(t("Er is iets misgegaan, probeer het opnieuw."));
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-900 via-slate-900 to-slate-950 text-white">
      <TopNav />
      <section className="max-w-md lg:max-w-lg mx-auto mt-16 md:mt-20 px-4 md:px-0 pb-24 min-w-0 w-full">
        <div className="p-6 bg-white/5 border border-white/10 rounded-2xl shadow">
        <h2 className="text-2xl font-bold mb-4 text-white">{isLogin ? t("Login") : t("Register")}</h2>
        {message && <p className="mb-4 text-rose-300">{message}</p>}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block mb-1 text-slate-200">{t("Gebruikersnaam")}</label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full border border-white/10 bg-white/5 text-white p-2 rounded"
              required
            />
          </div>

          {!isLogin && (
            <div>
              <label className="block mb-1 text-slate-200">{t("Email")}</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full border border-white/10 bg-white/5 text-white p-2 rounded"
                required
              />
            </div>
          )}

          <div>
            <label className="block mb-1 text-slate-200">{t("Wachtwoord")}</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full border border-white/10 bg-white/5 text-white p-2 rounded"
              required
            />
          </div>

          <button type="submit" className="w-full bg-cyan-700 hover:bg-cyan-600 text-white p-2 rounded">
            {isLogin ? t("Login") : t("Register")}
          </button>
        </form>

        <p className="mt-4 text-center text-sm text-slate-300">
          {isLogin ? t("Nog geen account?") : t("Al een account?")}{" "}
          <button
            onClick={() => {
              setIsLogin(!isLogin);
              setMessage("");
            }}
            className="text-cyan-200 underline"
          >
            {isLogin ? t("Registreer") : t("Login")}
          </button>
        </p>
        </div>
      </section>
      <BottomNav />
    </div>
  );
}
