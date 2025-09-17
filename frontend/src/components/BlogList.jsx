import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import AuthForm from "./AuthForm";

export default function BlogList() {
  const [posts, setPosts] = useState([]);

  useEffect(() => {
    fetch("http://127.0.0.1:8000/api/posts/")
      .then(res => res.json())
      .then(data => setPosts(data));
  }, []);

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">Blog</h1>
      {posts.map(post => (
        <div key={post.id} className="mb-4 p-4 border rounded-lg shadow-sm">
            {post.image && (
            <img src={`${post.image}`} alt={post.title} className="mb-2 w-full h-48 object-cover rounded" />
            )}
            <h2 className="text-xl font-semibold">
            <Link to={`/posts/${post.slug}`} className="text-blue-600 hover:underline">
                {post.title}
            </Link>
            </h2>
            <p className="text-gray-700">{post.content.substring(0, 100)}...</p>
        </div>
        ))}
      <AuthForm/>
    </div>
  );
}