import { useEffect } from "react";
import { Route, Routes } from "react-router-dom";
import { Header } from "@/components/Header";
import { TabBar } from "@/components/TabBar";
import { ConnectionBanner } from "@/components/ConnectionBanner";
import { DeviceView } from "@/views/device/DeviceView";
import { ControlView } from "@/views/control/ControlView";
import { LogsView } from "@/views/logs/LogsView";
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
          <Route path="/"        element={<DeviceView />} />
          <Route path="/control" element={<ControlView />} />
          <Route path="/logs"    element={<LogsView />} />
          <Route path="*"        element={<DeviceView />} />
        </Routes>
      </main>
    </div>
  );
}
