"use client";

import { motion } from "framer-motion";
import { FLAG_GIVEUP } from "@/lib/utils";
import Modal from "./Modal";

interface GiveUpModalProps {
  submitting: boolean;
  onSubmit: (word: string) => void;
  onClose?: () => void;
}

export default function GiveUpModal({ submitting, onSubmit, onClose }: GiveUpModalProps) {
  const handleGiveUp = () => {
    if (!submitting) {
      onClose?.();
      onSubmit(FLAG_GIVEUP);
    }
  };

  return (
    <Modal label="تأكيد الاستسلام" onClose={onClose}>
      <div className="text-center">
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ delay: 0.2, type: "spring", stiffness: 200 }}
          className="text-3xl mb-2"
          aria-hidden="true"
        >
          🏳️
        </motion.div>
        <motion.p
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ delay: 0.2, type: "spring", stiffness: 200 }}
          className="text-3xl mb-8"
        >
          إستسلام!
        </motion.p>

        <p className="text-xl text-gray-800 dark:text-gray-100 mb-8">
          هل أنت متأكد من رغبتك في الاستسلام؟ سيؤدي هذا إلى إنهاء اللعبة وكشف الكلمة السرية.
        </p>

        <div className="flex gap-3">
          <button
            onClick={handleGiveUp}
            disabled={submitting}
            className="flex-1 px-6 py-3 bg-green-500 dark:bg-green-600 text-white font-semibold rounded-lg hover:bg-green-600 dark:hover:bg-green-700 transition-colors disabled:opacity-50"
          >
            نعم، استسلم
          </button>

          {onClose && (
            <button
              onClick={onClose}
              className="flex-1 px-6 py-3 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-200 font-semibold rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
            >
              لا
            </button>
          )}
        </div>
      </div>
    </Modal>
  );
}
