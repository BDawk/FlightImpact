"""Sensor fusion — reconcile camera-derived and radar-derived measurements.

The camera gives ball speed via pixel-displacement / time. The radar gives
radial speed via Doppler. Both have known error characteristics; the fusion
step picks the best estimate (or weighted average) per metric, and produces
the per-metric confidence values stored on ShotMetrics.

Implementation lands in Phase 4 (after both sensors produce real outputs).
"""
