import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Home from "./components/Home";
import BlogDetail from "./components/BlogDetail";
import BlogList from "./components/BlogList";


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
        <Route path="/posts" element={<BlogList />} />
        <Route path="/posts/:slug" element={<BlogDetail />} />
      </Routes>
    </Router>
  );
}

export default App;
