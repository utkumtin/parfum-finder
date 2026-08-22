import { render } from "@testing-library/react";
import type { SVGProps } from "react";
import { describe, expect, it, vi } from "vitest";

vi.mock("motion/react", () => ({
  motion: {
    path: ({
      animate,
      initial,
      variants: _variants,
      ...props
    }: SVGProps<SVGPathElement> & {
      animate?: string;
      initial?: boolean | string;
      variants?: unknown;
    }) => (
      <path
        {...props}
        data-animate={animate}
        data-initial={String(initial)}
      />
    ),
  },
}));

import { BookmarkIcon } from "../../src/components/BookmarkIcon";

describe("BookmarkIcon", () => {
  it("mounts saved icons in their settled state", () => {
    const { container } = render(<BookmarkIcon filled />);
    const path = container.querySelector("path");

    // Saved rows remount whenever the user returns to Results. They must look
    // saved immediately, while the pop remains reserved for a new selection.
    expect(path).toHaveAttribute("data-initial", "false");
    expect(path).toHaveAttribute("data-animate", "animate");
  });
});
