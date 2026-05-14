import { cn } from "@/lib/cn";

export function MetricTile({
  label,
  value,
  unit,
  precision,
  confidence,
  className,
  size = "md",
}: {
  label: string;
  value: number | null | undefined;
  unit?: string;
  precision?: number;
  confidence?: number; // 0..1
  className?: string;
  size?: "sm" | "md" | "lg";
}) {
  const display =
    value === null || value === undefined || Number.isNaN(value)
      ? "—"
      : precision !== undefined
        ? value.toFixed(precision)
        : Math.abs(value) >= 100
          ? value.toFixed(0)
          : value.toFixed(1);

  const valSize = {
    sm: "text-xl",
    md: "text-2xl",
    lg: "text-4xl",
  }[size];

  const conf =
    confidence === undefined
      ? null
      : confidence > 0.7
        ? "ok"
        : confidence > 0.4
          ? "warn"
          : "bad";

  return (
    <div className={cn("panel p-3.5", className)}>
      <div className="flex items-center justify-between">
        <span className="cap">{label}</span>
        {conf && (
          <span className={`dot dot-${conf}`} title={`Confidence ${(confidence! * 100).toFixed(0)}%`} />
        )}
      </div>
      <div className="mt-1.5 flex items-baseline gap-1.5">
        <span className={cn("lcd text-ink", valSize)}>{display}</span>
        {unit && value !== null && value !== undefined && !Number.isNaN(value) && (
          <span className="cap !text-ink-dim !text-[10px]">{unit}</span>
        )}
      </div>
    </div>
  );
}
