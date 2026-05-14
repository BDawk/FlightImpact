import { cn } from "@/lib/cn";

export type StatusKind = "ok" | "warn" | "bad" | "off";

export function StatusPill({
  kind,
  label,
  value,
  className,
}: {
  kind: StatusKind;
  label: string;
  value?: string;
  className?: string;
}) {
  const dot = `dot dot-${kind}`;
  return (
    <span
      className={cn(
        "inline-flex items-center gap-2 rounded-md border border-line bg-bg-elev px-2 py-1 text-xs",
        className,
      )}
    >
      <span className={dot} />
      <span className="cap !text-[9px] !text-ink-muted">{label}</span>
      {value !== undefined && (
        <span className="lcd text-xs text-ink">{value}</span>
      )}
    </span>
  );
}
