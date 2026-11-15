"use client";

import { useRouter } from "next/navigation";
import { getTodayDateUTC, shiftDateUTC } from "@/lib/utils";

interface NavigationProps {
  currentDate: string;
}

export default function Navigation({ currentDate }: NavigationProps) {
  const router = useRouter();

  const today = getTodayDateUTC();
  const isToday = currentDate === today;

  // Calculate previous and next dates
  const prevDate = shiftDateUTC(currentDate, -1);
  const nextDate = shiftDateUTC(currentDate, 1);

  // Allow previous navigation (user can navigate to any past date)
  const hasPrev = true;
  // Disable next if current date is today or future
  const hasNext = currentDate < today;

  const goToPrev = () => {
    router.push(`/game/${prevDate}`);
  };

  const goToNext = () => {
    if (hasNext) {
      router.push(`/game/${nextDate}`);
    }
  };

  const goToToday = () => {
    // Redirect to home page for today's game
    router.push(`/`);
  };

  return (
    <div className="flex items-center justify-between gap-4 mb-6" dir="rtl">
      {hasPrev && (
        <button
          onClick={goToPrev}
          className="px-3 py-2 bg-gray-200 dark:bg-gray-600  text-sm rounded-sm hover:bg-gray-300 dark:hover:bg-gray-700 disabled:bg-gray-300 dark:disabled:bg-gray-600 disabled:cursor-not-allowed transition-colors font-semibold"
        >
          → السابق
        </button>
      )}

      <div className="flex-1 text-center">
        {!isToday && (
          <button
            onClick={goToToday}
            className="px-4 py-2 bg-gradient-to-r from-green-100 to-emerald-100 dark:from-green-900/40 dark:to-emerald-900/40 text-green-700 dark:text-green-200 text-sm rounded-lg hover:from-green-200 hover:to-emerald-200 dark:hover:from-green-800/50 dark:hover:to-emerald-800/50 transition-all font-semibold ring ring-green-200 dark:ring-green-700/50"
          >
            <span className="flex items-center gap-1 justify-center">🏠 العودة لتحدي اليوم</span>
          </button>
        )}
      </div>

      {hasNext && (
        <button
          onClick={goToNext}
          className="px-3 py-2 bg-gray-200 dark:bg-gray-600  text-sm rounded-sm hover:bg-gray-300 dark:hover:bg-gray-700 disabled:bg-gray-300 dark:disabled:bg-gray-600 disabled:cursor-not-allowed transition-colors font-semibold"
        >
          التالي ←
        </button>
      )}
    </div>
  );
}
