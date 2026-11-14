#!/usr/bin/env python3
"""Draw the food-picture-01 entry image procedurally with Pillow.

Close-up tonkotsu ramen bowl at a 45-degree angle: amber broth, lifted
noodles on chopsticks, soft egg, chashu, nori, scallions, steam, warm
wood table. Rendered at 2048x2048 and downsampled to 1024x1024 (LANCZOS).
All pixels drawn by this script — no stock photo, no text.

Run: python3 generate.py   (writes entry.png next to this file)
"""
import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

SS = 2048          # supersampled working size
OUT = 1024         # final size
HERE = Path(__file__).resolve().parent

# Palette
WOOD_DARK = (36, 22, 16)
WOOD_MID = (90, 58, 34)
WOOD_LIGHT = (122, 78, 44)
BOWL_NAVY = (31, 58, 95)
BOWL_DARK = (18, 34, 60)
BOWL_RIM = (52, 88, 138)
BROTH_DEEP = (180, 85, 31)
BROTH_MID = (224, 138, 46)
BROTH_LIGHT = (242, 176, 84)
NOODLE_A = (245, 214, 122)
NOODLE_B = (232, 184, 75)
CHOP = (122, 74, 33)
CHOP_LIGHT = (160, 104, 52)
EGG_WHITE = (255, 246, 224)
YOLK = (245, 158, 11)
YOLK_DEEP = (224, 122, 8)
CHASHU = (232, 180, 154)
CHASHU_EDGE = (201, 138, 107)
CHASHU_SWIRL = (150, 92, 66)
NORI = (30, 43, 26)
NORI_EDGE = (58, 78, 48)
SCALLION = (62, 142, 77)
SCALLION_DARK = (38, 102, 52)
WHITE = (255, 255, 255)

CX, CY = 1024, 1120   # bowl centre (rim ellipse centre)
RX, RY = 560, 330     # rim ellipse radii


def lerp(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def soft_disc(base, center, radius, color, blur, alpha=255):
    """Blurred glowing disc composited onto an RGBA image."""
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    x, y = center
    d.ellipse([x - radius, y - radius, x + radius, y + radius],
              fill=color + (alpha,))
    base.alpha_composite(layer.filter(ImageFilter.GaussianBlur(blur)))


def radial_disc(size, center, radius, c_inner, c_outer):
    """RGB image of a radial gradient disc (square `size`, transparent outside)."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    steps = 48
    for i in range(steps, 0, -1):
        t = i / steps
        r = radius * t
        col = lerp(c_inner, c_outer, t)
        d.ellipse([center[0] - r, center[1] - r,
                   center[0] + r, center[1] + r], fill=col + (255,))
    return img


def ellipse_poly(cx, cy, rx, ry, angle_deg, n=64):
    a = math.radians(angle_deg)
    ca, sa = math.cos(a), math.sin(a)
    pts = []
    for i in range(n):
        t = 2 * math.pi * i / n
        x = rx * math.cos(t)
        y = ry * math.sin(t)
        pts.append((cx + x * ca - y * sa, cy + x * sa + y * ca))
    return pts


def arc_points(cx, cy, rx, ry, start_deg, end_deg, n=60):
    pts = []
    for i in range(n + 1):
        t = math.radians(start_deg + (end_deg - start_deg) * i / n)
        pts.append((cx + rx * math.cos(t), cy + ry * math.sin(t)))
    return pts


def vgrad(w, h, stops):
    """Vertical gradient through color stops [(pos, rgb), ...]."""
    img = Image.new("RGB", (1, h))
    px = img.load()
    for y in range(h):
        t = y / max(h - 1, 1)
        for i in range(len(stops) - 1):
            p0, c0 = stops[i]
            p1, c1 = stops[i + 1]
            if p0 <= t <= p1:
                f = 0 if p1 == p0 else (t - p0) / (p1 - p0)
                px[0, y] = lerp(c0, c1, f)
                break
        else:
            px[0, y] = stops[-1][1]
    return img.resize((w, h))


def draw_background(img):
    draw = ImageDraw.Draw(img, "RGBA")
    # Dark warm wood base.
    draw.rectangle([0, 0, SS, SS], fill=WOOD_DARK)
    # Warm light pool centred on the bowl.
    soft_disc(img, (1024, 1150), 950, WOOD_MID, 220, alpha=210)
    soft_disc(img, (1024, 1150), 520, (150, 96, 52), 160, alpha=140)
    # Subtle wood grain: long soft horizontal arcs.
    layer = Image.new("RGBA", (SS, SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    rng = random.Random(7)
    for _ in range(9):
        y0 = rng.randint(80, 1960)
        d.arc([-300, y0, 2350, y0 + rng.randint(180, 420)], 180, 360,
              fill=(20, 12, 8, 70), width=rng.randint(10, 26))
    img.alpha_composite(layer.filter(ImageFilter.GaussianBlur(10)))


def draw_bowl(img):
    draw = ImageDraw.Draw(img, "RGBA")
    # Soft contact shadow under the bowl.
    layer = Image.new("RGBA", (SS, SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.ellipse([CX - 620, CY + 300, CX + 620, CY + 620], fill=(10, 5, 2, 130))
    img.alpha_composite(layer.filter(ImageFilter.GaussianBlur(40)))

    # Bowl body: smooth vertical navy gradient, lower crescent visible
    # below the rim (mask = bowl ellipse).
    grad = vgrad(SS, SS, [(0.0, BOWL_RIM), (0.45, BOWL_NAVY),
                          (1.0, BOWL_DARK)]).convert("RGBA")
    mask = Image.new("L", (SS, SS), 0)
    md = ImageDraw.Draw(mask)
    md.ellipse([CX - RX, CY - RY, CX + RX, CY + 580], fill=255)
    img.paste(grad, (0, 0), mask)

    # Rim band.
    draw.ellipse([CX - RX, CY - RY, CX + RX, CY + RY], fill=BOWL_NAVY)
    # Thin lighter ring just inside the rim edge.
    draw.ellipse([CX - RX + 14, CY - RY + 14, CX + RX - 14, CY + RY - 14],
                 outline=BOWL_RIM, width=10)
    # Front rim highlight (thin bright arc along the front edge).
    draw.arc([CX - RX + 26, CY - RY + 26, CX + RX - 26, CY + RY - 26],
             25, 155, fill=(120, 160, 205), width=12)

    # Broth: radial amber gradient inside the rim.
    broth = radial_disc(1100, (550, 550), 540, BROTH_LIGHT, BROTH_DEEP)
    bmask = Image.new("L", (1100, 1100), 0)
    bd = ImageDraw.Draw(bmask)
    bd.ellipse([40, 40, 1060, 1060], fill=255)
    broth.putalpha(bmask)
    # Squash vertically to the bowl's 45-degree ellipse and paste.
    broth = broth.resize((1000, 580), Image.LANCZOS)
    img.alpha_composite(broth, (CX - 500, CY - 290))
    # Dark thin ring at the inner broth edge.
    draw.ellipse([CX - 500, CY - 290, CX + 500, CY + 290],
                 outline=(120, 55, 15), width=8)

    # Broth gloss: three soft white ellipses, upper-left light.
    for (gx, gy, grx, gry, alpha) in ((800, 950, 180, 55, 110),
                                       (1050, 880, 130, 40, 80),
                                       (1250, 1030, 90, 30, 70)):
        layer = Image.new("RGBA", (SS, SS), (0, 0, 0, 0))
        d = ImageDraw.Draw(layer)
        d.ellipse([gx - grx, gy - gry, gx + grx, gy + gry],
                  fill=(255, 240, 210, alpha))
        img.alpha_composite(layer.filter(ImageFilter.GaussianBlur(14)))

    # Oil droplets: small shiny dots on the broth.
    rng = random.Random(11)
    for _ in range(14):
        ox = rng.randint(CX - 420, CX + 420)
        oy = rng.randint(CY - 210, CY + 210)
        # keep inside broth ellipse
        if ((ox - CX) / 470) ** 2 + ((oy - CY) / 260) ** 2 > 1:
            continue
        r = rng.randint(10, 22)
        layer = Image.new("RGBA", (SS, SS), (0, 0, 0, 0))
        d = ImageDraw.Draw(layer)
        d.ellipse([ox - r, oy - r * 0.6, ox + r, oy + r * 0.6],
                  fill=(255, 214, 140, 150))
        d.ellipse([ox - r * 0.4, oy - r * 0.35, ox + r * 0.2, oy + r * 0.1],
                  fill=(255, 255, 255, 170))
        img.alpha_composite(layer.filter(ImageFilter.GaussianBlur(4)))


def draw_nori(img):
    draw = ImageDraw.Draw(img, "RGBA")
    # Dark rectangle, tilted, standing at the back right of the broth.
    pts = ellipse_poly(1400, 830, 130, 190, -18)
    # Use a rotated rectangle instead: four corners.
    cx, cy, w, h, ang = 1400, 880, 240, 300, -22
    a = math.radians(ang)
    ca, sa = math.cos(a), math.sin(a)
    corners = []
    for (lx, ly) in ((-w / 2, -h / 2), (w / 2, -h / 2),
                     (w / 2, h / 2), (-w / 2, h / 2)):
        corners.append((cx + lx * ca - ly * sa, cy + lx * sa + ly * ca))
    draw.polygon(corners, fill=NORI)
    # Slightly lighter inner panel and edge sheen.
    inner = []
    for (lx, ly) in ((-w / 2 + 18, -h / 2 + 18), (w / 2 - 18, -h / 2 + 18),
                     (w / 2 - 18, h / 2 - 18), (-w / 2 + 18, h / 2 - 18)):
        inner.append((cx + lx * ca - ly * sa, cy + lx * sa + ly * ca))
    draw.polygon(inner, outline=NORI_EDGE, width=8)
    draw.line([corners[0], corners[1]], fill=(90, 115, 70), width=10)


def draw_chashu(img):
    draw = ImageDraw.Draw(img, "RGBA")
    for (sx, sy, r) in ((1330, 1180, 128), (1435, 1040, 112)):
        draw.ellipse([sx - r, sy - r * 0.82, sx + r, sy + r * 0.82],
                     fill=CHASHU, outline=CHASHU_EDGE, width=10)
        # Fat swirl: soft concentric arcs in the middle.
        draw.arc([sx - r * 0.55, sy - r * 0.45, sx + r * 0.55, sy + r * 0.45],
                 200, 480, fill=(178, 120, 92), width=9)
        draw.arc([sx - r * 0.28, sy - r * 0.22, sx + r * 0.28, sy + r * 0.22],
                 20, 300, fill=(178, 120, 92), width=8)
        # Gloss dot.
        draw.ellipse([sx - r * 0.45, sy - r * 0.5, sx - r * 0.15, sy - r * 0.3],
                     fill=(255, 235, 220))


def draw_egg(img):
    draw = ImageDraw.Draw(img, "RGBA")
    # Egg half at 10 o'clock, white slightly rotated.
    draw.polygon(ellipse_poly(700, 950, 145, 108, -18), fill=EGG_WHITE)
    draw.polygon(ellipse_poly(700, 950, 145, 108, -18),
                 outline=(232, 214, 180), width=6)
    draw.ellipse([640, 890, 762, 1012], fill=YOLK)
    draw.ellipse([652, 902, 750, 1000], fill=YOLK_DEEP)
    draw.ellipse([668, 908, 712, 946], fill=(255, 214, 130))
    # Specular dot.
    draw.ellipse([678, 918, 700, 938], fill=WHITE)


def draw_noodles(img):
    draw = ImageDraw.Draw(img, "RGBA")
    rng = random.Random(21)
    # ~13 thick arcs across the broth in two yellows.
    for i in range(13):
        col = NOODLE_A if i % 2 == 0 else NOODLE_B
        arx = rng.randint(150, 430)
        ary = int(arx * 0.58)
        start = rng.randint(0, 300)
        span = rng.randint(70, 150)
        offx = rng.randint(-90, 90)
        offy = rng.randint(-60, 60)
        draw.arc([CX - arx + offx, CY - ary + offy,
                  CX + arx + offx, CY + ary + offy],
                 start, start + span, fill=col, width=30)
    # A few short noodle strands near the centre for texture.
    for i in range(6):
        col = NOODLE_A if i % 2 else NOODLE_B
        arx = rng.randint(60, 150)
        ary = int(arx * 0.58)
        start = rng.randint(0, 300)
        draw.arc([CX - arx, CY - ary + 40, CX + arx, CY + ary + 40],
                 start, start + rng.randint(60, 130), fill=col, width=26)


def draw_scallions(img):
    draw = ImageDraw.Draw(img, "RGBA")
    rng = random.Random(33)
    placed = 0
    tries = 0
    while placed < 22 and tries < 120:
        tries += 1
        ox = rng.randint(CX - 440, CX + 440)
        oy = rng.randint(CY - 240, CY + 240)
        if ((ox - CX) / 470) ** 2 + ((oy - CY) / 260) ** 2 > 0.92:
            continue
        # Keep clear of egg and chashu centres.
        if ((ox - 700) / 170) ** 2 + ((oy - 950) / 130) ** 2 < 1:
            continue
        if ((ox - 1330) / 150) ** 2 + ((oy - 1180) / 120) ** 2 < 1:
            continue
        if ((ox - 1435) / 130) ** 2 + ((oy - 1040) / 110) ** 2 < 1:
            continue
        r = rng.randint(13, 22)
        col = SCALLION if placed % 3 else SCALLION_DARK
        draw.ellipse([ox - r, oy - r * 0.7, ox + r, oy + r * 0.7],
                     fill=col, outline=(20, 60, 28), width=4)
        draw.ellipse([ox - r * 0.45, oy - r * 0.3, ox + r * 0.45, oy + r * 0.3],
                     fill=(140, 200, 110))
        placed += 1


def draw_chopsticks_and_lift(img):
    draw = ImageDraw.Draw(img, "RGBA")
    # Noodle bundle lifted from the broth to the chopstick tips.
    # Sine-wave strands hanging from (1175, 730) down to the broth (~1120, 1060).
    for k, col in enumerate((NOODLE_A, NOODLE_B, NOODLE_A, NOODLE_B, NOODLE_A)):
        pts = []
        for i in range(41):
            t = i / 40
            x = 1175 - 55 * t + 46 * math.sin(t * math.pi * 2.6 + k * 0.9) * (1 - t * 0.4) + (k - 2) * 18
            y = 730 + 330 * t
            pts.append((x, y))
        draw.line(pts, fill=col, width=30, joint="curve")
    # Noodle blob where the chopsticks grip.
    draw.ellipse([1120, 680, 1260, 800], fill=NOODLE_A)
    draw.ellipse([1145, 700, 1235, 780], fill=NOODLE_B)
    draw.arc([1140, 700, 1240, 790], 200, 60, fill=NOODLE_A, width=18)

    # Two chopsticks, diagonal from top-right down to the grip point.
    for (x0, y0, x1, y1) in ((1960, 40, 1185, 715), (1900, 190, 1140, 760)):
        draw.line([(x0, y0), (x1, y1)], fill=CHOP, width=36, joint="curve")
        draw.line([(x0, y0), (x1, y1)], fill=CHOP_LIGHT, width=12, joint="curve")
    # Tapered tips.
    draw.polygon([(1185, 700), (1215, 725), (1180, 745)], fill=CHOP)


def draw_steam(img):
    # Three wavy white curves above the bowl, blurred, low alpha.
    layer = Image.new("RGBA", (SS, SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for (sx, amp, phase) in ((820, 55, 0.0), (1020, 65, 1.2), (1230, 50, 2.4)):
        pts = []
        for i in range(61):
            t = i / 60
            x = sx + amp * math.sin(t * math.pi * 2.2 + phase)
            y = 800 - 430 * t
            pts.append((x, y))
        d.line(pts, fill=(255, 255, 255, 110), width=34, joint="curve")
    img.alpha_composite(layer.filter(ImageFilter.GaussianBlur(22)))


def draw_vignette(img):
    # Soft darkening at the corners/edges.
    mask = Image.new("L", (SS, SS), 0)
    md = ImageDraw.Draw(mask)
    md.ellipse([140, 140, SS - 140, SS - 140], fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(220))
    dark = Image.new("RGBA", (SS, SS), (12, 6, 3, 255))
    inv = mask.point(lambda v: 255 - v)
    img.paste(Image.composite(dark, img.convert("RGBA"), inv), (0, 0))


def build():
    img = Image.new("RGBA", (SS, SS))
    draw_background(img)
    draw_bowl(img)
    draw_nori(img)
    draw_chashu(img)
    draw_egg(img)
    draw_noodles(img)
    draw_scallions(img)
    draw_chopsticks_and_lift(img)
    draw_steam(img)
    draw_vignette(img)
    img = img.convert("RGB").resize((OUT, OUT), Image.LANCZOS)
    img.save(HERE / "entry.png", optimize=True)
    print("wrote", HERE / "entry.png", img.size)


if __name__ == "__main__":
    build()
