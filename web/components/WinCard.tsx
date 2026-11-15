import { motion } from "framer-motion";
import { GameState } from "@/types/game";

interface WinCardProps {
  gameState: GameState | null;
}

export default function WinCard({ gameState }: WinCardProps) {
  return (
    gameState?.has_won &&
    gameState.game_status && (
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        className="mb-6 bg-green-50 dark:bg-green-900/20 border-2 border-green-200 dark:border-green-700 rounded-lg p-6"
        dir="rtl"
      >
        <div className="text-center">
          <div className="text-3xl mb-2">🎉</div>
          <div className="text-xl font-bold text-green-700 dark:text-green-400 mb-2">
            لقد فزت بالتحدي رقم #{gameState.game_number} !
          </div>
          <div className="text-gray-700 dark:text-gray-200">
            الكلمة هي: <span className="font-bold">{gameState.game_status.target_word}</span>
          </div>
          <div className="text-gray-600 dark:text-gray-300 text-sm mt-1">
            عدد المحاولات: {gameState.game_status.attempts}
          </div>
        </div>
      </motion.div>
    )
  );
}
