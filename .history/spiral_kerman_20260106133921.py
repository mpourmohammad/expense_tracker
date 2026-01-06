import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, FFMpegWriter
from matplotlib import font_manager
from mpl_toolkits.mplot3d import Axes3D

# ---------- FONT SETUP ----------
def set_english_font():
    preferred = ["Montserrat", "Poppins", "Inter", "Roboto", "Segoe UI", "Arial", "DejaVu Sans"]
    available = {f.name for f in font_manager.fontManager.ttflist}
    chosen = next((f for f in preferred if f in available), "DejaVu Sans")
    plt.rcParams["font.family"] = chosen

set_english_font()

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

# ---------- COLOR PALETTE ----------
def pct_color(v):
    if v >= 17.0:
        return (0.95, 0.25, 0.30)   # Red
    if v >= 9.0:
        return (1.00, 0.60, 0.10)   # Orange
    if v >= 6.0:
        return (1.00, 0.80, 0.35)   # Light Orange
    return (0.35, 0.85, 0.45)       # Green

def lerp(a, b, t):
    return a + (b - a) * t

def get_status(v):
    if v >= 17.0:
        return "CRITICAL", "#ff3344"
    if v >= 9.0:
        return "WARNING", "#ff9922"
    if v >= 6.0:
        return "MODERATE", "#ffcc66"
    return "EXCELLENT", "#35d555"

# ---------- SETTINGS ----------
FPS = 30
OUT_MP4 = "spiral_cylinder.mp4"
FRAMES_PER_ITEM = 35
HOLD_FRAMES = 8
TRAIL = 6
total_frames = n * (FRAMES_PER_ITEM + HOLD_FRAMES)

radius = 1.0
height = 0.3 * n  # فاصله محورها برای هر روز

theta_full = np.linspace(0, 2*np.pi, 300)

# ---------- FIGURE ----------
fig = plt.figure(figsize=(8, 6))
ax = fig.add_subplot(111, projection='3d')
fig.patch.set_facecolor("#0a0a0a")
ax.set_facecolor("#0a0a0a")

ax.set_xticks([])
ax.set_yticks([])
ax.set_zticks([])
ax.grid(False)

ax.set_box_aspect([1,1,0.6])
ax.view_init(elev=30, azim=-60)

# Trail storage
trail_lines = []

for _ in range(TRAIL):
    ln, = ax.plot([], [], [], lw=2, alpha=0)
    trail_lines.append(ln)

# ---------- ANIMATION FUNCTIONS ----------
def init():
    for ln in trail_lines:
        ln.set_data([], [])
        ln.set_3d_properties([])
        ln.set_alpha(0.0)
    return trail_lines

def update(frame):
    item_frame = frame % (FRAMES_PER_ITEM + HOLD_FRAMES)
    i = min(n-1, frame // (FRAMES_PER_ITEM + HOLD_FRAMES))
    
    # Drawing progress for current item
    if item_frame < FRAMES_PER_ITEM:
        draw_progress = item_frame / FRAMES_PER_ITEM
        draw_progress = 1 - (1 - draw_progress) ** 2
    else:
        draw_progress = 1.0
    
    points_to_draw = int(len(theta_full) * draw_progress)
    
    # Clear previous trails
    for ln in trail_lines:
        ln.set_data([], [])
        ln.set_3d_properties([])
        ln.set_alpha(0.0)
    
    # Determine which previous items to show
    start = max(0, i - TRAIL + 1)
    recent = list(range(start, i+1))
    denom = max(1, len(recent)-1)
    
    for k, j in enumerate(recent):
        if j < i:
            theta = theta_full
        else:
            if points_to_draw < 2:
                continue
            theta = theta_full[:points_to_draw]
        
        z = np.full_like(theta, j*0.3)
        r = radius * (0.5 + 0.5 * vals[j]/max(vals))
        x = r * np.cos(theta)
        y = r * np.sin(theta)
        
        color = pct_color(vals[j])
        fade = lerp(0.15, 0.8, k/denom) if j<i else 0.95
        
        ln = trail_lines[k]
        ln.set_data(x, y)
        ln.set_3d_properties(z)
        ln.set_color(color)
        ln.set_alpha(fade)
        ln.set_linewidth(2 + 1*(j==i))
    
    # Add date labels (show only current)
    ax.texts.clear()
    for idx in [i]:
        angle = np.pi/2
        x_label = (radius*1.1) * np.cos(angle)
        y_label = (radius*1.1) * np.sin(angle)
        ax.text(x_label, y_label, idx*0.3, labels[idx], color="white", fontsize=8, ha="center", va="center")
        # Center percentage
        ax.text(0,0, idx*0.3, f"{vals[idx]:.2f}%", color=pct_color(vals[idx]), fontsize=12, ha="center", va="center")
        stat, stat_color = get_status(vals[idx])
        ax.text(0,0, idx*0.3-0.05, stat, color=stat_color, fontsize=9, ha="center", va="center")
    
    return trail_lines + ax.texts

# ---------- SAVE ANIMATION ----------
anim = FuncAnimation(fig, update, frames=total_frames, init_func=init, blit=True)
writer = FFMpegWriter(fps=FPS, bitrate=4000)
anim.save(OUT_MP4, writer=writer)
print(f"✓ Cylinder animation saved: {OUT_MP4}")
plt.close()
