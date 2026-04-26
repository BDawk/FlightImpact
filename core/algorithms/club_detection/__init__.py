"""Club detection — locate clubhead approach and impact.

Approach: motion-vector field across pre-impact frames; cluster fast-moving
pixels in the lower portion of the frame; fit a path and orientation.

Implementation lands in Phase 3.
"""
