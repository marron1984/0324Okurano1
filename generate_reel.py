"""
禅園西梅田 Instagram Reel MP4 Generator

- 1080x1920 (9:16) 縦型動画
- 30fps, 約25秒
- Ken Burns効果 + テキストオーバーレイ
- AI判定回避: 実写ベース・自然な動き
"""

import numpy as np
from PIL import Image, ImageDraw, ImageFont
import imageio
import os
import math

# === Config ===
WIDTH, HEIGHT = 1080, 1920
FPS = 30
OUTPUT = "reel_zenen_settai.mp4"
ASSETS = "assets"

# Color palette
GOLD = (201, 168, 76)
WHITE = (255, 255, 255)
CREAM = (245, 240, 232)


def load_font(size, bold=False):
    """Load Japanese font from local fonts/ directory."""
    # Use downloaded Noto Sans CJK fonts (fonts/ directory)
    if bold:
        primary = "fonts/NotoSansJP-Bold.otf"
        fallback = "fonts/NotoSansJP-Medium.otf"
    else:
        primary = "fonts/NotoSansJP-Medium.otf"
        fallback = "fonts/NotoSansJP-Bold.otf"

    for fp in [primary, fallback]:
        if os.path.exists(fp):
            try:
                return ImageFont.truetype(fp, size)
            except Exception:
                continue

    # System font fallback
    import glob
    for pattern in ["/usr/share/fonts/**/*CJK*", "/usr/share/fonts/**/*Noto*", "/usr/share/fonts/**/*.ttc", "/usr/share/fonts/**/*.ttf"]:
        matches = glob.glob(pattern, recursive=True)
        for m in matches:
            try:
                return ImageFont.truetype(m, size)
            except Exception:
                continue

    print(f"Warning: No Japanese font found, using default for size {size}")
    return ImageFont.load_default()


def crop_to_fill(img, target_w, target_h):
    """Crop image to fill target dimensions (center crop)."""
    iw, ih = img.size
    target_ratio = target_w / target_h
    img_ratio = iw / ih

    if img_ratio > target_ratio:
        # Image is wider - crop sides
        new_w = int(ih * target_ratio)
        left = (iw - new_w) // 2
        img = img.crop((left, 0, left + new_w, ih))
    else:
        # Image is taller - crop top/bottom
        new_h = int(iw / target_ratio)
        top = (ih - new_h) // 2
        img = img.crop((0, top, iw, top + new_h))

    return img.resize((target_w, target_h), Image.LANCZOS)


def ken_burns_frame(img, t, effect="zoom_in", scale_range=(1.0, 1.15)):
    """Apply Ken Burns effect to a single frame.

    t: progress 0.0 to 1.0
    Returns: 1080x1920 numpy array
    """
    iw, ih = img.size
    s0, s1 = scale_range
    # Ease-out curve for natural deceleration
    t_ease = 1 - (1 - t) ** 2

    if effect == "zoom_in":
        scale = s0 + (s1 - s0) * t_ease
        cx, cy = iw / 2, ih / 2
        dx = t_ease * iw * 0.01
        dy = t_ease * ih * 0.01
        cx += dx
        cy += dy
    elif effect == "zoom_slow":
        scale = s0 + (s1 - s0) * t_ease * 0.7
        cx, cy = iw / 2, ih / 2
        dx = t_ease * iw * 0.015
        cy -= dy if (dy := t_ease * ih * 0.01) else 0
        cx += dx
    elif effect == "pan_right":
        scale = s0 + (s1 - s0) * t_ease * 0.5
        cx = iw / 2 + t_ease * iw * 0.04
        cy = ih / 2 - t_ease * ih * 0.005
    elif effect == "pan_left":
        scale = s0 + (s1 - s0) * t_ease * 0.5
        cx = iw / 2 - t_ease * iw * 0.04
        cy = ih / 2 - t_ease * ih * 0.005
    else:
        scale = s0
        cx, cy = iw / 2, ih / 2

    # Calculate crop region
    crop_w = iw / scale
    crop_h = ih / scale
    left = max(0, cx - crop_w / 2)
    top = max(0, cy - crop_h / 2)
    right = min(iw, left + crop_w)
    bottom = min(ih, top + crop_h)

    # Adjust if out of bounds
    if right - left < crop_w:
        left = max(0, right - crop_w)
    if bottom - top < crop_h:
        top = max(0, bottom - crop_h)

    cropped = img.crop((int(left), int(top), int(right), int(bottom)))
    return cropped.resize((WIDTH, HEIGHT), Image.LANCZOS)


def add_gradient_overlay(frame, style="bottom"):
    """Add gradient overlay to frame."""
    overlay = Image.new('RGBA', (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    if style == "bottom":
        for y in range(HEIGHT):
            if y < HEIGHT * 0.55:
                alpha = 0
            else:
                progress = (y - HEIGHT * 0.55) / (HEIGHT * 0.45)
                alpha = int(progress ** 1.5 * 210)
            draw.rectangle([(0, y), (WIDTH, y + 1)], fill=(0, 0, 0, min(alpha, 210)))
    elif style == "dark":
        for y in range(HEIGHT):
            if y < HEIGHT * 0.15:
                alpha = int((1 - y / (HEIGHT * 0.15)) * 80)
            elif y > HEIGHT * 0.7:
                progress = (y - HEIGHT * 0.7) / (HEIGHT * 0.3)
                alpha = int(40 + progress ** 1.5 * 170)
            else:
                alpha = 30
            draw.rectangle([(0, y), (WIDTH, y + 1)], fill=(0, 0, 0, min(alpha, 220)))
    elif style == "full":
        for y in range(HEIGHT):
            if y < HEIGHT * 0.2:
                alpha = int((1 - y / (HEIGHT * 0.2)) * 140 + 60)
            elif y > HEIGHT * 0.6:
                progress = (y - HEIGHT * 0.6) / (HEIGHT * 0.4)
                alpha = int(60 + progress ** 1.3 * 160)
            else:
                alpha = 60
            draw.rectangle([(0, y), (WIDTH, y + 1)], fill=(0, 0, 0, min(alpha, 220)))
    elif style == "vignette":
        # Simple vignette
        for y in range(HEIGHT):
            for x_block in range(0, WIDTH, 10):
                dx = (x_block - WIDTH / 2) / (WIDTH / 2)
                dy = (y - HEIGHT / 2) / (HEIGHT / 2)
                dist = math.sqrt(dx * dx + dy * dy)
                alpha = int(max(0, (dist - 0.5) * 200))
                draw.rectangle([(x_block, y), (x_block + 10, y + 1)], fill=(0, 0, 0, min(alpha, 150)))

    frame_rgba = frame.convert('RGBA')
    composited = Image.alpha_composite(frame_rgba, overlay)
    return composited.convert('RGB')


def draw_text_with_shadow(draw, pos, text, font, fill=WHITE, shadow_color=(0, 0, 0), shadow_offset=3, shadow_blur_steps=3):
    """Draw text with shadow for readability."""
    x, y = pos
    # Shadow layers
    for i in range(shadow_blur_steps, 0, -1):
        offset = shadow_offset + i
        alpha_color = tuple(list(shadow_color) + []) if len(shadow_color) == 3 else shadow_color
        draw.text((x + offset, y + offset), text, font=font, fill=shadow_color)
    # Main text
    draw.text((x, y), text, font=font, fill=fill)


def draw_centered_text(draw, y, text, font, fill=WHITE, shadow=True):
    """Draw centered text at given y position."""
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    x = (WIDTH - tw) // 2
    if shadow:
        draw_text_with_shadow(draw, (x, y), text, font, fill)
    else:
        draw.text((x, y), text, font=font, fill=fill)


def add_text_overlay(frame, texts, t_fade=1.0):
    """Add text overlays with fade-in effect.

    texts: list of dicts with keys: text, y, size, color, bold, delay
    t_fade: animation progress (0 to 1)
    """
    frame = frame.copy()
    draw = ImageDraw.Draw(frame)

    for item in texts:
        text = item["text"]
        y = item.get("y", HEIGHT - 300)
        size = item.get("size", 44)
        color = item.get("color", WHITE)
        bold = item.get("bold", False)
        delay = item.get("delay", 0.0)

        # Fade in timing
        local_t = max(0, min(1, (t_fade - delay) / 0.3))
        if local_t <= 0:
            continue

        font = load_font(size, bold)
        # Apply fade: shift y and alpha
        offset_y = int((1 - local_t) * 20)
        alpha_color = tuple(int(c * local_t) for c in color)

        draw_centered_text(draw, y + offset_y, text, font, fill=alpha_color)

    return frame


def add_badge(frame, text, t_fade=1.0):
    """Add a badge/pill UI element."""
    if t_fade <= 0:
        return frame

    frame = frame.copy()
    draw = ImageDraw.Draw(frame)
    font = load_font(26)

    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]

    pad_x, pad_y = 40, 14
    bw = tw + pad_x * 2
    bh = th + pad_y * 2
    bx = (WIDTH - bw) // 2
    by = 680

    # Badge background
    alpha = int(t_fade * 100)
    badge_overlay = Image.new('RGBA', (WIDTH, HEIGHT), (0, 0, 0, 0))
    badge_draw = ImageDraw.Draw(badge_overlay)
    badge_draw.rounded_rectangle(
        [(bx, by), (bx + bw, by + bh)],
        radius=bh // 2,
        fill=(0, 0, 0, alpha),
        outline=(255, 255, 255, int(t_fade * 40)),
        width=1
    )

    frame_rgba = frame.convert('RGBA')
    composited = Image.alpha_composite(frame_rgba, badge_overlay)
    frame = composited.convert('RGB')

    draw = ImageDraw.Draw(frame)
    text_alpha = int(t_fade * 230)
    color = (255, 255, 255)
    draw_centered_text(draw, by + pad_y, text, font, fill=color, shadow=False)

    return frame


def add_gold_line(frame, t, y=850, max_width=200):
    """Add animated gold accent line."""
    if t <= 0:
        return frame
    frame = frame.copy()
    draw = ImageDraw.Draw(frame)
    w = int(max_width * min(t, 1.0))
    x = (WIDTH - w) // 2
    draw.rectangle([(x, y), (x + w, y + 2)], fill=GOLD)
    return frame


def add_cta_button(frame, text, t_fade=1.0):
    """Add CTA button."""
    if t_fade <= 0:
        return frame

    frame = frame.copy()
    draw = ImageDraw.Draw(frame)
    font = load_font(29)

    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]

    pad_x, pad_y = 54, 20
    bw = tw + pad_x * 2
    bh = th + pad_y * 2
    bx = (WIDTH - bw) // 2
    by = 1600

    alpha = min(1.0, t_fade)
    color_gold = tuple(int(c * alpha) for c in GOLD)

    draw.rectangle([(bx, by), (bx + bw, by + bh)], outline=color_gold, width=2)
    draw_centered_text(draw, by + pad_y, text, font, fill=color_gold, shadow=False)

    return frame


def add_progress_bars(frame, current_scene, total_scenes, scene_progress):
    """Add Instagram-style progress bars at top."""
    frame = frame.copy()
    draw = ImageDraw.Draw(frame)

    margin = 16
    gap = 4
    bar_h = 3
    total_w = WIDTH - margin * 2
    segment_w = (total_w - gap * (total_scenes - 1)) / total_scenes

    y = margin

    for i in range(total_scenes):
        x = margin + i * (segment_w + gap)

        # Background
        draw.rectangle([(x, y), (x + segment_w, y + bar_h)], fill=(255, 255, 255, 64))

        # Fill
        if i < current_scene:
            fill_w = segment_w
        elif i == current_scene:
            fill_w = segment_w * scene_progress
        else:
            fill_w = 0

        if fill_w > 0:
            draw.rectangle([(x, y), (x + fill_w, y + bar_h)], fill=(255, 255, 255))

    return frame


def generate_crossfade(frame_a, frame_b, t):
    """Generate crossfade between two frames."""
    arr_a = np.array(frame_a, dtype=np.float32)
    arr_b = np.array(frame_b, dtype=np.float32)
    blended = arr_a * (1 - t) + arr_b * t
    return Image.fromarray(blended.astype(np.uint8))


def main():
    print("=== 禅園西梅田 Instagram Reel Generator ===")
    print(f"Output: {WIDTH}x{HEIGHT} @ {FPS}fps")

    # Load images
    print("\n[1/3] Loading images...")
    images = {}
    # Find new photo (0148) by scanning directory
    new_photo_0148 = None
    for f in os.listdir('.'):
        if '0148' in f and (f.endswith('.JPG') or f.endswith('.jpg')):
            new_photo_0148 = f
            break

    image_files = {
        "setting-sakura": "assets/setting-sakura.jpg",
        "private-room": new_photo_0148 or "assets/table-overhead.jpg",  # 新写真に差替
        "dining-closeup": "assets/dining-closeup.jpg",
        "dining-group": "assets/dining-group.jpg",
        "dining-conversation": "assets/dining-conversation.jpg",
        "counter-service": "assets/counter-service.jpg",
        "celebration-menu": "assets/celebration-menu.jpg",
    }

    for name, path in image_files.items():
        img = Image.open(path).convert('RGB')
        # Apply EXIF rotation
        from PIL import ExifTags
        try:
            exif = img._getexif()
            if exif:
                for tag, value in exif.items():
                    if ExifTags.TAGS.get(tag) == 'Orientation':
                        if value == 3:
                            img = img.rotate(180, expand=True)
                        elif value == 6:
                            img = img.rotate(270, expand=True)
                        elif value == 8:
                            img = img.rotate(90, expand=True)
        except Exception:
            pass
        # Pre-crop to 9:16 with some margin for Ken Burns
        images[name] = crop_to_fill(img, int(WIDTH * 1.2), int(HEIGHT * 1.2))
        print(f"  Loaded: {name} ({img.size[0]}x{img.size[1]})")

    # Load fonts
    print("\n[2/3] Loading fonts...")
    font_title_lg = load_font(72)
    font_title = load_font(52)
    font_caption = load_font(44)
    font_sub = load_font(34)
    font_small = load_font(26)
    font_logo = load_font(120)
    font_logo_sub = load_font(36)
    print("  Fonts ready")

    # === Define scenes (接待重視構成) ===
    scenes = [
        {
            "name": "Hook - 接待の悩み",
            "image": "setting-sakura",
            "duration": 3.0,
            "effect": "zoom_in",
            "overlay": "dark",
        },
        {
            "name": "個室会食",
            "image": "private-room",
            "duration": 3.0,
            "effect": "zoom_slow",
            "overlay": "bottom",
        },
        {
            "name": "会話シーン",
            "image": "dining-conversation",
            "duration": 3.0,
            "effect": "pan_left",
            "overlay": "bottom",
        },
        {
            "name": "おもてなし料理",
            "image": "dining-closeup",
            "duration": 3.0,
            "effect": "pan_left",
            "overlay": "bottom",
        },
        {
            "name": "カウンター接客",
            "image": "counter-service",
            "duration": 3.0,
            "effect": "pan_right",
            "overlay": "bottom",
        },
        {
            "name": "信頼の会食",
            "image": "dining-group",
            "duration": 2.5,
            "effect": "zoom_in",
            "overlay": "bottom",
        },
        {
            "name": "CTA - 接待予約",
            "image": "celebration-menu",
            "duration": 4.5,
            "effect": "zoom_slow",
            "overlay": "full",
        },
    ]

    crossfade_duration = 0.5  # seconds

    # Calculate total frames
    total_duration = sum(s["duration"] for s in scenes)
    total_frames = int(total_duration * FPS)
    print(f"\n  Total duration: {total_duration:.1f}s ({total_frames} frames)")

    # === Generate frames ===
    print("\n[3/3] Generating frames...")

    writer = imageio.get_writer(
        OUTPUT,
        fps=FPS,
        codec='libx264',
        quality=8,
        pixelformat='yuv420p',
        macro_block_size=2,
        output_params=['-preset', 'slow', '-crf', '18']
    )

    frame_count = 0
    scene_start_times = []
    t = 0
    for s in scenes:
        scene_start_times.append(t)
        t += s["duration"]

    for frame_idx in range(total_frames):
        current_time = frame_idx / FPS

        # Find current scene
        scene_idx = 0
        for i, start_t in enumerate(scene_start_times):
            if i + 1 < len(scene_start_times):
                if current_time >= scene_start_times[i + 1]:
                    scene_idx = i + 1
            else:
                if current_time >= start_t:
                    scene_idx = i

        scene = scenes[scene_idx]
        scene_start = scene_start_times[scene_idx]
        scene_time = current_time - scene_start
        scene_duration = scene["duration"]
        scene_progress = scene_time / scene_duration

        # Ken Burns
        img = images[scene["image"]]
        frame = ken_burns_frame(img, scene_progress, scene["effect"])

        # Gradient overlay
        frame = add_gradient_overlay(frame, scene["overlay"])

        # Text animation progress
        t_text = scene_time  # seconds into scene

        # === Per-scene text overlays (接待重視 / 文字1.1倍) ===
        if scene_idx == 0:
            # HOOK: 接待の課題提起
            badge_t = max(0, (t_text - 0.2) / 0.4)
            frame = add_badge(frame, "接 待 ・ ビ ジ ネ ス 会 食", min(1.0, badge_t))

            texts = [
                {"text": "「次の接待、", "y": 750, "size": 70, "color": WHITE, "bold": True, "delay": 0.13},
                {"text": "どこにしよう…」", "y": 840, "size": 70, "color": WHITE, "bold": True, "delay": 0.23},
                {"text": "その悩み、ここで解決します", "y": 945, "size": 37, "color": GOLD, "delay": 0.6},
            ]
            frame = add_text_overlay(frame, texts, t_text)
            frame = add_gold_line(frame, max(0, (t_text - 1.2) / 0.8), y=935)

        elif scene_idx == 1:
            # 個室会食 → 接待に最適な空間
            texts = [
                {"text": "周囲を気にしない完全個室", "y": 1530, "size": 48, "color": WHITE, "delay": 0.1},
                {"text": "商談も安心の静寂空間", "y": 1595, "size": 33, "color": GOLD, "delay": 0.3},
            ]
            frame = add_text_overlay(frame, texts, t_text)

        elif scene_idx == 2:
            # 会話シーン → 信頼構築
            texts = [
                {"text": "距離が縮まる、和の空間", "y": 1530, "size": 48, "color": WHITE, "delay": 0.1},
                {"text": "大切な商談を成功に導く", "y": 1595, "size": 33, "color": GOLD, "delay": 0.3},
            ]
            frame = add_text_overlay(frame, texts, t_text)

        elif scene_idx == 3:
            # 料理 → 接待の格を上げる
            texts = [
                {"text": "「さすが」と言わせる", "y": 1530, "size": 48, "color": WHITE, "delay": 0.1},
                {"text": "旬の懐石で格上のおもてなし", "y": 1595, "size": 33, "color": GOLD, "delay": 0.3},
            ]
            frame = add_text_overlay(frame, texts, t_text)

        elif scene_idx == 4:
            # カウンター → ライブ感
            texts = [
                {"text": "目の前で仕上げる特別感", "y": 1530, "size": 48, "color": WHITE, "delay": 0.1},
                {"text": "会話が自然と弾む演出", "y": 1595, "size": 33, "color": GOLD, "delay": 0.3},
            ]
            frame = add_text_overlay(frame, texts, t_text)

        elif scene_idx == 5:
            # グループ → 成功の会食
            texts = [
                {"text": "選んで正解だった ——", "y": 1545, "size": 48, "color": WHITE, "delay": 0.1},
                {"text": "お客様の満足が、信頼になる", "y": 1610, "size": 33, "color": GOLD, "delay": 0.3},
            ]
            frame = add_text_overlay(frame, texts, t_text)

        elif scene_idx == 6:
            # CTA: 接待予約
            texts = [
                {"text": "大阪で選ばれる接待の場", "y": 480, "size": 37, "color": GOLD, "delay": 0.1},
            ]
            frame = add_text_overlay(frame, texts, t_text)

            # Logo
            logo_t = max(0, (t_text - 0.5) / 0.5)
            if logo_t > 0:
                logo_texts = [
                    {"text": "西梅田 禅園", "y": 830, "size": 110, "color": WHITE, "bold": True, "delay": 0.0},
                ]
                frame = add_text_overlay(frame, logo_texts, min(1.0, logo_t))

            # 店舗情報
            info_texts = [
                {"text": "西梅田 禅園", "y": 1300, "size": 33, "color": WHITE, "bold": True, "delay": 0.33},
                {"text": "西梅田駅 徒歩3分 / 完全個室", "y": 1350, "size": 29, "color": WHITE, "delay": 0.4},
                {"text": "接待コース ¥8,800〜", "y": 1395, "size": 31, "color": GOLD, "delay": 0.5},
            ]
            frame = add_text_overlay(frame, info_texts, t_text)

            # CTA button
            cta_t = max(0, (t_text - 1.8) / 0.4)
            frame = add_cta_button(frame, "接待のご予約はプロフィールから", cta_t)

            # Handle
            handle_texts = [
                {"text": "@nishiumeda_zenen", "y": 1700, "size": 24, "color": (180, 180, 180), "delay": 0.7},
            ]
            frame = add_text_overlay(frame, handle_texts, t_text)

        # Crossfade between scenes
        if scene_time < crossfade_duration and scene_idx > 0:
            prev_scene = scenes[scene_idx - 1]
            prev_img = images[prev_scene["image"]]
            prev_frame = ken_burns_frame(prev_img, 1.0, prev_scene["effect"])
            prev_frame = add_gradient_overlay(prev_frame, prev_scene["overlay"])
            fade_t = scene_time / crossfade_duration
            frame = generate_crossfade(prev_frame, frame, fade_t)

        # Progress bars
        frame = add_progress_bars(frame, scene_idx, len(scenes), scene_progress)

        # Write frame
        writer.append_data(np.array(frame))
        frame_count += 1

        if frame_count % (FPS * 2) == 0:
            pct = frame_count / total_frames * 100
            print(f"  Progress: {pct:.0f}% ({frame_count}/{total_frames} frames)")

    writer.close()

    file_size = os.path.getsize(OUTPUT) / (1024 * 1024)
    print(f"\n=== Complete! ===")
    print(f"  File: {OUTPUT}")
    print(f"  Size: {file_size:.1f} MB")
    print(f"  Duration: {total_duration:.1f}s")
    print(f"  Resolution: {WIDTH}x{HEIGHT}")
    print(f"  FPS: {FPS}")


if __name__ == "__main__":
    main()
