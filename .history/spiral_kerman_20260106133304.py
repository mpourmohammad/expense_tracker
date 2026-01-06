import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, FFMpegWriter
import matplotlib as mpl
from matplotlib import font_manager
from mpl_toolkits.mplot3d import Axes3D

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

# Smooth lines
mpl.rcParams["path.sketch"] = (0.6, 80, 1.2)

# ---------- SETTINGS ----------
FPS = 30
SIZE_PX = 600
DPI = 150
OUT_MP4 = "spiral_kerman_cylinder.mp4"
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

# Enhanced color palette
def pct_color(v):
    if v >= 17.0:
        return (0.95, 0.25, 0.30)
    if v >= 9.0:
        return (1.00, 0.60, 0.10)
    if v >= 6.0:
        return (1.00, 0.80, 0.35)
    return (0.35, 0.85, 0.45)

def get_status(v):
    if v >= 17.0:
        return "CRITICAL", "#ff3344"
    if v >= 9.0:
        return "WARNING", "#ff9922"
    if v >= 6.0:
        return "MODERATE", "#ffcc66"
    return "EXCELLENT", "#35d555"

def lerp(a, b, t):
    return a + (b - a) * t

def ease_in_out(t):
    return t * t * (3 - 2 * t)

# ---------- ANIMATION SETTINGS ----------
FRAMES_PER_CIRCLE = 25  # Duration for each circle drawing
HOLD_FRAMES = 5         # Hold after completing circle
total_frames = n * (FRAMES_PER_CIRCLE + HOLD_FRAMES)

# Scale settings
PCT_MAX = 22.0
r_min, r_max = 0.3, 1.2
radii = r_min + np.clip(vals / PCT_MAX, 0, 1) * (r_max - r_min)

# Create circle points
theta_full = np.linspace(0, 2*np.pi, 200)

# ---------- FIGURE SETUP ----------
fig = plt.figure(figsize=(SIZE_PX / DPI, SIZE_PX / DPI), dpi=DPI)
fig.patch.set_facecolor("#0a0a0a")

ax = fig.add_subplot(111, projection='3d')
ax.set_facecolor("#0a0a0a")
ax.grid(False)
ax.set_xlim(-1.5, 1.5)
ax.set_ylim(-1.5, 1.5)
ax.set_zlim(0, n * 0.15)

# Hide axes
ax.set_xticks([])
ax.set_yticks([])
ax.set_zticks([])
ax.xaxis.pane.fill = False
ax.yaxis.pane.fill = False
ax.zaxis.pane.fill = False
ax.xaxis.pane.set_edgecolor('none')
ax.yaxis.pane.set_edgecolor('none')
ax.zaxis.pane.set_edgecolor('none')

# Set 3D view angle
ax.view_init(elev=25, azim=-60)

# Title at top
title_text = fig.text(0.5, 0.94, TITLE_TEXT, ha='center', va='top',
                      color='white', fontsize=14, fontweight='bold', alpha=0.95)

subtitle_text = fig.text(0.5, 0.90, SUBTITLE_TEXT, ha='center', va='top',
                         color='#888888', fontsize=7, alpha=0.85)

# Center percentage
value_text = fig.text(0.5, 0.53, "", ha='center', va='center',
                      color='white', fontsize=18, fontweight='bold', alpha=0.95)

# Status
status_text = fig.text(0.5, 0.46, "", ha='center', va='center',
                       color='white', fontsize=8, fontweight='bold', alpha=0.9)

# Date at bottom
date_text = fig.text(0.5, 0.06, "", ha='center', va='bottom',
                     color='#aaaaaa', fontsize=10, alpha=0.9)

# Storage for circles and glows
circles_3d = []
glows_3d = []
for i in range(n):
    # Glow
    glow, = ax.plot([], [], [], lw=5.0, alpha=0.0)
    glows_3d.append(glow)
    # Main line
    line, = ax.plot([], [], [], lw=2.5, alpha=0.0)
    circles_3d.append(line)

TRAIL = 8  # Number of visible previous circles

def init():
    for line, glow in zip(circles_3d, glows_3d):
        line.set_data([], [])
        line.set_3d_properties([])
        line.set_alpha(0.0)
        glow.set_data([], [])
        glow.set_3d_properties([])
        glow.set_alpha(0.0)
    return circles_3d + glows_3d + [title_text, subtitle_text, value_text, date_text, status_text]

def update(frame):
    item_frame = frame % (FRAMES_PER_CIRCLE + HOLD_FRAMES)
    i = min(n - 1, frame // (FRAMES_PER_CIRCLE + HOLD_FRAMES))
    
    # Calculate drawing progress for clockwise animation
    if item_frame < FRAMES_PER_CIRCLE:
        draw_progress = item_frame / FRAMES_PER_CIRCLE
        draw_progress = 1 - (1 - draw_progress) ** 2  # Ease-out
    else:
        draw_progress = 1.0
    
    # Slow rotation
    rotation = (frame / total_frames) * 30
    ax.view_init(elev=25, azim=-60 + rotation)
    
    # Clear all
    for line, glow in zip(circles_3d, glows_3d):
        line.set_data([], [])
        line.set_3d_properties([])
        line.set_alpha(0.0)
        glow.set_data([], [])
        glow.set_3d_properties([])
        glow.set_alpha(0.0)
    
    # Calculate visible range
    start = max(0, i - TRAIL + 1)
    recent = list(range(start, i + 1))
    denom = max(1, len(recent) - 1)
    
    for k, j in enumerate(recent):
        z_level = j * 0.15
        
        if j < i:
            # Previous circles - fully drawn
            theta = theta_full
            r = radii[j]
            x = r * np.cos(theta)
            y = r * np.sin(theta)
            z = np.full_like(theta, z_level)
        else:
            # Current circle - drawing clockwise
            num_points = len(theta_full)
            points_to_draw = int(num_points * draw_progress)
            if points_to_draw < 2:
                continue
            theta = theta_full[:points_to_draw]
            r = radii[j]
            x = r * np.cos(theta)
            y = r * np.sin(theta)
            z = np.full(len(theta), z_level)
        
        color = pct_color(vals[j])
        
        # Fade based on position
        if j < i:
            fade = lerp(0.20, 0.70, k / denom)
            line_width = 2.0
            glow_width = 4.5
        else:
            fade = 0.95
            line_width = 3.0
            glow_width = 6.5
        
        # Glow
        glow = glows_3d[j]
        glow.set_data(x, y)
        glow.set_3d_properties(z)
        glow.set_color(color)
        glow.set_alpha(fade * 0.2)
        glow.set_linewidth(glow_width)
        
        # Main line
        line = circles_3d[j]
        line.set_data(x, y)
        line.set_3d_properties(z)
        line.set_color(color)
        line.set_alpha(fade)
        line.set_linewidth(line_width)
    
    # Text updates
    if item_frame < 10:
        alpha = item_frame / 10
        value_text.set_alpha(alpha * 0.95)
        status_text.set_alpha(alpha * 0.9)
        date_text.set_alpha(alpha * 0.9)
    
    value_text.set_text(f"{vals[i]:.2f}%")
    value_text.set_color(pct_color(vals[i]))
    date_text.set_text(labels[i])
    
    stat, stat_color = get_status(vals[i])
    status_text.set_text(stat)
    status_text.set_color(stat_color)
    
    return (circles_3d + glows_3d + 
            [title_text, subtitle_text, value_text, date_text, status_text])

# ---------- SAVE ----------
anim = FuncAnimation(fig, update, frames=total_frames, init_func=init, blit=False, interval=1000/FPS)
anim.save(OUT_MP4, writer=FFMpegWriter(fps=FPS, bitrate=4500))
duration = total_frames / FPS
print(f"✓ 3D Cylinder animation saved: {OUT_MP4}")
print(f"Duration: {duration:.1f} seconds")
plt.close()