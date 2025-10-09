import React, { useEffect, useState } from "react";
import axios from "axios";
import TopNav from "./TopNav";
import BottomNav from "./BottomNav";

const API_URL = "http://localhost:8000/api"; // pas aan indien nodig

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

  return (
    <div className="max-w-lg mx-auto mt-10 border rounded-lg shadow">
      <TopNav />
      <h2 className="text-2xl font-bold mb-4 text-center">Profiel</h2>

      {profile.avatar && (
        <div className="flex justify-center mb-4">
          <img
            src={profile.avatar}
            alt="Profielfoto"
            className="w-24 h-24 rounded-full object-cover"
          />
        </div>
      )}

      <form onSubmit={handleSubmit}>
  <label className="block mb-2">
    Gebruikersnaam
    <input
      type="text"
      name="username"
      placeholder={profile.username || "Gebruikersnaam"}
      disabled
      className="w-full border p-2 rounded bg-gray-100 text-gray-600"
    />
  </label>

  <label className="block mb-2">
    Voornaam
    <input
      type="text"
      name="first_name"
      placeholder={profile.first_name || "Voornaam"}
      onChange={handleChange}
      className="w-full border p-2 rounded"
    />
  </label>

  <label className="block mb-2">
    Achternaam
    <input
      type="text"
      name="last_name"
      placeholder={profile.last_name || "Achternaam"}
      onChange={handleChange}
      className="w-full border p-2 rounded"
    />
  </label>

  <label className="block mb-2">
    Email
    <input
      type="email"
      name="email"
      placeholder={profile.email || "E-mail"}
      onChange={handleChange}
      className="w-full border p-2 rounded"
    />
  </label>

  <label className="block mb-2">
    Profielfoto
    <input
      type="file"
      accept="image/*"
      onChange={handleFileChange}
      className="w-full border p-2 rounded"
    />
  </label>

  <button
    type="submit"
    className="w-full bg-blue-600 text-white py-2 rounded mt-4 hover:bg-blue-700"
  >
    Profiel Opslaan
  </button>
</form>


      {message && (
        <p className="text-center text-green-600 mt-4 font-medium">{message}</p>
      )}
      <BottomNav />
    </div>
  );
};

export default Profile;
