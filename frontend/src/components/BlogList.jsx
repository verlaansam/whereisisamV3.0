import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";

// Strip media tags so preview snippets don't display images or embedded media
const stripMediaForPreview = (html) => {
  if (!html) return "";
  try {
    let s = String(html);
    // remove <figure>...</figure>
    s = s.replace(/<figure[\s\S]*?<\/figure>/gi, "");
    // remove <iframe>...</iframe> and <video>...</video>
    s = s.replace(/<(iframe|video)[\s\S]*?<\/\1>/gi, "");
    // remove any <img ...>
    s = s.replace(/<img[^>]*>/gi, "");
    return s;
  } catch (e) {
    return html;
  }
};

const toPlainPreviewText = (html) => {
  const withoutMedia = stripMediaForPreview(html);
  return String(withoutMedia).replace(/<[^>]+>/g, " ").replace(/\s+/g, " ").trim();
};


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
    throw new Error("Expected JSON response from posts endpoint");
  }

  try {
    return JSON.parse(text);
  } catch {
    throw new Error("Invalid JSON response from posts endpoint");
  }
}

export default function BlogList() {
  const { t } = useTranslation();
  const [posts, setPosts] = useState([]);
  const [error, setError] = useState(false);

  useEffect(() => {
    fetch(endpoint("posts/"))
      .then(parseJsonSafely)
      .then(data => setPosts(Array.isArray(data) ? data : []))
      .catch(() => setError(true));
  }, []);

  if (error) return <p className="p-4 text-red-300">{t("Fout bij ophalen van posts.")}</p>;

  if (!posts.length) return <p className="p-4 text-white">{t("Geen posts beschikbaar")}</p>;

  const [latestPost, ...otherPosts] = posts; // meest recente
  const smallPosts = otherPosts.slice(0, 3); // maximaal 3

  return (
    <section className="rounded-3xl border border-white/10 p-4 md:p-6 text-white bg-slate-900/80 shadow-lg backdrop-blur min-w-0">
      <h1 className="text-2xl font-bold mb-4 text-white ">{t("Logboek")}</h1>

      {/* 🔹 Grote tile */}
      {latestPost && (
        <Link
          to={`/posts/${latestPost.slug}`}
          className="block mb-6 rounded-3xl overflow-hidden shadow-lg hover:shadow-2xl transition border border-white/10 bg-white/5"
        >
          {latestPost.image && (
            <img
              src={latestPost.image.startsWith('http') ? latestPost.image : `${API_URL}${latestPost.image}`}
              alt={latestPost.title}
              className="w-full h-72 object-cover"
              loading="eager"
              decoding="async"
              fetchPriority="high"
            />
          )}
          <div className="p-3 bg-white/5">
            <p className="text-slate-200 text-sm line-clamp-2">
              {latestPost.excerpt || toPlainPreviewText(latestPost.content)}
            </p>
          </div>
        </Link>
      )}

      {/* 🔹 Kleine list max 3 */}
      <div className="space-y-4 sm:space-y-0 sm:grid lg:grid-cols-2 sm:gap-4 min-w-0">
        {smallPosts.map(post => (
          <Link
            to={`/posts/${post.slug}`}
            key={post.id}
            className="flex items-center bg-white/5 p-3 rounded-lg shadow hover:shadow-md transition border border-white/10"
          >
            {post.image && (
              <img
                src={post.image.startsWith('http') ? post.image : `${API_URL}${post.image}`}
                alt={post.title}
                className="w-24 h-24 object-contain rounded mr-4 flex-shrink-0 "
                loading="lazy"
                decoding="async"
                fetchPriority="low"
              />
            )}
              <div>
              <h3 className="text-lg font-semibold text-white">{post.title}</h3>
              <p className="text-slate-200 line-clamp-2">
                {post.excerpt || toPlainPreviewText(post.content)}
              </p>
            </div>
          </Link>
        ))}
      </div>
    </section>
  );
}
