import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";

const API_URL = process.env.REACT_APP_API_URL;
if (!API_URL) {
  throw new Error("Missing REACT_APP_API_URL environment variable");
}

const endpoint = (path) => `${API_URL.replace(/\/$/, "")}/${path.replace(/^\//, "")}`;

async function parseJsonSafely(res) {
  const contentType = res.headers.get("content-type") || "";
  const text = await res.text();

  if (!res.ok) {
    throw new Error(`HTTP ${res.status}`);
  }

  if (!contentType.includes("application/json")) {
    throw new Error("Expected JSON response from albums endpoint");
  }

  try {
    return JSON.parse(text);
  } catch {
    throw new Error("Invalid JSON response from albums endpoint");
  }
}

export default function AlbumsCarousel() {
  const { t } = useTranslation();
  const [albums, setAlbums] = useState([]);
  const [error, setError] = useState(false);

  useEffect(() => {
    fetch(endpoint("albums/"))
      .then(parseJsonSafely)
      .then(data => {
        // sorteer op created_at desc en neem de laatste 5
        const safeData = Array.isArray(data) ? data : [];
        const latest = safeData.sort((a, b) => new Date(b.created_at) - new Date(a.created_at)).slice(0, 5);
        setAlbums(latest);
      })
      .catch(() => setError(true));
  }, []);

  if (error) return <p className="p-4 text-red-300">{t("Fout bij ophalen van albums.")}</p>;

  if (!albums.length) return <p className="p-4 text-white">{t("Geen albums beschikbaar")}</p>;

  return (
    <section className="p-4 md:p-6 text-white rounded-3xl border border-white/10 bg-white/5 shadow-lg">
      <h2 className="text-2xl font-bold mb-4 text-white">{t("Laatste albums")}</h2>
      <div className="flex space-x-3 overflow-x-auto scrollbar-thin scrollbar-thumb-white/30 scrollbar-track-white/10 sm:grid  lg:grid-cols-3 md:gap-4 md:space-x-0 md:overflow-visible min-w-0 max-w-full">
        {albums.map(album => (
          <Link
            to={`/albums/${album.id}`}
            key={album.id}
            className="flex-shrink-0 w-52 sm:w-full rounded-xl overflow-hidden shadow hover:shadow-lg transition border border-white/10 bg-white/5 min-w-0 max-w-full"
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
