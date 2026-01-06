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
SIZE_PX = 600
DPI = 150
OUT_MP4 = "spiral_kerman_cylinder.mp4"
TITLE_TEXT = "Kerman Branch"

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

# ---------- ANIMATION PHASES ----------
PHASE1_FRAMES = 60   # Flat circle view
PHASE2_FRAMES = 80   # Transition to 3D cylinder
PHASE3_FRAMES = 120  # Stack circles to build cylinder
total_frames = PHASE1_FRAMES + PHASE2_FRAMES + PHASE3_FRAMES

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

# Title
title_text = fig.text(0.5, 0.95, TITLE_TEXT, ha='center', va='top',
                      color='white', fontsize=16, fontweight='bold')

# Date text
date_text = fig.text(0.5, 0.05, "", ha='center', va='bottom',
                     color='#aaaaaa', fontsize=11)

# Value text
value_text = fig.text(0.5, 0.90, "", ha='center', va='top',
                      color='white', fontsize=13, fontweight='bold')

# Scale settings
PCT_MAX = 22.0
r_min, r_max = 0.3, 1.2
radii = r_min + np.clip(vals / PCT_MAX, 0, 1) * (r_max - r_min)

# Create circle data
theta = np.linspace(0, 2*np.pi, 200)

def lerp(a, b, t):
    return a + (b - a) * t

def ease_in_out(t):
    return t * t * (3 - 2 * t)

# Storage for 3D lines
circles_3d = []
for i in range(n):
    line, = ax.plot([], [], [], lw=2.5, alpha=0.0)
    circles_3d.append(line)

def init():
    for line in circles_3d:
        line.set_data([], [])
        line.set_3d_properties([])
    return circles_3d + [title_text, date_text, value_text]

def update(frame):
    # Clear all circles
    for line in circles_3d:
        line.set_data([], [])
        line.set_3d_properties([])
        line.set_alpha(0.0)
    
    # PHASE 1: Show flat circle view (top view)
    if frame < PHASE1_FRAMES:
        idx = int((frame / PHASE1_FRAMES) * n)
        idx = min(idx, n - 1)
        
        # Set top view
        ax.view_init(elev=90, azim=0)
        
        # Draw current circle
        r = radii[idx]
        x = r * np.cos(theta)
        y = r * np.sin(theta)
        z = np.zeros_like(theta)
        
        circles_3d[0].set_data(x, y)
        circles_3d[0].set_3d_properties(z)
        circles_3d[0].set_color(pct_color(vals[idx]))
        circles_3d[0].set_alpha(0.95)
        circles_3d[0].set_linewidth(3.0)
        
        date_text.set_text(labels[idx])
        value_text.set_text(f"{vals[idx]:.2f}%")
        value_text.set_color(pct_color(vals[idx]))
    
    # PHASE 2: Transition to 3D view
    elif frame < PHASE1_FRAMES + PHASE2_FRAMES:
        progress = (frame - PHASE1_FRAMES) / PHASE2_FRAMES
        progress = ease_in_out(progress)
        
        # Rotate camera
        elev = lerp(90, 25, progress)
        azim = lerp(0, -60, progress)
        ax.view_init(elev=elev, azim=azim)
        
        # Show first few circles stacking
        num_show = int(progress * 8) + 1
        for i in range(min(num_show, n)):
            r = radii[i]
            x = r * np.cos(theta)
            y = r * np.sin(theta)
            z_level = i * 0.15 * progress
            z = np.full_like(theta, z_level)
            
            circles_3d[i].set_data(x, y)
            circles_3d[i].set_3d_properties(z)
            circles_3d[i].set_color(pct_color(vals[i]))
            circles_3d[i].set_alpha(0.85)
            circles_3d[i].set_linewidth(2.5)
        
        date_text.set_text("Building Cylinder...")
        value_text.set_text("")
    
    # PHASE 3: Build complete cylinder
    else:
        progress = (frame - PHASE1_FRAMES - PHASE2_FRAMES) / PHASE3_FRAMES
        
        # Slow rotation
        azim = -60 + (progress * 30)
        ax.view_init(elev=25, azim=azim)
        
        # Build cylinder progressively
        num_show = int(progress * n)
        num_show = min(num_show, n)
        
        for i in range(num_show):
            r = radii[i]
            x = r * np.cos(theta)
            y = r * np.sin(theta)
            z_level = i * 0.15
            z = np.full_like(theta, z_level)
            
            circles_3d[i].set_data(x, y)
            circles_3d[i].set_3d_properties(z)
            circles_3d[i].set_color(pct_color(vals[i]))
            
            # Fade older circles slightly
            age_factor = 1.0 - (i / max(1, num_show)) * 0.3
            circles_3d[i].set_alpha(0.75 * age_factor)
            circles_3d[i].set_linewidth(2.2)
        
        # Show current date
        if num_show > 0:
            current_idx = num_show - 1
            date_text.set_text(labels[current_idx])
            value_text.set_text(f"{vals[current_idx]:.2f}%")
            value_text.set_color(pct_color(vals[current_idx]))
        
        # Highlight current circle
        if num_show > 0:
            circles_3d[num_show - 1].set_alpha(0.95)
            circles_3d[num_show - 1].set_linewidth(3.5)
    
    return circles_3d + [title_text, date_text, value_text]

# ---------- SAVE ----------
anim = FuncAnimation(fig, update, frames=total_frames, init_func=init, blit=False, interval=1000/FPS)
anim.save(OUT_MP4, writer=FFMpegWriter(fps=FPS, bitrate=4000))
print(f"✓ 3D Cylinder animation saved: {OUT_MP4}")
print(f"Duration: {total_frames/FPS:.1f} seconds")
plt.close()