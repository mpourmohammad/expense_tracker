import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, FFMpegWriter
import matplotlib as mpl
from matplotlib import font_manager

# ---------- PREMIUM FONT SETUP ----------
def set_english_font():
    preferred = ["Montserrat", "Poppins", "Inter", "Roboto", "Segoe UI", "Arial", "DejaVu Sans"]
    available = {f.name for f in font_manager.fontManager.ttflist}
    chosen = next((f for f in preferred if f in available), "DejaVu Sans")
    
    mpl.rcParams["font.family"] = chosen
    mpl.rcParams["axes.unicode_minus"] = False
    mpl.rcParams["text.usetex"] = False
    mpl.rcParams["mathtext.default"] = "regular"

set_english_font()

# Smooth, elegant lines
mpl.rcParams["path.sketch"] = (0.6, 80, 1.2)

# ---------- SETTINGS ----------
FPS = 30
SIZE_PX = 480
DPI = 200
OUT_MP4 = "spiral_kerman_clockwise.mp4"
TITLE_TEXT = "Kerman Branch"
SUBTITLE_TEXT = "Daily Performance Analysis"

# ---------- DATA ----------
rows = [
    ("1404/09/01", 11.40), ("1404/09/02", 4.44), ("1404/09/03", 16.81),
    ("1404/09/04", 5.26), ("1404/09/05", 5.39), ("1404/09/06", 14.19),
    ("1404/09/08", 10.05), ("1404/09/09", 10.63), ("1404/09/10", 10.93),
    ("1404/09/11", 10.67), ("1404/09/12", 21.14), ("1404/09/13", 11.83),
    ("1404/09/15", 6.33), ("1404/09/16", 4.97), ("1404/09/17", 20.75),
    ("1404/09/18", 10.38), ("1404/09/19", 10.17), ("1404/09/20", 10.95),
    ("1404/09/21", 17.53), ("1404/09/22", 18.05), ("1404/09/23", 8.28),
    ("1404/09/24", 14.52), ("1404/09/25", 9.72), ("1404/09/26", 9.76),
    ("1404/09/27", 15.62), ("1404/09/28", 14.76), ("1404/09/29", 8.34),
    ("1404/09/30", 10.23),
]

labels = [d for d, _ in rows]
vals = np.array([v for _, v in rows], dtype=float)
n = len(vals)

if n == 0:
    raise SystemExit("rows is empty")

# Scale settings
PCT_MAX = 22.0
r_small, r_big = 0.22, 0.95
r = r_small + np.clip(vals / PCT_MAX, 0, 1) * (r_big - r_small)

# Enhanced color palette
def pct_color(v):
    if v >= 17.0:
        return (0.95, 0.25, 0.30)   # Vibrant red
    if v >= 9.0:
        return (1.00, 0.60, 0.10)   # Rich orange
    if v >= 6.0:
        return (1.00, 0.80, 0.35)   # Warm light orange
    return (0.35, 0.85, 0.45)       # Fresh green

def lerp(a, b, t):
    return a + (b - a) * t

# ---------- FIGURE SETUP ----------
fig = plt.figure(figsize=(SIZE_PX / DPI, SIZE_PX / DPI), dpi=DPI)
fig.patch.set_facecolor("#0a0a0a")

ax = plt.subplot(111, projection="polar")
ax.set_facecolor("#0a0a0a")
ax.set_theta_direction(-1)
ax.set_theta_offset(np.pi/2)

ax.set_xticks([])
ax.set_xticklabels([])
ax.set_rlim(0.0, 1.20)
ax.set_yticklabels([])
ax.grid(False)
ax.spines['polar'].set_visible(False)

# Elegant guide rings
tt = np.linspace(0, 2*np.pi, 800)
for pct, alpha in [(5, 0.2), (10, 0.3), (15, 0.4), (20, 0.5)]:
    rr = r_small + (pct / PCT_MAX) * (r_big - r_small)
    ax.plot(tt, np.full_like(tt, rr), color="#2a2a2a", lw=1.0, alpha=alpha, zorder=1)

# Center glow
center_glow = plt.Circle((0, 0), 0.18, color="#1a1a1a", alpha=0.7, 
                         transform=ax.transData._b, zorder=0)
ax.add_patch(center_glow)

# Premium text styling - TITLE AT TOP
title_text = ax.text(
    0.5, 0.94, TITLE_TEXT,
    transform=ax.transAxes,
    ha="center", va="center",
    color="#ffffff",
    fontsize=14,
    fontweight="bold",
    alpha=0.95
)

subtitle_text = ax.text(
    0.5, 0.89, SUBTITLE_TEXT,
    transform=ax.transAxes,
    ha="center", va="center",
    color="#888888",
    fontsize=7,
    alpha=0.85
)

# Large percentage in CENTER
main_text = ax.text(
    0.5, 0.52, f"{vals[0]:.2f}%",
    transform=ax.transAxes,
    ha="center", va="center",
    color="#ffffff",
    fontsize=20,
    fontweight="bold",
    alpha=0.95
)

# Status indicator
status_text = ax.text(
    0.5, 0.44, "EXCELLENT",
    transform=ax.transAxes,
    ha="center", va="center",
    color="#35d555",
    fontsize=8,
    fontweight="bold",
    alpha=0.9
)

# DATE AT BOTTOM
date_text = ax.text(
    0.5, 0.06, labels[0],
    transform=ax.transAxes,
    ha="center", va="center",
    color="#aaaaaa",
    fontsize=10,
    alpha=0.9
)

# ---------- CLOCKWISE DRAWING ANIMATION ----------
TRAIL = 8  # Keep fewer visible circles for cleaner look
trail_lines = []
glow_lines = []

for _ in range(TRAIL):
    # Main line
    ln, = ax.plot([], [], lw=2.0, alpha=0.0, zorder=3)
    ln.set_sketch_params(scale=0.6, length=80, randomness=1.2)
    trail_lines.append(ln)
    
    # Glow effect
    glow, = ax.plot([], [], lw=5.0, alpha=0.0, zorder=2)
    glow.set_sketch_params(scale=0.6, length=80, randomness=1.2)
    glow_lines.append(glow)

FRAMES_PER_ITEM = 35  # Longer animation for smooth clockwise drawing
HOLD_FRAMES = 8  # Hold complete circle briefly
total_frames = n * (FRAMES_PER_ITEM + HOLD_FRAMES)

def get_status(v):
    if v >= 17.0:
        return "CRITICAL", "#ff3344"
    if v >= 9.0:
        return "WARNING", "#ff9922"
    if v >= 6.0:
        return "MODERATE", "#ffcc66"
    return "EXCELLENT", "#35d555"

def init():
    for ln, glow in zip(trail_lines, glow_lines):
        ln.set_data([], [])
        ln.set_alpha(0.0)
        glow.set_data([], [])
        glow.set_alpha(0.0)
    return trail_lines + glow_lines + [title_text, subtitle_text, main_text, date_text, status_text]

def update(frame):
    item_frame = frame % (FRAMES_PER_ITEM + HOLD_FRAMES)
    i = min(n - 1, frame // (FRAMES_PER_ITEM + HOLD_FRAMES))
    
    # Calculate drawing progress (0 to 1) for current circle
    if item_frame < FRAMES_PER_ITEM:
        draw_progress = item_frame / FRAMES_PER_ITEM
        # Ease-out for smoother end
        draw_progress = 1 - (1 - draw_progress) ** 2
    else:
        draw_progress = 1.0  # Fully drawn, holding
    
    # Number of points to draw for clockwise animation
    num_points = 1000
    theta_full = np.linspace(0, 2*np.pi, num_points)
    points_to_draw = int(num_points * draw_progress)
    
    # Clear all lines
    for ln, glow in zip(trail_lines, glow_lines):
        ln.set_data([], [])
        ln.set_alpha(0.0)
        glow.set_data([], [])
        glow.set_alpha(0.0)
    
    # Calculate which previous circles to show
    start = max(0, i - TRAIL + 1)
    recent = list(range(start, i + 1))
    denom = max(1, len(recent) - 1)
    
    for k, j in enumerate(recent):
        if j < i:
            # Previous circles - fully drawn with fade
            theta = theta_full
            wiggle = 0.003 * np.sin(theta * 5 + frame * 0.1)
            rr = np.full_like(theta, r[j]) + wiggle
        else:
            # Current circle - drawing clockwise
            if points_to_draw < 2:
                continue
            theta = theta_full[:points_to_draw]
            wiggle = 0.003 * np.sin(theta * 5 + frame * 0.1)
            rr = np.full(len(theta), r[j]) + wiggle
        
        color = pct_color(vals[j])
        
        # Fade based on position in trail
        if j < i:
            fade = lerp(0.15, 0.65, k / denom)
            line_width = 1.3
            glow_width = 4.0
        else:
            # Current circle - brighter
            fade = 0.95
            line_width = 2.5
            glow_width = 6.0
        
        # Glow layer
        glow = glow_lines[k]
        glow.set_data(theta, rr)
        glow.set_color(color)
        glow.set_alpha(fade * 0.2)
        glow.set_linewidth(glow_width)
        
        # Main line
        ln = trail_lines[k]
        ln.set_data(theta, rr)
        ln.set_color(color)
        ln.set_alpha(fade)
        ln.set_linewidth(line_width)
    
    # Smooth text transitions
    if item_frame < 10:
        alpha = item_frame / 10
        main_text.set_alpha(alpha * 0.95)
        status_text.set_alpha(alpha * 0.9)
        date_text.set_alpha(alpha * 0.9)
    
    main_text.set_text(f"{vals[i]:.2f}%")
    main_text.set_color(pct_color(vals[i]))
    date_text.set_text(labels[i])
    
    stat, stat_color = get_status(vals[i])
    status_text.set_text(stat)
    status_text.set_color(stat_color)
    
    return (trail_lines + glow_lines + 
            [title_text, subtitle_text, main_text, date_text, status_text])

# ---------- SAVE ----------
anim = FuncAnimation(fig, update, frames=total_frames, init_func=init, blit=True)
anim.save(OUT_MP4, writer=FFMpegWriter(fps=FPS, bitrate=4000))
print(f"✓ Premium clockwise animation saved: {OUT_MP4}")
plt.close()