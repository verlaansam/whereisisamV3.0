import { Cloud, FileText, Image, User } from "lucide-react";
import { Link } from "react-router-dom";

export default function BottomNav() {
  return (
    <nav className="fixed bottom-0 w-full bg-white border-t p-2 flex justify-around z-40">
      <Link to="/weer" className="flex flex-col items-center text-gray-600 hover:text-cyan-800">
        <Cloud className="w-8 h-8" />
        <span className="text-xs">Weer</span>
      </Link>

      <Link to="/posts" className="flex flex-col items-center text-gray-600 hover:text-cyan-800">
        <FileText className="w-8 h-8" />
        <span className="text-xs">Blog</span>
      </Link>

      <Link to="/albums" className="flex flex-col items-center text-gray-600 hover:text-cyan-800">
        <Image className="w-8 h-8" />
        <span className="text-xs">Foto's</span>
      </Link>

      <Link to="/profiel" className="flex flex-col items-center text-gray-600 hover:text-cyan-800">
        <User className="w-8 h-8" />
        <span className="text-xs">Profiel</span>
      </Link>
    </nav>
  );
}

