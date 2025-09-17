import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";

export default function BlogDetail() {
  const { slug } = useParams();
  const [post, setPost] = useState(null);

  useEffect(() => {
    fetch(`http://127.0.0.1:8000/api/posts/${slug}/`)
      .then(res => res.json())
      .then(data => setPost(data));
  }, [slug]);

  if (!post) return <p>Loading...</p>;

  return (
    <div className="p-6">
        <Link to="/" className="text-blue-600 hover:underline">← Terug</Link>
        <h1 className="text-3xl font-bold mb-2">{post.title}</h1>
        <p className="text-gray-500 mb-4">Geplaatst op: {new Date(post.created_at).toLocaleDateString()}</p>

        {post.image && (
            <img src={`${post.image}`} alt={post.title} className="mb-4 w-full h-96 object-cover rounded" />
        )}

        <div className="prose max-w-none" dangerouslySetInnerHTML={{ __html: post.content }} />
    </div>
  );
}
