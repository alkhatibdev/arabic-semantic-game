"use client";

import { motion } from "framer-motion";
import { GameStatus } from "@/types/game";
import { getShareText, sendGAEvent } from "@/lib/utils";
import { useToast } from "@/components/ToastProvider";
import Modal from "./Modal";

interface WinModalProps {
  gameStatus: GameStatus;
  gameNumber: number;
  onClose?: () => void;
}

export default function WinModal({ gameStatus, gameNumber, onClose }: WinModalProps) {
  const { showToast } = useToast();

  const copyToClipboard = (text: string) => {
    navigator.clipboard
      .writeText(text)
      .then(() => showToast("تم النسخ إلى الحافظة!", "success"))
      .catch(() => showToast("تعذّر النسخ إلى الحافظة", "warning"));
  };

  const handleShare = () => {
    const text = getShareText(gameStatus.attempts, gameNumber, gameStatus.won);
    const url = window.location.href;
    sendGAEvent("share_result", { game_number: gameNumber, attempts: gameStatus.attempts });

    if (navigator.share) {
      navigator
        .share({
          title: "ألعاب تفكير وتحدي - تحدي التشابه والتقارب",
          text: text + "...\n",
          url,
        })
        .catch(() => copyToClipboard(`${text}\n${url}`));
    } else {
      copyToClipboard(`${text}\n${url}`);
    }
  };

  if (!gameStatus.won) return null;

  return (
    <Modal label="لقد فزت بالتحدي" onClose={onClose}>
      <div className="text-center">
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ delay: 0.2, type: "spring", stiffness: 200 }}
          className="text-6xl mb-4"
          aria-hidden="true"
        >
          🎉
        </motion.div>

        <p className="text-3xl font-bold text-gray-800 dark:text-gray-100 mb-2">أحسنت! لقد فزت!</p>

        <p className="text-gray-600 dark:text-gray-300 mb-6">سنراك غداً في التحدي القادم!</p>

        <div className="bg-green-50 dark:bg-green-900/20 border-2 border-green-200 dark:border-green-700 rounded-lg p-6 mb-6">
          <div className="text-sm text-gray-600 dark:text-gray-300 mb-2">الكلمة هي:</div>
          <div className="text-3xl font-bold text-green-700 dark:text-green-400 mb-4">
            {gameStatus.target_word}
          </div>

          <div className="text-sm text-gray-600 dark:text-gray-300">عدد المحاولات:</div>
          <div className="text-2xl font-bold text-gray-800 dark:text-gray-100">
            {gameStatus.attempts}
          </div>
        </div>

        <div className="flex gap-3">
          <button
            onClick={handleShare}
            className="flex-1 px-6 py-3 bg-green-500 dark:bg-green-600 text-white font-semibold rounded-lg hover:bg-green-600 dark:hover:bg-green-700 transition-colors"
          >
            مشاركة ✨
          </button>

          {onClose && (
            <button
              onClick={onClose}
              className="flex-1 px-6 py-3 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-200 font-semibold rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
            >
              إغلاق
            </button>
          )}
        </div>
      </div>
    </Modal>
  );
}
