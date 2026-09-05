#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Antigravity Token Capsule - High-Quality Interactive Demo GIF Generator
========================================================================
Generates a smooth, loopable demo GIF (approx 7.7s, ~16 fps, 124 frames)
showcasing:
  1. Pill Mode (streamlined token ticking & breathing pulse)
  2. In-situ Telemetry Card expansion & 5-segment breakdown bar growth
  3. Subagent Cluster Tab switching & recursive multi-level tree hierarchy
  4. Instant Theme Hot-Swapping (Cyberpunk / Matrix Neon desktop aesthetics)
  5. Seamless transition back to the initial Pill Mode for infinite looping.

Output:
  tools/token-capsule/docs/images/00-demo.gif
"""

import sys
import os
import io
import math
import time
from PIL import Image, ImageDraw, ImageFilter
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QBuffer, QIODevice, Qt
from PySide6.QtGui import QColor

# Locate directories
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TOOL_DIR = os.path.dirname(SCRIPT_DIR)
SRC_DIR = os.path.join(TOOL_DIR, "src")
OUTPUT_GIF_PATH = os.path.join(TOOL_DIR, "docs", "images", "00-demo.gif")

for p in [TOOL_DIR, SRC_DIR]:
    if p not in sys.path:
        sys.path.insert(0, p)

from capsule_ui import CapsuleWindow, fmt_tokens

# Canvas and timing settings
CANVAS_WIDTH = 400
CANVAS_HEIGHT = 540
TARGET_CARD_WIDTH = 360  # Width of the card rendered on canvas
FRAME_DURATION_MS = 62   # ~16.1 fps, 124 frames -> 7.69s


def create_sample_dataset(active_ctx=42500, ttft=0.38, speed=68.0, subagent_running=True):
    """Generates structured mock telemetry data for driving CapsuleWindow state."""
    l2_1 = {
        "id": "l2-child-0001",
        "parentId": "l1-root-0001",
        "depth": 2,
        "role": "Backend Scout",
        "type": "researcher",
        "state": "running" if subagent_running else "done",
        "totalTokens": 20000,
        "costUsd": 0.024,
        "promptTokens": 18000,
        "candidateTokens": 2000,
        "thinkingTokens": 400,
        "cachedTokens": 12000,
        "ttft": 0.28,
        "speed": 62.0,
        "lastAction": "正在搜索架构代码...",
        "children": []
    }
    l2_2 = {
        "id": "l2-child-0002",
        "parentId": "l1-root-0001",
        "depth": 2,
        "role": "Frontend Scout",
        "type": "developer",
        "state": "done",
        "totalTokens": 30000,
        "costUsd": 0.036,
        "promptTokens": 26000,
        "candidateTokens": 4000,
        "thinkingTokens": 600,
        "cachedTokens": 18000,
        "ttft": 0.32,
        "speed": 75.0,
        "lastAction": "已完成组件构建",
        "children": []
    }
    l1 = {
        "id": "l1-root-0001",
        "parentId": "primary-0001",
        "depth": 1,
        "role": "Lead Architect",
        "type": "architect",
        "state": "running",
        "totalTokens": 45000,
        "costUsd": 0.054,
        "promptTokens": 40000,
        "candidateTokens": 5000,
        "thinkingTokens": 1000,
        "cachedTokens": 30000,
        "ttft": 0.38,
        "speed": 80.0,
        "lastAction": "协调子任务执行",
        "children": [l2_1, l2_2]
    }

    cluster = {
        "totalTokens": 95000,
        "totalCostUsd": 0.114,
        "combinedCostUsd": round(0.099 + 0.114, 3),
        "totalCount": 3,
        "runningCount": 2 if subagent_running else 1,
        "doneCount": 1 if subagent_running else 2,
        "activeCount": 2 if subagent_running else 1,
        "completedCount": 1 if subagent_running else 2,
        "subagents": [l1]
    }

    sys_tok = 8200
    tool_tok = 5400
    mcp_tok = 2300
    skills_tok = 1800
    msg_tok = max(0, active_ctx - (sys_tok + tool_tok + mcp_tok + skills_tok))

    return {
        "conversationId": "primary-demo-01",
        "title": "Antigravity Active Task",
        "autoFollow": True,
        "activeContext": active_ctx,
        "breakdown": {
            "system": {"tokens": sys_tok, "pct": round(sys_tok / 256000 * 100, 1)},
            "tools": {"tokens": tool_tok, "pct": round(tool_tok / 256000 * 100, 1)},
            "messages": {"tokens": msg_tok, "pct": round(msg_tok / 256000 * 100, 1)},
            "mcp": {"tokens": mcp_tok, "pct": round(mcp_tok / 256000 * 100, 1)},
            "skills": {"tokens": skills_tok, "pct": round(skills_tok / 256000 * 100, 1)}
        },
        "turn": {
            "promptTokens": 6200,
            "candidateTokens": 1400,
            "cachedTokens": 4500,
            "thinkingTokens": 350,
            "costUsd": 0.015,
            "ttft": ttft,
            "speed": speed
        },
        "cumulative": {
            "promptTokens": 32000,
            "candidateTokens": 9800,
            "cachedTokens": 21000,
            "thinkingTokens": 1800,
            "billedTokens": active_ctx,
            "totalContext": active_ctx + 21000,
            "cacheRatio": 38.5,
            "costUsd": round(0.080 + (active_ctx - 42500) / 300000, 3),
            "avgTtft": 0.38,
            "avgSpeed": round((68.0 + speed) / 2, 1)
        },
        "cluster": cluster
    }


def grab_as_pil_image(widget) -> Image.Image:
    """Grabs Qt widget snapshot with pixel-perfect alpha integrity via QBuffer."""
    pix = widget.grab()
    buf = QBuffer()
    buf.open(QIODevice.OpenModeFlag.WriteOnly)
    pix.save(buf, "PNG")
    img = Image.open(io.BytesIO(buf.data().data()))
    return img.convert("RGBA")


def build_base_canvas(width: int, height: int) -> Image.Image:
    """Constructs an elegant, modern dark studio background with subtle rounded border."""
    im = Image.new("RGB", (width, height), (13, 15, 20))
    draw = ImageDraw.Draw(im)

    # Subtle vertical gradient background
    for y in range(height):
        ratio = y / height
        r = int(18 - ratio * 7)
        g = int(21 - ratio * 8)
        b = int(28 - ratio * 10)
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    # Clean outer subtle border with rounded corner
    draw.rounded_rectangle(
        [6, 6, width - 7, height - 7],
        radius=14,
        fill=None,
        outline=(38, 44, 58),
        width=1
    )
    return im


def draw_soft_shadow(base_img: Image.Image, box, radius=12, offset_y=4, shadow_color=(0, 0, 0, 110)):
    """Draws a soft, natural drop shadow underneath a floating element."""
    shadow_mask = Image.new("RGBA", base_img.size, (0, 0, 0, 0))
    sdraw = ImageDraw.Draw(shadow_mask)
    x0, y0, x1, y1 = box
    sdraw.rounded_rectangle(
        [x0, y0 + offset_y, x1, y1 + offset_y],
        radius=14,
        fill=shadow_color
    )
    blurred_shadow = shadow_mask.filter(ImageFilter.GaussianBlur(radius))
    base_img.paste(blurred_shadow, (0, 0), blurred_shadow)


def composite_frame(
    bg_canvas: Image.Image,
    fg_image: Image.Image,
    target_width: int,
    pos_y: int,
    clip_height: int = None
) -> Image.Image:
    """Composites a foreground snapshot onto the studio canvas with soft shadow and scaling."""
    frame = bg_canvas.copy()

    # Scale to target width while keeping aspect ratio
    scale = target_width / fg_image.width
    scaled_w = int(fg_image.width * scale)
    scaled_h = int(fg_image.height * scale)
    scaled_fg = fg_image.resize((scaled_w, scaled_h), Image.Resampling.LANCZOS)

    if clip_height is not None and clip_height < scaled_h:
        # Clip from top downwards for expanding animation
        scaled_fg = scaled_fg.crop((0, 0, scaled_w, clip_height))
        scaled_h = clip_height

    pos_x = (bg_canvas.width - scaled_w) // 2

    # Draw natural drop shadow
    draw_soft_shadow(frame, (pos_x + 2, pos_y + 2, pos_x + scaled_w - 2, pos_y + scaled_h - 2))

    # Paste foreground
    frame.paste(scaled_fg, (pos_x, pos_y), scaled_fg)
    return frame


def main():
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

    print("=" * 65)
    print("  Antigravity Token Capsule - Demo GIF Synthesizer")
    print(f"  Target Output: {OUTPUT_GIF_PATH}")
    print("=" * 65)

    os.makedirs(os.path.dirname(OUTPUT_GIF_PATH), exist_ok=True)

    app = QApplication.instance() or QApplication(sys.argv)
    app.setApplicationName("DemoSynthesizer")

    # Initialize CapsuleWindow in compact mode
    win = CapsuleWindow(default_layout_mode="compact")
    win.show()
    app.processEvents()

    frames = []
    base_canvas = build_base_canvas(CANVAS_WIDTH, CANVAS_HEIGHT)

    # Initial data
    base_data = create_sample_dataset(active_ctx=42500)
    win.update_data(base_data)
    app.processEvents()

    total_sw_time = time.time()

    # -------------------------------------------------------------------------
    # STAGE 1: Pill Mode (Frames 0 ~ 23, 24 frames, ~1.49s)
    # Streamlined floating pill, live token ticks & breathing pulse
    # -------------------------------------------------------------------------
    print("\n[1/5] Synthesizing Stage 1: Pill Mode (Frames 0 ~ 23)...")
    win.card_frame.setVisible(False)
    win.pill_frame.setVisible(True)
    win.setMinimumWidth(0)
    win.setMaximumWidth(16777215)
    win.is_expanded = False
    win.set_theme("light", save=False)

    for i in range(24):
        # Progress token growth from 42.5k to 48.2k
        step_ratio = i / 23.0
        cur_tok = int(42500 + 5700 * (step_ratio ** 0.85))
        cur_ttft = round(0.38 - 0.03 * step_ratio, 2)
        cur_speed = round(68.0 + 10.5 * step_ratio, 1)

        d = create_sample_dataset(cur_tok, cur_ttft, cur_speed)
        win.update_data(d)

        # Breathing indicator pulse on pill_dot
        green_intensity = int(175 + 65 * math.sin(i * 0.45))
        win.pill_dot.setStyleSheet(
            f"background-color: rgb(16, {green_intensity}, 129); border-radius: 4px;"
        )

        win.adjustSize()
        app.processEvents()

        fg = grab_as_pil_image(win)
        frame = composite_frame(base_canvas, fg, target_width=335, pos_y=45)
        frames.append(frame)

    # -------------------------------------------------------------------------
    # STAGE 2: In-situ Telemetry Card Expansion (Frames 24 ~ 53, 30 frames, ~1.86s)
    # Expand into Telemetry Card, 5-segment breakdown bar growth & TTFT/Speed
    # -------------------------------------------------------------------------
    print("[2/5] Synthesizing Stage 2: In-situ Telemetry Card (Frames 24 ~ 53)...")
    win.card_frame.setVisible(True)
    win.pill_frame.setVisible(False)
    win.setFixedWidth(340)
    win.card_frame.setFixedWidth(340)
    win.is_expanded = True
    win.switch_tab("primary")

    card_data = create_sample_dataset(48200, ttft=0.35, speed=78.5)
    win.update_data(card_data)
    win.adjustSize()
    app.processEvents()

    # Pre-grab the fully laid out card
    fg_card_full = grab_as_pil_image(win)
    scale = TARGET_CARD_WIDTH / fg_card_full.width
    full_card_height = int(fg_card_full.height * scale)

    # Pill height on canvas when scaled
    pill_canvas_height = 36
    card_pos_y = 22

    # A. Smooth in-situ expansion animation (Frames 24 ~ 29, 6 frames)
    for i in range(6):
        t = (i + 1) / 6.0
        # Ease-out cubic curve
        ease_t = 1 - (1 - t) ** 3
        cur_clip_h = int(pill_canvas_height + (full_card_height - pill_canvas_height) * ease_t)
        frame = composite_frame(
            base_canvas,
            fg_card_full,
            target_width=TARGET_CARD_WIDTH,
            pos_y=card_pos_y,
            clip_height=cur_clip_h
        )
        frames.append(frame)

    # B. 5-Segment Progress Bar Growth & Metric Refresh (Frames 30 ~ 53, 24 frames)
    b_sys = 8200 / 256000
    b_tools = 5400 / 256000
    b_msg = (48200 - 8200 - 5400 - 2300 - 1800) / 256000
    b_mcp = 2300 / 256000
    b_skills = 1800 / 256000

    for i in range(24):
        # Progress bar growth factor from 0.0 to 1.0
        growth = min(1.0, (i + 1) / 10.0)
        win.prog_bar.set_segments([
            (b_sys * growth, QColor("#10b981")),
            (b_tools * growth, QColor("#f59e0b")),
            (b_msg * growth, QColor("#8b5cf6")),
            (b_mcp * growth, QColor("#06b6d4")),
            (b_skills * growth, QColor("#3b82f6")),
        ])

        # Subtly dynamic speed & ttft
        sp_jitter = 78.5 + 2.0 * math.sin(i * 0.6)
        ttft_jitter = round(0.35 + 0.02 * math.cos(i * 0.5), 2)
        win.val_speed.setText(f"{sp_jitter:.1f} tok/s (均速 73)")
        win.val_ttft.setText(f"{ttft_jitter:.2f}s (均值 0.38s)")

        win.adjustSize()
        app.processEvents()

        fg = grab_as_pil_image(win)
        frame = composite_frame(base_canvas, fg, target_width=TARGET_CARD_WIDTH, pos_y=card_pos_y)
        frames.append(frame)

    # -------------------------------------------------------------------------
    # STAGE 3: Subagent Cluster Accordion & Hierarchy (Frames 54 ~ 85, 32 frames, ~1.98s)
    # Switch to Subagents Tab, accordion expansion, L1 -> L2 recursive tree
    # -------------------------------------------------------------------------
    print("[3/5] Synthesizing Stage 3: Subagent Cluster & Multi-Level Tree (Frames 54 ~ 85)...")

    # A. Tab switch to Subagents (Frames 54 ~ 57, 4 frames)
    win.switch_tab("cluster")
    win.expanded_accordions.clear()
    win.expanded_branches.clear()
    win.update_data(card_data)
    win.adjustSize()
    app.processEvents()

    for i in range(4):
        fg = grab_as_pil_image(win)
        frame = composite_frame(base_canvas, fg, target_width=TARGET_CARD_WIDTH, pos_y=card_pos_y)
        frames.append(frame)

    # B. Open L1 Accordion (Frames 58 ~ 67, 10 frames)
    win.expanded_accordions.add("l1-root-0001")
    win.update_data(card_data)
    win.adjustSize()
    app.processEvents()

    for i in range(10):
        # Subtle heartbeat jitter on action
        if i % 4 == 0 and win.subagent_cards:
            win.subagent_cards[0].status_dot.setStyleSheet("background-color: #34d399; border-radius: 3px;")
        elif win.subagent_cards:
            win.subagent_cards[0].status_dot.setStyleSheet("background-color: #10b981; border-radius: 3px;")

        app.processEvents()
        fg = grab_as_pil_image(win)
        frame = composite_frame(base_canvas, fg, target_width=TARGET_CARD_WIDTH, pos_y=card_pos_y)
        frames.append(frame)

    # C. Open Recursive L2 Branch Tasks (Frames 68 ~ 85, 18 frames)
    win.expanded_branches.add("l1-root-0001")
    win.update_data(card_data)
    win.adjustSize()
    app.processEvents()

    for i in range(18):
        # Heartbeat pulse on running child
        tick_tok = 95000 + (i * 250)
        win.micro_metric_val.setText(f"计费 {fmt_tokens(tick_tok)} · $0.114")
        app.processEvents()
        fg = grab_as_pil_image(win)
        frame = composite_frame(base_canvas, fg, target_width=TARGET_CARD_WIDTH, pos_y=card_pos_y)
        frames.append(frame)

    # -------------------------------------------------------------------------
    # STAGE 4: Theme Hot-Swapping (Frames 86 ~ 111, 26 frames, ~1.61s)
    # Instant switch to Cyberpunk / Matrix Neon neon dark desktop aesthetics
    # -------------------------------------------------------------------------
    print("[4/5] Synthesizing Stage 4: Theme Hot-Swapping to Cyberpunk (Frames 86 ~ 111)...")
    win.set_theme("cyberpunk", save=False)
    win.adjustSize()
    app.processEvents()

    # Subagents view in Cyberpunk (Frames 86 ~ 98, 13 frames)
    for i in range(13):
        app.processEvents()
        fg = grab_as_pil_image(win)
        frame = composite_frame(base_canvas, fg, target_width=TARGET_CARD_WIDTH, pos_y=card_pos_y)
        frames.append(frame)

    # Switch back to Primary view to show glowing breakdown bar (Frames 99 ~ 111, 13 frames)
    win.switch_tab("primary")
    win.prog_bar.set_segments([
        (b_sys, QColor("#00ff9d")),
        (b_tools, QColor("#facc15")),
        (b_msg, QColor("#00f0ff")),
        (b_mcp, QColor("#38bdf8")),
        (b_skills, QColor("#a855f7")),
    ])
    win.adjustSize()
    app.processEvents()

    for i in range(13):
        app.processEvents()
        fg = grab_as_pil_image(win)
        frame = composite_frame(base_canvas, fg, target_width=TARGET_CARD_WIDTH, pos_y=card_pos_y)
        frames.append(frame)

    # -------------------------------------------------------------------------
    # STAGE 5: Smooth Transition Back to Pill Mode (Frames 112 ~ 123, 12 frames, ~0.74s)
    # Fold back smoothly into initial pill mode, seamlessly matching Frame 0
    # -------------------------------------------------------------------------
    print("[5/5] Synthesizing Stage 5: Loop Transition to Pill (Frames 112 ~ 123)...")
    # Restore light theme
    win.set_theme("light", save=False)
    win.card_frame.setVisible(True)
    win.adjustSize()
    app.processEvents()
    fg_card_light = grab_as_pil_image(win)

    # A. Smooth folding back upward (Frames 112 ~ 117, 6 frames)
    for i in range(6):
        t = (i + 1) / 6.0
        ease_t = 1.0 - (t ** 2)
        cur_clip_h = int(pill_canvas_height + (full_card_height - pill_canvas_height) * ease_t)
        frame = composite_frame(
            base_canvas,
            fg_card_light,
            target_width=TARGET_CARD_WIDTH,
            pos_y=card_pos_y,
            clip_height=cur_clip_h
        )
        frames.append(frame)

    # B. Back to Pill and smoothly interpolate back to Frame 0 values (Frames 118 ~ 123, 6 frames)
    win.card_frame.setVisible(False)
    win.pill_frame.setVisible(True)
    win.setMinimumWidth(0)
    win.setMaximumWidth(16777215)
    win.is_expanded = False

    for i in range(6):
        t = (i + 1) / 6.0
        # Interpolate from 48.2k back to 42.5k
        interp_tok = int(48200 - (48200 - 42500) * t)
        d = create_sample_dataset(interp_tok, ttft=0.38, speed=68.0)
        win.update_data(d)
        win.adjustSize()
        app.processEvents()

        fg = grab_as_pil_image(win)
        frame = composite_frame(base_canvas, fg, target_width=335, pos_y=45)
        frames.append(frame)

    # Close Qt
    app.quit()

    print(f"\nAll {len(frames)} frames rendered in {time.time() - total_sw_time:.2f}s.")
    print("Quantizing each frame with adaptive local palette and synthesizing GIF (loop=0)...")

    # Quantize each frame with its own local optimal palette (retaining crisp light & neon colors)
    quantized_frames = []
    for f in frames:
        q = f.convert("RGB").quantize(
            colors=256,
            method=Image.Resampling.LANCZOS,
            dither=Image.Dither.FLOYDSTEINBERG
        )
        quantized_frames.append(q)

    # Save animated GIF
    quantized_frames[0].save(
        OUTPUT_GIF_PATH,
        save_all=True,
        append_images=quantized_frames[1:],
        duration=FRAME_DURATION_MS,
        loop=0,
        optimize=True
    )

    file_size_bytes = os.path.getsize(OUTPUT_GIF_PATH)
    file_size_mb = file_size_bytes / (1024 * 1024)
    total_duration_sec = len(frames) * FRAME_DURATION_MS / 1000.0

    print("\n" + "=" * 65)
    print("SUCCESS: GIF Synthesis Completed Successfully!")
    print(f"  • Output Path: {OUTPUT_GIF_PATH}")
    print(f"  • Total Frames: {len(frames)}")
    print(f"  • Frame Rate: ~{1000.0 / FRAME_DURATION_MS:.1f} fps (Duration: {FRAME_DURATION_MS} ms/frame)")
    print(f"  • Total Duration: {total_duration_sec:.2f} seconds")
    print(f"  • Image Dimensions: {CANVAS_WIDTH} x {CANVAS_HEIGHT}")
    print(f"  • File Size: {file_size_mb:.2f} MB ({file_size_bytes:,} bytes)")
    print("=" * 65)


if __name__ == "__main__":
    main()
