import { useState } from "react";

export default function AuthForm() {
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
        setMessage("Voer een geldig e-mailadres in.");
        return;
      }
      if (password.length < 6) {
        setMessage("Wachtwoord moet minimaal 6 tekens bevatten.");
        return;
      }
    }

    try {
      if (isLogin) {
        // Login via JWT
        const res = await fetch("http://127.0.0.1:8000/api/token/", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ username, password }),
        });
        const data = await res.json();

        if (res.ok) {
          localStorage.setItem("accessToken", data.access);
          localStorage.setItem("refreshToken", data.refresh);
          setMessage("Succesvol ingelogd!");
        } else {
          setMessage(data.detail || "Fout bij login");
        }
      } else {
        // Register via API
        const res = await fetch("http://127.0.0.1:8000/api/register/", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ username, password, email }),
        });
        const data = await res.json();

        if (res.ok) {
          setMessage("Account aangemaakt! Je kunt nu inloggen.");
          setIsLogin(true);
          setEmail("");
          setPassword("");
        } else {
          setMessage(data.detail || "Fout bij registreren");
        }
      }
    } catch (error) {
      setMessage("Er is iets misgegaan, probeer het opnieuw.");
    }
  };

  return (
    <div className="max-w-md mx-auto p-6 border rounded shadow mt-10">
      <h2 className="text-2xl font-bold mb-4">{isLogin ? "Login" : "Register"}</h2>
      {message && <p className="mb-4 text-red-600">{message}</p>}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block mb-1">Gebruikersnaam</label>
          <input
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            className="w-full border p-2 rounded"
            required
          />
        </div>

        {!isLogin && (
          <div>
            <label className="block mb-1">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full border p-2 rounded"
              required
            />
          </div>
        )}

        <div>
          <label className="block mb-1">Wachtwoord</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full border p-2 rounded"
            required
          />
        </div>

        <button type="submit" className="w-full bg-blue-600 text-white p-2 rounded">
          {isLogin ? "Login" : "Register"}
        </button>
      </form>

      <p className="mt-4 text-center text-sm text-gray-600">
        {isLogin ? "Nog geen account?" : "Al een account?"}{" "}
        <button
          onClick={() => {
            setIsLogin(!isLogin);
            setMessage("");
          }}
          className="text-blue-600 underline"
        >
          {isLogin ? "Registreer" : "Login"}
        </button>
      </p>
    </div>
  );
}

