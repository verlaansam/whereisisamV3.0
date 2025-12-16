import { useEffect, useState } from "react";
import { useParams, Link, useNavigate } from "react-router-dom";
import TopNav from "./TopNav";
import BottomNav from "./BottomNav";
import { useTranslation } from "react-i18next";

const API_URL = process.env.REACT_APP_API_URL;
if (!API_URL) {
  throw new Error("Missing REACT_APP_API_URL environment variable");
}

export default function AlbumDetail() {
  const { t } = useTranslation();
  const { id } = useParams();
  const [album, setAlbum] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    fetch(`${API_URL}/albums/${id}/`)
      .then(res => {
        if (!res.ok) throw new Error(t("Album niet gevonden"));
        return res.json();
      })
      .then(data => {
        setAlbum(data);
        setLoading(false);
      })
      .catch(err => {
        setError(err.message);
        setLoading(false);
      });
  }, [id]);

  if (loading) return <p>{t("Laden...")}</p>;
  if (error) return <p className="text-red-600">{error}</p>;

  return (
    <section className="">
      <TopNav />
      <section className="p-4 mt-8">
      <button onClick={() => navigate(-1)} className="text-cyan-800 hover:underline">{t("← Terug")}</button>
      {album.cover_image && (
        <img
          src={album.cover_image}
          alt={album.title}
          className="w-full max-h-36 object-cover rounded mb-6"
        />
      )}
      <h1 className="text-3xl font-bold">{album.title}</h1>
      {album.post && (
        <p className="text-gray-600 mb-2">
          {t("Ook te zien bij:")} <Link to={`/post/${album.post}`}>{album.post_title}</Link>
        </p>
      )}
      {album.description && <p className="text-gray-700 mb-4">{album.description}</p>}

      <h2 className="text-2xl font-semibold mb-4 text-gray-600">{t("Foto’s")}</h2>
      {album.photos && album.photos.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {album.photos.map((photo, idx) => (
            <img
                key={idx}
                src={photo.image} // ⚡ hier gebruiken we de image property
                alt={photo.caption || `${t("Foto’s")} ${idx + 1}`}
                className="w-full h-60 object-cover rounded shadow"
            />
            ))}
        </div>
        ) : (
        <p className="text-gray-500">{t("Geen foto’s beschikbaar.")}</p>
        )}
        </section>
    <BottomNav />
    </section>
  );
}
