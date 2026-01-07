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
SIZE_PX = 720
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

# Scale settings - دایره‌های بزرگتر
PCT_MAX = 22.0
r_small, r_big = 0.25, 1.25  # محدوده بزرگتر
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

def ease_out_cubic(t):
    """Smoother easing for drawing"""
    return 1 - pow(1 - t, 3)

# ---------- ANIMATION PHASES ----------
FRAMES_PER_CIRCLE = 40
PHASE1_FRAMES = n * FRAMES_PER_CIRCLE
PHASE2_FRAMES = 120
PHASE3_FRAMES = 150
HOLD_FRAMES = 90

total_frames = PHASE1_FRAMES + PHASE2_FRAMES + PHASE3_FRAMES + HOLD_FRAMES

# ---------- FIGURE SETUP ----------
fig = plt.figure(figsize=(SIZE_PX / DPI, SIZE_PX / DPI), dpi=DPI)
fig.patch.set_facecolor("#0a0a0a")

ax = fig.add_subplot(111, projection='3d')
ax.set_facecolor("#0a0a0a")
ax.grid(False)
ax.set_xlim(-1.6, 1.6)
ax.set_ylim(-1.6, 1.6)
ax.set_zlim(0, n * 0.12)

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

# Initial view: top-down
ax.view_init(elev=90, azim=-90)

# Text elements
title_text = fig.text(0.5, 0.95, TITLE_TEXT, ha="center", va="center",
                      color="#ffffff", fontsize=16, fontweight="bold", alpha=0.95)
subtitle_text = fig.text(0.5, 0.91, SUBTITLE_TEXT, ha="center", va="center",
                         color="#888888", fontsize=8, alpha=0.85)

# Store objects
lines = []
center_texts = []
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
    return lines + center_texts + [title_text, subtitle_text]

def update(frame):
    # Clear previous objects
    for line in lines:
        line.remove()
    lines.clear()
    
    for txt in center_texts:
        txt.remove()
    center_texts.clear()
    
    for txt in date_labels_3d:
        txt.remove()
    date_labels_3d.clear()
    
    # Determine phase
    if frame < PHASE1_FRAMES:
        # PHASE 1: 2D spiral animation
        circle_idx = frame // FRAMES_PER_CIRCLE
        circle_progress = (frame % FRAMES_PER_CIRCLE) / FRAMES_PER_CIRCLE
        circle_progress = ease_out_cubic(circle_progress)
        
        if circle_idx >= n:
            circle_idx = n - 1
            circle_progress = 1.0
        
        elev = 90
        azim = -90
        
        # رسم دایره‌های قبلی
        for i in range(circle_idx):
            theta = np.linspace(0, 2*np.pi, 200)
            x = r[i] * np.cos(theta)
            y = r[i] * np.sin(theta)
            z = np.zeros_like(theta)
            
            color = pct_color(vals[i])
            alpha = 0.5 - (i * 0.015)
            alpha = max(alpha, 0.15)
            lw = 2.5
            
            line = ax.plot(x, y, z, color=color, alpha=alpha, lw=lw)[0]
            lines.append(line)
        
        # رسم دایره فعلی
        if circle_idx < n:
            num_points = int(200 * circle_progress)
            if num_points >= 2:
                theta = np.linspace(0, 2*np.pi * circle_progress, num_points)
                x = r[circle_idx] * np.cos(theta)
                y = r[circle_idx] * np.sin(theta)
                z = np.zeros_like(theta)
                
                color = pct_color(vals[circle_idx])
                alpha = 0.95
                lw = 3.0
                
                line = ax.plot(x, y, z, color=color, alpha=alpha, lw=lw)[0]
                lines.append(line)
                
                # Glow effect
                line_glow = ax.plot(x, y, z, color=color, alpha=0.3, lw=7.0)[0]
                lines.append(line_glow)
            
            # نمایش متن در مرکز دایره (در مرکز صفحه)
            if circle_progress > 0.5:
                text_alpha = (circle_progress - 0.5) / 0.5
                
                # درصد در مرکز
                txt_pct = ax.text(0, 0, 0.01, f"{vals[circle_idx]:.1f}%",
                                color=pct_color(vals[circle_idx]),
                                fontsize=14, fontweight='bold',
                                ha='center', va='center',
                                alpha=text_alpha * 0.95)
                center_texts.append(txt_pct)
                
                # تاریخ زیر درصد
                txt_date = ax.text(0, 0, -0.05, labels[circle_idx],
                                 color="#aaaaaa",
                                 fontsize=8,
                                 ha='center', va='top',
                                 alpha=text_alpha * 0.85)
                center_texts.append(txt_date)
        
    elif frame < PHASE1_FRAMES + PHASE2_FRAMES:
        # PHASE 2: Transform to 3D cylinder
        phase_progress = (frame - PHASE1_FRAMES) / PHASE2_FRAMES
        t = ease_in_out(phase_progress)
        
        z_spacing = 0.12 * t
        elev = 90 - (45 * t)
        azim = -90 + (15 * t)
        
        for i in range(n):
            theta = np.linspace(0, 2*np.pi, 200)
            x = r[i] * np.cos(theta)
            y = r[i] * np.sin(theta)
            z = np.full_like(theta, i * z_spacing)
            
            color = pct_color(vals[i])
            alpha = 0.75 - (i * 0.01)
            alpha = max(alpha, 0.3)
            lw = 2.5
            
            line = ax.plot(x, y, z, color=color, alpha=alpha, lw=lw)[0]
            lines.append(line)
        
        # نمایش تاریخ‌ها در کنار استوانه با فاصله مشخص
        if t > 0.3:
            label_alpha = min(1.0, (t - 0.3) / 0.4)
            for i in range(n):
                # تاریخ‌ها در سمت راست با فاصله از استوانه
                txt = ax.text(1.5, 0, i * z_spacing, labels[i],
                            color="#ffffff", fontsize=7, alpha=label_alpha * 0.9,
                            ha='left', va='center',
                            bbox=dict(boxstyle='round,pad=0.3', 
                                    facecolor='#1a1a1a', 
                                    edgecolor='none',
                                    alpha=0.7))
                date_labels_3d.append(txt)
        
    elif frame < PHASE1_FRAMES + PHASE2_FRAMES + PHASE3_FRAMES:
        # PHASE 3: Rotate to side view
        phase_progress = (frame - PHASE1_FRAMES - PHASE2_FRAMES) / PHASE3_FRAMES
        t = ease_in_out(phase_progress)
        
        z_spacing = 0.12
        elev = 45 - (45 * t)
        azim = -75 + (75 * t)
        
        for i in range(n):
            theta = np.linspace(0, 2*np.pi, 200)
            x = r[i] * np.cos(theta)
            y = r[i] * np.sin(theta)
            z = np.full_like(theta, i * z_spacing)
            
            color = pct_color(vals[i])
            alpha = 0.85
            lw = 2.8
            
            line = ax.plot(x, y, z, color=color, alpha=alpha, lw=lw)[0]
            lines.append(line)
        
        # تاریخ‌ها در کنار با background برای خوانایی بهتر
        for i in range(n):
            txt = ax.text(1.5, 0, i * z_spacing, labels[i],
                        color="#ffffff", fontsize=7, alpha=0.9,
                        ha='left', va='center',
                        bbox=dict(boxstyle='round,pad=0.3', 
                                facecolor='#1a1a1a', 
                                edgecolor='none',
                                alpha=0.8))
            date_labels_3d.append(txt)
        
    else:
        # HOLD final view
        z_spacing = 0.12
        elev = 0
        azim = 0
        
        for i in range(n):
            theta = np.linspace(0, 2*np.pi, 200)
            x = r[i] * np.cos(theta)
            y = r[i] * np.sin(theta)
            z = np.full_like(theta, i * z_spacing)
            
            color = pct_color(vals[i])
            alpha = 0.85
            lw = 2.8
            
            line = ax.plot(x, y, z, color=color, alpha=alpha, lw=lw)[0]
            lines.append(line)
        
        # تاریخ‌ها با background مشکی برای جدا شدن از رنگ‌ها
        for i in range(n):
            txt = ax.text(1.5, 0, i * z_spacing, labels[i],
                        color="#ffffff", fontsize=7, alpha=0.9,
                        ha='left', va='center',
                        bbox=dict(boxstyle='round,pad=0.3', 
                                facecolor='#1a1a1a', 
                                edgecolor='none',
                                alpha=0.8))
            date_labels_3d.append(txt)
    
    # Update view smoothly
    ax.view_init(elev=elev, azim=azim)
    
    return lines + center_texts + date_labels_3d + [title_text, subtitle_text]

# ---------- SAVE ----------
anim = FuncAnimation(fig, update, frames=total_frames, init_func=init, interval=1000/FPS, blit=False)
anim.save(OUT_MP4, writer=FFMpegWriter(fps=FPS, bitrate=5000))
print(f"✓ Premium 3D transformation animation saved: {OUT_MP4}")
plt.close()