"""Design tokens — colors, typography, spacing.

These are a direct port of the CSS custom properties + class styles from
`devkit/screen-mockups/index.html`. The mockups are the source of truth;
when this file drifts from them, update both. Same names where reasonable
so a designer reading both files sees the mapping.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from PIL import ImageFont


# --- Canvas --------------------------------------------------------------

WIDTH = 240
HEIGHT = 280
CORNER_RADIUS = 34  # only used by the mockup HTML for the bezel mask —
                    # the physical panel has its own rounded glass mask,
                    # so we draw to the full rectangle and let the glass crop.

# Standard inset for screen content. The mockup uses 16px `pad`.
PAD = 16


# --- Color palette -------------------------------------------------------
# RGB tuples — convert to PIL by passing directly.

BG = (5, 8, 16)          # --bg / screen background (#050810)
SURFACE = (15, 20, 29)   # --surface / tile background (#0f141d)
SURFACE_RAISED = (22, 27, 35)  # (#161b23) — for elevated panels

TEXT = (232, 238, 245)         # --text (#e8eef5)
TEXT_DIM = (138, 150, 163)     # --text-dim (#8a96a3)
TEXT_FAINT = (108, 122, 140)   # --text-faint (#6c7a8c)

MINT = (52, 211, 153)    # --mint (#34d399)
AMBER = (251, 191, 36)   # --amb (#fbbf24)
RED = (239, 68, 68)      # --red (#ef4444)
BLUE = (96, 165, 250)    # --blu (#60a5fa)

# Grid / divider lines on radar plots and trajectory chart.
GRID = (31, 42, 56)      # #1f2a38
GRID_FAINT = (15, 20, 29)  # #0f141d

# Mint tint for active CTA backgrounds (mockup uses `#34d39911` = 7% alpha).
MINT_TINT = (12, 36, 28)


# --- Typography ----------------------------------------------------------
# The mockups use system fonts (-apple-system / Inter). On the Pi we want a
# small set of fonts shipped with the package so we get pixel-identical
# renders. Fall back to DejaVu Sans if the bundled fonts aren't present.

_FONT_DIR = Path(__file__).parent / "fonts"

_FALLBACK_REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
_FALLBACK_MEDIUM = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def _resolve_font(name: str, fallback: str) -> str:
    candidate = _FONT_DIR / name
    if candidate.exists():
        return str(candidate)
    return fallback


@lru_cache(maxsize=32)
def font(size: int, *, weight: str = "regular") -> ImageFont.FreeTypeFont:
    """Look up a TTF at the given size. Cached — PIL font creation is cheap
    but we call this on every frame, so the cache adds up."""
    if weight == "medium" or weight == "bold":
        path = _resolve_font("Inter-Medium.ttf", _FALLBACK_MEDIUM)
    else:
        path = _resolve_font("Inter-Regular.ttf", _FALLBACK_REGULAR)
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.load_default()


# Type scale — mirrors the mockup `.h1` / `.h2` / `.h3` / `.cap` etc.
def font_h1() -> ImageFont.FreeTypeFont: return font(48, weight="medium")  # 152 mph
def font_h2() -> ImageFont.FreeTypeFont: return font(32, weight="medium")  # Ready / Capturing
def font_h3() -> ImageFont.FreeTypeFont: return font(18, weight="medium")  # screen titles
def font_body() -> ImageFont.FreeTypeFont: return font(13)                 # default body
def font_small() -> ImageFont.FreeTypeFont: return font(12)
def font_cap() -> ImageFont.FreeTypeFont: return font(10)                  # uppercase tag
def font_tile_label() -> ImageFont.FreeTypeFont: return font(9)            # tile small caps
def font_tile_value() -> ImageFont.FreeTypeFont: return font(18, weight="medium")


# --- Layout primitives ---------------------------------------------------

@dataclass(frozen=True)
class Tile:
    """A surface tile — rounded rectangle background with a small-caps
    label and a value. Used in the result & trajectory screens."""

    x: int
    y: int
    w: int
    h: int
    label: str
    value: str
    unit: str = ""


# Tile grids used by Result / Trajectory screens.
RESULT_TILE_GAP = 6
RESULT_TILE_RADIUS = 10
