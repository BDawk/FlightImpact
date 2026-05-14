import { cn } from "@/lib/cn";
import type { ButtonHTMLAttributes, ReactNode } from "react";

type Variant = "primary" | "secondary" | "ghost" | "danger";
type Size = "sm" | "md";

export function Button({
  variant = "secondary",
  size = "md",
  className,
  children,
  ...rest
}: ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: Variant;
  size?: Size;
  children: ReactNode;
}) {
  const base =
    "inline-flex items-center justify-center gap-1.5 rounded-md border font-medium transition-colors disabled:cursor-not-allowed disabled:opacity-40";
  const sizeCls = {
    sm: "px-2.5 py-1 text-xs",
    md: "px-3 py-1.5 text-sm",
  }[size];
  const variantCls = {
    primary:
      "border-brand/40 bg-brand/15 text-brand hover:bg-brand/25 active:bg-brand/30",
    secondary:
      "border-line bg-bg-elev text-ink hover:border-line-strong",
    ghost:
      "border-transparent bg-transparent text-ink-muted hover:bg-bg-elev hover:text-ink",
    danger:
      "border-signal-bad/40 bg-signal-bad/10 text-signal-bad hover:bg-signal-bad/20",
  }[variant];
  return (
    <button className={cn(base, sizeCls, variantCls, className)} {...rest}>
      {children}
    </button>
  );
}
