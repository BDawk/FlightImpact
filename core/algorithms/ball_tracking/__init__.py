"""Ball tracking — link per-frame detections into a trajectory.

Approach: Kalman filter with constant-acceleration model in image space,
then back-project to world coordinates using the camera calibration.

Implementation lands in Phase 2.
"""
