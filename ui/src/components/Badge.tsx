import type { ReactNode } from "react";

type BadgeKind = "stale" | "clone" | "weak" | "value" | "good";

export function Badge({
  kind,
  title,
  children,
}: {
  kind: BadgeKind;
  title?: string;
  children: ReactNode;
}) {
  return (
    <span className={`badge ${kind}`} title={title}>
      {children}
    </span>
  );
}
