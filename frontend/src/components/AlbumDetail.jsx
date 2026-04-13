import { useEffect, useState } from "react";
import { useParams, Link, useNavigate } from "react-router-dom";
import TopNav from "./TopNav";
import BottomNav from "./BottomNav";
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
    throw new Error("Expected JSON response from album endpoint");
  }

  try {
    return JSON.parse(text);
  } catch {
    throw new Error("Invalid JSON response from album endpoint");
  }
}

export default function AlbumDetail() {
  const { t } = useTranslation();
  const { id } = useParams();
  const [album, setAlbum] = useState(null);
  const [selectedPhoto, setSelectedPhoto] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    fetch(endpoint(`albums/${id}/`))
      .then(parseJsonSafely)
      .then(data => {
        setAlbum(data);
        setLoading(false);
      })
      .catch(err => {
        setError(err.message === "HTTP 404" ? t("Album niet gevonden") : t("Fout bij ophalen van album."));
        setLoading(false);
      });
  }, [id, t]);

  useEffect(() => {
    if (!selectedPhoto) return undefined;

    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";

    const handleKeyDown = (event) => {
      if (event.key === "Escape") {
        setSelectedPhoto(null);
      }
    };

    window.addEventListener("keydown", handleKeyDown);

    return () => {
      document.body.style.overflow = previousOverflow;
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, [selectedPhoto]);

  if (loading) return <p>{t("Laden...")}</p>;
  if (error) return <p className="text-red-600">{error}</p>;

  return (
    <section className="min-h-screen bg-gradient-to-b from-slate-900 via-slate-900 to-slate-950 text-white">
      <TopNav />
      <div className="max-w-6xl lg:max-w-7xl mx-auto px-4 md:px-6 lg:px-8 pt-16 pb-24 space-y-6 min-w-0 w-full">
        <button
          onClick={() => navigate(-1)}
          className="text-cyan-100 hover:text-white transition font-medium inline-flex items-center gap-2"
        >
          <span aria-hidden>←</span> {t("← Terug")}
        </button>

        <article className="bg-white/5 border border-white/10 rounded-3xl shadow-xl overflow-hidden">
          {album.cover_image && (
            <img
              src={album.cover_image}
              alt={album.title}
              className="w-full h-64 md:h-80 object-cover"
            />
          )}

          <div className="p-5 md:p-7 space-y-4">
            <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-3">
              <h1 className="text-3xl font-bold text-white">{album.title}</h1>
              {album.post && (
                <p className="text-sm text-slate-200">
                  {t("Ook te zien bij:")}{" "}
                  <Link to={`/post/${album.post}`} className="text-cyan-200 underline">
                    {album.post_title}
                  </Link>
                </p>
              )}
            </div>

            {album.description && (
              <p className="text-slate-200 leading-relaxed">{album.description}</p>
            )}

            <div className="space-y-3">
              <h2 className="text-2xl font-semibold text-white">{t("Foto’s")}</h2>
              {album.photos && album.photos.length > 0 ? (
                <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
                  {album.photos.map((photo, idx) => (
                    <button
                      key={idx}
                      type="button"
                      onClick={() => setSelectedPhoto(photo)}
                      className="group overflow-hidden rounded-xl border border-white/10 shadow-lg text-left bg-transparent"
                    >
                      <img
                        src={photo.image}
                        alt={photo.caption || `${t("Foto’s")} ${idx + 1}`}
                        className="w-full h-56 object-cover transition duration-300 group-hover:scale-[1.02]"
                      />
                    </button>
                  ))}
                </div>
              ) : (
                <p className="text-slate-300">{t("Geen foto’s beschikbaar.")}</p>
              )}
            </div>
          </div>
        </article>
      </div>
      {selectedPhoto && (
        <div
          className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center px-4 py-8"
          onClick={() => setSelectedPhoto(null)}
          role="dialog"
          aria-modal="true"
          aria-label={t("Foto groot bekijken")}
        >
          <button
            type="button"
            onClick={() => setSelectedPhoto(null)}
            className="absolute top-5 right-5 h-11 w-11 rounded-full bg-zinc-700/90 text-zinc-100 text-2xl leading-none flex items-center justify-center hover:bg-zinc-600 transition"
            aria-label={t("Sluiten")}
          >
            ×
          </button>
          <div
            className="max-w-6xl w-full flex flex-col items-center gap-3"
            onClick={(event) => event.stopPropagation()}
          >
            <img
              src={selectedPhoto.image}
              alt={selectedPhoto.caption || t("Foto’s")}
              className="max-h-[85vh] w-auto max-w-full object-contain rounded-2xl shadow-2xl"
            />
            {selectedPhoto.caption && (
              <p className="text-sm text-slate-200 bg-black/30 px-4 py-2 rounded-full">
                {selectedPhoto.caption}
              </p>
            )}
          </div>
        </div>
      )}
      <BottomNav />
    </section>
  );
}
