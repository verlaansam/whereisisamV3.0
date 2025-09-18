import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

export default function BlogList() {
  const [posts, setPosts] = useState([]);

  useEffect(() => {
    fetch("http://127.0.0.1:8000/api/posts/")
      .then(res => res.json())
      .then(data => setPosts(data));
  }, []);

  return (
    <section className="-mt-12 bg-slate-50 rounded-3xl border-2 border-slate-300 shadow-xl">
      <h1 className="text-2xl font-bold  p-4">Logboek</h1>
      {posts.map(post => (
        <article key={post.id} className="mb-4 p-4 border rounded-lg shadow-sm"> 
          <Link to={`/posts/${post.slug}`} className="text-blue-600 hover:underline">
            {post.image && (
              <img src={`${post.image}`} alt={post.title} className="mb-2 w-full h-48 object-cover rounded" />
            )}
            <h2 className="text-xl font-semibold">
              {post.title}
            </h2>
            <p className="text-gray-700">{post.content.substring(0, 100)}...</p>
          </Link>
        </article>
        ))}
    </section>
  );
}