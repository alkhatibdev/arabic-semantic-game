"use client";

import { useEffect, useState } from "react";
import { ThemeContext, Theme, getInitialTheme, setThemeInStorage } from "@/lib/theme";

export default function ThemeProvider({ children }: { children: React.ReactNode }) {
  // Resolved lazily on the client. The inline script in app/layout.tsx has
  // already applied the `dark` class before paint, so this only needs to agree
  // with it - reading it in an initializer rather than an effect avoids the
  // extra render pass (and the render-cascade lint error).
  const [theme, setTheme] = useState<Theme>(() =>
    typeof window === "undefined" ? "light" : getInitialTheme()
  );

  useEffect(() => {
    document.documentElement.classList.toggle("dark", theme === "dark");
  }, [theme]);

  const toggleTheme = () => {
    const newTheme = theme === "light" ? "dark" : "light";
    setTheme(newTheme);
    setThemeInStorage(newTheme);
  };

  return <ThemeContext.Provider value={{ theme, toggleTheme }}>{children}</ThemeContext.Provider>;
}
