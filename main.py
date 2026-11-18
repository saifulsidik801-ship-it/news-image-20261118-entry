#!/usr/bin/env python3
"""Wednesday 18 November 2026 — one-page world-news front page.

Draws a dense 1024x1024 newspaper front page with Pillow: a masthead,
three illustrated lead stories, twelve boxed stories, a by-the-numbers
strip, a dotted world map with numbered pins, and a 25-item digest.
Every story on the page happened, or was first reported, on Wednesday
18 November 2026. Deterministic: no randomness, no network, no clock.
Writes entry.png next to this script and to /output/entry.png.
"""

import hashlib
import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
MARGIN = 28
CONTENT_W = W - 2 * MARGIN
COL_W = 312
COL_GAP = 16

PAPER = (248, 243, 230)
INK = (26, 26, 24)
NAVY = (23, 35, 62)
NAVY_SOFT = (38, 54, 88)
GOLD = (201, 162, 39)
GOLD_LIGHT = (232, 196, 90)
RED = (164, 31, 36)
RED_SOFT = (178, 58, 52)
MUTED = (90, 90, 82)
RULE = (60, 60, 56)
TEAL = (31, 111, 111)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def font(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


F_TITLE = font("DejaVuSerif-Bold.ttf", 52)
F_SUB = font("DejaVuSerif.ttf", 15)
F_KICK = font("DejaVuSans-Bold.ttf", 15)
F_HEAD = font("DejaVuSerif-Bold.ttf", 23)
F_HEAD_SM = font("DejaVuSans-Bold.ttf", 15)
F_BODY = font("DejaVuSans.ttf", 13)
F_BODY_SM = font("DejaVuSans.ttf", 11)
F_KICK_SM = font("DejaVuSans-Bold.ttf", 11)
F_LABEL = font("DejaVuSans-Bold.ttf", 13)
F_NUM_BIG = font("DejaVuSerif-Bold.ttf", 24)
F_NUM_CAP = font("DejaVuSans.ttf", 11)
F_ALSO = font("DejaVuSans.ttf", 10)
F_ALSO_B = font("DejaVuSans-Bold.ttf", 10)
F_FOOT = font("DejaVuSans.ttf", 10)
F_CAP = font("DejaVuSans-Bold.ttf", 10)
F_PIN = font("DejaVuSans-Bold.ttf", 9)
F_BADGE = font("DejaVuSans-Bold.ttf", 11)
F_BADGE_SM = font("DejaVuSans-Bold.ttf", 10)
F_EURO = font("DejaVuSans-Bold.ttf", 28)


def col_x(i):
    return MARGIN + i * (COL_W + COL_GAP)


def wrap(fnt, text, width):
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if fnt.getlength(trial) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def para(d, x, y, text, fnt, width, fill, leading):
    for line in wrap(fnt, text, width):
        d.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


def hrule(d, y, color=RULE, width=1, x0=None, x1=None):
    d.line([(x0 if x0 is not None else MARGIN, y),
            (x1 if x1 is not None else W - MARGIN, y)],
           fill=color, width=width)


def num_disc(d, cx, cy, r, n, fill=RED):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=fill)
    s = str(n)
    tw = F_BADGE.getlength(s) if r > 9 else F_BADGE_SM.getlength(s)
    fnt = F_BADGE if r > 9 else F_BADGE_SM
    d.text((cx - tw / 2, cy - (7 if r > 9 else 6)), s, font=fnt, fill=(255, 255, 255))


# ---------------------------------------------------------------- stories

HEROES = [
    {
        "n": 1, "kick": "MIDDLE EAST · CONFLICT", "scene": "bahrain",
        "cap": "SHEIKH ISA BASE · QESHM ISLAND",
        "head": "US and Iran trade fire over Bahrain",
        "body": ("US jets struck an Iranian missile site on Qeshm, officials say, "
                 "after drones targeted a US radar in Bahrain. "
                 "No injuries were reported."),
    },
    {
        "n": 2, "kick": "EUROPE · WAR IN UKRAINE", "scene": "kerch",
        "cap": "KERCH STRAIT · 19 KM CROSSING",
        "head": "A span of the Crimea bridge falls into the sea",
        "body": ("Kyiv says a second strike in two days destroyed the road arch. "
                 "Moscow says it downed 1,441 drones; the rail arch stands."),
    },
    {
        "n": 3, "kick": "ASIA · DIPLOMACY", "scene": "manila",
        "cap": "MANILA · FIRST QUAD IN TWO YEARS",
        "head": "Trump meets Marcos, then flies to Shenzhen",
        "body": ("Talks and a working lunch in Manila, a day after the first Quad "
                 "summit in two years. A trilateral with Xi and Putin is set "
                 "for Thursday."),
    },
]

MIDS = [
    {"n": 4, "kick": "UNITED STATES · BUSINESS", "icon": "chip",
     "head": "Nvidia revenue doubles to $115.8bn",
     "body": ("Sales rose 103% on data-centre demand. The board will not "
              "bring back Huang.")},
    {"n": 5, "kick": "ISRAEL · POLITICS", "icon": "parliament",
     "head": "Knesset elects Kahana as speaker, 66–52",
     "body": ("Kahana, an ally of Gadi Eisenkot, replaces Amir Ohana after "
              "a seven-hour debate.")},
    {"n": 6, "kick": "EUROPE · UKRAINE", "icon": "euro",
     "head": "EU proposes a €45bn loan for Ukraine",
     "body": ("It covers two-thirds of Kyiv's 2027 gap, repaid only if "
              "Russia pays reparations.")},
    {"n": 7, "kick": "SOUTH ASIA · WEATHER", "icon": "cyclone",
     "head": "Cyclone Akvan bears down on Andhra Pradesh",
     "body": ("Landfall is due Friday, gusts to 145 km/h. Odisha is moving "
              "200,000 people.")},
    {"n": 8, "kick": "UNITED STATES · MARKETS", "icon": "chart",
     "head": "Wall Street slides as the Dow drops 849 points",
     "body": ("The S&P 500 closed at its lowest since July in a fourth "
              "straight fall.")},
    {"n": 9, "kick": "CHINA · SUMMIT", "icon": "globe",
     "head": "APEC opens in Shenzhen with Xi keynote",
     "body": ("Leaders of 21 Pacific economies meet today and tomorrow; "
              "Trump and Lee arrive.")},
    {"n": 10, "kick": "UNITED KINGDOM · SANCTIONS", "icon": "shield",
     "head": "Britain sanctions settlement builders",
     "body": ("Eight Israeli firms and group Tzav 9 face asset freezes ahead "
              "of the E1 deadline.")},
    {"n": 11, "kick": "TRADE · CHINA–CANADA", "icon": "ship",
     "head": "China cuts tariffs as Xi meets Carney",
     "body": ("C$400m relief on pork and seafood; steel relief extended "
              "for two years.")},
    {"n": 12, "kick": "RUSSIA · DISASTER", "icon": "plane",
     "head": "Russian military plane crashes in Siberia; 19 dead",
     "body": ("An An-12 came down near Yagunovo after an engine fire. "
              "All aboard were killed.")},
    {"n": 13, "kick": "INDIA · SPORT", "icon": "cricket",
     "head": "Dhoni ends IPL playing career",
     "body": ("CSK name him Team Mentor for 2027: five titles, 272 "
              "appearances, no farewell match.")},
    {"n": 14, "kick": "ASIA · SECURITY", "icon": "jet",
     "head": "Japan scrambles fighters at Russian jets",
     "body": ("Tokyo protests after suspected Russian aircraft entered "
              "its airspace.")},
    {"n": 15, "kick": "INDIA · BUSINESS", "icon": "solar",
     "head": "Amazon to invest $7bn in India",
     "body": ("The plan backs solar and wind power for its Indian "
              "operations by 2030.")},
]

NUMBERS = [
    ("66–52", "Kahana's margin for speaker"),
    ("$115.8bn", "Nvidia's revenue, up 103%"),
    ("145 km/h", "Akvan's gusts at landfall"),
    ("200,000", "People Odisha is moving"),
]

ALSO = [
    (16, "Toledo train crash", "64 dead in Spain."),
    (17, "Settler sanctions", "Australia lists 7; UK 8 firms."),
    (18, "Gaza warning", "Board of Peace fears truce collapse."),
    (19, "Voyager 1", "First craft one light-day from Earth."),
    (20, "Anthropic IPO", "Priced today; ANT trades Thursday."),
    (21, "Measles status lost", "US loses status held since 2000."),
    (22, "Cyberattack", "Optimizely code hit 178 organisations."),
    (23, "Guinea crackdown", "224 jailed over illegal mining."),
    (24, "Costa Rica journalist shot dead", "first in 25 years."),
    (25, "Fishermen sue US", "16 sue over Pacific drone strike."),
    (26, "Telegram blocked", "Jordan and Iraq block the app."),
    (27, "NSA network down", "Fails in maintenance; no hack seen."),
    (28, "Apple outage", "Update hits iCloud, App Store, Pay."),
    (29, "Tech bets slashed", "Biggest cut since 2006, BofA finds."),
    (30, "Sudan drone toll", "UN: drones killed 1,630 civilians."),
    (31, "Tanker attacked", "TARA GAS hit; one seafarer missing."),
    (32, "Plotter sentenced", "27½ years for 2024 Trump plot."),
    (33, "Ukraine toll", "UN: 372 killed in October, up 95%."),
    (34, "India GDP grew 7.5%", "last quarter."),
    (35, "Ebola cases pass 11,000", "in Congo."),
    (36, "Estonia to shut Russia border", "on 1 Dec."),
    (37, "Pope Leo forgives", "rosary thrower."),
    (38, "COP31 draft", "'Accelerated action' on fossil fuels."),
    (39, "India re-elected to ITU Council", "for 2027–2030."),
    (40, "Baidu chief warns", "of AI 'bubble' ahead of APEC."),
]

# ---------------------------------------------------------------- scenes


def banner_frame(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], outline=RULE, width=1)


def caption_strip(d, x, y, w, text):
    d.rectangle([x, y + 122, x + w, y + 140], fill=(20, 20, 18))
    d.text((x + 8, y + 127), text, font=F_CAP, fill=(240, 236, 220))


def scene_bahrain(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(26, 43, 77))
    for fx, fy, r in [(0.08, 0.20, 2), (0.20, 0.12, 2), (0.35, 0.25, 2),
                      (0.50, 0.10, 2), (0.65, 0.22, 2), (0.80, 0.15, 2),
                      (0.92, 0.30, 2), (0.45, 0.35, 1), (0.72, 0.38, 1)]:
        d.ellipse([x + fx * w - r, y + fy * h - r, x + fx * w + r, y + fy * h + r],
                  fill=(235, 235, 225))
    d.ellipse([x + 0.78 * w, y + 0.18 * h, x + 0.78 * w + 30, y + 0.18 * h + 30],
              fill=GOLD_LIGHT)
    d.rectangle([x, y + 0.72 * h, x + w, y + h], fill=TEAL)
    for wy in (0.78, 0.86, 0.94):
        d.line([(x + 8, y + wy * h), (x + w - 8, y + wy * h)],
               fill=(190, 220, 210), width=1)
    d.line([(x + 0.16 * w, y + 0.72 * h), (x + 0.16 * w, y + 0.52 * h)],
           fill=(235, 235, 225), width=3)
    d.arc([x + 0.10 * w, y + 0.38 * h, x + 0.22 * w, y + 0.56 * h],
          start=180, end=360, fill=(235, 235, 225), width=3)
    d.polygon([(x + 0.52 * w, y + 0.30 * h), (x + 0.66 * w, y + 0.36 * h),
               (x + 0.52 * w, y + 0.40 * h), (x + 0.47 * w, y + 0.36 * h)],
              fill=(200, 200, 190))
    for tx in (0.30, 0.36, 0.42):
        d.line([(x + tx * w, y + 0.36 * h), (x + (tx + 0.04) * w, y + 0.36 * h)],
               fill=GOLD_LIGHT, width=2)
    d.polygon([(x + 0.02 * w, y + 0.72 * h), (x + 0.30 * w, y + 0.72 * h),
               (x + 0.26 * w, y + 0.64 * h), (x + 0.08 * w, y + 0.66 * h)],
              fill=(18, 30, 54))
    caption_strip(d, x, y, w, "SHEIKH ISA BASE · QESHM ISLAND")
    banner_frame(d, x, y, w, h)


def scene_kerch(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(215, 226, 232))
    d.ellipse([x + 0.10 * w, y + 0.10 * h, x + 0.30 * w, y + 0.20 * h],
              fill=(245, 248, 250))
    d.ellipse([x + 0.62 * w, y + 0.06 * h, x + 0.84 * w, y + 0.16 * h],
              fill=(245, 248, 250))
    d.rectangle([x, y + 0.66 * h, x + w, y + h], fill=(111, 154, 168))
    for wy in (0.74, 0.84, 0.93):
        d.line([(x + 8, y + wy * h), (x + w - 8, y + wy * h)],
               fill=(200, 222, 228), width=1)
    deck_y = y + 0.52 * h
    d.rectangle([x + 0.03 * w, deck_y, x + 0.38 * w, deck_y + 7], fill=(52, 58, 64))
    d.rectangle([x + 0.62 * w, deck_y, x + 0.97 * w, deck_y + 7], fill=(52, 58, 64))
    d.polygon([(x + 0.42 * w, deck_y + 4), (x + 0.55 * w, deck_y + 4),
               (x + 0.52 * w, deck_y + 26), (x + 0.45 * w, deck_y + 26)],
              fill=(52, 58, 64))
    for ax in (0.06, 0.66):
        d.arc([x + ax * w, y + 0.30 * h, x + (ax + 0.28) * w, y + 0.62 * h],
              start=180, end=360, fill=(52, 58, 64), width=3)
    for sx, sy, sr in [(0.46, 0.36, 9), (0.52, 0.28, 12), (0.58, 0.36, 8)]:
        d.ellipse([x + sx * w - sr, y + sy * h - sr, x + sx * w + sr, y + sy * h + sr],
                  fill=(150, 150, 148))
    d.polygon([(x + 0.12 * w, y + 0.80 * h), (x + 0.22 * w, y + 0.80 * h),
               (x + 0.20 * w, y + 0.86 * h), (x + 0.14 * w, y + 0.86 * h)],
              fill=(40, 44, 48))
    d.line([(x + 0.17 * w, y + 0.80 * h), (x + 0.17 * w, y + 0.72 * h)],
           fill=(40, 44, 48), width=2)
    caption_strip(d, x, y, w, "KERCH STRAIT · 19 KM CROSSING")
    banner_frame(d, x, y, w, h)


def scene_manila(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(233, 217, 172))
    d.ellipse([x + 0.80 * w, y + 0.10 * h, x + 0.80 * w + 26, y + 0.10 * h + 26],
              fill=GOLD)
    base = y + h
    for bx, bw, bh in [(0.02, 0.16, 0.42), (0.20, 0.12, 0.55), (0.34, 0.18, 0.38),
                       (0.54, 0.12, 0.60), (0.68, 0.16, 0.44), (0.86, 0.12, 0.52)]:
        d.rectangle([x + bx * w, base - bh * h, x + (bx + bw) * w, base],
                    fill=NAVY)
        for wy in (0.62, 0.74, 0.86):
            for wx in (0.04, 0.09):
                d.rectangle([x + (bx + wx) * w, base - wy * bh * h,
                             x + (bx + wx) * w + 3, base - wy * bh * h + 4],
                            fill=(232, 196, 90))
    flags = [
        (0.10, [(201, 60, 60), (245, 245, 240), (201, 60, 60)]),
        (0.30, [(245, 245, 240)]),
        (0.52, [(255, 153, 51), (245, 245, 240), (19, 136, 8)]),
        (0.74, [(0, 0, 139)]),
    ]
    for fx, bands in flags:
        px = x + fx * w
        d.line([(px, y + 0.30 * h), (px, y + 0.72 * h)], fill=(60, 60, 56), width=2)
        fh = 18
        for i, col in enumerate(bands):
            d.rectangle([px, y + 0.30 * h + i * fh // len(bands),
                         px + 26, y + 0.30 * h + (i + 1) * fh // len(bands)],
                        fill=col)
        if len(bands) == 1 and bands[0] == (245, 245, 240):
            d.ellipse([px + 9, y + 0.30 * h + 5, px + 17, y + 0.30 * h + 13],
                      fill=(188, 0, 45))
        if bands[0] == (0, 0, 139):
            for sx, sy in [(6, 4), (18, 6), (12, 12)]:
                d.ellipse([px + sx, y + 0.30 * h + sy, px + sx + 2, y + 0.30 * h + sy + 2],
                          fill=(255, 255, 255))
    caption_strip(d, x, y, w, "MANILA · FIRST QUAD IN TWO YEARS")
    banner_frame(d, x, y, w, h)


SCENES = {"bahrain": scene_bahrain, "kerch": scene_kerch, "manila": scene_manila}

# ---------------------------------------------------------------- icons


def tile_box(d, x, y, bg):
    d.rounded_rectangle([x, y, x + 56, y + 56], radius=6, fill=bg,
                        outline=RULE, width=1)


def icon_chip(d, x, y):
    tile_box(d, x, y, (20, 83, 45))
    d.rectangle([x + 16, y + 16, x + 40, y + 40], outline=(255, 255, 255), width=2)
    for py in (22, 28, 34):
        d.line([(x + 8, y + py), (x + 16, y + py)], fill=(255, 255, 255), width=2)
        d.line([(x + 40, y + py), (x + 48, y + py)], fill=(255, 255, 255), width=2)


def icon_parliament(d, x, y):
    tile_box(d, x, y, (232, 224, 200))
    d.polygon([(x + 10, y + 22), (x + 46, y + 22), (x + 28, y + 10)],
              fill=(52, 58, 64))
    for cx in (14, 25, 36):
        d.rectangle([x + cx, y + 26, x + cx + 5, y + 44], fill=(52, 58, 64))
    d.rectangle([x + 10, y + 46, x + 46, y + 49], fill=(52, 58, 64))


def icon_euro(d, x, y):
    tile_box(d, x, y, (30, 58, 138))
    s = "€"
    tw = F_EURO.getlength(s)
    d.text((x + 28 - tw / 2, y + 12), s, font=F_EURO, fill=(255, 255, 255))


def icon_cyclone(d, x, y):
    tile_box(d, x, y, (15, 118, 110))
    for r in (8, 14, 20):
        d.arc([x + 28 - r, y + 28 - r, x + 28 + r, y + 28 + r],
              start=40, end=300, fill=(255, 255, 255), width=2)
    d.ellipse([x + 25, y + 25, x + 31, y + 31], fill=(255, 255, 255))


def icon_chart(d, x, y):
    tile_box(d, x, y, (127, 29, 29))
    pts = [(x + 10, y + 14), (x + 20, y + 22), (x + 30, y + 18),
           (x + 40, y + 34), (x + 48, y + 42)]
    d.line(pts, fill=(255, 255, 255), width=3)
    d.polygon([(x + 48, y + 42), (x + 40, y + 40), (x + 46, y + 34)],
              fill=(255, 255, 255))


def icon_globe(d, x, y):
    tile_box(d, x, y, (29, 78, 216))
    d.ellipse([x + 12, y + 12, x + 44, y + 44], outline=(255, 255, 255), width=2)
    d.ellipse([x + 22, y + 12, x + 34, y + 44], outline=(255, 255, 255), width=1)
    d.line([(x + 12, y + 28), (x + 44, y + 28)], fill=(255, 255, 255), width=1)


def icon_shield(d, x, y):
    tile_box(d, x, y, (127, 29, 29))
    d.polygon([(x + 16, y + 10), (x + 40, y + 10), (x + 40, y + 28),
               (x + 28, y + 46), (x + 16, y + 28)], outline=(255, 255, 255), width=2)
    d.line([(x + 16, y + 12), (x + 40, y + 44)], fill=(255, 255, 255), width=2)


def icon_ship(d, x, y):
    tile_box(d, x, y, (51, 65, 85))
    d.rectangle([x + 14, y + 14, x + 26, y + 24], fill=(201, 60, 60))
    d.rectangle([x + 28, y + 18, x + 40, y + 24], fill=(232, 196, 90))
    d.polygon([(x + 10, y + 26), (x + 46, y + 26), (x + 40, y + 40),
               (x + 16, y + 40)], fill=(255, 255, 255))
    d.line([(x + 8, y + 44), (x + 48, y + 44)], fill=(190, 220, 210), width=2)


def icon_plane(d, x, y):
    tile_box(d, x, y, (71, 85, 105))
    d.polygon([(x + 8, y + 30), (x + 30, y + 24), (x + 48, y + 24),
               (x + 44, y + 30), (x + 30, y + 32), (x + 28, y + 38),
               (x + 22, y + 32), (x + 10, y + 34)], fill=(255, 255, 255))


def icon_cricket(d, x, y):
    tile_box(d, x, y, (22, 101, 52))
    d.polygon([(x + 18, y + 12), (x + 24, y + 12), (x + 34, y + 40),
               (x + 28, y + 42)], fill=(255, 255, 255))
    d.ellipse([x + 38, y + 38, x + 46, y + 46], fill=(232, 196, 90))


def icon_jet(d, x, y):
    tile_box(d, x, y, (3, 105, 161))
    d.polygon([(x + 10, y + 30), (x + 34, y + 20), (x + 48, y + 24),
               (x + 36, y + 30), (x + 30, y + 36), (x + 16, y + 34)],
              fill=(255, 255, 255))
    for tx in (0.06, 0.14, 0.22):
        d.line([(x + tx * 56, y + 34), (x + (tx + 0.05) * 56, y + 34)],
               fill=(255, 255, 255), width=1)


def icon_solar(d, x, y):
    tile_box(d, x, y, (180, 83, 9))
    d.polygon([(x + 12, y + 30), (x + 34, y + 18), (x + 46, y + 28),
               (x + 24, y + 42)], fill=(38, 54, 88))
    d.line([(x + 20, y + 24), (x + 36, y + 34)], fill=(232, 196, 90), width=1)
    d.line([(x + 28, y + 20), (x + 20, y + 36)], fill=(232, 196, 90), width=1)
    d.ellipse([x + 38, y + 10, x + 48, y + 20], fill=(255, 220, 120))


ICONS = {"chip": icon_chip, "parliament": icon_parliament, "euro": icon_euro,
         "cyclone": icon_cyclone, "chart": icon_chart, "globe": icon_globe,
         "shield": icon_shield, "ship": icon_ship, "plane": icon_plane,
         "cricket": icon_cricket, "jet": icon_jet, "solar": icon_solar}

# ---------------------------------------------------------------- map

MAP_W, MAP_H = 302, 132
LAND = [
    [(14, 42), (34, 30), (62, 26), (84, 34), (92, 48), (84, 62),
     (70, 72), (58, 86), (48, 98), (36, 92), (24, 78), (14, 60)],
    [(66, 100), (84, 96), (96, 106), (90, 122), (78, 128), (68, 122), (62, 110)],
    [(150, 66), (172, 58), (192, 66), (198, 86), (190, 108),
     (172, 122), (156, 106), (148, 84)],
    [(148, 44), (166, 34), (184, 38), (190, 50), (176, 58), (158, 56), (146, 50)],
    [(192, 34), (232, 26), (272, 32), (294, 44), (286, 62), (266, 74),
     (246, 70), (232, 84), (216, 74), (200, 62), (194, 48)],
    [(258, 112), (280, 106), (292, 116), (278, 128), (260, 124)],
]
PINS = {
    1: (202, 76), 2: (182, 48), 3: (262, 84), 4: (24, 58), 5: (184, 66),
    6: (156, 48), 7: (242, 84), 8: (44, 52), 9: (252, 74), 10: (142, 36),
    11: (258, 52), 12: (244, 34), 13: (232, 92), 14: (276, 62), 15: (226, 68),
}


def draw_map(d, x, y):
    mask = Image.new("L", (MAP_W, MAP_H), 0)
    md = ImageDraw.Draw(mask)
    for poly in LAND:
        md.polygon(poly, fill=255)
    d.rectangle([x, y, x + MAP_W, y + MAP_H], fill=(226, 236, 232),
                outline=RULE, width=1)
    px = mask.load()
    step = 4
    for gy in range(2, MAP_H - 1, step):
        for gx in range(2, MAP_W - 1, step):
            if px[gx, gy]:
                d.ellipse([x + gx - 1, y + gy - 1, x + gx + 1, y + gy + 1],
                          fill=(96, 130, 110))
    for n, (px_, py_) in PINS.items():
        cx, cy = x + px_, y + py_
        d.ellipse([cx - 7, cy - 7, cx + 7, cy + 7], fill=RED,
                  outline=(255, 255, 255), width=1)
        s = str(n)
        tw = F_PIN.getlength(s)
        d.text((cx - tw / 2, cy - 5), s, font=F_PIN, fill=(255, 255, 255))


# ---------------------------------------------------------------- page


def draw_masthead(d):
    d.rectangle([0, 0, W, 108], fill=NAVY)
    d.text((MARGIN, 14), "THE DAY IN WORLD NEWS", font=F_KICK, fill=GOLD_LIGHT)
    right = "40 STORIES · 6 CONTINENTS · ONE PAGE"
    d.text((W - MARGIN - F_KICK.getlength(right), 14), right, font=F_KICK,
           fill=GOLD_LIGHT)
    d.text((MARGIN, 36), "Wednesday 18 November 2026", font=F_TITLE,
           fill=(255, 255, 255))
    d.text((MARGIN, 90),
           "Every story on this page happened, or was first reported, on this day.",
           font=F_SUB, fill=(207, 212, 222))
    d.rectangle([0, 108, W, 112], fill=GOLD)


def draw_heroes(d):
    for i, st in enumerate(HEROES):
        x = col_x(i)
        SCENES[st["scene"]](d, x, 122, COL_W, 140)
        num_disc(d, x + 12, 282, 12, st["n"])
        d.text((x + 30, 276), st["kick"], font=F_KICK_SM, fill=RED)
        y = para(d, x, 296, st["head"], F_HEAD, COL_W, INK, 27)
        para(d, x, y + 6, st["body"], F_BODY, COL_W, (58, 58, 52), 17)


def draw_mids(d):
    for row in range(4):
        y0 = 446 + row * 80
        for col in range(3):
            st = MIDS[row * 3 + col]
            x = col_x(col)
            ICONS[st["icon"]](d, x, y0)
            tx = x + 66
            num_disc(d, tx + 8, y0 + 8, 8, st["n"])
            d.text((tx + 20, y0 + 2), st["kick"], font=F_KICK_SM, fill=RED)
            y1 = para(d, tx, y0 + 18, st["head"], F_HEAD_SM, COL_W - 66, INK, 17)
            para(d, tx, y1 + 2, st["body"], F_BODY_SM, COL_W - 66,
                 (58, 58, 52), 13)


def draw_numbers(d):
    d.text((MARGIN, 772), "BY THE NUMBERS", font=F_LABEL, fill=RED)
    cell_w = CONTENT_W // 4
    for i, (val, cap) in enumerate(NUMBERS):
        x = MARGIN + i * cell_w
        if i:
            d.line([(x - 8, 788), (x - 8, 816)], fill=(180, 175, 160), width=1)
        d.text((x, 786), val, font=F_NUM_BIG, fill=NAVY)
        d.text((x, 812), cap, font=F_NUM_CAP, fill=MUTED)


def draw_bottom(d):
    d.text((MARGIN, 834), "WHERE THE NEWS HAPPENED", font=F_LABEL, fill=INK)
    d.text((346, 834), "ALSO ON WEDNESDAY 18 NOVEMBER — 25 MORE STORIES",
           font=F_LABEL, fill=INK)
    hrule(d, 848, color=RULE, width=1, x0=MARGIN, x1=330)
    hrule(d, 848, color=RULE, width=1, x0=346, x1=W - MARGIN)
    draw_map(d, MARGIN, 856)
    cap = "Numbered dots mark stories 1–15."
    d.rectangle([MARGIN + 4, 856 + MAP_H - 17, MARGIN + 10 + F_FOOT.getlength(cap),
                 856 + MAP_H - 3], fill=PAPER)
    d.text((MARGIN + 7, 856 + MAP_H - 15), cap, font=F_FOOT, fill=MUTED)
    col1 = ALSO[:13]
    col2 = ALSO[13:]
    for ci, items in enumerate((col1, col2)):
        lx = 346 + ci * 332
        y = 856
        for n, title, detail in items:
            d.text((lx, y), str(n) + ".", font=F_ALSO_B, fill=RED)
            nx = lx + F_ALSO_B.getlength(str(n) + ". ")
            d.text((nx, y), title, font=F_ALSO_B, fill=INK)
            tx = nx + F_ALSO_B.getlength(title)
            d.text((tx, y), " — " + detail, font=F_ALSO, fill=(58, 58, 52))
            y += 10
        _ = y


def draw_footer(d):
    d.text((MARGIN, 992),
           "All stories happened or were first reported on Wednesday 18 November 2026. "
           "Disputed claims are attributed.",
           font=F_FOOT, fill=MUTED)
    d.text((MARGIN, 1005),
           "Sources: Reuters, AP, AFP, BBC, Al Jazeera, CNN, IMD, UN, ICC. "
           "Original drawings.",
           font=F_FOOT, fill=MUTED)


def build_page():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    draw_masthead(d)
    draw_heroes(d)
    hrule(d, 418, color=RULE, width=2)
    d.text((MARGIN, 426), "MORE OF THE DAY — STORIES 4–15", font=F_LABEL, fill=INK)
    draw_mids(d)
    draw_numbers(d)
    hrule(d, 826, color=RULE, width=1)
    draw_bottom(d)
    draw_footer(d)
    return img


def main():
    here = Path(__file__).resolve().parent
    img = build_page()
    for target in (here / "entry.png", Path("/output/entry.png")):
        target.parent.mkdir(parents=True, exist_ok=True)
        img.save(target, format="PNG")
        data = target.read_bytes()
        print("wrote", target, len(data), "bytes",
              "sha256", hashlib.sha256(data).hexdigest())


if __name__ == "__main__":
    main()
