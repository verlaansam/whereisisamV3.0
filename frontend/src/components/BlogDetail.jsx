import { useEffect, useMemo, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { Share2, User } from "lucide-react";
import BottomNav from "./BottomNav";
import TopNav from "./TopNav";

const API_URL = process.env.REACT_APP_API_URL;
if (!API_URL) {
  throw new Error("Missing REACT_APP_API_URL environment variable");
}

export default function BlogDetail() {
  const { slug } = useParams();
  const [post, setPost] = useState(null);
  const [comments, setComments] = useState([]);
  const [newComment, setNewComment] = useState("");
  const [message, setMessage] = useState("");
  const navigate = useNavigate();

  const token = localStorage.getItem("accessToken");
  const shareUrl = useMemo(() => `${window.location.origin}/posts/${slug}`, [slug]);

  useEffect(() => {
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
  }, [slug]);

  useEffect(() => {
    if (!post?.id) return;
    const fetchComments = async () => {
      try {
        const res = await fetch(`${API_URL}/comments/?post=${post.id}`);
        const data = await res.json();
        if (Array.isArray(data)) {
          setComments(data);
        } else if (Array.isArray(data.results)) {
          setComments(data.results);
        } else {
          setComments([]);
        }
      } catch (err) {
        console.error(err);
        setComments([]);
      }
    };
    fetchComments();
  }, [post?.id]);

  const handleShare = (platform) => {
    const encodedUrl = encodeURIComponent(shareUrl);
    const encodedTitle = encodeURIComponent(post?.title || "");

    const shareLinks = {
      facebook: `https://www.facebook.com/sharer/sharer.php?u=${encodedUrl}`,
      instagram: `https://www.instagram.com/?url=${encodedUrl}`,
      x: `https://x.com/intent/tweet?url=${encodedUrl}&text=${encodedTitle}`,
      whatsapp: `https://api.whatsapp.com/send?text=${encodedTitle}%20${encodedUrl}`,
    };

    const target = shareLinks[platform];
    if (target) {
      window.open(target, "_blank", "noopener,noreferrer");
    }
  };

  const handleCommentSubmit = async (e) => {
    e.preventDefault();
    if (!token) {
      setMessage("Login of maak een account aan om een comment te plaatsen.");
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

  if (!post) return <p className="p-4 text-white">Loading...</p>;

  return (
    <section className="min-h-screen bg-gradient-to-b from-slate-900 via-slate-900 to-slate-950 text-white">
      <TopNav />
      <article className="max-w-4xl mx-auto mt-16 mb-20 px-4">
        <button
          onClick={() => navigate(-1)}
          className="text-cyan-100 hover:text-white transition font-medium mb-4 inline-flex items-center gap-2"
        >
          <span aria-hidden>←</span> Terug
        </button>

        <section className="bg-slate-900/80 border border-white/10 rounded-3xl shadow-2xl overflow-hidden backdrop-blur">
          <div className="relative h-64 md:h-96">
            {post.image ? (
              <img
                src={post.image}
                alt={post.title}
                className="absolute inset-0 w-full h-full object-cover"
              />
            ) : (
              <div className="absolute inset-0 w-full h-full bg-gradient-to-br from-slate-900 via-slate-800 to-cyan-800" />
            )}
            <div className="absolute inset-0 bg-gradient-to-t from-slate-900/80 via-slate-900/20 to-transparent" />
            <div className="absolute inset-0 flex flex-col justify-end p-6 md:p-8 text-white space-y-3">
              <h1 className="text-3xl md:text-4xl font-bold leading-tight drop-shadow">
                {post.title}
              </h1>
              <div className="flex flex-wrap gap-3 text-sm text-white/85">
                {post.author?.username && (
                  <span className="text-whtie/85">
                    Door {post.author.username}
                  </span>
                )}
                <span>{new Date(post.created_at).toLocaleDateString()}</span>
              </div>
            </div>
          </div>

          <div className="p-6 md:p-8 space-y-6">
            <div className="flex flex-wrap gap-2">
              {post.categories?.length ? (
                post.categories.map(cat => (
                  <span
                    key={cat.id}
                    className="bg-white/10 text-white px-3 py-1 text-xs rounded-full border border-white/10"
                  >
                    {cat.name}
                  </span>
                ))
              ) : (
                <span className="text-slate-400 text-sm">Geen categorieën</span>
              )}
            </div>

            {(post.windspeed || post.winddirection || post.seastate) && (
              <p className="text-slate-200 text-sm md:text-base bg-white/5 border border-white/10 p-4 rounded-2xl">
                Een woei van {post.windspeed?.name || "onbekend"} uit {post.winddirection?.name || "onbekend"} met een {post.seastate?.name || "onbekende"} zee.
              </p>
            )}

            <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
              <div className="flex items-center gap-2 text-white font-semibold">
                <Share2 className="h-5 w-5" />
                Deel dit verhaal
              </div>
              <div className="flex flex-wrap gap-2">
                <button
                  type="button"
                  onClick={() => handleShare("facebook")}
                  className="px-3 py-2 rounded-full text-white text-sm font-semibold bg-[#1877f2] hover:opacity-90 transition"
                >
                  Facebook
                </button>
                <button
                  type="button"
                  onClick={() => handleShare("instagram")}
                  className="px-3 py-2 rounded-full text-white text-sm font-semibold bg-gradient-to-r from-pink-500 to-orange-400 hover:opacity-90 transition"
                >
                  Instagram
                </button>
                <button
                  type="button"
                  onClick={() => handleShare("x")}
                  className="px-3 py-2 rounded-full text-white text-sm font-semibold bg-black hover:opacity-80 transition"
                >
                  X
                </button>
                <button
                  type="button"
                  onClick={() => handleShare("whatsapp")}
                  className="px-3 py-2 rounded-full text-white text-sm font-semibold bg-[#25d366] hover:opacity-90 transition"
                >
                  WhatsApp
                </button>
              </div>
            </div>

            <hr className="border-white/10" />

            <article
              className="prose prose-invert max-w-none leading-relaxed"
              dangerouslySetInnerHTML={{ __html: post.content }}
            />
          </div>
        </section>

        {post.albums?.length ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 my-10">
            {post.albums.map(album => (
              <Link
                key={album.id}
                to={`/albums/${album.id}`}
                className="rounded-xl shadow-lg bg-slate-900/80 backdrop-blur border border-white/10 p-4 hover:shadow-xl transition"
              >
                {album.cover_image ? (
                  <img
                    src={album.cover_image}
                    alt={album.title}
                    className="w-full h-40 object-cover rounded-lg mb-3"
                  />
                ) : (
                  <div className="w-full h-40 bg-white/5 rounded-lg flex items-center justify-center mb-3">
                    <span className="text-slate-400">Geen cover</span>
                  </div>
                )}
                <h3 className="font-bold text-lg text-white">{album.title}</h3>
              </Link>
            ))}
          </div>
        ) : null}

        <section className="shadow-2xl bg-slate-900/80 border border-white/10 rounded-3xl p-6 md:p-8 w-full">
          <div className="flex items-center justify-between flex-wrap gap-3 mb-2">
            <div>
              <h2 className="text-2xl font-semibold text-white">Reacties</h2>
              <p className="text-slate-400">De beste stuurlui staan aan wal</p>
            </div>
            <span className="px-3 py-1 text-sm rounded-full border border-white/10 bg-white/5 text-white">
              {comments.length} {comments.length === 1 ? "reactie" : "reacties"}
            </span>
          </div>
          {message && <p className="text-red-300 mb-3">{message}</p>}

          <form onSubmit={handleCommentSubmit} className="mb-6 space-y-3">
            <textarea
              className="w-full border border-white/10 bg-white/5 text-white p-3 rounded-xl focus:ring-2 focus:ring-cyan-600 focus:outline-none placeholder:text-slate-400"
              value={newComment}
              onChange={e => setNewComment(e.target.value)}
              placeholder={token ? "Schrijf een reactie..." : "Log eerst in om een reactie achter te laten."}
              required
              disabled={!token}
            />
            <button
              type="submit"
              className="bg-white text-slate-900 px-4 py-2 rounded-xl disabled:bg-slate-500 disabled:text-white disabled:cursor-not-allowed hover:-translate-y-0.5 transition"
              disabled={!token}
            >
              Plaats reactie
            </button>
          </form>

          <div className="space-y-4">
            {comments.length === 0 && (
              <div className="border border-dashed border-white/10 bg-white/5 p-4 rounded-2xl text-slate-400">
                Nog geen reacties. Wees de eerste!
              </div>
            )}
            {comments.map(comment => (
              <div
                key={comment.id}
                className="border border-white/10 bg-white/5 p-4 rounded-2xl flex items-start space-x-3 shadow-sm"
              >
                {comment.author_avatar ? (
                  <img src={comment.author_avatar} alt={comment.author_username} className="w-11 h-11 rounded-full object-cover border border-white/10" />
                ) : (
                  <div className="w-11 h-11 rounded-full bg-white/10 flex items-center justify-center border border-white/10">
                    <User className="w-6 h-6 text-slate-300" />
                  </div>
                )}
                <div className="flex-1">
                  <div className="flex items-center justify-between gap-3 mb-1">
                    <div className="flex items-center gap-2">
                      <span className="text-white font-semibold">{comment.author_username}</span>
                      <span className="text-xs text-slate-300 px-2 py-1 rounded-full bg-white/10 border border-white/10">
                        {new Date(comment.created_at).toLocaleDateString()}
                      </span>
                    </div>
                  </div>
                  <p className="text-slate-100 leading-relaxed">{comment.content}</p>
                </div>
              </div>
            ))}
          </div>
        </section>
      </article>
      <BottomNav />
    </section>
  );
}
