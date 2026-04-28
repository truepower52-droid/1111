"""
Promotional video for Дистанционная медицинская школа (ДМШ)
15 seconds, 1920x1080, 30fps, MP4
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import os, math

# ── Constants ──────────────────────────────────────────────────────────
W, H = 1920, 1080
FPS  = 30
TOTAL_FRAMES = FPS * 15  # 450

# Brand colors
C_DEEP   = (74,  48, 112)   # #4A3070  deep purple
C_MID    = (82,  41, 221)   # #5229DD  primary purple
C_LIGHT  = (107, 76, 154)   # #6B4C9A  lighter purple
C_BRIGHT = (149, 127, 225)  # #957FE1  accent purple
C_WHITE  = (255, 255, 255)
C_PALE   = (243, 234, 255)  # #F3EAFF  bg pale
C_GREEN  = (39,  174, 96)   # #27AE60
C_DARK   = (45,  32,  64)   # #2D2040  dark text
C_SUBTEXT= (180, 160, 220)

FONT_DIR = "/usr/share/fonts/truetype/liberation"
FONT_BOLD   = os.path.join(FONT_DIR, "LiberationSans-Bold.ttf")
FONT_REGULAR= os.path.join(FONT_DIR, "LiberationSans-Regular.ttf")

def font(size, bold=False):
    f = FONT_BOLD if bold else FONT_REGULAR
    return ImageFont.truetype(f, size)

def lerp(a, b, t):
    return a + (b - a) * t

def ease_out(t):
    return 1 - (1 - t) ** 3

def ease_in_out(t):
    return t * t * (3 - 2 * t)

def clamp(v, lo=0.0, hi=1.0):
    return max(lo, min(hi, v))

# ── Gradient helpers ────────────────────────────────────────────────────
def make_grad_bg(w, h, c1=C_DEEP, c2=C_MID, angle_deg=135):
    """Diagonal linear gradient background as numpy array."""
    arr = np.zeros((h, w, 3), dtype=np.uint8)
    angle = math.radians(angle_deg)
    cx, cy = w / 2, h / 2
    for y in range(h):
        for x in range(0, w, 1):
            dx, dy = x - cx, y - cy
            proj = dx * math.cos(angle) + dy * math.sin(angle)
            d = math.sqrt(cx**2 + cy**2)
            t = clamp(proj / (2 * d) + 0.5)
            arr[y, x] = [int(lerp(c1[i], c2[i], t)) for i in range(3)]
    return arr

def fast_grad_bg(w, h, c1=C_DEEP, c2=C_MID):
    """Fast horizontal gradient."""
    t = np.linspace(0, 1, w, dtype=np.float32)
    row = np.stack([
        (c1[0] + (c2[0]-c1[0]) * t).astype(np.uint8),
        (c1[1] + (c2[1]-c1[1]) * t).astype(np.uint8),
        (c1[2] + (c2[2]-c1[2]) * t).astype(np.uint8),
    ], axis=1)  # (w, 3)
    return np.tile(row[np.newaxis, :, :], (h, 1, 1))

def vert_grad_bg(w, h, c1, c2):
    t = np.linspace(0, 1, h, dtype=np.float32)
    col = np.stack([
        (c1[0] + (c2[0]-c1[0]) * t).astype(np.uint8),
        (c1[1] + (c2[1]-c1[1]) * t).astype(np.uint8),
        (c1[2] + (c2[2]-c1[2]) * t).astype(np.uint8),
    ], axis=1)  # (h, 3)
    return np.tile(col[:, np.newaxis, :], (1, w, 1))

# ── Drawing helpers ─────────────────────────────────────────────────────
def draw_text_center(draw, text, y, size, color=C_WHITE, bold=True, alpha=1.0):
    f = font(size, bold)
    bbox = draw.textbbox((0, 0), text, font=f)
    tw = bbox[2] - bbox[0]
    x = (W - tw) // 2
    c = tuple(int(v * alpha) for v in color)
    draw.text((x, y), text, font=f, fill=c)

def draw_text_at(draw, text, x, y, size, color=C_WHITE, bold=True):
    f = font(size, bold)
    draw.text((x, y), text, font=f, fill=color)

def text_width(draw, text, size, bold=True):
    f = font(size, bold)
    bbox = draw.textbbox((0, 0), text, font=f)
    return bbox[2] - bbox[0]

def text_height(draw, text, size, bold=True):
    f = font(size, bold)
    bbox = draw.textbbox((0, 0), text, font=f)
    return bbox[3] - bbox[1]

def rounded_rect(draw, x1, y1, x2, y2, r, fill, alpha=255):
    fill_a = fill + (alpha,)
    draw.rounded_rectangle([x1, y1, x2, y2], radius=r, fill=fill)

def overlay_alpha(base_arr, overlay_img, alpha):
    """Blend RGBA overlay image onto base numpy array."""
    overlay_arr = np.array(overlay_img.convert("RGBA"))
    a = overlay_arr[:, :, 3:4].astype(np.float32) / 255.0 * alpha
    rgb = overlay_arr[:, :, :3].astype(np.float32)
    base_f = base_arr.astype(np.float32)
    result = base_f * (1 - a) + rgb * a
    return result.astype(np.uint8)

def apply_fade(arr, alpha):
    if alpha >= 1.0:
        return arr
    black = np.zeros_like(arr)
    t = float(alpha)
    return (arr.astype(np.float32) * t + black * (1 - t)).astype(np.uint8)

# ── Decorative circles ──────────────────────────────────────────────────
def draw_circles(draw, alpha=1.0):
    """Soft decorative circles on background."""
    circles = [
        (1700, 150, 200, (100, 70, 180, 40)),
        (200,  900, 280, (82, 41, 221, 30)),
        (960,  540, 500, (60, 30, 140, 15)),
        (1600, 800, 150, (149, 127, 225, 35)),
        (100,  200, 120, (107, 76, 154, 25)),
    ]
    for cx, cy, r, col in circles:
        a = int(col[3] * alpha)
        c = col[:3] + (a,)
        draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=c)

# ── Scene renderers ────────────────────────────────────────────────────

def scene1(frame, total=90):
    """0-3s: Title intro — platform name + subtitle"""
    t = frame / total  # 0..1

    bg = fast_grad_bg(W, H, C_DEEP, C_MID)
    img = Image.fromarray(bg)
    draw = ImageDraw.Draw(img, "RGBA")
    draw_circles(draw, alpha=0.6)

    # Animated line at top
    line_w = int(W * ease_out(clamp(t * 3)))
    draw.rectangle([0, 0, line_w, 6], fill=C_BRIGHT + (200,))

    # TITLE — slides up + fades in
    title_alpha = clamp(t * 2.5)
    title_y_base = 330
    title_y = int(title_y_base + (1 - ease_out(clamp(t * 2))) * 60)
    title = "Дистанционная медицинская школа"
    tw = text_width(draw, title, 72, bold=True)
    x = (W - tw) // 2
    draw.text((x, title_y), title, font=font(72, True),
              fill=(*C_WHITE, int(255 * title_alpha)))

    # Subtitle
    sub_alpha = clamp((t - 0.25) * 3)
    sub_y_base = 430
    sub_y = int(sub_y_base + (1 - ease_out(clamp((t - 0.25) * 3))) * 40)
    sub = "Цифровая платформа «Будущий врач»"
    tw2 = text_width(draw, sub, 42, bold=False)
    x2 = (W - tw2) // 2
    draw.text((x2, sub_y), sub, font=font(42, False),
              fill=(*C_PALE, int(255 * sub_alpha)))

    # Minzdrav badge
    badge_alpha = clamp((t - 0.5) * 4)
    if badge_alpha > 0:
        badge_text = "При поддержке Минздрава России"
        tw3 = text_width(draw, badge_text, 28, bold=False)
        bx = (W - tw3 - 40) // 2
        by = 530
        draw.rounded_rectangle([bx, by, bx + tw3 + 40, by + 46],
                                radius=23, fill=(*C_BRIGHT, int(60 * badge_alpha)))
        draw.text((bx + 20, by + 9), badge_text, font=font(28, False),
                  fill=(*C_WHITE, int(255 * badge_alpha)))

    # Bottom website hint
    site_alpha = clamp((t - 0.7) * 5)
    if site_alpha > 0:
        site = "futuredoc.minzdrav.gov.ru"
        tw4 = text_width(draw, site, 26, bold=False)
        draw.text(((W - tw4) // 2, H - 80), site, font=font(26, False),
                  fill=(*C_SUBTEXT, int(200 * site_alpha)))

    return np.array(img)


def scene2(frame, total=90):
    """3-6s: The problem — why schools need this"""
    t = frame / total

    bg = fast_grad_bg(W, H, C_DEEP, (90, 55, 160))
    img = Image.fromarray(bg)
    draw = ImageDraw.Draw(img, "RGBA")
    draw_circles(draw, 0.4)

    # Top line
    draw.rectangle([0, 0, W, 6], fill=C_BRIGHT + (180,))

    # Heading
    h_alpha = clamp(t * 4)
    heading = "С какими сложностями сталкиваются школы?"
    tw = text_width(draw, heading, 52, True)
    draw.text(((W - tw) // 2, 100), heading, font=font(52, True),
              fill=(*C_WHITE, int(255 * h_alpha)))

    # 4 problem cards sliding in from right
    problems = [
        ("📚", "Нет контента вузовского уровня"),
        ("🏆", "Подготовка к олимпиадам доступна не везде"),
        ("🏥", "Качественная программа первой помощи"),
        ("🤝", "Партнёрство с медицинским вузом"),
    ]
    card_w = 800
    card_h = 110
    start_x = (W - card_w) // 2
    for i, (icon, text) in enumerate(problems):
        delay = i * 0.18
        card_t = clamp((t - delay) * 4)
        if card_t <= 0:
            continue
        x_off = int((1 - ease_out(card_t)) * 300)
        cy = 240 + i * 160
        cx = start_x + x_off

        # Card background
        draw.rounded_rectangle([cx, cy, cx + card_w, cy + card_h],
                                radius=18,
                                fill=(*C_BRIGHT, int(50 * card_t)))
        draw.rounded_rectangle([cx, cy, cx + card_w, cy + card_h],
                                radius=18,
                                outline=(*C_BRIGHT, int(120 * card_t)),
                                width=2)
        # Icon
        draw.text((cx + 24, cy + 28), icon, font=font(44, False),
                  fill=(*C_WHITE, int(255 * card_t)))
        # Text
        draw.text((cx + 90, cy + 32), text, font=font(34, False),
                  fill=(*C_WHITE, int(255 * card_t)))

    # Bottom tagline
    tag_alpha = clamp((t - 0.7) * 5)
    if tag_alpha > 0:
        tag = "Наша платформа помогает решить каждую из этих задач"
        tw2 = text_width(draw, tag, 30, False)
        draw.text(((W - tw2) // 2, H - 90), tag, font=font(30, False),
                  fill=(*C_PALE, int(220 * tag_alpha)))

    return np.array(img)


def scene3(frame, total=90):
    """6-9s: Key metrics + journey"""
    t = frame / total

    bg = vert_grad_bg(W, H, C_DEEP, (50, 25, 100))
    img = Image.fromarray(bg)
    draw = ImageDraw.Draw(img, "RGBA")
    draw_circles(draw, 0.5)

    draw.rectangle([0, 0, W, 6], fill=C_GREEN + (200,))

    # Platform name header
    h_alpha = clamp(t * 5)
    draw.text((W//2 - text_width(draw, "Платформа «Будущий врач»", 52, True)//2, 70),
              "Платформа «Будущий врач»", font=font(52, True),
              fill=(*C_WHITE, int(255 * h_alpha)))

    # Stats row: 3 big numbers
    stats = [
        ("20 000+", "пользователей"),
        ("100+",    "партнёров"),
        ("370+",    "единиц контента"),
    ]
    stat_w = 420
    stat_gap = 60
    total_w = len(stats) * stat_w + (len(stats) - 1) * stat_gap
    sx = (W - total_w) // 2
    for i, (num, label) in enumerate(stats):
        delay = i * 0.15
        st = clamp((t - delay) * 5)
        if st <= 0:
            continue
        scale = ease_out(st)
        x = sx + i * (stat_w + stat_gap)
        cy = 200

        # Card
        draw.rounded_rectangle([x, cy, x + stat_w, cy + 180],
                                radius=20,
                                fill=(*C_MID, int(120 * st)))

        # Number with scale effect
        num_size = int(64 * scale)
        nw = text_width(draw, num, max(num_size, 10), True)
        draw.text((x + (stat_w - nw) // 2, cy + 28), num,
                  font=font(max(num_size, 10), True),
                  fill=(*C_WHITE, int(255 * st)))
        lw = text_width(draw, label, 28, False)
        draw.text((x + (stat_w - lw) // 2, cy + 110), label,
                  font=font(28, False),
                  fill=(*C_PALE, int(220 * st)))

    # Journey path
    path_alpha = clamp((t - 0.4) * 4)
    if path_alpha > 0:
        steps = [
            ("1", "5–8 кл", "Профориентация"),
            ("2", "9 кл",   "Отбор в медкласс"),
            ("3", "10–11 кл", "Подготовка\nк поступлению"),
            ("4", "Выпуск", "Сертификат"),
        ]
        step_w = 300
        gap = 80
        total_sw = len(steps) * step_w + (len(steps)-1) * gap
        stx = (W - total_sw) // 2
        sy = 450

        for i, (num, grade, desc) in enumerate(steps):
            x = stx + i * (step_w + gap)
            # connector line
            if i < len(steps) - 1:
                lx1 = x + step_w
                lx2 = x + step_w + gap
                draw.line([(lx1, sy + 50), (lx2, sy + 50)],
                          fill=(*C_BRIGHT, int(160 * path_alpha)), width=3)
                # arrow
                draw.polygon([(lx2 - 2, sy + 42), (lx2 - 2, sy + 58),
                               (lx2 + 12, sy + 50)],
                             fill=(*C_BRIGHT, int(160 * path_alpha)))

            # circle badge
            draw.ellipse([x + step_w//2 - 40, sy + 10,
                          x + step_w//2 + 40, sy + 90],
                         fill=(*C_MID, int(200 * path_alpha)))
            nw = text_width(draw, num, 36, True)
            draw.text((x + step_w//2 - nw//2, sy + 27), num,
                      font=font(36, True),
                      fill=(*C_WHITE, int(255 * path_alpha)))

            gw = text_width(draw, grade, 28, True)
            draw.text((x + step_w//2 - gw//2, sy + 105), grade,
                      font=font(28, True),
                      fill=(*C_WHITE, int(255 * path_alpha)))

            for j, line in enumerate(desc.split("\n")):
                lw = text_width(draw, line, 24, False)
                draw.text((x + step_w//2 - lw//2, sy + 145 + j*32), line,
                          font=font(24, False),
                          fill=(*C_SUBTEXT, int(220 * path_alpha)))

    return np.array(img)


def scene4(frame, total=90):
    """9-12s: ДМШ features"""
    t = frame / total

    bg = fast_grad_bg(W, H, (50, 25, 100), C_DEEP)
    img = Image.fromarray(bg)
    draw = ImageDraw.Draw(img, "RGBA")
    draw_circles(draw, 0.45)

    draw.rectangle([0, 0, W, 6], fill=C_BRIGHT + (200,))

    # Heading
    h_alpha = clamp(t * 5)
    heading = "Что входит в ДМШ?"
    tw = text_width(draw, heading, 56, True)
    draw.text(((W - tw) // 2, 80), heading, font=font(56, True),
              fill=(*C_WHITE, int(255 * h_alpha)))

    # 6 feature cards in 2 rows
    features = [
        ("🏆", "Олимпиадный\nтренажёр"),
        ("🩺", "Первая помощь\n+ сертификат"),
        ("🧠", "Медицинский\nАтлас"),
        ("📖", "Подготовка\nк ЕГЭ"),
        ("🎯", "Профориентация"),
        ("🎓", "Сертификаты"),
    ]
    cols, rows = 3, 2
    card_w, card_h = 480, 200
    h_gap, v_gap = 40, 30
    total_fw = cols * card_w + (cols-1) * h_gap
    fx = (W - total_fw) // 2
    fy = 200

    for i, (icon, label) in enumerate(features):
        col = i % cols
        row = i // cols
        delay = (col + row * cols) * 0.08
        ft = clamp((t - delay) * 5)
        if ft <= 0:
            continue
        y_off = int((1 - ease_out(ft)) * 50)
        x = fx + col * (card_w + h_gap)
        y = fy + row * (card_h + v_gap) + y_off

        draw.rounded_rectangle([x, y, x + card_w, y + card_h],
                                radius=22,
                                fill=(*C_MID, int(140 * ft)))
        draw.rounded_rectangle([x, y, x + card_w, y + card_h],
                                radius=22,
                                outline=(*C_BRIGHT, int(100 * ft)),
                                width=2)

        # Icon
        draw.text((x + 28, y + card_h//2 - 28), icon, font=font(52, False),
                  fill=(*C_WHITE, int(255 * ft)))
        # Label
        lines = label.split("\n")
        lh = 38
        ly_start = y + card_h//2 - len(lines) * lh//2 - 6
        for j, line in enumerate(lines):
            lw = text_width(draw, line, 34, True)
            draw.text((x + 100, ly_start + j * lh), line,
                      font=font(34, True),
                      fill=(*C_WHITE, int(255 * ft)))

    return np.array(img)


def scene5(frame, total=90):
    """12-15s: CTA"""
    t = frame / total

    bg = fast_grad_bg(W, H, C_DEEP, C_MID)
    img = Image.fromarray(bg)
    draw = ImageDraw.Draw(img, "RGBA")
    draw_circles(draw, 0.7)

    # Animated green line top
    lw = int(W * ease_out(clamp(t * 3)))
    draw.rectangle([0, 0, lw, 6], fill=C_GREEN + (220,))

    # Main CTA
    cta_alpha = clamp(t * 4)
    cta = "Подключите вашу школу"
    tw = text_width(draw, cta, 80, True)
    draw.text(((W - tw) // 2, 270), cta, font=font(80, True),
              fill=(*C_WHITE, int(255 * cta_alpha)))

    # Sub
    sub_alpha = clamp((t - 0.2) * 4)
    sub = "Старт с сентября 2026"
    tw2 = text_width(draw, sub, 44, False)
    draw.text(((W - tw2) // 2, 380), sub, font=font(44, False),
              fill=(*C_PALE, int(255 * sub_alpha)))

    # 3 contact items
    contacts = [
        ("🌐", "futuredoc.minzdrav.gov.ru"),
        ("✉",  "futuredoctor@pimunn.net"),
        ("📞", "+7 (831) 422-20-53"),
    ]
    btn_w = 500
    for i, (icon, info) in enumerate(contacts):
        delay = 0.3 + i * 0.12
        ct = clamp((t - delay) * 5)
        if ct <= 0:
            continue
        bx = (W - btn_w) // 2
        by = 480 + i * 95
        draw.rounded_rectangle([bx, by, bx + btn_w, by + 70],
                                radius=35,
                                fill=(*C_MID, int(180 * ct)))
        draw.text((bx + 20, by + 16), icon, font=font(36, False),
                  fill=(*C_WHITE, int(255 * ct)))
        iw = text_width(draw, info, 30, False)
        draw.text((bx + 65, by + 20), info, font=font(30, False),
                  fill=(*C_WHITE, int(255 * ct)))

    # Fade out at the very end
    if t > 0.85:
        fade = (t - 0.85) / 0.15
        return apply_fade(np.array(img), 1 - fade * 0.3)

    return np.array(img)


# ── Main render loop ───────────────────────────────────────────────────
def make_frame(f):
    """Return RGB numpy array for global frame f."""
    # Scene boundaries (frames)
    s1_end = 90    # 0–3s
    s2_end = 180   # 3–6s
    s3_end = 270   # 6–9s
    s4_end = 360   # 9–12s
    s5_end = 450   # 12–15s

    # Cross-fade duration (frames)
    XFADE = 15

    def xfade(fr_a, fr_b, xf):
        """Blend frame A into B over xf frames."""
        t = clamp(xf / XFADE)
        a = fr_a.astype(np.float32)
        b = fr_b.astype(np.float32)
        return (a * (1 - t) + b * t).astype(np.uint8)

    if f < s1_end:
        return scene1(f, s1_end)

    elif f < s1_end + XFADE:
        xf = f - s1_end
        return xfade(scene1(s1_end - 1, s1_end), scene2(0, s2_end - s1_end), xf)

    elif f < s2_end:
        return scene2(f - s1_end, s2_end - s1_end)

    elif f < s2_end + XFADE:
        xf = f - s2_end
        return xfade(scene2(s2_end - s1_end - 1, s2_end - s1_end),
                     scene3(0, s3_end - s2_end), xf)

    elif f < s3_end:
        return scene3(f - s2_end, s3_end - s2_end)

    elif f < s3_end + XFADE:
        xf = f - s3_end
        return xfade(scene3(s3_end - s2_end - 1, s3_end - s2_end),
                     scene4(0, s4_end - s3_end), xf)

    elif f < s4_end:
        return scene4(f - s3_end, s4_end - s3_end)

    elif f < s4_end + XFADE:
        xf = f - s4_end
        return xfade(scene4(s4_end - s3_end - 1, s4_end - s3_end),
                     scene5(0, s5_end - s4_end), xf)

    else:
        return scene5(f - s4_end, s5_end - s4_end)


if __name__ == "__main__":
    from moviepy import VideoClip
    print("Rendering frames…")

    def frame_func(t):
        f = int(t * FPS)
        f = min(f, TOTAL_FRAMES - 1)
        return make_frame(f)

    clip = VideoClip(frame_func, duration=15)
    out = "/home/user/1111/ДМШ_промо_15сек.mp4"
    clip.write_videofile(out, fps=FPS, codec="libx264",
                         preset="fast", ffmpeg_params=["-crf", "18"],
                         logger="bar")
    print(f"\nDone → {out}")
