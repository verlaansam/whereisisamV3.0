import React, { useEffect, useState } from "react";
import axios from "axios";
import { Link } from "react-router-dom";
import TopNav from "./TopNav";
import BottomNav from "./BottomNav";

const API_URL = process.env.REACT_APP_API_URL;
if (!API_URL) {
  throw new Error("Missing REACT_APP_API_URL environment variable");
}

export default function AlbumList() {
  const [albums, setAlbums] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    axios
      .get(`${API_URL}/albums/`)
      .then((res) => {
        setAlbums(res.data);
        setLoading(false);
      })
      .catch((err) => {
        setError("Fout bij ophalen van albums.");
        setLoading(false);
      });
  }, []);

  if (loading) return <p>Laden...</p>;
  if (error) return <p>{error}</p>;

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-900 via-slate-900 to-slate-950 text-white">
      <TopNav />
      <section className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-16 mb-20 px-4">
        {albums.map((album) => (
          <Link
            key={album.id}
            to={`/albums/${album.id}`} // hier geef je de route naar de album-detailpagina
            className="rounded-2xl shadow-md bg-white/5 border border-white/10 p-4 m-2 hover:shadow-lg transition block"
          >
            {album.cover_image ? (
              <img
                src={album.cover_image}
                alt={album.title}
                className="rounded-xl w-full h-48 object-cover mb-3"
              />
            ) : (
              <div className="w-full h-48 bg-gray-200 flex items-center justify-center rounded-xl mb-3">
                <span className="text-gray-500">Geen cover</span>
              </div>
            )}

            <h2 className="text-xl font-semibold text-white">{album.title}</h2>
            <p className="text-slate-200 text-sm mt-2">{album.description}</p>

            <h3 className="font-medium mt-3">Foto’s:</h3>
            <div className="grid grid-cols-3 gap-2 mt-2">
              {album.photos.map((photo) => (
                <img
                  key={photo.id}
                  src={photo.image}
                  alt={photo.caption || "Foto"}
                  className="w-full h-20 object-cover rounded-lg"
                />
              ))}
              {album.photos.length === 0 && (
                <span className="text-slate-300 text-sm col-span-3">
                  Geen foto’s
                </span>
              )}
            </div>
          </Link>
        ))}
      </section>
      <BottomNav />
    </div>
  );
}
