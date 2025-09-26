import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";

export default function AlbumDetail() {
  const { id } = useParams();
  const [album, setAlbum] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    fetch(`http://127.0.0.1:8000/api/albums/${id}/`)
      .then(res => {
        if (!res.ok) throw new Error("Album niet gevonden");
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

  if (loading) return <p>Laden...</p>;
  if (error) return <p className="text-red-600">{error}</p>;

  return (
    <div className="p-6">
      <Link to="/" className="text-blue-600 hover:underline">← Terug</Link>

      <h1 className="text-3xl font-bold mb-2">{album.title}</h1>
      {album.description && <p className="text-gray-700 mb-4">{album.description}</p>}

      {album.post && (
        <p className="text-gray-600 mb-4">
          Gekoppeld aan post: <Link to={`/post/${album.post}`}>{album.post_title}</Link>
        </p>
      )}

      {album.cover_image && (
        <img
          src={album.cover_image}
          alt={album.title}
          className="w-full max-h-96 object-cover rounded mb-6"
        />
      )}

      <h2 className="text-2xl font-semibold mb-4">Foto’s</h2>
      {album.photos && album.photos.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {album.photos.map((photo, idx) => (
            <img
                key={idx}
                src={photo.image} // ⚡ hier gebruiken we de image property
                alt={photo.caption || `Foto ${idx + 1}`}
                className="w-full h-60 object-cover rounded shadow"
            />
            ))}
        </div>
        ) : (
        <p className="text-gray-500">Geen foto’s beschikbaar.</p>
        )}

    </div>
  );
}
