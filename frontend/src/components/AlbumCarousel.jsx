import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";

const API_URL = process.env.REACT_APP_API_URL;
if (!API_URL) {
  throw new Error("Missing REACT_APP_API_URL environment variable");
}

export default function AlbumsCarousel() {
  const { t } = useTranslation();
  const [albums, setAlbums] = useState([]);

  useEffect(() => {
    fetch(`${API_URL}/albums/`)
      .then(res => res.json())
      .then(data => {
        // sorteer op created_at desc en neem de laatste 5
        const latest = data.sort((a, b) => new Date(b.created_at) - new Date(a.created_at)).slice(0, 5);
        setAlbums(latest);
      });
  }, []);

  if (!albums.length) return <p className="p-4 text-white">{t("Geen albums beschikbaar")}</p>;

  return (
    <section className="p-4 text-white">
      <h2 className="text-2xl font-bold mb-4 text-white">{t("Laatste albums")}</h2>
      <div className="flex space-x-4 overflow-x-auto scrollbar-thin scrollbar-thumb-white/30 scrollbar-track-white/10">
        {albums.map(album => (
          <Link
            to={`/albums/${album.id}`}
            key={album.id}
            className="flex-shrink-0 w-60 rounded-xl overflow-hidden shadow hover:shadow-lg transition border border-white/10 bg-white/5"
          >
            {album.cover_image ? (
              <img
                src={album.cover_image}
                alt={album.title}
                className="w-full h-40 object-cover"
              />
            ) : (
              <div className="w-full h-40 bg-gray-200 flex items-center justify-center">
                <span className="text-gray-500">{t("Geen cover")}</span>
              </div>
            )}
            <div className="p-2 bg-white/5">
              <h3 className="font-semibold text-white">{album.title}</h3>
            </div>
          </Link>
        ))}
      </div>
    </section>
  );
}
