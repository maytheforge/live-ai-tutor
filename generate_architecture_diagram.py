#!/usr/bin/env python3
"""Generate the architecture diagram for Live AI Tutor hackathon submission."""

from PIL import Image, ImageDraw, ImageFont
import os

W, H = 1600, 1000
BG = "#0F172A"       # dark navy
CARD = "#1E293B"     # card bg
BORDER = "#334155"   # card border
ACCENT1 = "#3B82F6"  # blue (Google)
ACCENT2 = "#10B981"  # green (agents)
ACCENT3 = "#F59E0B"  # amber (frontend)
ACCENT4 = "#8B5CF6"  # purple (cloud)
WHITE = "#F8FAFC"
GRAY = "#94A3B8"
ARROW = "#64748B"

img = Image.new("RGB", (W, H), BG)
draw = ImageDraw.Draw(img)

# Try to load a font
try:
    font_title = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 28)
    font_heading = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 18)
    font_body = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 14)
    font_small = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 12)
    font_label = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 11)
except:
    font_title = ImageFont.load_default()
    font_heading = font_title
    font_body = font_title
    font_small = font_title
    font_label = font_title


def rounded_rect(xy, fill, outline, radius=12, width=2):
    x0, y0, x1, y1 = xy
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)


def draw_arrow(x1, y1, x2, y2, color=ARROW, width=2, dashed=False):
    draw.line([(x1, y1), (x2, y2)], fill=color, width=width)
    # arrowhead
    import math
    angle = math.atan2(y2 - y1, x2 - x1)
    size = 10
    draw.polygon([
        (x2, y2),
        (x2 - size * math.cos(angle - 0.4), y2 - size * math.sin(angle - 0.4)),
        (x2 - size * math.cos(angle + 0.4), y2 - size * math.sin(angle + 0.4)),
    ], fill=color)


def draw_bidir_arrow(x1, y1, x2, y2, color=ARROW, width=2):
    draw.line([(x1, y1), (x2, y2)], fill=color, width=width)
    import math
    angle = math.atan2(y2 - y1, x2 - x1)
    size = 10
    # Forward arrow
    draw.polygon([
        (x2, y2),
        (x2 - size * math.cos(angle - 0.4), y2 - size * math.sin(angle - 0.4)),
        (x2 - size * math.cos(angle + 0.4), y2 - size * math.sin(angle + 0.4)),
    ], fill=color)
    # Backward arrow
    angle2 = angle + math.pi
    draw.polygon([
        (x1, y1),
        (x1 - size * math.cos(angle2 - 0.4), y1 - size * math.sin(angle2 - 0.4)),
        (x1 - size * math.cos(angle2 + 0.4), y1 - size * math.sin(angle2 + 0.4)),
    ], fill=color)


# ============================================================
# TITLE
# ============================================================
draw.text((W // 2, 30), "Live AI Tutor — System Architecture", fill=WHITE, font=font_title, anchor="mt")
draw.text((W // 2, 62), "Google Gemini Live Agent Challenge  |  Real-Time Multimodal Socratic Tutoring", fill=GRAY, font=font_small, anchor="mt")

# ============================================================
# SECTION: STUDENT (left)
# ============================================================
sx, sy = 30, 110
rounded_rect((sx, sy, sx + 240, sy + 220), CARD, ACCENT3, 14, 2)
draw.text((sx + 120, sy + 14), "Student", fill=ACCENT3, font=font_heading, anchor="mt")
draw.line([(sx + 20, sy + 38), (sx + 220, sy + 38)], fill=BORDER, width=1)
draw.text((sx + 20, sy + 50), "Voice (Microphone)", fill=WHITE, font=font_body)
draw.text((sx + 20, sy + 72), "Camera (Webcam)", fill=WHITE, font=font_body)
draw.text((sx + 20, sy + 94), "File Upload (Image)", fill=WHITE, font=font_body)
draw.text((sx + 20, sy + 116), "Text Input", fill=WHITE, font=font_body)
draw.text((sx + 20, sy + 150), "Receives:", fill=GRAY, font=font_small)
draw.text((sx + 20, sy + 168), "Voice responses", fill=WHITE, font=font_body)
draw.text((sx + 20, sy + 190), "Canvas drawings", fill=WHITE, font=font_body)

# ============================================================
# SECTION: REACT FRONTEND (center-left)
# ============================================================
fx, fy = 310, 100
rounded_rect((fx, fy, fx + 340, fy + 370), CARD, ACCENT3, 14, 2)
draw.text((fx + 170, fy + 14), "React Frontend (Vite)", fill=ACCENT3, font=font_heading, anchor="mt")
draw.text((fx + 170, fy + 36), "localhost:5173 / Cloud Run static", fill=GRAY, font=font_small, anchor="mt")
draw.line([(fx + 15, fy + 54), (fx + 325, fy + 54)], fill=BORDER, width=1)

# Sub-boxes inside frontend
# useGeminiLive hook
rounded_rect((fx + 15, fy + 65, fx + 325, fy + 120), "#1a2744", ACCENT1, 8, 1)
draw.text((fx + 25, fy + 72), "useGeminiLive.js", fill=ACCENT1, font=font_body)
draw.text((fx + 25, fy + 92), "WebSocket → Gemini Live API", fill=GRAY, font=font_small)

# App.jsx
rounded_rect((fx + 15, fy + 130, fx + 325, fy + 185), "#1a2744", ACCENT3, 8, 1)
draw.text((fx + 25, fy + 137), "App.jsx — Tool Call Handler", fill=ACCENT3, font=font_body)
draw.text((fx + 25, fy + 157), "Routes snapshots + messages → Backend", fill=GRAY, font=font_small)

# CanvasBoard
rounded_rect((fx + 15, fy + 195, fx + 325, fy + 250), "#1a2744", "#10B981", 8, 1)
draw.text((fx + 25, fy + 202), "CanvasBoard.jsx (Excalidraw)", fill="#10B981", font=font_body)
draw.text((fx + 25, fy + 222), "Interactive whiteboard + AI drawings", fill=GRAY, font=font_small)

# Pages
rounded_rect((fx + 15, fy + 260, fx + 160, fy + 305), "#1a2744", BORDER, 8, 1)
draw.text((fx + 25, fy + 268), "HomePage.jsx", fill=WHITE, font=font_body)
draw.text((fx + 25, fy + 286), "Landing / Upload", fill=GRAY, font=font_small)

rounded_rect((fx + 170, fy + 260, fx + 325, fy + 305), "#1a2744", BORDER, 8, 1)
draw.text((fx + 180, fy + 268), "TutorPage.jsx", fill=WHITE, font=font_body)
draw.text((fx + 180, fy + 286), "Session Interface", fill=GRAY, font=font_small)

# Tech badges
draw.text((fx + 15, fy + 320), "React 18  |  Vite 7  |  Excalidraw  |  Axios", fill=GRAY, font=font_label)
draw.text((fx + 15, fy + 340), "react-webcam  |  lucide-react  |  react-router", fill=GRAY, font=font_label)

# ============================================================
# SECTION: GEMINI LIVE API (top center)
# ============================================================
gx, gy = 700, 100
rounded_rect((gx, gy, gx + 280, gy + 130), CARD, ACCENT1, 14, 2)
draw.text((gx + 140, gy + 14), "Gemini Live API", fill=ACCENT1, font=font_heading, anchor="mt")
draw.text((gx + 140, gy + 36), "Google Cloud", fill=GRAY, font=font_small, anchor="mt")
draw.line([(gx + 15, gy + 54), (gx + 265, gy + 54)], fill=BORDER, width=1)
draw.text((gx + 20, gy + 64), "Real-time voice (WebSocket)", fill=WHITE, font=font_body)
draw.text((gx + 20, gy + 84), "Audio in: 16kHz PCM", fill=GRAY, font=font_small)
draw.text((gx + 20, gy + 102), "Audio out: 24kHz PCM", fill=GRAY, font=font_small)

# ============================================================
# SECTION: FASTAPI BACKEND (center-right)
# ============================================================
bx, by = 700, 280
rounded_rect((bx, by, bx + 560, by + 410), CARD, ACCENT2, 14, 2)
draw.text((bx + 280, by + 14), "FastAPI Backend (Python 3.11)", fill=ACCENT2, font=font_heading, anchor="mt")
draw.text((bx + 280, by + 36), "Cloud Run  |  Port 8080  |  Uvicorn", fill=GRAY, font=font_small, anchor="mt")
draw.line([(bx + 15, by + 56), (bx + 545, by + 56)], fill=BORDER, width=1)

# API Endpoints
draw.text((bx + 20, by + 65), "API Endpoints:", fill=GRAY, font=font_small)
draw.text((bx + 20, by + 83), "POST /interact   GET /health   GET /session/*", fill=WHITE, font=font_body)

# Vision Agent
rounded_rect((bx + 15, by + 110, bx + 265, by + 175), "#1a2744", ACCENT1, 8, 1)
draw.text((bx + 25, by + 117), "Vision Agent", fill=ACCENT1, font=font_body)
draw.text((bx + 25, by + 137), "Gemini 1.5 Flash", fill=GRAY, font=font_small)
draw.text((bx + 25, by + 153), "Image → Problem analysis", fill=GRAY, font=font_small)

# ADK Orchestrator box
rounded_rect((bx + 15, by + 185, bx + 545, by + 390), "#162033", ACCENT4, 10, 2)
draw.text((bx + 280, by + 192), "Google ADK Orchestrator (InMemoryRunner)", fill=ACCENT4, font=font_body, anchor="mt")
draw.line([(bx + 25, by + 212), (bx + 535, by + 212)], fill=BORDER, width=1)

# Root Agent
rounded_rect((bx + 25, by + 222, bx + 280, by + 295), "#1a2744", ACCENT2, 8, 1)
draw.text((bx + 35, by + 229), "Root: Tutor Agent", fill=ACCENT2, font=font_body)
draw.text((bx + 35, by + 249), "Gemini 2.5 Flash", fill=GRAY, font=font_small)
draw.text((bx + 35, by + 265), "Socratic prompting logic", fill=GRAY, font=font_small)

# Canvas Sub-Agent
rounded_rect((bx + 290, by + 222, bx + 535, by + 295), "#1a2744", ACCENT3, 8, 1)
draw.text((bx + 300, by + 229), "Sub: Canvas Agent", fill=ACCENT3, font=font_body)
draw.text((bx + 300, by + 249), "add_text, clear_board", fill=GRAY, font=font_small)
draw.text((bx + 300, by + 265), "highlight_area", fill=GRAY, font=font_small)

# Diagram Sub-Agent
rounded_rect((bx + 25, by + 305, bx + 280, by + 378), "#1a2744", ACCENT3, 8, 1)
draw.text((bx + 35, by + 312), "Sub: Diagram Agent", fill=ACCENT3, font=font_body)
draw.text((bx + 35, by + 332), "draw_math_equation_steps", fill=GRAY, font=font_small)
draw.text((bx + 35, by + 348), "draw_math_number_line", fill=GRAY, font=font_small)
draw.text((bx + 35, by + 362), "draw_science_flow", fill=GRAY, font=font_small)

# Review + Reinforcement
rounded_rect((bx + 290, by + 305, bx + 535, by + 378), "#1a2744", BORDER, 8, 1)
draw.text((bx + 300, by + 312), "Review Agent", fill=WHITE, font=font_body)
draw.text((bx + 300, by + 332), "Session recording & summary", fill=GRAY, font=font_small)
draw.text((bx + 300, by + 352), "Reinforcement Agent", fill=WHITE, font=font_body)
draw.text((bx + 300, by + 370), "Practice problem generation", fill=GRAY, font=font_small)

# ============================================================
# SECTION: GOOGLE CLOUD (bottom)
# ============================================================
cx, cy = 30, 780
rounded_rect((cx, cy, cx + 620, cy + 100), CARD, ACCENT4, 14, 2)
draw.text((cx + 310, cy + 12), "Google Cloud Platform", fill=ACCENT4, font=font_heading, anchor="mt")
draw.line([(cx + 15, cy + 34), (cx + 605, cy + 34)], fill=BORDER, width=1)

services = ["Cloud Run", "Cloud Build", "Artifact Registry", "Container Registry"]
for i, svc in enumerate(services):
    sx2 = cx + 20 + i * 150
    rounded_rect((sx2, cy + 42, sx2 + 140, cy + 78), "#1a2744", BORDER, 6, 1)
    draw.text((sx2 + 70, cy + 52), svc, fill=WHITE, font=font_body, anchor="mt")

# Tech stack badge at bottom
rounded_rect((cx + 660, cy, cx + 960, cy + 100), CARD, BORDER, 14, 2)
draw.text((cx + 810, cy + 12), "Tech Stack", fill=GRAY, font=font_heading, anchor="mt")
draw.line([(cx + 675, cy + 34), (cx + 945, cy + 34)], fill=BORDER, width=1)
draw.text((cx + 675, cy + 44), "AI: Gemini 2.5 Flash, 1.5 Flash", fill=WHITE, font=font_small)
draw.text((cx + 675, cy + 62), "Orchestration: Google ADK 1.27", fill=WHITE, font=font_small)
draw.text((cx + 675, cy + 80), "Deploy: Docker + Cloud Run", fill=WHITE, font=font_small)

# Category badge
rounded_rect((cx + 970, cy, cx + 1240, cy + 100), CARD, ACCENT1, 14, 2)
draw.text((cx + 1105, cy + 12), "Hackathon Category", fill=ACCENT1, font=font_heading, anchor="mt")
draw.line([(cx + 985, cy + 34), (cx + 1225, cy + 34)], fill=BORDER, width=1)
draw.text((cx + 1105, cy + 52), "Live Agents", fill=ACCENT3, font=font_heading, anchor="mt")
draw.text((cx + 1105, cy + 76), "Real-time Voice + Vision", fill=GRAY, font=font_small, anchor="mt")

# ============================================================
# ARROWS / CONNECTIONS
# ============================================================

# Student → Frontend
draw_bidir_arrow(270, 220, 310, 220, ACCENT3, 2)

# Frontend (useGeminiLive) → Gemini Live API
draw_bidir_arrow(650, 165, 700, 165, ACCENT1, 2)
draw.text((655, 145), "WebSocket", fill=ACCENT1, font=font_label)

# Frontend (App.jsx) → Backend
draw_arrow(650, 340, 700, 400, ACCENT2, 2)
draw.text((648, 355), "POST /interact", fill=ACCENT2, font=font_label)

# Backend → Frontend (canvas actions)
draw_arrow(700, 430, 650, 370, ACCENT3, 2)
draw.text((632, 410), "Canvas JSON", fill=ACCENT3, font=font_label)

# Vision Agent arrow (internal)
draw_arrow(bx + 140, by + 175, bx + 140, by + 185, ACCENT1, 2)

# Backend to Cloud
draw_arrow(bx + 100, by + 410, 310, 830, ACCENT4, 2)

# ============================================================
# DATA FLOW LABEL (right side)
# ============================================================
rounded_rect((1310, 110, 1570, 440), CARD, BORDER, 14, 2)
draw.text((1440, 124), "Data Flow", fill=WHITE, font=font_heading, anchor="mt")
draw.line([(1325, 148), (1555, 148)], fill=BORDER, width=1)

flows = [
    ("1.", "Student speaks / shows paper", ACCENT3),
    ("2.", "Voice → Gemini Live (WS)", ACCENT1),
    ("3.", "Snapshot → POST /interact", ACCENT2),
    ("4.", "VisionAgent analyzes image", ACCENT1),
    ("5.", "ADK Orchestrator routes", ACCENT4),
    ("6.", "TutorAgent asks Socratic Q", ACCENT2),
    ("7.", "Sub-agents draw on canvas", ACCENT3),
    ("8.", "Voice + visuals → Student", WHITE),
]

for i, (num, text, color) in enumerate(flows):
    y = 162 + i * 34
    draw.text((1325, y), num, fill=color, font=font_body)
    draw.text((1348, y), text, fill=GRAY, font=font_small)

# ============================================================
# SAVE
# ============================================================
out_path = os.path.join(os.path.dirname(__file__), "architecture-diagram.png")
img.save(out_path, "PNG", quality=95)
print(f"Saved: {out_path}")
