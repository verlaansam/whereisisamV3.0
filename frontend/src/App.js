import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Home from "./components/Home";
import BlogDetail from "./components/BlogDetail";
import BlogPage from "./components/BlogPage";
import AlbumDetail from "./components/AlbumDetail";
import AlbumList from "./components/AlbumList";
import Profile from "./components/Profile";
import AuthForm from "./components/AuthForm";


function App() {
  const token = localStorage.getItem("accessToken");
  if (token) {
    console.log("User is authenticated");
  } else {
    // toon AuthForm
  }

  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/posts" element={<BlogPage />} />
        <Route path="/posts/:slug" element={<BlogDetail />} />
        <Route path="/albums" element={<AlbumList />} />
        <Route path="/albums/:id" element={<AlbumDetail />} />
        <Route path="/profiel" element={<Profile />} />
        <Route path="/login" element={<AuthForm />} />
      </Routes>
    </Router>
  );
}

export default App;
