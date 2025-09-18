import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";

export default function BlogDetail() {
  const { slug } = useParams();
  const [post, setPost] = useState(null);
  const [comments, setComments] = useState([]);
  const [newComment, setNewComment] = useState("");
  const [message, setMessage] = useState("");

  const token = localStorage.getItem("accessToken");

  useEffect(() => {
    fetch(`http://127.0.0.1:8000/api/posts/${slug}/`)
      .then(res => res.json())
      .then(data => setPost(data));

    fetch(`http://127.0.0.1:8000/api/comments/?post=${slug}`)
      .then(res => res.json())
      .then(data => setComments(data));
  }, [slug]);

  const handleCommentSubmit = async (e) => {
    e.preventDefault();
    if (!token) {
      setMessage("Je moet ingelogd zijn om een comment te plaatsen.");
      return;
    }

    const res = await fetch("http://127.0.0.1:8000/api/comments/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        post: post.id,
        content: newComment,
      }),
    });

    const data = await res.json();

    if (res.ok) {
      setComments([data, ...comments]);
      setNewComment("");
      setMessage("");
    } else {
      setMessage(data.detail || "Fout bij toevoegen comment");
    }
  };

  if (!post) return <p>Loading...</p>;

  return (
    <div className="p-6">
      <Link to="/" className="text-blue-600 hover:underline">← Terug</Link>
      <h1 className="text-3xl font-bold mb-2">{post.title}</h1>
      <p>{post.windspeed?.name}</p>
      <p>{post.winddirection?.name}</p>
      <p>{post.seastate?.name}</p>
      <p className="text-gray-600">
        Categorieën:{" "}
        {post.categories && post.categories.length > 0 ? (
          post.categories.map(cat => (
            <span key={cat.id} className="mr-2">
              {cat.name}
            </span>
          ))
        ) : (
          "Geen categorieën"
        )}
      </p>
      <p className="text-gray-500 mb-4">{new Date(post.created_at).toLocaleDateString()}</p>

      {post.image && (
        <img src={`${post.image}`} alt={post.title} className="mb-4 w-screen  object-cover rounded" />
      )}

      <div className="prose max-w-none mb-6" dangerouslySetInnerHTML={{ __html: post.content }} />
      

      <h2 className="text-2xl font-semibold mb-2">Reacties</h2>
      {message && <p className="text-red-600 mb-2">{message}</p>}

      <form onSubmit={handleCommentSubmit} className="mb-6">
        <textarea
          className="w-full border p-2 rounded mb-2"
          value={newComment}
          onChange={(e) => setNewComment(e.target.value)}
          placeholder={token ? "Schrijf een reactie..." : "Login om te reageren"}
          required
          disabled={!token}
        />
        <button type="submit" className="bg-blue-600 text-white px-4 py-2 rounded" disabled={!token}>
          Plaats reactie
        </button>
      </form>

      <div className="space-y-4">
        {comments.map(comment => (
          <div key={comment.id} className="border p-3 rounded">
            <p className="text-gray-700">{comment.content}</p>
            <p className="text-gray-500 text-sm">— {comment.author_username}, {new Date(comment.created_at).toLocaleDateString()}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
