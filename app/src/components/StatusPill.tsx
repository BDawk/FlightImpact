import { cn } from "@/lib/cn";

export type StatusKind = "ok" | "warn" | "bad" | "off";

export function StatusPill({
  kind,
  label,
  className,
}: {
  kind: StatusKind;
  label: string;
  className?: string;
}) {
  const dotColor = {
    ok: "bg-signal-ok",
    warn: "bg-signal-warn",
    bad: "bg-signal-bad",
    off: "bg-ink-dim",
  }[kind];
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full bg-bg-elev px-2.5 py-1 text-xs text-ink-muted",
        className,
      )}
    >
      <span className={cn("h-1.5 w-1.5 rounded-full", dotColor)} />
      {label}
    </span>
  );
}
