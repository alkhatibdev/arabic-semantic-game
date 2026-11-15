import type { GtagParams } from "@/types/analytics";

export const FLAG_GIVEUP = "giveup-flag";

export const getTodayDateUTC = () => {
  return new Date().toISOString().slice(0, 10);
};

/**
 * Shift a YYYY-MM-DD date by whole days, staying in UTC.
 *
 * Challenge dates are UTC everywhere (see getTodayDateUTC), so this must not
 * round-trip through local time - date-fns' format() did, which moved the date
 * by a day for anyone west of UTC.
 */
export function shiftDateUTC(date: string, days: number): string {
  const d = new Date(`${date}T00:00:00Z`);
  d.setUTCDate(d.getUTCDate() + days);
  return d.toISOString().slice(0, 10);
}

export function getSimilarityColor(score: number): string {
  if (score >= 100)
    return "bg-green-100 dark:bg-green-900/40 border-green-300 dark:border-green-800";
  if (score >= 70) return "bg-lime-100 dark:bg-lime-900/40 border-lime-300 dark:border-lime-800";
  if (score >= 50)
    return "bg-yellow-100 dark:bg-yellow-900/40 border-yellow-300 dark:border-yellow-800";
  if (score >= 30)
    return "bg-orange-100 dark:bg-orange-900/40 border-orange-300 dark:border-orange-800";
  return "bg-red-100 dark:bg-red-900/40 border-red-300 dark:border-red-800";
}

export function getSimilarityGradient(score: number): string {
  // Using actual CSS color values for proper gradients
  if (score >= 100) return "#22c55e, #16a34a"; // green-500 to green-600
  if (score >= 70) return "#84cc16, #65a30d"; // lime-500 to lime-600
  if (score >= 50) return "#eab308, #ca8a04"; // yellow-500 to yellow-600
  if (score >= 30) return "#f97316, #ea580c"; // orange-500 to orange-600
  return "#ef4444, #dc2626"; // red-500 to red-600
}

export function getShareText(attempts: number, gameNumber: number, won: boolean): string {
  const header = `🎯 ألعاب تفكير وتحدي - تحدي التشابه والتقارب \n🏆 التحدي رقم #${gameNumber}\n`;
  return won
    ? `${header}✅ فزت في ${attempts} محاولة!\n`
    : `${header}✅ لعبت ${attempts} محاولة!\n`;
}

export function sendGAEvent(eventName: string, eventParams: GtagParams = {}) {
  const gaId = process.env.NEXT_PUBLIC_GA_MEASUREMENT_ID;
  if (typeof window !== "undefined" && window.gtag && gaId) {
    window.gtag("event", eventName, eventParams);
  }
}
