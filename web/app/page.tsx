"use client";

import { useState } from "react";
import GameBoard from "@/components/GameBoard";
import { getTodayDateUTC } from "@/lib/utils";

export default function Home() {
  // Computed in a lazy initializer rather than an effect: the server renders an
  // empty date (GameBoard shows its loading state), and the client resolves it
  // on first render instead of forcing a second pass.
  const [todayDate] = useState<string>(() =>
    typeof window === "undefined" ? "" : getTodayDateUTC()
  );

  return <GameBoard date={todayDate} />;
}
