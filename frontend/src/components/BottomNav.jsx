import { Cloud, FileText, Image, User, House } from "lucide-react";
import { Link } from "react-router-dom";

export default function BottomNav() {
  return (
    <nav className="fixed bottom-0 w-full bg-slate-900/90 backdrop-blur border-t border-white/10 p-2 flex justify-around z-40 text-white">
      <Link to="/weather" className="flex flex-col items-center text-slate-200 hover:text-cyan-200">
        <Cloud className="w-8 h-8" />
        <span className="text-xs">Weer</span>
      </Link>

      <Link to="/posts" className="flex flex-col items-center text-slate-200 hover:text-cyan-200">
        <FileText className="w-8 h-8" />
        <span className="text-xs">Blog</span>
      </Link>

      <Link to="/" className="flex flex-col items-center text-slate-200 hover:text-cyan-200">
        <House className="w-8 h-8" />
        <span className="text-xs">Home</span>
      </Link> 

      <Link to="/albums" className="flex flex-col items-center text-slate-200 hover:text-cyan-200">
        <Image className="w-8 h-8" />
        <span className="text-xs">Foto's</span>
      </Link>

      <Link to="/profiel" className="flex flex-col items-center text-slate-200 hover:text-cyan-200">
        <User className="w-8 h-8" />
        <span className="text-xs">Profiel</span>
      </Link>
    </nav>
  );
}
