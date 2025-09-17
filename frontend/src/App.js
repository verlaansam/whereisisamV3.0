import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import BlogList from "./components/BlogList";
import BlogDetail from "./components/BlogDetail";

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
        <Route path="/" element={<BlogList />} />
        <Route path="/posts/:slug" element={<BlogDetail />} />
      </Routes>
    </Router>
  );
}

export default App;
