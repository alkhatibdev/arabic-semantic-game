"use client";

import { AnimatePresence, motion } from "framer-motion";
import { ReactNode, useEffect, useId, useRef } from "react";

interface ModalProps {
  /** Accessible name for the dialog, announced on open. */
  label: string;
  children: ReactNode;
  onClose?: () => void;
  /** Tailwind max-width class for the panel. */
  widthClass?: string;
}

const FOCUSABLE =
  'a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])';

/**
 * Shared dialog shell: backdrop, animation, and the accessibility behaviour the
 * three game modals all need - a real dialog role, Escape to close, focus moved
 * in on open and restored on close, and Tab kept inside the panel.
 */
export default function Modal({ label, children, onClose, widthClass = "max-w-md" }: ModalProps) {
  const panelRef = useRef<HTMLDivElement>(null);
  const previouslyFocused = useRef<HTMLElement | null>(null);
  const titleId = useId();

  useEffect(() => {
    previouslyFocused.current = document.activeElement as HTMLElement | null;

    const panel = panelRef.current;
    const first = panel?.querySelector<HTMLElement>(FOCUSABLE);
    (first ?? panel)?.focus();

    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        event.stopPropagation();
        onClose?.();
        return;
      }

      if (event.key !== "Tab" || !panel) return;

      const focusable = Array.from(panel.querySelectorAll<HTMLElement>(FOCUSABLE));
      if (focusable.length === 0) return;

      const edge = event.shiftKey ? focusable[0] : focusable[focusable.length - 1];
      if (document.activeElement === edge) {
        event.preventDefault();
        (event.shiftKey ? focusable[focusable.length - 1] : focusable[0]).focus();
      }
    };

    document.addEventListener("keydown", onKeyDown);
    const { overflow } = document.body.style;
    document.body.style.overflow = "hidden";

    return () => {
      document.removeEventListener("keydown", onKeyDown);
      document.body.style.overflow = overflow;
      previouslyFocused.current?.focus();
    };
  }, [onClose]);

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 bg-black/50 dark:bg-black/70 flex items-center justify-center z-50 p-4"
        onClick={onClose}
      >
        <motion.div
          ref={panelRef}
          role="dialog"
          aria-modal="true"
          aria-labelledby={titleId}
          tabIndex={-1}
          initial={{ scale: 0.8, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.8, opacity: 0 }}
          transition={{ type: "spring", duration: 0.5 }}
          className={`bg-white dark:bg-gray-800 rounded-2xl p-8 ${widthClass} w-full shadow-2xl max-h-[90vh] overflow-y-auto focus:outline-none`}
          onClick={(e) => e.stopPropagation()}
          dir="rtl"
        >
          <h2 id={titleId} className="sr-only">
            {label}
          </h2>
          {children}
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
}
