import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { User } from "lucide-react";
import BottomNav from "./BottomNav";

const API_URL = "http://127.0.0.1:8000/api";

export default function BlogDetail() {
  const { slug } = useParams();
  const [post, setPost] = useState(null);
  const [comments, setComments] = useState([]);
  const [newComment, setNewComment] = useState("");
  const [message, setMessage] = useState("");

  const token = localStorage.getItem("accessToken");

  // Fetch post en comments
  useEffect(() => {
  const fetchComments = async () => {
    try {
      const res = await fetch(`${API_URL}/comments/?post=${slug}`);
      const data = await res.json();
      console.log("Fetched comments:", data); // check wat hier staat
      if (Array.isArray(data)) {
        setComments(data);
      } else if (Array.isArray(data.results)) {
        setComments(data.results);
      } else {
        setComments([]); // fallback
      }
    } catch (err) {
      console.error(err);
      setComments([]);
    }
  };

  const fetchPost = async () => {
    try {
      const res = await fetch(`${API_URL}/posts/${slug}/`);
      const data = await res.json();
      setPost(data);
    } catch (err) {
      console.error(err);
    }
  };

  fetchPost();
  fetchComments();
}, [slug]);


  // Nieuwe comment plaatsen
  const handleCommentSubmit = async (e) => {
    e.preventDefault();
    if (!token) {
      setMessage("Je moet ingelogd zijn om een comment te plaatsen.");
      return;
    }

    try {
      const res = await fetch(`${API_URL}/comments/`, {
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
        // Alleen toevoegen aan deze post
        setComments([data, ...comments]);
        setNewComment("");
        setMessage("");
      } else {
        setMessage(data.detail || "Fout bij toevoegen comment");
      }
    } catch (err) {
      setMessage("Er is iets misgegaan.");
    }
  };

  if (!post) return <p>Loading...</p>;

  return (
    <div className="">
      <Link to="/" className="text-blue-600 hover:underline">← Terug</Link>

      {/* Post header */}
      <h1 className="text-3xl font-bold mb-2">{post.title}</h1>
      <p>Een windje van {post.windspeed?.name} uit het {post.winddirection?.name}</p>
      <p>met een {post.seastate?.name} zeetje</p>
      <p className="text-gray-600 mb-2">
        {post.categories?.length > 0
          ? post.categories.map(cat => <span key={cat.id} className="mr-2">{cat.name}</span>)
          : "Geen categorieën"}
      </p>
      <p className="text-gray-500 mb-4">{new Date(post.created_at).toLocaleDateString()}</p>
      <hr className="my-4" />

      {/* Post image */}
      {post.image && (
        <img src={post.image} alt={post.title} className="mb-4 w-full object-cover rounded" />
      )}

      {/* Post content */}
      <div className="prose max-w-none mb-6" dangerouslySetInnerHTML={{ __html: post.content }} />

      {/* Albums */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
        {post.albums?.map(album => (
          <Link key={album.id} to={`/albums/${album.id}`} className="rounded-lg shadow bg-white p-4 hover:shadow-lg">
            {album.cover_image ? (
              <img src={album.cover_image} alt={album.title} className="w-full h-40 object-cover rounded mb-2" />
            ) : (
              <div className="w-full h-40 bg-gray-200 rounded flex items-center justify-center mb-2">
                <span className="text-gray-500">Geen cover</span>
              </div>
            )}
            <h3 className="font-bold text-lg">{album.title}</h3>
          </Link>
        ))}
      </div>

      {/* Comments */}
      <section className="shadow p-4 mt-4 w-full">
        <h2 className="text-2xl font-semibold mb-2">Reacties</h2>
        <p className="text-gray-500 mb-2">De beste stuurlui staan aan wal</p>
        {message && <p className="text-red-600 mb-2">{message}</p>}

        {/* Comment form */}
        <form onSubmit={handleCommentSubmit} className="mb-6">
          <textarea
            className="w-full border p-2 rounded mb-2"
            value={newComment}
            onChange={e => setNewComment(e.target.value)}
            placeholder={token ? "Schrijf een reactie..." : "Login om te reageren"}
            required
            disabled={!token}
          />
          <button
            type="submit"
            className="bg-cyan-800 text-white px-4 py-2 rounded"
            disabled={!token}
          >
            Plaats reactie
          </button>
        </form>

        {/* Comment lijst */}
        <div className="space-y-4">
          {comments.map(comment => (
            <div key={comment.id} className="border p-3 rounded flex items-start space-x-3">
              {comment.author_avatar ? (
                <img src={comment.author_avatar} alt={comment.author_username} className="w-10 h-10 rounded-full object-cover" />
              ) : (
                <div className="w-10 h-10 rounded-full bg-gray-200 flex items-center justify-center">
                  <User className="w-6 h-6 text-gray-500" />
                </div>
              )}
              <div>
                <p className="text-gray-700">{comment.content}</p>
                <p className="text-gray-500 text-sm">
                  — {comment.author_username}, {new Date(comment.created_at).toLocaleDateString()}
                </p>
              </div>
            </div>
          ))}
        </div>
      </section>
      <BottomNav />
    </div>
  );
}