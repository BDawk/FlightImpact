import { useEffect } from "react";
import { Route, Routes } from "react-router-dom";
import { Header } from "@/components/Header";
import { TabBar } from "@/components/TabBar";
import { ConnectionBanner } from "@/components/ConnectionBanner";
import { SessionView } from "@/views/session/SessionView";
import { HistoryView } from "@/views/history/HistoryView";
import { SettingsView } from "@/views/settings/SettingsView";
import { DevView } from "@/views/dev/DevView";
import { useTelemetry } from "@/lib/store";
import { IS_DEVKIT } from "@/lib/feature_flags";

export function App() {
  const start = useTelemetry((s) => s.start);
  useEffect(() => {
    start();
  }, [start]);

  return (
    <div className="flex min-h-screen flex-col bg-bg">
      <Header />
      <ConnectionBanner />
      <main className="flex-1 overflow-y-auto">
        <Routes>
          <Route path="/" element={<SessionView />} />
          <Route path="/history" element={<HistoryView />} />
          <Route path="/settings" element={<SettingsView />} />
          {IS_DEVKIT && <Route path="/dev" element={<DevView />} />}
          <Route path="*" element={<SessionView />} />
        </Routes>
      </main>
      <TabBar />
    </div>
  );
}
