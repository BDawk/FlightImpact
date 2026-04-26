# API reference

The dev kit exposes a versioned REST + WebSocket API. The same contract will
be implemented by production firmware, so anything you build against this
will keep working.

Base URL: `http://flightimpact.local:8000` (or `http://192.168.4.1:8000` in
AP mode).

## REST endpoints

All paths under `/api/v1/`. Responses are JSON.

### `GET /api/v1/version`
Returns `{api_version, service}`. Use this for compatibility detection.

### `GET /api/v1/status`
Returns the current `DeviceStatus`. Same shape as the periodic WS heartbeat.

### `GET /api/v1/shots?limit=50&offset=0`
List recent shots, newest first.

### `GET /api/v1/shots/{id}`
Single shot by UUID. Returns `404` if not found.

### `POST /api/v1/shots/{id}/notes`
Body: `{notes?, club?}`. Update freeform notes or club tag for an existing
shot. Returns the updated `Shot`.

### `POST /api/v1/test/trigger`
Manually fire a test shot. Returns the shot stub immediately; the final
metrics arrive via WebSocket as the processor finishes. Dev-mode only —
returns `403` in production builds.

## WebSocket

Connect to `/ws`. Messages flow in both directions.

### Server → client

Every message is a JSON object with a `type` discriminator. See
`core/models/telemetry.py` and `app/src/lib/types.ts` for full schemas.

| Type | When | Subscribe needed? |
|------|------|-------------------|
| `device_status` | Every 2s + on-connect | No (default-on) |
| `shot_updated`  | Each transition (capturing → processing → complete) | No |
| `live_frame`    | ~10 Hz JPEG preview | Yes |
| `radar_spectrum` | Per FFT block (~20 Hz) | Yes |
| `log`           | Server log entries | Yes |

### Client → server

Plain text command frames, one per line:

| Command | Effect |
|---------|--------|
| `subscribe_live_frame` | Start receiving `live_frame` messages |
| `unsubscribe_live_frame` | Stop |
| `subscribe_radar_spectrum` | Start receiving `radar_spectrum` |
| `unsubscribe_radar_spectrum` | Stop |
| `subscribe_logs` | Start receiving `log` messages |
| `unsubscribe_logs` | Stop |

The default-off, opt-in pattern for high-bandwidth streams matters more than
it sounds: a phone on AP-mode Wi-Fi can saturate a 5 GHz link if you stream
1080p MJPEG to it continuously. The app subscribes only when the dev panel
mounts.

## Reconnection

The TypeScript socket client (`app/src/lib/transport/socket.ts`) handles
auto-reconnect with exponential backoff (1s → 8s cap) and replays any pending
subscription commands on each successful reconnect, so a brief Wi-Fi blip
doesn't require user intervention.

## Versioning

`API_VERSION` lives in `core/api_contract/__init__.py`. Bump it on any
breaking change. Clients should fetch `/api/v1/version` on connect and warn
if the major doesn't match.
