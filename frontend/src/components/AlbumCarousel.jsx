import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

export default function AlbumsCarousel() {
  const [albums, setAlbums] = useState([]);

  useEffect(() => {
    fetch("http://127.0.0.1:8000/api/albums/")
      .then(res => res.json())
      .then(data => {
        // sorteer op created_at desc en neem de laatste 5
        const latest = data.sort((a, b) => new Date(b.created_at) - new Date(a.created_at)).slice(0, 5);
        setAlbums(latest);
      });
  }, []);

  if (!albums.length) return <p className="p-4">Geen albums beschikbaar</p>;

  return (
    <section className="p-4">
      <h2 className="text-2xl font-bold mb-4">Laatste albums</h2>
      <div className="flex space-x-4 overflow-x-auto scrollbar-thin scrollbar-thumb-gray-400 scrollbar-track-gray-200">
        {albums.map(album => (
          <Link
            to={`/albums/${album.id}`}
            key={album.id}
            className="flex-shrink-0 w-60 rounded-xl overflow-hidden shadow hover:shadow-lg transition"
          >
            {album.cover_image ? (
              <img
                src={album.cover_image}
                alt={album.title}
                className="w-full h-40 object-cover"
              />
            ) : (
              <div className="w-full h-40 bg-gray-200 flex items-center justify-center">
                <span className="text-gray-500">Geen cover</span>
              </div>
            )}
            <div className="p-2 bg-white">
              <h3 className="font-semibold">{album.title}</h3>
            </div>
          </Link>
        ))}
      </div>
    </section>
  );
}
