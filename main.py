#!/usr/bin/env python3
"""SOLARFLASH — studio catalogue photo of an impossible gadget.

Pure-Pillow renderer: a slim black/silver solar-powered flashlight standing on
a clean white studio sweep, with a small yellow sun in the corner.

Part 1: backdrop, contact shadow, torch body, head and solar panel.
Part 2 (below): product wordmark, corner sun, save to /output/entry.png.
"""

import os
from PIL import Image, ImageDraw, ImageFilter, ImageChops

W = H = 1024          # final output size
SS = 2                # supersampling factor (draw big, shrink down)
CW, CH = W * SS, H * SS


# --------------------------------------------------------------------------
# small gradient helpers (Pillow only, no numpy)
# --------------------------------------------------------------------------
def _lerp_stops(stops, t):
    """Interpolate a list of (pos, (r, g, b)) stops at position t in 0..1."""
    if t <= stops[0][0]:
        return stops[0][1]
    if t >= stops[-1][0]:
        return stops[-1][1]
    for i in range(len(stops) - 1):
        p0, c0 = stops[i]
        p1, c1 = stops[i + 1]
        if p0 <= t <= p1:
            f = 0.0 if p1 == p0 else (t - p0) / (p1 - p0)
            return tuple(int(round(c0[k] + (c1[k] - c0[k]) * f)) for k in range(3))
    return stops[-1][1]


def vgrad(w, h, stops):
    """Vertical gradient image of size (w, h)."""
    strip = Image.new("RGB", (1, h))
    px = strip.load()
    for y in range(h):
        px[0, y] = _lerp_stops(stops, y / max(1, h - 1))
    return strip.resize((w, h), Image.NEAREST)


def hgrad(w, h, stops):
    """Horizontal gradient image of size (w, h)."""
    strip = Image.new("RGB", (1, w))
    px = strip.load()
    for x in range(w):
        px[0, x] = _lerp_stops(stops, x / max(1, w - 1))
    strip = strip.transpose(Image.TRANSPOSE).resize((w, h), Image.NEAREST)
    return strip


def rounded_mask(size, radius, corners=None):
    """Antialiased-ish rounded rectangle mask (L)."""
    m = Image.new("L", size, 0)
    d = ImageDraw.Draw(m)
    d.rounded_rectangle((0, 0, size[0] - 1, size[1] - 1), radius=radius,
                        fill=255, corners=corners)
    return m


def metal_panel(size, stops, radius, vertical=False):
    """Cylindrical metal slab: gradient + rounded mask -> RGBA layer."""
    w, h = size
    grad = vgrad(w, h, stops) if vertical else hgrad(w, h, stops)
    layer = grad.convert("RGBA")
    layer.putalpha(rounded_mask(size, radius))
    return layer


# --------------------------------------------------------------------------
# palette
# --------------------------------------------------------------------------
SILVER = [
    (0.00, (74, 79, 88)),
    (0.08, (118, 125, 136)),
    (0.26, (236, 240, 246)),
    (0.40, (198, 204, 213)),
    (0.62, (150, 156, 167)),
    (0.80, (214, 219, 227)),
    (0.93, (126, 132, 143)),
    (1.00, (84, 89, 98)),
]
SILVER_WARM = [
    (0.00, (66, 70, 78)),
    (0.10, (140, 146, 156)),
    (0.30, (244, 247, 251)),
    (0.55, (188, 194, 203)),
    (0.78, (232, 236, 243)),
    (1.00, (96, 101, 110)),
]
BLACK = [
    (0.00, (14, 14, 16)),
    (0.06, (32, 33, 36)),
    (0.22, (62, 64, 70)),
    (0.38, (46, 48, 53)),
    (0.62, (26, 27, 30)),
    (0.84, (44, 46, 50)),
    (0.95, (24, 25, 28)),
    (1.00, (10, 10, 12)),
]


# --------------------------------------------------------------------------
# geometry (supersampled coords)
# --------------------------------------------------------------------------
CX = CW // 2
BASE_Y = 1690                     # where the torch touches the studio floor
BODY_X0, BODY_X1 = CX - 134, CX + 134
HEAD_X0, HEAD_X1 = CX - 186, CX + 186
HEAD_Y0, HEAD_Y1 = 700, 802
COLLAR_Y0, COLLAR_Y1 = 802, 850
GRIP_Y0, GRIP_Y1 = 850, 1544
CAP_Y0, CAP_Y1 = 1544, BASE_Y


# --------------------------------------------------------------------------
# backdrop
# --------------------------------------------------------------------------
def paint_backdrop(canvas):
    """Clean white studio: soft radial glow, gentle sweep, faint vignette."""
    small = (128, 128)
    bg = Image.new("RGB", small)
    px = bg.load()
    cx, cy = 64, 58
    for y in range(small[1]):
        for x in range(small[0]):
            dx = (x - cx) / 64.0
            dy = (y - cy) / 64.0
            r = min(1.0, (dx * dx + dy * dy) ** 0.5)
            # 255 at the centre -> 246 at the corners: clean studio white
            v = 255.0 - 9.0 * (r ** 2.4)
            # seamless sweep: floor starts slightly greyer near the bottom
            if y > 92:
                f = (y - 92) / 36.0
                v -= 4.5 * f
            px[x, y] = (int(v), int(v), int(min(255, v + 1)))

    bg = bg.resize((CW, CH), Image.BICUBIC)
    canvas.paste(bg, (0, 0))

    # bright key-light pool behind the product
    glow = Image.new("L", (CW, CH), 0)
    ImageDraw.Draw(glow).ellipse(
        (CX - 620, 120, CX + 620, 1500), fill=58)
    glow = glow.filter(ImageFilter.GaussianBlur(120))
    canvas.paste(Image.new("RGB", (CW, CH), (255, 255, 255)), (0, 0), glow)


# --------------------------------------------------------------------------
# shadow
# --------------------------------------------------------------------------
def paint_shadow(canvas):
    """Soft elliptical contact shadow on the sweep."""
    sh = Image.new("L", (CW, CH), 0)
    d = ImageDraw.Draw(sh)
    d.ellipse((CX - 300, BASE_Y - 30, CX + 300, BASE_Y + 58), fill=120)
    d.ellipse((CX - 430, BASE_Y - 18, CX + 430, BASE_Y + 92), fill=52)
    d.ellipse((CX - 160, BASE_Y - 8, CX + 160, BASE_Y + 26), fill=90)
    sh = sh.filter(ImageFilter.GaussianBlur(34))
    canvas.paste(Image.new("RGB", (CW, CH), (96, 100, 108)), (0, 0), sh)


# --------------------------------------------------------------------------
# torch
# --------------------------------------------------------------------------
def paint_torch(canvas):
    """Slim standing torch: base cap, ribbed grip, collar, head."""

    # --- base cap (silver, rounded bottom) -------------------------------
    cap = metal_panel((CAP_Y1 - CAP_Y0, CAP_Y1 - CAP_Y0), SILVER_WARM, 0)
    cap = metal_panel((BODY_X1 - BODY_X0 + 24, CAP_Y1 - CAP_Y0 + 8),
                      SILVER_WARM, 34)
    canvas.paste(cap, (BODY_X0 - 12, CAP_Y0 - 8), cap)
    # dark seam above the cap
    seam = Image.new("RGBA", (BODY_X1 - BODY_X0 + 24, 6), (0, 0, 0, 120))
    canvas.paste(seam, (BODY_X0 - 12, CAP_Y0 - 12), seam)

    # --- grip (black rubber) ---------------------------------------------
    grip_w = BODY_X1 - BODY_X0
    grip = metal_panel((grip_w, GRIP_Y1 - GRIP_Y0 + 40), BLACK, 26)
    canvas.paste(grip, (BODY_X0, GRIP_Y0 - 20), grip)

    # subtle ribs on the grip
    ribs = Image.new("RGBA", (CW, CH), (0, 0, 0, 0))
    rd = ImageDraw.Draw(ribs)
    y = GRIP_Y0 + 6
    while y < GRIP_Y1 - 8:
        rd.line((BODY_X0 + 10, y, BODY_X1 - 10, y), fill=(120, 124, 132, 26))
        rd.line((BODY_X0 + 10, y + 3, BODY_X1 - 10, y + 3), fill=(0, 0, 0, 60))
        y += 34
    canvas.alpha_composite(ribs)

    # specular sheen down the grip
    sheen = Image.new("RGBA", (CW, CH), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sheen)
    sd.rounded_rectangle((BODY_X0 + 34, GRIP_Y0, BODY_X0 + 66, GRIP_Y1),
                         radius=16, fill=(255, 255, 255, 46))
    sd.rounded_rectangle((BODY_X0 + 30, GRIP_Y0, BODY_X0 + 40, GRIP_Y1),
                         radius=6, fill=(255, 255, 255, 34))
    sheen = sheen.filter(ImageFilter.GaussianBlur(10))
    canvas.alpha_composite(sheen)

    # --- collar ring -----------------------------------------------------
    collar = metal_panel((BODY_X1 - BODY_X0 + 26, COLLAR_Y1 - COLLAR_Y0),
                         SILVER, 10)
    canvas.paste(collar, (BODY_X0 - 13, COLLAR_Y0), collar)

    # --- head ------------------------------------------------------------
    head = metal_panel((HEAD_X1 - HEAD_X0, HEAD_Y1 - HEAD_Y0), SILVER, 30)
    canvas.paste(head, (HEAD_X0, HEAD_Y0), head)

    # brushed metal bands on the head
    bands = Image.new("RGBA", (CW, CH), (0, 0, 0, 0))
    bd = ImageDraw.Draw(bands)
    for i, yy in enumerate(range(HEAD_Y1 - 46, HEAD_Y1 - 6, 12)):
        bd.line((HEAD_X0 + 26, yy, HEAD_X1 - 26, yy),
                fill=(255, 255, 255, 70) if i % 2 == 0 else (0, 0, 0, 34),
                width=3)
    bd.rounded_rectangle((HEAD_X0, HEAD_Y0 + 6, HEAD_X1, HEAD_Y0 + 12),
                         radius=4, fill=(255, 255, 255, 110))
    bd.rounded_rectangle((HEAD_X0, HEAD_Y1 - 26, HEAD_X1, HEAD_Y1),
                         radius=10, fill=(0, 0, 0, 40))
    canvas.alpha_composite(bands)


# --------------------------------------------------------------------------
# solar panel on top
# --------------------------------------------------------------------------
def make_panel():
    """Tilted photovoltaic slab: silver frame, dark cells, glass sheen."""
    pw, ph = 410, 158
    panel = Image.new("RGBA", (pw, ph), (0, 0, 0, 0))

    frame = metal_panel((pw, ph), SILVER_WARM, 22)
    panel.paste(frame, (0, 0), frame)

    # inner glass area
    ix0, iy0, ix1, iy1 = 18, 18, pw - 18, ph - 18
    cells = hgrad(ix1 - ix0, iy1 - iy0, [
        (0.0, (16, 26, 48)),
        (0.5, (30, 46, 82)),
        (1.0, (13, 21, 40)),
    ]).convert("RGBA")
    cells.putalpha(rounded_mask((ix1 - ix0, iy1 - iy0), 8))
    panel.paste(cells, (ix0, iy0), cells)

    # photovoltaic cell grid
    g = ImageDraw.Draw(panel)
    cols, rows = 6, 2
    cw = (ix1 - ix0) / cols
    ch = (iy1 - iy0) / rows
    for c in range(cols + 1):
        x = ix0 + c * cw
        g.line((x, iy0, x, iy1), fill=(128, 152, 186, 190), width=3)
    for r in range(rows + 1):
        y = iy0 + r * ch
        g.line((ix0, y, ix1, y), fill=(128, 152, 186, 190), width=3)
    # fine busbars
    for c in range(cols):
        for k in (0.33, 0.66):
            x = ix0 + c * cw + cw * k
            g.line((x, iy0, x, iy1), fill=(96, 118, 150, 90), width=1)

    # glass reflection
    sheen = Image.new("RGBA", (pw, ph), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sheen)
    sd.polygon([(26, iy1), (150, iy0), (232, iy0), (108, iy1)],
               fill=(255, 255, 255, 52))
    sd.polygon([(250, iy1), (330, iy0), (352, iy0), (272, iy1)],
               fill=(255, 255, 255, 30))
    sheen = sheen.filter(ImageFilter.GaussianBlur(3))
    panel.alpha_composite(sheen)
    return panel


def paint_panel(canvas):
    """Place the panel tilted on the torch head, with a small cast shadow."""
    panel = make_panel().rotate(6.5, resample=Image.BICUBIC, expand=True)

    px, py = CX - panel.width // 2, 596 - panel.height // 2

    # soft cast shadow of the panel on the head / backdrop
    sh = panel.split()[3].filter(ImageFilter.GaussianBlur(16))
    shadow = Image.new("RGBA", panel.size, (28, 30, 36, 0))
    shadow.putalpha(sh.point(lambda v: int(v * 0.42)))
    canvas.alpha_composite(shadow, (px + 4, py + 20))

    canvas.alpha_composite(panel, (px, py))


# --------------------------------------------------------------------------
# part 2 — product wordmark, corner sun, composition
# --------------------------------------------------------------------------
from PIL import ImageFont            # noqa: E402

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def paint_wordmark(canvas):
    """'SOLARFLASH' running up the black grip, catalogue-print style."""
    text = "SOLARFLASH"
    size = 66
    font = ImageFont.truetype(FONT_BOLD, size)

    # measure with letter spacing
    spacing = 9
    widths = [font.getbbox(ch)[2] - font.getbbox(ch)[0] for ch in text]
    total = sum(widths) + spacing * (len(text) - 1)

    tmp = Image.new("RGBA", (total + 40, size * 2 + 40), (0, 0, 0, 0))
    d = ImageDraw.Draw(tmp)
    x = 20
    for ch, w in zip(text, widths):
        # dark halo for legibility on the black rubber
        d.text((x + 2, 22), ch, font=font, fill=(0, 0, 0, 170))
        d.text((x, 20), ch, font=font, fill=(238, 242, 248, 255))
        x += w + spacing
    # crop to ink
    bbox = tmp.getbbox()
    tmp = tmp.crop(bbox)
    # rotate so the word reads bottom-to-top along the body
    tmp = tmp.rotate(90, expand=True, resample=Image.BICUBIC)

    gx = CX - tmp.width // 2
    gy = (GRIP_Y0 + GRIP_Y1) // 2 - tmp.height // 2 + 6
    canvas.alpha_composite(tmp, (gx, gy))


def paint_sun(canvas):
    """Small yellow sun in the top-right corner — the punchline."""
    cx, cy, r = 1818, 292, 60

    # ambient glow
    glow = Image.new("L", (CW, CH), 0)
    ImageDraw.Draw(glow).ellipse((cx - 190, cy - 190, cx + 190, cy + 190), fill=52)
    glow = glow.filter(ImageFilter.GaussianBlur(90))
    canvas.alpha_composite(Image.merge("RGBA", (
        Image.new("L", (CW, CH), 255),
        Image.new("L", (CW, CH), 214),
        Image.new("L", (CW, CH), 138),
        glow)))

    # rays
    rays = Image.new("RGBA", (CW, CH), (0, 0, 0, 0))
    rd = ImageDraw.Draw(rays)
    import math
    for i in range(12):
        a = math.radians(i * 30 + 15)
        r0, r1 = r + 20, r + (78 if i % 2 == 0 else 58)
        half = math.radians(5.5 if i % 2 == 0 else 4.2)
        p1 = (cx + r0 * math.cos(a - half), cy + r0 * math.sin(a - half))
        p2 = (cx + r0 * math.cos(a + half), cy + r0 * math.sin(a + half))
        p3 = (cx + r1 * math.cos(a), cy + r1 * math.sin(a))
        rd.polygon([p1, p2, p3], fill=(255, 186, 46, 240))
    rays = rays.filter(ImageFilter.GaussianBlur(1.2))
    canvas.alpha_composite(rays)

    # disc, shaded like a sphere
    disc = Image.new("RGBA", (CW, CH), (0, 0, 0, 0))
    dd = ImageDraw.Draw(disc)
    dd.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(255, 198, 52, 255))
    canvas.alpha_composite(disc)

    shade = Image.new("L", (CW, CH), 0)
    sd = ImageDraw.Draw(shade)
    sd.ellipse((cx - r, cy - r, cx + r, cy + r), fill=255)
    sd.ellipse((cx - r - 26, cy - r - 26, cx + r - 26, cy + r - 26), fill=0)
    shade = shade.filter(ImageFilter.GaussianBlur(18))
    canvas.alpha_composite(Image.merge("RGBA", (
        Image.new("L", (CW, CH), 240),
        Image.new("L", (CW, CH), 150),
        Image.new("L", (CW, CH), 40),
        shade.point(lambda v: int(v * 0.55)))))

    # highlight
    hl = Image.new("L", (CW, CH), 0)
    ImageDraw.Draw(hl).ellipse((cx - r * 0.55, cy - r * 0.72,
                                cx + r * 0.10, cy - r * 0.12), fill=225)
    hl = hl.filter(ImageFilter.GaussianBlur(14))
    canvas.alpha_composite(Image.merge("RGBA", (
        Image.new("L", (CW, CH), 255),
        Image.new("L", (CW, CH), 250),
        Image.new("L", (CW, CH), 214),
        hl)))


# --------------------------------------------------------------------------
def build():
    canvas = Image.new("RGBA", (CW, CH), (255, 255, 255, 255))
    paint_backdrop(canvas)
    paint_shadow(canvas)
    paint_torch(canvas)
    paint_panel(canvas)
    paint_wordmark(canvas)
    paint_sun(canvas)

    img = canvas.convert("RGB").resize((W, H), Image.LANCZOS)
    out_dir = "/output"
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    img.save(path, "PNG", optimize=True)

    size = os.path.getsize(path)
    print(f"saved {path} {img.size[0]}x{img.size[1]} {size} bytes "
          f"({size / 1024:.1f} KiB)")
    assert img.size == (1024, 1024), img.size
    assert size < 1024 * 1024, size
    return path


if __name__ == "__main__":
    build()
