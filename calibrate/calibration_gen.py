#!/usr/bin/env python3
"""
Calibration SVG for iDraw H A1 base plate.

Nested DIN A4-A1 frames (landscape + portrait) anchored at origin (0,0),
each with full diagonals. cm tick scales along the max-X and max-Y edges
of the A1 frame.

Output: 841 x 594 mm, true 1:1 coordinates, stroke-only plottable SVG.
"""

from pathlib import Path

# DIN sizes in mm: (name, width, height)
FRAMES = [
    ('A4 landscape', 297, 210),
    ('A4 portrait',  210, 297),
    ('A3 landscape', 420, 297),
    ('A3 portrait',  297, 420),
    ('A2 landscape', 594, 420),
    ('A2 portrait',  420, 594),
    ('A1 landscape', 841, 594),   # outer bound
]

W, H = 841, 594                   # A1 landscape canvas

STROKE  = 0.35                    # matches existing cuboid.py plotting style

# Tick lengths (mm), measured inward from the A1 edge
TICK_S  = 2                       # every 1 cm
TICK_M  = 4                       # every 5 cm
TICK_L  = 7                       # every 10 cm


def tick_len(cm: int) -> float:
    if cm % 10 == 0: return TICK_L
    if cm % 5  == 0: return TICK_M
    return TICK_S


out_lines = []
out_lines.append(
    f'<svg xmlns="http://www.w3.org/2000/svg" '
    f'viewBox="0 0 {W} {H}" width="{W}mm" height="{H}mm">'
)
out_lines.append('<rect width="100%" height="100%" fill="white"/>')
out_lines.append(
    f'<g fill="none" stroke="black" stroke-width="{STROKE}" '
    f'stroke-linecap="round" stroke-linejoin="miter">'
)

# --- Frames + diagonals ---
for name, w, h in FRAMES:
    out_lines.append(f'  <!-- {name} -->')
    out_lines.append(f'  <rect x="0" y="0" width="{w}" height="{h}"/>')
    out_lines.append(f'  <line x1="0" y1="0" x2="{w}" y2="{h}"/>')
    out_lines.append(f'  <line x1="0" y1="{h}" x2="{w}" y2="0"/>')

# --- X scale along max-Y edge of A1 (bottom) ---
# cm = 1..84 covers 10..840mm; 0 skipped to avoid overlap with A1 left edge
out_lines.append('  <!-- X scale (cm) along bottom of A1 -->')
for cm in range(1, 85):
    x = cm * 10
    t = tick_len(cm)
    out_lines.append(f'  <line x1="{x}" y1="{H - t}" x2="{x}" y2="{H}"/>')

# --- Y scale along max-X edge of A1 (right) ---
out_lines.append('  <!-- Y scale (cm) along right of A1 -->')
for cm in range(1, 60):
    y = cm * 10
    t = tick_len(cm)
    out_lines.append(f'  <line x1="{W - t}" y1="{y}" x2="{W}" y2="{y}"/>')

out_lines.append('</g>')
out_lines.append('</svg>')

out_path = Path(__file__).parent / 'svg' / 'calibration_a1.svg'
out_path.write_text('\n'.join(out_lines))

# --- Report ---
n_frames = len(FRAMES)
n_x_ticks = len(range(1, 85))
n_y_ticks = len(range(1, 60))
print(f"Written: {out_path}")
print(f"Canvas : {W} x {H} mm (A1 landscape)")
print(f"Frames : {n_frames} (A4/A3/A2 landscape+portrait, A1 landscape)")
print(f"X ticks: {n_x_ticks}  (long every 10cm, medium every 5cm, short every 1cm)")
print(f"Y ticks: {n_y_ticks}")
