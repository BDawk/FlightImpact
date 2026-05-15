import type { DeviceStatus, ScreenScenarioUpdate, ScreenStateSnapshot, Shot } from "@/lib/types";

const BASE = "/api/v1";

async function jsonFetch<T>(input: RequestInfo, init?: RequestInit): Promise<T> {
  const r = await fetch(input, init);
  if (!r.ok) throw new Error(`${r.status} ${r.statusText}`);
  return r.json() as Promise<T>;
}

export const api = {
  version: () => jsonFetch<{ api_version: string; service: string }>(`${BASE}/version`),
  status: () => jsonFetch<DeviceStatus>(`${BASE}/status`),
  listShots: (limit = 50, offset = 0) =>
    jsonFetch<Shot[]>(`${BASE}/shots?limit=${limit}&offset=${offset}`),
  getShot: (id: string) => jsonFetch<Shot>(`${BASE}/shots/${id}`),
  updateNotes: (id: string, body: { notes?: string; club?: string }) =>
    jsonFetch<Shot>(`${BASE}/shots/${id}/notes`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    }),
  triggerTestShot: () =>
    jsonFetch<Shot>(`${BASE}/test/trigger`, { method: "POST" }),
  getScreenState: () => jsonFetch<ScreenStateSnapshot>(`${BASE}/screen/state`),
  setScreenMode: (mode: string) =>
    jsonFetch<ScreenStateSnapshot>(`${BASE}/screen/mode`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ mode }),
    }),
  applyScreenScenario: (body: ScreenScenarioUpdate) =>
    jsonFetch<ScreenStateSnapshot>(`${BASE}/screen/scenario`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    }),
};
