import { Suspense, lazy } from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import AnalyticsLoader from "./components/AnalyticsLoader";
import CookieBanner from "./components/CookieBanner";

const Home = lazy(() => import("./components/Home"));
const BlogDetail = lazy(() => import("./components/BlogDetail"));
const BlogPage = lazy(() => import("./components/BlogPage"));
const AlbumDetail = lazy(() => import("./components/AlbumDetail"));
const AlbumList = lazy(() => import("./components/AlbumList"));
const Profile = lazy(() => import("./components/Profile"));
const AuthForm = lazy(() => import("./components/AuthForm"));
const Weather = lazy(() => import("./components/Weather"));

function RouteFallback() {
  return <div className="min-h-screen bg-gradient-to-b from-slate-900 via-slate-900 to-slate-950" />;
}

function App() {
  return (
    <div className=" min-h-screen bg-gradient-to-b from-slate-900 via-slate-900 to-slate-950 text-white">
      <Router>
        <AnalyticsLoader />
        <CookieBanner />
        <Suspense fallback={<RouteFallback />}>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/posts" element={<BlogPage />} />
            <Route path="/posts/:slug" element={<BlogDetail />} />
            <Route path="/albums" element={<AlbumList />} />
            <Route path="/albums/:id" element={<AlbumDetail />} />
            <Route path="/profiel" element={<Profile />} />
            <Route path="/login" element={<AuthForm />} />
            <Route path="/weather" element={<Weather />} />
          </Routes>
        </Suspense>
      </Router>
    </div>
  );
}

export default App;
