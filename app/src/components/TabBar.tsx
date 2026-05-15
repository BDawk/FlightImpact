import { NavLink } from "react-router-dom";
import { cn } from "@/lib/cn";

const tabs = [
  { to: "/", label: "Device",  icon: DeviceIcon },
  { to: "/control", label: "Control", icon: ControlIcon },
  { to: "/logs", label: "Logs", icon: LogsIcon },
];

export function TabBar() {
  return (
    <nav className="border-b border-line bg-bg-elev/40">
      <div className="mx-auto flex max-w-6xl items-stretch gap-0.5 px-4">
        {tabs.map((t) => (
          <NavLink
            key={t.to}
            to={t.to}
            end={t.to === "/"}
            className={({ isActive }) =>
              cn(
                "group relative flex items-center gap-1.5 px-3 py-2.5 text-sm font-medium transition-colors",
                isActive
                  ? "text-brand"
                  : "text-ink-muted hover:text-ink",
              )
            }
          >
            {({ isActive }) => (
              <>
                <t.icon active={isActive} />
                <span>{t.label}</span>
                {isActive && (
                  <span className="absolute inset-x-2 -bottom-px h-0.5 rounded-full bg-brand" />
                )}
              </>
            )}
          </NavLink>
        ))}
      </div>
    </nav>
  );
}

function DeviceIcon({ active }: { active: boolean }) {
  return (
    <svg width="14" height="14" viewBox="0 0 14 14" fill="none" stroke="currentColor" strokeWidth={active ? "1.6" : "1.4"} strokeLinecap="round" strokeLinejoin="round">
      <rect x="1" y="2" width="12" height="9" rx="1.5" />
      <path d="M4.5 11v1M9.5 11v1M3 12h8" />
      <circle cx="7" cy="6.5" r="1.5" />
    </svg>
  );
}

function ControlIcon({ active }: { active: boolean }) {
  return (
    <svg width="14" height="14" viewBox="0 0 14 14" fill="none" stroke="currentColor" strokeWidth={active ? "1.6" : "1.4"} strokeLinecap="round" strokeLinejoin="round">
      <circle cx="7" cy="7" r="5.5" />
      <path d="M7 4v3l2 1.5" />
    </svg>
  );
}

function LogsIcon({ active }: { active: boolean }) {
  return (
    <svg width="14" height="14" viewBox="0 0 14 14" fill="none" stroke="currentColor" strokeWidth={active ? "1.6" : "1.4"} strokeLinecap="round" strokeLinejoin="round">
      <path d="M2 3.5h10M2 7h7M2 10.5h5" />
    </svg>
  );
}
