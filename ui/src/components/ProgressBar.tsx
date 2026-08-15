import { motion } from "motion/react";

/**
 * A 2px line under the toolbar, `value` from 0 to 1.
 *
 * Critically damped: a progress bar that overshoots reads as the work having
 * gone further than it has and then coming back, which it never does.
 */
export function ProgressBar({ value }: { value: number }) {
  return (
    <div
      className="progress"
      role="progressbar"
      aria-valuemin={0}
      aria-valuemax={100}
      aria-valuenow={Math.round(value * 100)}
    >
      <motion.div
        className="progress-fill"
        initial={{ width: 0 }}
        animate={{ width: `${Math.min(100, Math.max(0, value * 100))}%` }}
        transition={{ type: "spring", bounce: 0, duration: 0.4 }}
      />
    </div>
  );
}
