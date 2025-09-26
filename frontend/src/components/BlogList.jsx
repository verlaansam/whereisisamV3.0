import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

export default function BlogList() {
  const [posts, setPosts] = useState([]);

  useEffect(() => {
    fetch("http://127.0.0.1:8000/api/posts/")
      .then(res => res.json())
      .then(data => setPosts(data));
  }, []);

  if (!posts.length) return <p className="p-4">Geen posts beschikbaar</p>;

  const [latestPost, ...otherPosts] = posts; // meest recente
  const smallPosts = otherPosts.slice(0, 3); // maximaal 3

  return (
    <section className="-mt-12 bg-slate-50 rounded-3xl border-t-2 border-slate-300  p-4">
      <h1 className="text-2xl font-bold mb-4">Logboek</h1>

      {/* 🔹 Grote tile */}
      {latestPost && (
        <Link
          to={`/posts/${latestPost.slug}`}
          className="block mb-6 rounded-3xl overflow-hidden shadow-lg hover:shadow-2xl transition"
        >
          {latestPost.image && (
            <img
              src={latestPost.image}
              alt={latestPost.title}
              className="w-full h-72 object-cover"
            />
          )}
          <div className="p-4 bg-white">
            <h2 className="text-3xl font-bold mb-2">{latestPost.title}</h2>
            <p className="text-gray-700 line-clamp-3">{latestPost.content}</p>
          </div>
        </Link>
      )}

      {/* 🔹 Kleine list max 3 */}
      <div className="space-y-4">
        {smallPosts.map(post => (
          <Link
            to={`/posts/${post.slug}`}
            key={post.id}
            className="flex items-center bg-white p-3 rounded-lg shadow hover:shadow-md transition"
          >
            {post.image && (
              <img
                src={post.image}
                alt={post.title}
                className="w-24 h-24 object-cover rounded mr-4 flex-shrink-0"
              />
            )}
            <div>
              <h3 className="text-lg font-semibold">{post.title}</h3>
              <p className="text-gray-600 line-clamp-2">{post.content}</p>
            </div>
          </Link>
        ))}
      </div>
    </section>
  );
}
