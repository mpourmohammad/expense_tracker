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

# ---------- SETTINGS ----------
FPS = 30
SIZE_PX = 480
DPI = 200
OUT_MP4 = "spiral_3d_transformation.mp4"
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

def ease_in_out(t):
    """Smooth easing function"""
    return t * t * (3 - 2 * t)

# ---------- ANIMATION PHASES ----------
# Phase 1: 2D clockwise spiral (like your original)
# Phase 2: Transform to 3D cylinder
# Phase 3: Rotate to side view with dates

PHASE1_FRAMES = n * 35  # Original 2D spiral animation
PHASE2_FRAMES = 90      # Transform to 3D cylinder
PHASE3_FRAMES = 120     # Rotate to side view
HOLD_FRAMES = 60        # Hold final view

total_frames = PHASE1_FRAMES + PHASE2_FRAMES + PHASE3_FRAMES + HOLD_FRAMES

# ---------- FIGURE SETUP ----------
fig = plt.figure(figsize=(SIZE_PX / DPI, SIZE_PX / DPI), dpi=DPI)
fig.patch.set_facecolor("#0a0a0a")

ax = fig.add_subplot(111, projection='3d')
ax.set_facecolor("#0a0a0a")
ax.grid(False)
ax.set_xlim(-1.2, 1.2)
ax.set_ylim(-1.2, 1.2)
ax.set_zlim(0, n * 0.08)

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

# Initial view: top-down (like polar plot)
ax.view_init(elev=90, azim=0)

# Text elements
title_text = fig.text(0.5, 0.94, TITLE_TEXT, ha="center", va="center",
                      color="#ffffff", fontsize=14, fontweight="bold", alpha=0.95)
subtitle_text = fig.text(0.5, 0.89, SUBTITLE_TEXT, ha="center", va="center",
                         color="#888888", fontsize=7, alpha=0.85)
main_text = fig.text(0.5, 0.52, "", ha="center", va="center",
                     color="#ffffff", fontsize=20, fontweight="bold", alpha=0.95)
status_text = fig.text(0.5, 0.44, "", ha="center", va="center",
                       color="#35d555", fontsize=8, fontweight="bold", alpha=0.9)
date_text = fig.text(0.5, 0.06, "", ha="center", va="center",
                     color="#aaaaaa", fontsize=10, alpha=0.9)

# Store line objects
lines = []
date_labels_3d = []

def get_status(v):
    if v >= 17.0:
        return "CRITICAL", "#ff3344"
    if v >= 9.0:
        return "WARNING", "#ff9922"
    if v >= 6.0:
        return "MODERATE", "#ffcc66"
    return "EXCELLENT", "#35d555"

def init():
    return lines + [title_text, subtitle_text, main_text, date_text, status_text]

def update(frame):
    # Clear previous lines
    for line in lines:
        line.remove()
    lines.clear()
    
    for txt in date_labels_3d:
        txt.remove()
    date_labels_3d.clear()
    
    # Determine phase
    if frame < PHASE1_FRAMES:
        # PHASE 1: 2D spiral animation
        phase = 1
        phase_progress = frame / PHASE1_FRAMES
        
        # Calculate which circle we're drawing
        item_idx = int(phase_progress * n)
        if item_idx >= n:
            item_idx = n - 1
        
        z_depth = 0  # Flat
        elev = 90
        azim = 0
        
        # Draw completed circles
        for i in range(item_idx + 1):
            theta = np.linspace(0, 2*np.pi, 200)
            x = r[i] * np.cos(theta)
            y = r[i] * np.sin(theta)
            z = np.zeros_like(theta)
            
            color = pct_color(vals[i])
            alpha = 0.8 if i == item_idx else 0.4
            lw = 2.5 if i == item_idx else 1.5
            
            line = ax.plot(x, y, z, color=color, alpha=alpha, lw=lw)[0]
            lines.append(line)
        
        # Update text
        if item_idx < n:
            main_text.set_text(f"{vals[item_idx]:.2f}%")
            main_text.set_color(pct_color(vals[item_idx]))
            date_text.set_text(labels[item_idx])
            stat, stat_color = get_status(vals[item_idx])
            status_text.set_text(stat)
            status_text.set_color(stat_color)
        
    elif frame < PHASE1_FRAMES + PHASE2_FRAMES:
        # PHASE 2: Transform to 3D cylinder
        phase = 2
        phase_progress = (frame - PHASE1_FRAMES) / PHASE2_FRAMES
        t = ease_in_out(phase_progress)
        
        # Gradually increase Z spacing and rotate view
        z_spacing = 0.08 * t
        elev = 90 - (40 * t)  # Tilt from 90 to 50 degrees
        azim = 0
        
        for i in range(n):
            theta = np.linspace(0, 2*np.pi, 200)
            x = r[i] * np.cos(theta)
            y = r[i] * np.sin(theta)
            z = np.full_like(theta, i * z_spacing)
            
            color = pct_color(vals[i])
            alpha = 0.7
            lw = 2.0
            
            line = ax.plot(x, y, z, color=color, alpha=alpha, lw=lw)[0]
            lines.append(line)
        
        # Fade out 2D text
        main_text.set_alpha(0.95 * (1 - t))
        status_text.set_alpha(0.9 * (1 - t))
        date_text.set_alpha(0.9 * (1 - t))
        
    elif frame < PHASE1_FRAMES + PHASE2_FRAMES + PHASE3_FRAMES:
        # PHASE 3: Rotate to side view
        phase = 3
        phase_progress = (frame - PHASE1_FRAMES - PHASE2_FRAMES) / PHASE3_FRAMES
        t = ease_in_out(phase_progress)
        
        z_spacing = 0.08
        elev = 50 - (50 * t)  # Tilt to 0 degrees (side view)
        azim = 0 + (0 * t)
        
        for i in range(n):
            theta = np.linspace(0, 2*np.pi, 200)
            x = r[i] * np.cos(theta)
            y = r[i] * np.sin(theta)
            z = np.full_like(theta, i * z_spacing)
            
            color = pct_color(vals[i])
            alpha = 0.8
            lw = 2.0
            
            line = ax.plot(x, y, z, color=color, alpha=alpha, lw=lw)[0]
            lines.append(line)
        
        # Add date labels in side view
        if t > 0.5:
            label_alpha = (t - 0.5) * 2
            for i in range(0, n, 3):  # Show every 3rd date
                txt = ax.text(1.0, 0, i * z_spacing, labels[i],
                            color="#aaaaaa", fontsize=6, alpha=label_alpha)
                date_labels_3d.append(txt)
        
        main_text.set_alpha(0)
        status_text.set_alpha(0)
        date_text.set_alpha(0)
        
    else:
        # HOLD final view
        phase = 4
        z_spacing = 0.08
        elev = 0
        azim = 0
        
        for i in range(n):
            theta = np.linspace(0, 2*np.pi, 200)
            x = r[i] * np.cos(theta)
            y = r[i] * np.sin(theta)
            z = np.full_like(theta, i * z_spacing)
            
            color = pct_color(vals[i])
            alpha = 0.8
            lw = 2.0
            
            line = ax.plot(x, y, z, color=color, alpha=alpha, lw=lw)[0]
            lines.append(line)
        
        # Show all date labels
        for i in range(0, n, 2):
            txt = ax.text(1.0, 0, i * z_spacing, labels[i],
                        color="#aaaaaa", fontsize=6, alpha=0.9)
            date_labels_3d.append(txt)
        
        main_text.set_alpha(0)
        status_text.set_alpha(0)
        date_text.set_alpha(0)
    
    # Update view
    ax.view_init(elev=elev, azim=azim)
    
    return lines + date_labels_3d + [title_text, subtitle_text, main_text, date_text, status_text]

# ---------- SAVE ----------
anim = FuncAnimation(fig, update, frames=total_frames, init_func=init, interval=1000/FPS)
anim.save(OUT_MP4, writer=FFMpegWriter(fps=FPS, bitrate=4000))
print(f"✓ 3D transformation animation saved: {OUT_MP4}")
plt.close()