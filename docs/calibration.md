# Calibration

Two things need calibration before metrics will be accurate to within 5%:

1. **Camera intrinsics** — focal length, principal point, lens distortion
2. **Radar speed coefficient** — the cosine-angle correction from the look angle

Both are persisted in SQLite as JSON blobs and loaded at service startup.

## Camera calibration

We use OpenCV's standard checkerboard routine. The dev kit ships with a UI
wizard at Settings → Calibration → Camera; this section explains what's
happening behind it.

**Print pattern.** Standard 9x6 inner-corner checkerboard with 25 mm squares.
Tape it flat to a piece of foam board or hardback book. Glossy paper introduces
glare — matte print is much better.

**Capture.** Hold the board roughly where the ball will sit. Move it through
~15 different orientations: tilted left, right, forward, back, rotated, near,
far. The wizard accepts a frame each time it detects all 54 corners cleanly,
then refuses duplicates that are too similar to ones it already has.

**Solve.** Once 15+ valid frames are captured, the wizard runs
`cv2.calibrateCamera()` and produces an intrinsic matrix + distortion
coefficients. These are stored as a `CameraCalibration`.

**Sanity check.** A well-calibrated 25° M12 lens at 1080p should give you:
- `fx ≈ fy ≈ 4400` pixels (close, since fx and fy should match for square pixels)
- `cx ≈ 960`, `cy ≈ 540` (within ~30 px of image center)
- `|k1| < 0.3` and the rest near zero (the 25° lens is "low distortion" by spec)

Big deviations point to a bad capture set — re-shoot.

## Camera extrinsics — where the camera sits relative to the ball

For launch-side measurement we need to know:
- distance from camera to ball (mm)
- height of camera above ball (mm)
- side offset (mm)
- yaw and pitch of the camera relative to the ball-to-target line

The wizard asks for these as direct measurements (tape measure / digital level).
A future improvement is auto-extrinsic-extraction by placing the checkerboard
exactly where the ball will be and solving for the camera pose from the same
calibration session.

The derived `mm_per_pixel` at the ball plane is what we use to convert pixel
displacements between frames into real-world ball speed. This is the link
between camera measurements and the radar — they should agree, and any
disagreement is what fusion catches.

## Radar calibration

The textbook coefficient for an HB100 at 10.525 GHz is
**0.03187 mph per Hz** of Doppler shift. That's true only if the radar is
pointed exactly at the ball's flight direction. In a real launch-side install,
the radar sits a few feet to the side, and the cosine of that angle scales
the apparent speed.

**Procedure.** Use a known-speed reference — a ball thrown by hand isn't
precise enough; better is a tennis-ball machine or, ideally, your reference
launch monitor on the same shot. Take 10 shots with both the FlightImpact dev
kit and the reference monitor logging. The wizard fits the linear coefficient
that minimizes error against the reference, then writes it into the
`RadarCalibration.speed_per_hz_mph` field.

If you have no reference monitor handy, point the radar directly along the
firing line and use the textbook coefficient — it'll be accurate to within
a few percent for shots that fly close to that line.

## How often to re-calibrate

- **Camera intrinsics**: once per camera. Stable forever unless you change the
  lens or take a hard knock to the assembly.
- **Camera extrinsics**: every time you set the rig up. The whole point of
  the dev kit is portability, so the geometry changes every session.
- **Radar coefficient**: per-installation. Once you've got the radar mount
  finalized, it's stable.
