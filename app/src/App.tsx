import { useEffect } from "react";
import { Route, Routes } from "react-router-dom";
import { Header } from "@/components/Header";
import { TabBar } from "@/components/TabBar";
import { ConnectionBanner } from "@/components/ConnectionBanner";
import { ConsoleView } from "@/views/console/ConsoleView";
import { SessionView } from "@/views/session/SessionView";
import { SettingsView } from "@/views/settings/SettingsView";
import { useTelemetry } from "@/lib/store";

export function App() {
  const start = useTelemetry((s) => s.start);
  useEffect(() => { start(); }, [start]);

  return (
    <div className="flex min-h-screen flex-col bg-bg text-ink">
      <Header />
      <TabBar />
      <ConnectionBanner />
      <main className="flex-1 overflow-y-auto">
        <Routes>
          <Route path="/" element={<ConsoleView />} />
          <Route path="/session" element={<SessionView />} />
          <Route path="/settings" element={<SettingsView />} />
          <Route path="*" element={<ConsoleView />} />
        </Routes>
      </main>
    </div>
  );
}
