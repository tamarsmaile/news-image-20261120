#!/usr/bin/env python3
"""World news of Friday 20 November 2026, in one image.

Writes a deterministic 1024x1024 PNG to $MAKEFUN_OUTPUT_DIR/entry.png
(or /output/entry.png). Python 3.13 standard library only, no network,
no timestamps, no randomness: two runs produce byte-identical output.

The image is drawn from scratch with a small built-in 5x7 bitmap font and
a minimal PNG encoder (zlib, fixed compression level).

Facts (all events that happened, or were first reported, on Friday
20 November 2026 - Reuters, BBC, AP, AFP, Just Security):
  * Russia launches one of the largest attacks of the war on Ukraine:
    more than 400 drones and over 110 missiles, 27 of them ballistic.
    Three bridges across the Dnipro in Kyiv are hit, power plants are
    struck, eight people are killed and 28 injured across Ukraine.
  * Two Russian missiles and a jet drone cross into Poland during the
    attack and fall in the south-east; Warsaw calls it a provocation
    and NATO jets scramble.
  * The EU and the UK hold their second summit in Brussels: PM Andy
    Burnham meets Antonio Costa and Ursula von der Leyen on trade,
    energy, defence and youth mobility, and condemns the Poland
    incursion.
  * COP31 reaches its final day in Antalya with the draft deal stripped
    of all fossil-fuel language; Panama threatens to veto any deal
    without an oil-production cap, leaving talks deadlocked.
  * Iraqi forces deploy at Jurf al-Sakhar, stronghold of the
    Iran-backed Kataib Hezbollah militia, under a deal to curb the
    group, which the government accuses of smuggling state oil.
  * Estonia says it will close its border with Russia for at least
    six months, citing security threats.
  * Also that day: Haitian forces kill 34 suspected gang members in a
    raid; a migrant boat capsizes off Senegal with dozens missing;
    Nayib Bukele registers for a third term as president of
    El Salvador.
"""

import os
import struct
import zlib
from pathlib import Path

W, H = 1024, 1024

# ---------------------------------------------------------------- palette
PAPER = (247, 243, 232)
INK = (17, 24, 39)
NAVY = (15, 42, 74)
NAVY_LT = (30, 68, 110)
GOLD = (201, 162, 39)
WHITE = (255, 255, 255)
GREY = (90, 96, 108)
CARD = (255, 255, 255)
LINE = (203, 199, 186)
RED = (178, 34, 34)
TEAL = (13, 110, 102)
ORANGE = (196, 96, 16)
GREEN = (34, 120, 60)
PURPLE = (96, 64, 140)
STEEL = (58, 96, 140)

# ---------------------------------------------------------------- 5x7 font
# Each glyph: 7 rows of 5 bits, written as strings of '#' / '.'.
_G = {
    'A': ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    'B': ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    'C': ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    'D': ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    'E': ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    'F': ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    'G': ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    'H': ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    'I': ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    'J': ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    'K': ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    'L': ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    'M': ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    'N': ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    'O': ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    'P': ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    'Q': ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    'R': ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    'S': ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    'T': ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    'U': ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    'V': ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    'W': ("10001", "10001", "10001", "10101", "10101", "10101", "01010"),
    'X': ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    'Y': ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    'Z': ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    '0': ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    '1': ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    '2': ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    '3': ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    '4': ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    '5': ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    '6': ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    '7': ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    '8': ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    '9': ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    ' ': ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    '.': ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ',': ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ':': ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ';': ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '!': ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    '?': ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    '-': ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    '(': ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ')': ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    '/': ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    '&': ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    '%': ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    '$': ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    '+': ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    '=': ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    '*': ("00000", "00100", "10101", "01110", "10101", "00100", "00000"),
    '#': ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
    '@': ("01110", "10001", "10111", "10101", "10110", "10000", "01110"),
    '_': ("00000", "00000", "00000", "00000", "00000", "00000", "11111"),
    '<': ("00010", "00100", "01000", "10000", "01000", "00100", "00010"),
    '>': ("01000", "00100", "00010", "00001", "00010", "00100", "01000"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
}
FONT = {ch: tuple(int(r, 2) for r in rows) for ch, rows in _G.items()}

# ---------------------------------------------------------------- canvas
buf = bytearray(W * H * 3)


def px(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        buf[i], buf[i + 1], buf[i + 2] = c


def rect(x, y, w, h, c):
    for yy in range(y, y + h):
        for xx in range(x, x + w):
            px(xx, yy, c)


def hline(x0, x1, y, c, t=1):
    for yy in range(y, y + t):
        for xx in range(x0, x1 + 1):
            px(xx, yy, c)


def vline(x, y0, y1, c, t=1):
    for xx in range(x, x + t):
        for yy in range(y0, y1 + 1):
            px(xx, yy, c)


def line(x0, y0, x1, y1, c, t=1):
    dx, dy = abs(x1 - x0), -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    while True:
        for a in range(t):
            for b in range(t):
                px(x0 + a, y0 + b, c)
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy


def circle(cx, cy, r, c, fill=True):
    if fill:
        for yy in range(cy - r, cy + r + 1):
            dx = int((r * r - (yy - cy) ** 2) ** 0.5) if abs(yy - cy) <= r else 0
            for xx in range(cx - dx, cx + dx + 1):
                px(xx, yy, c)
    else:
        for a in range(360):
            import math
            px(int(cx + r * math.cos(math.radians(a))),
               int(cy + r * math.sin(math.radians(a))), c)


def poly(points, c):
    # scanline fill of a simple polygon
    ys = [p[1] for p in points]
    for y in range(min(ys), max(ys) + 1):
        xs = []
        n = len(points)
        for i in range(n):
            x0, y0 = points[i]
            x1, y1 = points[(i + 1) % n]
            if (y0 <= y < y1) or (y1 <= y < y0):
                xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
        xs.sort()
        for i in range(0, len(xs) - 1, 2):
            for x in range(int(xs[i]), int(xs[i + 1]) + 1):
                px(x, y, c)


# ---------------------------------------------------------------- text
def text_w(s, scale):
    return len(s) * 6 * scale - scale


def draw_text(x, y, s, scale, c):
    s = s.upper()
    cx = x
    for ch in s:
        glyph = FONT.get(ch, FONT[' '])
        for row in range(7):
            bits = glyph[row]
            for col in range(5):
                if bits & (1 << (4 - col)):
                    rect(cx + col * scale, y + row * scale, scale, scale, c)
        cx += 6 * scale
    return cx


def wrap(s, scale, max_w):
    words = s.upper().split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if text_w(trial, scale) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def para(x, y, s, scale, c, max_w, leading=None):
    lh = leading if leading is not None else 10 * scale
    for ln in wrap(s, scale, max_w):
        draw_text(x, y, ln, scale, c)
        y += lh
    return y


# ---------------------------------------------------------------- icons
def icon_scales(cx, cy, s, c):
    # scales of justice, size s
    line(cx, cy - s, cx, cy + s, c, 3)
    line(cx - s, cy - s + 6, cx + s, cy - s + 6, c, 3)
    line(cx - s, cy - s + 6, cx - s, cy - 6, c, 2)
    line(cx + s, cy - s + 6, cx + s, cy - 6, c, 2)
    poly([(cx - s - 14, cy - 2), (cx - s + 14, cy - 2), (cx - s, cy + 16)], c)
    poly([(cx + s - 14, cy - 2), (cx + s + 14, cy - 2), (cx + s, cy + 16)], c)
    rect(cx - 16, cy + s - 2, 32, 4, c)


def icon_flags(cx, cy, s):
    # three small flags: USA, CHN, RUS (no labels: the headline names them)
    cols = [(RED, WHITE), (RED, GOLD), (WHITE, RED)]
    for i, (a, b) in enumerate(cols):
        x = cx - s + i * (2 * s // 3 + 8)
        rect(x, cy - s // 2, 2 * s // 3, s // 2, a)
        rect(x, cy, 2 * s // 3, s // 2, b)
        vline(x, cy - s // 2 - 10, cy + s // 2, INK, 2)


def icon_globe(cx, cy, r, c, accent):
    circle(cx, cy, r, c, fill=False)
    for k in range(-2, 3):
        line(cx + k * r // 3, cy - r, cx + k * r // 3, cy + r, c, 1)
    line(cx - r, cy, cx + r, cy, c, 1)
    circle(cx - r // 3, cy - r // 4, r // 4, accent)
    circle(cx + r // 4, cy + r // 3, r // 5, accent)


def icon_flame(cx, cy, s, c):
    poly([(cx, cy - s), (cx + s // 2, cy - s // 3), (cx + s // 3, cy + s // 4),
          (cx + s // 2, cy + s // 2), (cx, cy + s), (cx - s // 2, cy + s // 2),
          (cx - s // 3, cy + s // 4), (cx - s // 2, cy - s // 3)], c)
    circle(cx, cy + s // 3, s // 4, GOLD)


def icon_chart(cx, cy, s, c):
    line(cx - s, cy + s // 2, cx - s // 3, cy, c, 4)
    line(cx - s // 3, cy, cx + s // 4, cy - s // 4, c, 4)
    line(cx + s // 4, cy - s // 4, cx + s, cy - s, c, 4)
    poly([(cx + s, cy - s), (cx + s - 12, cy - s + 2), (cx + s - 2, cy - s + 12)], c)
    line(cx - s, cy + s, cx + s, cy + s, c, 3)


def icon_shield(cx, cy, s, c):
    poly([(cx - s // 2, cy - s // 2), (cx + s // 2, cy - s // 2),
          (cx + s // 2, cy), (cx, cy + s // 2), (cx - s // 2, cy)], c)
    draw_text(cx - 9, cy - 12, "*", 3, WHITE)


# ---------------------------------------------------------------- layout
def card(x, y, w, h, tag, tag_c, headline, body, icon=None):
    rect(x, y, w, h, CARD)
    rect(x, y, w, 5, tag_c)
    # border
    hline(x, x + w - 1, y + h - 1, LINE)
    vline(x, y, y + h - 1, LINE)
    vline(x + w - 1, y, y + h - 1, LINE)
    tx = x + 18
    ty = y + 20
    draw_text(tx, ty, tag, 2, tag_c)
    if icon is not None:
        icon(x + w - 62, y + 58, 26)
    hy = ty + 28
    for ln in wrap(headline, 3, w - 110):
        draw_text(tx, hy, ln, 3, INK)
        hy += 30
    para(tx, hy + 6, body, 2, (52, 58, 70), w - 36, leading=18)


def main():
    rect(0, 0, W, H, PAPER)

    # ---- masthead ------------------------------------------------------
    rect(0, 0, W, 150, NAVY)
    rect(0, 150, W, 5, GOLD)
    draw_text(28, 22, "THE WORLD IN ONE DAY", 6, WHITE)
    draw_text(28, 80, "FRIDAY 20 NOVEMBER 2026", 5, GOLD)
    draw_text(28, 124, "SIX STORIES FROM AROUND THE GLOBE - SOURCES: REUTERS, BBC, AP, AFP", 2, (190, 205, 225))
    icon_globe(930, 75, 48, (150, 175, 205), GOLD)

    # ---- lead story: Kyiv bridges --------------------------------------
    lx, ly, lw, lh = 24, 168, 976, 196
    rect(lx, ly, lw, lh, CARD)
    rect(lx, ly, lw, 5, RED)
    hline(lx, lx + lw - 1, ly + lh - 1, LINE)
    vline(lx, ly, ly + lh - 1, LINE)
    vline(lx + lw - 1, ly, ly + lh - 1, LINE)
    icon_flame(120, ly + 108, 42, RED)
    draw_text(lx + 210, ly + 20, "LEAD STORY  -  KYIV", 2, RED)
    hy = ly + 48
    for ln in wrap("RUSSIA HITS THREE KYIV BRIDGES", 4, lw - 240):
        draw_text(lx + 210, hy, ln, 4, INK)
        hy += 40
    para(lx + 210, hy + 4,
         "Russia launches one of its biggest attacks of the war: more "
         "than 400 drones and 110 missiles hit Kyiv's three Dnipro "
         "bridges and power plants. Eight people are killed and 28 "
         "injured across Ukraine.", 2, (52, 58, 70), lw - 240, leading=19)

    # ---- four story cards ----------------------------------------------
    gx, gy = 24, 378
    cw, ch, gap = 480, 212, 16
    card(gx, gy, cw, ch, "WARSAW  -  POLAND", NAVY_LT,
         "RUSSIAN MISSILES CROSS INTO POLAND",
         "Two Russian missiles and a jet drone fall in south-east "
         "Poland during the attack on Ukraine. Warsaw calls it a "
         "provocation; NATO jets scramble and Rzeszow airport "
         "suspends flights.",
         lambda cx, cy, s: icon_shield(cx, cy, s, NAVY_LT))
    card(gx + cw + gap, gy, cw, ch, "BRUSSELS  -  EUROPE", TEAL,
         "EU AND UK HOLD SECOND SUMMIT",
         "Prime Minister Andy Burnham meets Ursula von der Leyen and "
         "Antonio Costa in Brussels to rebuild trade, energy and "
         "defence ties, and to condemn the Poland incursion.",
         lambda cx, cy, s: icon_flags(cx - 10, cy, s))
    card(gx, gy + ch + gap, cw, ch, "ANTALYA  -  CLIMATE", ORANGE,
         "COP31 DEADLOCKED ON FOSSIL FUELS",
         "On the summit's final day the draft deal drops all mention "
         "of fossil fuels. Panama threatens to veto any deal without "
         "an oil-production cap.",
         lambda cx, cy, s: icon_globe(cx, cy, s, ORANGE, GOLD))
    card(gx + cw + gap, gy + ch + gap, cw, ch, "BAGHDAD  -  IRAQ", GREEN,
         "IRAQ MOVES ON IRAN-BACKED MILITIA",
         "Iraqi forces deploy at Jurf al-Sakhar, stronghold of the "
         "Iran-backed Kataib Hezbollah, under a deal to curb the "
         "group, accused of smuggling state oil.",
         lambda cx, cy, s: icon_flame(cx, cy, s, GREEN))

    # ---- Estonia (short card, drawn inline) ---------------------------
    ux, uy, uw, uh = 24, 830, 976, 110
    rect(ux, uy, uw, uh, CARD)
    rect(ux, uy, uw, 5, PURPLE)
    hline(ux, ux + uw - 1, uy + uh - 1, LINE)
    vline(ux, uy, uy + uh - 1, LINE)
    vline(ux + uw - 1, uy, uy + uh - 1, LINE)
    draw_text(ux + 18, uy + 14, "TALLINN  -  EUROPE", 2, PURPLE)
    draw_text(ux + 18, uy + 38, "ESTONIA TO SHUT ITS RUSSIA BORDER", 3, INK)
    icon_shield(ux + uw - 62, uy + 52, 26, PURPLE)
    para(ux + 18, uy + 70,
         "Estonia announces it will close its border with Russia for "
         "at least six months, citing security threats, and will "
         "decide later whether to extend the closure.",
         2, (52, 58, 70), uw - 36, leading=18)

    # ---- also strip ------------------------------------------------------
    ay = 954
    rect(24, ay, 976, 70, NAVY)
    draw_text(44, ay + 8, "ALSO ON 20 NOVEMBER 2026", 2, GOLD)
    para(44, ay + 30,
         "HAITI: 34 GANG SUSPECTS KILLED IN RAID  |  SENEGAL BOAT "
         "CAPSIZES, DOZENS MISSING  |  BUKELE SEEKS THIRD TERM",
         2, WHITE, 936, leading=17)

    # ---- encode PNG (deterministic: no ancillary chunks, zlib level 9) --
    raw = bytearray()
    for y in range(H):
        raw.append(0)
        raw += buf[y * W * 3:(y + 1) * W * 3]
    idat = zlib.compress(bytes(raw), 9)

    def chunk(tag, data):
        c = struct.pack(">I", len(data)) + tag + data
        return c + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", idat)
    png += chunk(b"IEND", b"")

    out = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    out.mkdir(parents=True, exist_ok=True)
    (out / "entry.png").write_bytes(png)


if __name__ == "__main__":
    main()
