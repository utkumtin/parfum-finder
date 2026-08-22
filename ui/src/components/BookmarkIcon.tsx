import type { Variants } from "motion/react";
import { motion } from "motion/react";
import type { SVGAttributes } from "react";

interface BookmarkIconProps extends SVGAttributes<SVGSVGElement> {
  filled?: boolean;
  size?: number;
}

const variants: Variants = {
  normal: { scaleX: 1, scaleY: 1 },
  animate: {
    scaleY: [1, 1.3, 0.9, 1.05, 1],
    scaleX: [1, 0.9, 1.1, 0.95, 1],
    transition: { duration: 0.6, ease: "easeOut" },
  },
};

export function BookmarkIcon({
  filled = false,
  size = 18,
  ...props
}: BookmarkIconProps) {
  return (
    <svg
      fill="none"
      height={size}
      stroke="currentColor"
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth="1.5"
      viewBox="0 0 24 24"
      width={size}
      xmlns="http://www.w3.org/2000/svg"
      {...props}
    >
      <motion.path
        animate={filled ? "animate" : "normal"}
        d="M17.593 3.322c1.1.128 1.907 1.077 1.907 2.185V21L12 17.25 4.5 21V5.507c0-1.108.806-2.057 1.907-2.185a48.507 48.507 0 0 1 11.186 0Z"
        fill={filled ? "currentColor" : "none"}
        initial={false}
        variants={variants}
      />
    </svg>
  );
}
