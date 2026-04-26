"""Spin extraction — measure ball spin rate and axis.

Two strategies:
  1. Marked-ball: detect logo / marks across post-impact frames, fit rotation.
  2. Dimple-pattern: optical flow on dimple texture (much harder, needs
     either very high frame rate or very sharp images).

Implementation lands in Phase 3 — marked-ball first, dimple-pattern as
a stretch goal.
"""
