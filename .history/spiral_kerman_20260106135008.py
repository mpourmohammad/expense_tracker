import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, FFMpegWriter

# ---------- ENGLISH FONT ONLY ----------
import matplotlib as mpl
from matplotlib import font_manager

def set_english_font():
    preferred = ["Montserrat", "Poppins", "Inter", "Roboto", "Segoe UI", "Arial", "DejaVu Sans"]
    available = {f.name for f in font_manager.fontManager.ttflist}
    chosen = next((f for f in preferred if f in available), "DejaVu Sans")

    mpl.rcParams["font.family"] = chosen
    mpl.rcParams["axes.unicode_minus"] = False
    mpl.rcParams["text.usetex"] = False
    mpl.rcParams["mathtext.default"] = "regular"

set_english_font()

# ✏️ hand-drawn / pencil effect for paths
mpl.rcParams["path.sketch"] = (1.2, 120, 2.5)

# ---------- SETTINGS ----------
FPS = 30
SIZE_PX = 360
DPI = 180
OUT_MP4 = "spiral_kerman.mp4"
TITLE_TEXT = "Kerman Branch"

# ---------- DATA ----------
rows = [
    ("1404/09/01", 11.40),
    ("1404/09/02", 4.44),
    ("1404/09/03", 16.81),
    ("1404/09/04", 5.26),
    ("1404/09/05", 5.39),
    ("1404/09/06", 14.19),
    ("1404/09/08", 10.05),
    ("1404/09/09", 10.63),
    ("1404/09/10", 10.93),
    ("1404/09/11", 10.67),
    ("1404/09/12", 21.14),
    ("1404/09/13", 11.83),
    ("1404/09/15", 6.33),
    ("1404/09/16", 4.97),
    ("1404/09/17", 20.75),
    ("1404/09/18", 10.38),
    ("1404/09/19", 10.17),
    ("1404/09/20", 10.95),
    ("1404/09/21", 17.53),
    ("1404/09/22", 18.05),
    ("1404/09/23", 8.28),
    ("1404/09/24", 14.52),
    ("1404/09/25", 9.72),
    ("1404/09/26", 9.76),
    ("1404/09/27", 15.62),
    ("1404/09/28", 14.76),
    ("1404/09/29", 8.34),
    ("1404/09/30", 10.23),
]

labels = [d for d, _ in rows]
vals = np.array([v for _, v in rows], dtype=float)
n = len(vals)

if n == 0:
    raise SystemExit("rows is empty")

# scale for Kerman (max ~21.14)
PCT_MAX = 22.0

r_small, r_big = 0.15, 1.05
r = r_small + np.clip(vals / PCT_MAX, 0, 1) * (r_big - r_small)

theta_smooth = np.linspace(0, 2*np.pi, 720)

# ✅ NEW color rules:
# >=17 red
# 9..17 orange
# 6..9 light orange
# <6 green
def pct_color(v):
    if v >= 17.0:
        return (0.90, 0.20, 0.20)   # red
    if v >= 9.0:
        return (1.00, 0.55, 0.00)   # orange
    if v >= 6.0:
        return (1.00, 0.75, 0.40)   # light orange
    return (0.30, 0.75, 0.35)       # green

def lerp(a, b, t):
    return a + (b - a) * t

# ---------- FIGURE ----------
fig = plt.figure(figsize=(SIZE_PX / DPI, SIZE_PX / DPI), dpi=DPI)
fig.patch.set_facecolor("black")

ax = plt.subplot(111, projection="polar")
ax.set_facecolor("black")
ax.set_theta_direction(-1)
ax.set_theta_offset(np.pi/2)

ax.set_xticks([])
ax.set_xticklabels([])
ax.set_rlim(0.0, 1.2)
ax.set_yticklabels([])
ax.grid(False)

# guide rings (subtle)
tt = np.linspace(0, 2*np.pi, 600)
for pct in [0, 1, 2]:
    rr = r_small + (pct / PCT_MAX) * (r_big - r_small)
    ax.plot(tt, np.full_like(tt, rr), color="#444444", lw=0.6, alpha=0.6)

# texts
title_text = ax.text(
    0.5, 0.93, TITLE_TEXT,
    transform=ax.transAxes,
    ha="center", va="center",
    color="white",
    fontsize=9
)

main_text = ax.text(
    0.5, 0.52, f"{vals[0]:.2f}%",
    transform=ax.transAxes,
    ha="center", va="center",
    color="white",
    fontsize=11,
    fontweight="bold"
)

date_text = ax.text(
    0.5, 0.08, labels[0],
    transform=ax.transAxes,
    ha="center", va="center",
    color="white",
    fontsize=8
)

# ---------- HAND-DRAWN CIRCLES ----------
TRAIL = 25
trail_lines = []
for _ in range(TRAIL):
    ln, = ax.plot([], [], lw=0.9, alpha=0.0)
    ln.set_sketch_params(scale=1.2, length=120, randomness=2.5)
    trail_lines.append(ln)

FRAMES_PER_ITEM = 18
total_frames = n * FRAMES_PER_ITEM

def init():
    for ln in trail_lines:
        ln.set_data([], [])
        ln.set_alpha(0.0)
    return trail_lines + [title_text, main_text, date_text]

def update(frame):
    i = min(n - 1, frame // FRAMES_PER_ITEM)

    start = max(0, i - TRAIL + 1)
    recent = list(range(start, i + 1))
    denom = max(1, len(recent) - 1)

    for ln in trail_lines:
        ln.set_data([], [])
        ln.set_alpha(0.0)

    for k, j in enumerate(recent):
        # subtle "pencil" wiggle
        wiggle = 0.003 * np.sin(theta_smooth * 7 + frame * 0.15)
        rr = np.full_like(theta_smooth, r[j]) + wiggle

        ln = trail_lines[k]
        ln.set_data(theta_smooth, rr)
        ln.set_color(pct_color(vals[j]))
        ln.set_alpha(lerp(0.15, 0.85, k / denom))
        ln.set_linewidth(0.7 if j < i else 1.2)

    main_text.set_text(f"{vals[i]:.2f}%")
    date_text.set_text(labels[i])

    return trail_lines + [title_text, main_text, date_text]

# ---------- SAVE ----------
anim = FuncAnimation(fig, update, frames=total_frames, init_func=init, blit=True)
anim.save(OUT_MP4, writer=FFMpegWriter(fps=FPS, bitrate=2500))
print("Saved:", OUT_MP4)