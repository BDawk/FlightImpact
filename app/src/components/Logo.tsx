export function Logo({ size = 26 }: { size?: number }) {
  // Loaded from /public/logo.svg — Vite serves it at /logo.svg in dev and prod.
  return (
    <img
      src="/logo.svg"
      alt="FlightImpact"
      width={size}
      height={Math.round(size * 856 / 730)}
      draggable={false}
      style={{ display: "block" }}
    />
  );
}
