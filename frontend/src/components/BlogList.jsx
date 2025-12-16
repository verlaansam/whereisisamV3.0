import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
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
  const smallPosts = otherPosts.slice(0, 3); // maximaal 3

  return (
    <section className="-mt-12  rounded-3xl border-t-2 border-white/10 p-4 text-white bg-slate-900">
      <h1 className="text-2xl font-bold mb-4 text-white ">{t("Logboek")}</h1>

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

      {/* 🔹 Kleine list max 3 */}
      <div className="space-y-4">
        {smallPosts.map(post => (
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
            <div>
              <h3 className="text-lg font-semibold text-white">{post.title}</h3>
              <p className="text-slate-200 line-clamp-2" dangerouslySetInnerHTML={{ __html: post.content }} />
            </div>
          </Link>
        ))}
      </div>
    </section>
  );
}
