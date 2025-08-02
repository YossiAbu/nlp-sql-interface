import { useEffect, useState } from "react";
import { Sun, Moon } from "lucide-react";
import { toggleDarkMode } from "@/utils/theme";

const ThemeToggle = () => {
  const [isDark, setIsDark] = useState(false);

  useEffect(() => {
    setIsDark(document.documentElement.classList.contains("dark"));
  }, []);

  const handleToggle = () => {
    toggleDarkMode();
    setIsDark((prev) => !prev);
  };

  return (
    <button
      onClick={handleToggle}
      className="w-full flex items-center justify-center gap-2 text-sm font-medium text-slate-300 hover:text-white hover:bg-slate-800/50 transition rounded-lg px-3 py-2 border border-slate-700/50"
      title={isDark ? "Switch to Light Mode" : "Switch to Dark Mode"}
    >
      {isDark ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
      {isDark ? "Light Mode" : "Dark Mode"}
    </button>
  );
};

export default ThemeToggle;
