"use client";

import { useMemo } from "react";
import { Guess } from "@/types/game";
import GuessListRow from "./GuessListRow";

interface GuessListProps {
  guesses: Guess[];
}

export default function GuessList({ guesses }: GuessListProps) {
  // Sorted into a new array: `guesses` is the parent's state, and sorting it in
  // place mutated that state during render.
  const sorted = useMemo(
    () => [...guesses].sort((a, b) => b.similarity_score - a.similarity_score),
    [guesses]
  );

  const lastGuess = useMemo(() => {
    if (guesses.length <= 2) return null;
    return guesses.reduce((latest, current) =>
      new Date(current.created_at) > new Date(latest.created_at) ? current : latest
    );
  }, [guesses]);

  if (guesses.length === 0) {
    return (
      <div className="text-center text-gray-500 dark:text-gray-400 py-8" dir="rtl">
        لم تقم بأي محاولات بعد
      </div>
    );
  }

  return (
    <div className="w-full max-w-2xl mx-auto space-y-3" dir="rtl">
      <div className="flex justify-between items-center mb-4 px-2">
        <span className="text-sm text-gray-600 dark:text-gray-300">
          المحاولات: {guesses.length}
        </span>
        <span className="text-sm text-gray-600 dark:text-gray-300">ترتيب: حسب التشابه</span>
      </div>

      {lastGuess && !lastGuess.is_correct && lastGuess.word !== sorted[0].word && (
        <GuessListRow guess={lastGuess} index={0} />
      )}

      <hr className="border border-gray-200 dark:border-gray-700 my-4" />

      {sorted.map((guess, index) => (
        <GuessListRow key={guess.id} guess={guess} index={index + 1} />
      ))}
    </div>
  );
}
