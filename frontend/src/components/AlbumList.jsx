import React, { useEffect, useState } from "react";
import axios from "axios";
import { Link } from "react-router-dom";

export default function AlbumList() {
  const [albums, setAlbums] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    axios
      .get("http://127.0.0.1:8000/api/albums/") // pas dit aan naar jouw backend URL, bv. http://localhost:8000/api/albums/
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
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Link to="/" className="text-blue-600 hover:underline">← Terug</Link>
      {albums.map((album) => (
        <div
          key={album.id}
          className="rounded-2xl shadow-md bg-white p-4 hover:shadow-lg transition"
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

          <h2 className="text-xl font-semibold">{album.title}</h2>
          {album.post_title && (
            <p className="text-sm text-gray-600">
              Gekoppeld aan post: {album.post_title}
            </p>
          )}
          <p className="text-gray-700 text-sm mt-2">{album.description}</p>

          <h3 className="font-medium mt-3">Foto’s:</h3>
          <div className="grid grid-cols-3 gap-2 mt-2">
            {album.photos.slice(0, 3).map((photo) => (
              <img
                key={photo.id}
                src={photo.image}
                alt={photo.caption || "Foto"}
                className="w-full h-20 object-cover rounded-lg"
              />
            ))}
            {album.photos.length === 0 && (
              <span className="text-gray-400 text-sm col-span-3">
                Geen foto’s
              </span>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}
