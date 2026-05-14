import { NavLink } from "react-router-dom";
import { cn } from "@/lib/cn";
import { IS_DEVKIT } from "@/lib/feature_flags";

const tabs = [
  { to: "/", label: "Console", desc: "Live data + controls" },
  { to: "/session", label: "Session", desc: "Recent shots" },
  { to: "/settings", label: "Settings", desc: "Device & network" },
];

export function TabBar() {
  return (
    <nav className="border-b border-line bg-bg-elev/40">
      <div className="mx-auto flex max-w-6xl items-stretch gap-1 px-4">
        {tabs.map((t) => (
          <NavLink
            key={t.to}
            to={t.to}
            end={t.to === "/"}
            className={({ isActive }) =>
              cn(
                "group relative px-3 py-2.5 text-sm font-medium transition-colors",
                isActive
                  ? "text-brand"
                  : "text-ink-muted hover:text-ink",
              )
            }
          >
            {({ isActive }) => (
              <>
                <span>{t.label}</span>
                {isActive && (
                  <span className="absolute inset-x-2 -bottom-px h-0.5 bg-brand" />
                )}
              </>
            )}
          </NavLink>
        ))}
        {IS_DEVKIT && (
          <span className="ml-auto self-center cap text-brand/70">
            DEV BUILD
          </span>
        )}
      </div>
    </nav>
  );
}
