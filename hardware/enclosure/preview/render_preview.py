#!/usr/bin/env python3
"""
Approximate matplotlib preview of the FlightImpact enclosure.
Mirrors params.scad — does NOT execute OpenSCAD. Run OpenSCAD locally on
base.scad for the high-fidelity view.
"""
from __future__ import annotations
import re
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from matplotlib.patches import Rectangle, Circle
import numpy as np


def load_params(scad_path: Path) -> dict:
    text = scad_path.read_text()
    text = re.sub(r"//.*", "", text)
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)
    pattern = re.compile(r"^\s*([A-Z_][A-Z0-9_]*)\s*=\s*([^;]+);", re.MULTILINE)
    env: dict = {"max": max, "min": min}
    for m in pattern.finditer(text):
        name, expr = m.group(1), m.group(2).strip()
        try:
            value = eval(expr, {"__builtins__": {}}, env)
            if isinstance(value, (int, float)):
                env[name] = float(value)
        except Exception:
            pass
    env.pop("max", None); env.pop("min", None)
    return env


def frustum_vertices(w_bot, d_bot, w_top, d_top, height):
    return np.array([
        [-w_bot/2, -d_bot/2, 0], [w_bot/2, -d_bot/2, 0],
        [w_bot/2, d_bot/2, 0], [-w_bot/2, d_bot/2, 0],
        [-w_top/2, -d_top/2, height], [w_top/2, -d_top/2, height],
        [w_top/2, d_top/2, height], [-w_top/2, d_top/2, height],
    ])


def frustum_faces(v):
    return [
        [v[0], v[1], v[2], v[3]],
        [v[4], v[5], v[6], v[7]],
        [v[0], v[1], v[5], v[4]],
        [v[2], v[3], v[7], v[6]],
        [v[1], v[2], v[6], v[5]],
        [v[3], v[0], v[4], v[7]],
    ]


LONG_TAPER_F = 0.3


def render_iso(p, out):
    fig = plt.figure(figsize=(9, 7))
    ax = fig.add_subplot(111, projection="3d")
    base_w, base_d, base_h = p["BASE_W"], p["BASE_D"], p["BASE_H"]
    taper = p["BASE_TAPER"]
    top_w = base_w - 2 * taper * LONG_TAPER_F
    top_d = base_d - 2 * taper

    v = frustum_vertices(base_w, base_d, top_w, top_d, base_h)
    ax.add_collection3d(Poly3DCollection(
        frustum_faces(v), facecolor="#7a8b99",
        edgecolor="#1f2933", linewidths=0.6, alpha=0.85))

    rail_gap = p["DOCK_RAIL_GAP"]; rail_len = p["DOCK_RAIL_LEN"]
    rail_w = p["DOCK_RAIL_HEAD"]; rail_h = p["DOCK_RAIL_H"]
    for sy in (-1, 1):
        cx, cy = 0.0, sy * rail_gap / 2
        x0, x1 = cx - rail_len/2, cx + rail_len/2
        y0, y1 = cy - rail_w/2, cy + rail_w/2
        z0, z1 = base_h, base_h + rail_h
        v2 = np.array([
            [x0, y0, z0], [x1, y0, z0], [x1, y1, z0], [x0, y1, z0],
            [x0, y0, z1], [x1, y0, z1], [x1, y1, z1], [x0, y1, z1],
        ])
        ax.add_collection3d(Poly3DCollection(
            frustum_faces(v2), facecolor="#3b4a59",
            edgecolor="#0f1721", linewidths=0.6))

    pad = 10
    ax.set_xlim(-base_w/2 - pad, base_w/2 + pad)
    ax.set_ylim(-base_d/2 - pad, base_d/2 + pad)
    ax.set_zlim(0, base_h + 20)
    ax.set_box_aspect((base_w, base_d, base_h + 20))
    ax.view_init(elev=22, azim=-55)
    ax.set_xlabel("X (mm) — long")
    ax.set_ylabel("Y (mm) — depth")
    ax.set_zlabel("Z (mm) — height")
    ax.set_title(f"FlightImpact base — iso view\n{base_w:.1f} x {base_d:.1f} x {base_h:.1f} mm")
    fig.tight_layout(); fig.savefig(out, dpi=130); plt.close(fig)


def render_top(p, out):
    fig, ax = plt.subplots(figsize=(8, 6))
    base_w, base_d = p["BASE_W"], p["BASE_D"]
    taper = p["BASE_TAPER"]
    top_w = base_w - 2 * taper * LONG_TAPER_F
    top_d = base_d - 2 * taper

    ax.add_patch(Rectangle((-base_w/2, -base_d/2), base_w, base_d,
        facecolor="#dde4ec", edgecolor="#7a8b99", linewidth=1.0,
        label="bottom footprint"))
    ax.add_patch(Rectangle((-top_w/2, -top_d/2), top_w, top_d,
        facecolor="#9fb1c4", edgecolor="#1f2933", linewidth=1.2,
        label="top dock surface"))

    rail_gap = p["DOCK_RAIL_GAP"]; rail_len = p["DOCK_RAIL_LEN"]
    rail_head = p["DOCK_RAIL_HEAD"]
    for sy in (-1, 1):
        ax.add_patch(Rectangle(
            (-rail_len/2, sy * rail_gap/2 - rail_head/2),
            rail_len, rail_head, facecolor="#3b4a59",
            edgecolor="#0f1721", linewidth=0.8))
    ax.add_patch(Circle((0, -p["DOCK_CABLE_OD"]), p["DOCK_CABLE_OD"]/2,
        facecolor="white", edgecolor="#0f1721", linewidth=0.8))

    ax.set_aspect("equal")
    ax.set_xlim(-base_w/2 - 10, base_w/2 + 10)
    ax.set_ylim(-base_d/2 - 10, base_d/2 + 10)
    ax.set_xlabel("X (mm)"); ax.set_ylabel("Y (mm) — front is +Y")
    ax.set_title("Top view — dock interface")
    ax.grid(True, alpha=0.25); ax.legend(loc="upper right", fontsize=8)
    fig.tight_layout(); fig.savefig(out, dpi=130); plt.close(fig)


def render_front(p, out):
    fig, ax = plt.subplots(figsize=(9, 5))
    base_w, base_h = p["BASE_W"], p["BASE_H"]
    taper = p["BASE_TAPER"]
    top_w = base_w - 2 * taper * LONG_TAPER_F

    ax.add_patch(plt.Polygon([
        (-base_w/2, 0), (base_w/2, 0),
        (top_w/2, base_h), (-top_w/2, base_h),
    ], facecolor="#dde4ec", edgecolor="#1f2933", linewidth=1.2))

    ax.add_patch(Circle((p["FRONT_LED_X"], p["FRONT_LED_Z"]),
        p["LED_BEZEL_OD"]/2, facecolor="#ffd166",
        edgecolor="#1f2933", linewidth=0.8, label="status LED"))
    ax.add_patch(Circle((p["FRONT_BTN_X"], p["FRONT_BTN_Z"]),
        p["BTN_HOLE_OD"]/2, facecolor="#ef476f",
        edgecolor="#1f2933", linewidth=0.8, label="button"))
    ax.add_patch(Rectangle(
        (p["FRONT_USBC_X"] - 9.5/2, p["FRONT_USBC_Z"] - 3.8/2),
        9.5, 3.8, facecolor="#06d6a0",
        edgecolor="#1f2933", linewidth=0.8, label="USB-C in"))
    ax.add_patch(Rectangle(
        (p["FRONT_USBA_X"] - 13.8/2, p["FRONT_USBA_Z"] - 6.7/2),
        13.8, 6.7, facecolor="#118ab2",
        edgecolor="#1f2933", linewidth=0.8, label="USB-A out"))

    n = int(p["VENT_SLOTS_N"])
    pitch = p["VENT_SLOT_PITCH"]
    base_z = p.get("VENT_BASE_Z", 4.0)
    for i in range(n):
        x = -((n - 1) * pitch) / 2 + i * pitch
        ax.add_patch(Rectangle(
            (x - p["VENT_SLOT_W"]/2, base_z),
            p["VENT_SLOT_W"], p["VENT_SLOT_LEN"],
            facecolor="#1f2933"))

    ax.set_aspect("equal")
    ax.set_xlim(-base_w/2 - 10, base_w/2 + 10)
    ax.set_ylim(-5, base_h + 10)
    ax.set_xlabel("X (mm) — looking at front face")
    ax.set_ylabel("Z (mm) — height from floor")
    ax.set_title("Front panel layout")
    ax.grid(True, alpha=0.25); ax.legend(loc="upper right", fontsize=8)
    fig.tight_layout(); fig.savefig(out, dpi=130); plt.close(fig)


def main():
    here = Path(__file__).resolve().parent
    params = load_params(here.parent / "params.scad")
    print(f"Loaded {len(params)} params")
    render_iso(params, here / "preview_iso.png")
    render_top(params, here / "preview_top.png")
    render_front(params, here / "preview_front.png")
    print("Wrote previews to", here)


if __name__ == "__main__":
    main()
