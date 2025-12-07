import React, { useEffect, useState } from "react";
import axios from "axios";
import TopNav from "./TopNav";
import BottomNav from "./BottomNav";
import { Navigate } from "react-router-dom";
import { User } from "lucide-react";

const API_URL = process.env.REACT_APP_API_URL;
if (!API_URL) {
  throw new Error("Missing REACT_APP_API_URL environment variable");
}
const MEDIA_URL = API_URL.replace(/\/api\/?$/, "");

const Profile = () => {
  const [profile, setProfile] = useState({
    username: "",
    email: "",
    first_name: "",
    last_name: "",
    avatar: null,
  });
  const [message, setMessage] = useState("");
  const [passwordData, setPasswordData] = useState({
    old_password: "",
    new_password: "",
  });

  const token = localStorage.getItem("accessToken");

  

  useEffect(() => {
    axios
      .get(`${API_URL}/profile/`, {
        headers: { Authorization: `Bearer ${token}` },
      })
      .then((res) => setProfile(res.data))
      .catch((err) => console.error(err));
  }, []);

  const handleChange = (e) => {
    setProfile({ ...profile, [e.target.name]: e.target.value });
  };

  const handleFileChange = (e) => {
    setProfile({ ...profile, avatar: e.target.files[0] });
  };

  const handleSubmit = (e) => {
  e.preventDefault();
  const formData = new FormData();

  if (profile.first_name) formData.append("first_name", profile.first_name);
  if (profile.last_name) formData.append("last_name", profile.last_name);
  if (profile.email) formData.append("email", profile.email);
  if (profile.avatar) formData.append("avatar", profile.avatar);

  axios
    .put(`${API_URL}/profile/`, formData, {
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "multipart/form-data",
      },
    })
    .then((res) => setMessage(res.data.detail))
    .catch((err) => console.error(err));
};


  const handlePasswordChange = (e) => {
    e.preventDefault();
    axios
      .post(`${API_URL}/change-password/`, passwordData, {
        headers: { Authorization: `Bearer ${token}` },
      })
      .then((res) => setMessage(res.data.detail))
      .catch((err) => setMessage(err.response?.data?.detail || "Fout bij wijzigen wachtwoord."));
  };

  if (!token) {
    return <Navigate to="/login" replace />; 
  }

  return (
    <section className="min-h-screen bg-gradient-to-b from-slate-900 via-slate-900 to-slate-950 text-white">
      <TopNav />
      <div className="max-w-10/12  mt-16 mx-4 border border-white/10 rounded-lg bg-white/5 px-4 shadow">
      <h2 className="text-2xl font-bold mb-4 mt-2 text-center text-white">Profiel</h2>

      <article className="flex justify-center mb-4 relative w-">
        {profile.avatar ? (
          <img
            src={`${MEDIA_URL}${profile.avatar}`}
            alt="Profielfoto"
            className="w-24 h-24 rounded-full object-cover shadow-lg ring-4 ring-cyan-800"
          />
        ) : (
          <div className="w-24 h-24 rounded-full bg-white/10 flex items-center justify-center shadow-lg ring-4 ring-cyan-800">
            <User size={48} className="text-slate-200" />
          </div>
        )}

        {/* Verborgen file input */}
        <input
          type="file"
          accept="image/*"
          id="avatarUpload"
          onChange={handleFileChange}
          className="hidden"
        />

        {/* Knop over de foto */}
        <label
          htmlFor="avatarUpload"
          className="absolute bottom-0 right-0 bg-cyan-700 text-white text-xs px-2 py-1 rounded-full cursor-pointer shadow-md hover:bg-cyan-600"
        >
          Wijzig
        </label>
      </article>
    <form onSubmit={handleSubmit} className="p-4">
      <label className="block mb-2">
        Gebruikersnaam
        <input
          type="text"
          name="username"
          placeholder={profile.username || "Gebruikersnaam"}
          disabled
          className="w-full border border-white/10 p-2 rounded bg-white/5 text-slate-200"
        />
      </label>

      <label className="block mb-2">
        Voornaam
        <input
          type="text"
          name="first_name"
          placeholder={profile.first_name || "Voornaam"}
          onChange={handleChange}
          className="w-full border border-white/10 p-2 rounded bg-white/5 text-slate-200"
        />
      </label>

      <label className="block mb-2">
        Achternaam
        <input
          type="text"
          name="last_name"
          placeholder={profile.last_name || "Achternaam"}
          onChange={handleChange}
          className="w-full border border-white/10 p-2 rounded bg-white/5 text-slate-200"
        />
      </label>

      <label className="block mb-2">
        Email
        <input
          type="email"
          name="email"
          placeholder={profile.email || "E-mail"}
          onChange={handleChange}
          className="w-full border border-white/10 p-2 rounded bg-white/5 text-slate-200"
        />
      </label>
      <button
        type="submit"
        className="w-full bg-cyan-700 text-white py-2 rounded mt-4 hover:bg-cyan-600"
      >
        Profiel Opslaan
      </button>
      <button
        onClick={() => {
          localStorage.removeItem("accessToken");
          window.location.href = "/login";  // of gebruik Navigate
        }}
        className="w-full bg-red-600 text-white py-2 rounded mt-4 hover:bg-red-500"
      >
        Uitloggen
    </button>
    </form>
    


      {message && (
        <p className="text-center text-green-300 mt-4 font-medium">{message}</p>
      )}
      </div>
      <BottomNav />
    </section>
  );
};

export default Profile;
