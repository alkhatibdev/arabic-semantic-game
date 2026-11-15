"use client";

import { useTheme } from "@/lib/theme";
import { motion } from "framer-motion";
import Link from "next/link";

export default function Header() {
  const { theme, toggleTheme } = useTheme();

  return (
    <header className="sticky top-0 z-50 w-full border-b border-gray-200 dark:border-gray-700 bg-white/80 dark:bg-slate-900/80 backdrop-blur-md">
      <div className="container mx-auto px-4 h-16 flex items-center justify-between">
        {/* Logo - a real link, so it is keyboard reachable */}
        <Link href="/" className="flex items-center gap-3 rounded-lg" dir="rtl">
          <span className="text-3xl" aria-hidden="true">
            🎯
          </span>
          <span>
            <span className="block text-xl font-bold text-gray-800 dark:text-gray-100">
              تحدي التشابه والتقارب
            </span>
            <span className="block text-xs font-bold text-cyan-600 dark:text-cyan-500">
              ألعاب تفكير وتحدي
            </span>
          </span>
        </Link>

        {/* Theme Toggle */}
        <motion.button
          whileTap={{ scale: 0.95 }}
          onClick={toggleTheme}
          className="p-3 rounded-full bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors shadow-sm"
          aria-label={theme === "light" ? "التبديل إلى الوضع الليلي" : "التبديل إلى الوضع النهاري"}
        >
          {theme === "light" ? (
            <svg
              className="w-5 h-5 text-gray-800"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"
              />
            </svg>
          ) : (
            <svg
              className="w-5 h-5 text-yellow-300"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"
              />
            </svg>
          )}
        </motion.button>
      </div>
    </header>
  );
}
