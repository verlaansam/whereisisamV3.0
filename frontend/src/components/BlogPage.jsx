import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import TopNav from "./TopNav";
import BottomNav from "./BottomNav";
import { useTranslation } from "react-i18next";

const API_URL = process.env.REACT_APP_API_URL;
if (!API_URL) {
  throw new Error("Missing REACT_APP_API_URL environment variable");
}

export default function BlogList() {
  const { t } = useTranslation();
  const [posts, setPosts] = useState([]);

  useEffect(() => {
    fetch(`${API_URL}/posts/`)
      .then(res => res.json())
      .then(data => setPosts(data));
  }, []);

  if (!posts.length) return <p className="p-4 text-white">{t("Geen posts beschikbaar")}</p>;

  const [latestPost, ...otherPosts] = posts; // meest recente

  return (
    <section className="min-h-screen bg-gradient-to-b from-slate-900 via-slate-900 to-slate-950 text-white pt-16 pb-24">
      <TopNav />
      <div className="p-4 md:p-6 lg:px-8 max-w-6xl mx-auto space-y-6 min-w-0 w-full">
      {/* 🔹 Grote tile */}
      {latestPost && (
        <Link
          to={`/posts/${latestPost.slug}`}
          className="block mb-6 rounded-3xl overflow-hidden shadow-lg hover:shadow-2xl transition border border-white/10 bg-white/5"
        >
          {latestPost.image && (
            <img
              src={latestPost.image}
              alt={latestPost.title}
              className="w-full h-72 object-cover"
            />
          )}
          <div className="p-4 bg-white/5">
            <h2 className="text-3xl font-bold mb-2 text-white">{latestPost.title}</h2>
            <p className="text-slate-200 line-clamp-3" dangerouslySetInnerHTML={{ __html: latestPost.content }} />
          </div>
        </Link>
      )}

      {/* 🔹 Kleine list van alle */}
      <article className="space-y-4 sm:space-y-0 sm:grid sm:grid-cols-2 md:grid-cols-2 lg:grid-cols-3 sm:gap-4 min-w-0 max-w-full">
        {otherPosts.map(post => (
          <Link
            to={`/posts/${post.slug}`}
            key={post.id}
            className="flex items-center bg-white/5 p-3 rounded-lg shadow hover:shadow-md transition border border-white/10"
          >
            {post.image && (
              <img
                src={post.image}
                alt={post.title}
                className="w-24 h-24 object-cover rounded mr-4 flex-shrink-0"
              />
            )}
            <section>
              <h3 className="text-lg font-semibold text-white">{post.title}</h3>
              <p className="text-slate-200 line-clamp-2" dangerouslySetInnerHTML={{ __html: post.content }} />
            </section>
          </Link>
        ))}
      </article>
      </div>
      <BottomNav />
    </section>
  );
}
