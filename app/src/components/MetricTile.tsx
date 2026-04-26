import { cn } from "@/lib/cn";

export function MetricTile({
  label,
  value,
  unit,
  confidence,
  className,
}: {
  label: string;
  value: number | null | undefined;
  unit?: string;
  confidence?: number; // 0..1
  className?: string;
}) {
  const display =
    value === null || value === undefined || Number.isNaN(value)
      ? "—"
      : Math.abs(value) >= 100
        ? value.toFixed(0)
        : value.toFixed(1);

  const confColor =
    confidence === undefined
      ? null
      : confidence > 0.7
        ? "bg-signal-ok"
        : confidence > 0.4
          ? "bg-signal-warn"
          : "bg-signal-bad";

  return (
    <div className={cn("rounded-xl border border-line bg-bg-elev p-4", className)}>
      <div className="flex items-center justify-between">
        <div className="text-xs uppercase tracking-wide text-ink-dim">{label}</div>
        {confColor && (
          <span
            className={cn("h-1.5 w-1.5 rounded-full", confColor)}
            title={`Confidence: ${(confidence! * 100).toFixed(0)}%`}
          />
        )}
      </div>
      <div className="mt-2 flex items-baseline gap-1.5 tabular">
        <span className="text-3xl font-semibold text-ink">{display}</span>
        {unit && value !== null && value !== undefined && (
          <span className="text-sm text-ink-muted">{unit}</span>
        )}
      </div>
    </div>
  );
}
