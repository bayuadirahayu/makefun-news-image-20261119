#!/usr/bin/env python3
"""THE WORLD IN ONE DAY - Thursday 19 November 2026.

Draws a dense newspaper front page summing up one day of world news:
masthead, day-in-figures strip, world map with hotspots, three illustrated
lead stories, and 33 further stories in three columns.

Pure Python 3 standard library. Deterministic: the same input always
produces the same bytes. Writes entry.png (1024x1024) into
$MAKEFUN_OUTPUT_DIR (default "out").
"""

import os
import struct
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- palette
PAPER = (247, 243, 232)
INK = (26, 26, 26)
NAVY = (16, 41, 75)
NAVY_LT = (32, 68, 110)
RED = (176, 42, 48)
GOLD = (200, 162, 74)
BLUE = (43, 95, 138)
OCEAN = (207, 224, 234)
LAND = (232, 226, 200)
LAND_EDGE = (170, 162, 128)
GREY = (110, 108, 100)
RULE = (190, 184, 168)
WHITE = (255, 255, 255)
CREAM = (250, 246, 236)

# ------------------------------------------------------- 5x7 bitmap font
# Every glyph is 7 rows of 5 cells; '#' is ink, '.' is blank.
FONT = {
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
    'W': ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
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
    '%': ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    '$': ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    '&': ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    '+': ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    '=': ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    '*': ("00000", "10101", "01110", "11111", "01110", "10101", "00000"),
    '#': ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
    'X': ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
}


def char_advance(scale):
    return 6 * scale


def text_width(text, scale):
    return len(text) * char_advance(scale) - scale


def wrap_text(text, max_width, scale):
    """Greedy word wrap; returns a list of lines that fit max_width px."""
    adv = char_advance(scale)
    max_chars = max(1, (max_width + scale) // adv)
    words = text.split(" ")
    lines, cur = [], ""
    for word in words:
        while len(word) > max_chars:  # over-long word: hard split it
            lines.append(word[:max_chars])
            word = word[max_chars:]
        trial = word if not cur else cur + " " + word
        if len(trial) <= max_chars:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


# ------------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.buf = bytearray(w * h * 3)
        self.fill_rect(0, 0, w, h, bg)

    def px(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.buf[i], self.buf[i + 1], self.buf[i + 2] = color

    def fill_rect(self, x, y, w, h, color):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                i = base + (xx - x0) * 3
                self.buf[i], self.buf[i + 1], self.buf[i + 2] = color

    def hline(self, x, y, w, color):
        self.fill_rect(x, y, w, 1, color)

    def vline(self, x, y, h, color):
        self.fill_rect(x, y, 1, h, color)

    def line(self, x0, y0, x1, y1, color):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        while True:
            self.px(x0, y0, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r, color):
        for dy in range(-r, r + 1):
            half = int((r * r - dy * dy) ** 0.5)
            for dx in range(-half, half + 1):
                self.px(cx + dx, cy + dy, color)

    def ring(self, cx, cy, r, color):
        for a in range(0, 360, 2):
            import math
            rad = math.radians(a)
            self.px(cx + int(r * math.cos(rad)), cy + int(r * math.sin(rad)), color)

    def poly_fill(self, pts, color):
        """Even-odd scanline fill of a polygon given as (x, y) points."""
        if len(pts) < 3:
            return
        ys = [p[1] for p in pts]
        for y in range(min(ys), max(ys) + 1):
            xs = []
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
            xs.sort()
            for k in range(0, len(xs) - 1, 2):
                xa, xb = int(xs[k]), int(xs[k + 1])
                for x in range(xa, xb + 1):
                    self.px(x, y, color)

    def draw_text(self, x, y, text, scale, color, bold=False):
        """Draw upper-case text; returns the x just past the last glyph."""
        text = text.upper()
        cx = x
        for ch in text:
            glyph = FONT.get(ch, FONT[' '])
            for gy, row in enumerate(glyph):
                for gx, cell in enumerate(row):
                    if cell == '1':
                        for sy in range(scale):
                            for sx in range(scale):
                                self.px(cx + gx * scale + sx, y + gy * scale + sy, color)
                                if bold:
                                    self.px(cx + gx * scale + sx + 1, y + gy * scale + sy, color)
            cx += char_advance(scale)
        return cx

    def draw_lines(self, x, y, lines, scale, color, pitch, bold=False):
        for ln in lines:
            self.draw_text(x, y, ln, scale, color, bold=bold)
            y += pitch
        return y


# ---------------------------------------------------------------- PNG writer
def write_png(path, canvas):
    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        return out + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    raw = bytearray()
    row_len = canvas.w * 3
    for y in range(canvas.h):
        raw.append(0)  # filter: none
        raw += canvas.buf[y * row_len:(y + 1) * row_len]
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", canvas.w, canvas.h, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)
    return len(png)

# ------------------------------------------------------------- story data
# 36 stories, all verified as happening or first reported on
# Thursday 19 November 2026. Headlines and decks are upper-case by
# design; the renderer upper-cases everything it draws.

LEADS = [
    {
        "kicker": "SHENZHEN - THE SUMMIT",
        "head": "TRUMP, XI AND PUTIN MEET IN SHENZHEN",
        "deck": "FIRST THREE-WAY SUMMIT OF THE NUCLEAR POWERS",
        "art": "summit",
    },
    {
        "kicker": "THE HAGUE - JUSTICE",
        "head": "WORLD COURT: MYANMAR COMMITTED GENOCIDE",
        "deck": "ICJ RULES 9-6 THAT THE 2017 CAMPAIGN WAS GENOCIDE",
        "art": "court",
    },
    {
        "kicker": "NEW YORK - MARKETS",
        "head": "ANTHROPIC'S $81.3BN IPO, LARGEST EVER",
        "deck": "ANT DEBUTS ON THE NASDAQ AT ABOUT $1.5 TRILLION",
        "art": "ipo",
    },
]

# (headline, deck) - 33 further stories, grouped by section in reading order.
GRID = [
    ("UKRAINE HITS CRIMEA BRIDGE A THIRD TIME",
     "ROAD TRAFFIC HALTED AGAIN"),
    ("IRAN STRIKES GULF STATES AFTER US ATTACK",
     "MISSILES FOLLOW US STRIKES"),
    ("ISRAEL PUSHES INTO CENTRAL GAZA",
     "BEYOND THE YELLOW LINE"),
    ("EU PLANS 45BN EURO LOAN FOR UKRAINE",
     "ALLIES MEET IN BERLIN"),
    ("NORTH KOREA EXPANDS URANIUM ENRICHMENT",
     "NEW WORK AT YONGBYON"),
    ("ETHIOPIA AND ERITREA MASS TROOPS",
     "FORCES BUILD ON THE BORDER"),
    ("SUDAN DRONES DRIVE CIVILIAN TOLL",
     "AID REACHES THE DISPLACED"),
    ("BANGLADESH IN TURMOIL OVER HASINA",
     "VIOLENCE HITS 28 DISTRICTS"),
    ("US AND VENEZUELA RESTORE MILITARY TIES",
     "COOPERATION DEAL SIGNED"),
    ("DEMOCRATS WIN ALASKA, TAKE SENATE 56-44",
     "DEMOCRATS TAKE 56 SEATS"),
    ("PASTOR GUILTY OVER HAITI PRESIDENT MURDER",
     "CONVICTED IN MOISE CASE"),
    ("ISRAEL DELAYS E1 SETTLEMENT PLAN",
     "KILLING NEAR JERICHO"),
    ("FIVE EU STATES TO SEND ASYLUM SEEKERS TO RWANDA",
     "SHARP TURN IN EU POLICY"),
    ("IMAMOGLU JAILED IN TURKISH CHP CASE",
     "EIGHT OTHERS JAILED TOO"),
    ("ISOLATED AWA GROUP MAKES RARE CONTACT",
     "UNCONTACTED PEOPLE EMERGE"),
    ("MILEI BILL TO AXE PRIMARIES ADVANCES",
     "REFORM CLEARS A KEY VOTE"),
    ("INDONESIA PASSES ASSET SEIZURE LAW",
     "SEIZURE WITHOUT CONVICTION"),
    ("ONE DEAD IN INDONESIA REFINERY BLAST",
     "BLAST AT CEPU PLANT"),
    ("IMF UNLOCKS $2.3BN FOR EGYPT",
     "DEAL REACHED WITH CAIRO"),
    ("EU APPROVES TRADE DEAL WITH INDONESIA",
     "PACT WITH SOUTHEAST ASIA"),
    ("AUSTRALIA JOBLESS RATE RISES TO 4.9%",
     "HIGHEST SINCE 2021"),
    ("SENSEX JUMPS 989 POINTS TO 83,021",
     "AUTOS LEAD INDIAN RALLY"),
    ("EQUINOR CYBERATTACK STILL UNDER WAY",
     "OUTPUT UNAFFECTED SO FAR"),
    ("HACKERS HIT 4,000 RETIRED NYC WORKERS",
     "DATA STOLEN FROM DATABASE"),
    ("WAYMO PULLS ROBOTAXIS OFF FREEWAYS",
     "DRIVERLESS CARS WITHDRAWN"),
    ("COP31 TALKS DEADLOCKED IN ANTALYA",
     "MINISTERS RACE FOR A DEAL"),
    ("US LOSES MEASLES-FREE STATUS",
     "26 YEARS OF PROGRESS ENDS"),
    ("EBOLA VACCINES TO BE TRIALLED IN CONGO",
     "JABS HEADED FOR EAST CONGO"),
    ("FIJI AND TONGA DECLARE DROUGHT EMERGENCY",
     "EL NINO DRIES THE PACIFIC"),
    ("BLUE WHALES UP TENFOLD SINCE WHALING",
     "ANTARCTIC RECOVERY SURVEY"),
    ("VOYAGER 1 REACHES ONE LIGHT-DAY",
     "ONE LIGHT-DAY FROM EARTH"),
    ("ALCARAZ BEATS MEDVEDEV AT ATP FINALS",
     "SPANISH STAR WINS IN TURIN"),
    ("GTA VI GOES ON SALE AFTER 13 YEARS",
     "ROCKSTAR GAME HITS SHELVES"),
]

FIGURES = [
    ("$81.3BN", "LARGEST IPO EVER"),
    ("9-6", "MYANMAR GENOCIDE"),
    ("$3,725", "GOLD, DOWN 3.2%"),
    ("4.9%", "JOBLESS SINCE 2021"),
]

# ------------------------------------------------------------- world map
# Simplified continent outlines as (lon, lat) points, equirectangular.
CONTINENTS = [
    [(-168, 66), (-140, 70), (-120, 71), (-95, 80), (-80, 73), (-65, 60),
     (-55, 47), (-70, 42), (-80, 32), (-97, 26), (-105, 20), (-95, 16),
     (-83, 9), (-79, 9), (-90, 14), (-105, 20), (-117, 32), (-125, 40),
     (-125, 49), (-145, 60), (-168, 66)],
    [(-55, 60), (-40, 60), (-30, 68), (-22, 70), (-30, 76), (-58, 76),
     (-68, 70), (-55, 60)],
    [(-79, 9), (-77, 4), (-80, -3), (-81, -6), (-70, -18), (-70, -30),
     (-72, -40), (-73, -50), (-65, -55), (-68, -52), (-57, -38), (-48, -28),
     (-40, -20), (-35, -8), (-43, -3), (-52, 4), (-60, 8), (-70, 11),
     (-79, 9)],
    [(-17, 15), (-10, 30), (0, 36), (10, 37), (20, 32), (30, 31), (35, 28),
     (43, 12), (51, 11), (48, 0), (40, -10), (35, -18), (32, -26), (20, -35),
     (15, -30), (12, -18), (9, 4), (-8, 5), (-17, 15)],
    [(-10, 36), (-9, 43), (-2, 48), (0, 50), (5, 53), (8, 57), (10, 59),
     (18, 56), (21, 55), (24, 58), (30, 62), (40, 68), (55, 69), (70, 72),
     (90, 75), (110, 76), (130, 72), (150, 70), (170, 67), (178, 65),
     (170, 60), (162, 56), (158, 52), (142, 50), (140, 40), (130, 35),
     (127, 33), (122, 30), (120, 22), (110, 20), (105, 10), (100, 8),
     (98, 12), (92, 16), (89, 22), (85, 19), (80, 15), (76, 10), (72, 20),
     (66, 25), (60, 25), (57, 26), (52, 28), (48, 30), (43, 29), (39, 21),
     (35, 18), (33, 15), (30, 31), (25, 36), (20, 40), (15, 44), (10, 44),
     (5, 43), (0, 44), (-2, 48), (-10, 36)],
    [(113, -22), (114, -30), (115, -35), (124, -33), (130, -32), (137, -35),
     (140, -38), (146, -39), (150, -37), (153, -32), (153, -27), (146, -19),
     (142, -11), (136, -12), (132, -12), (126, -14), (122, -17), (113, -22)],
    [(95, 5), (100, 0), (104, -3), (106, -6), (100, -6), (95, 5)],
    [(109, 1), (113, 4), (117, 6), (119, 1), (117, -3), (112, -3), (109, 1)],
    [(131, -1), (136, -2), (141, -3), (146, -6), (150, -8), (147, -9),
     (141, -8), (136, -6), (131, -1)],
    [(130, 31), (132, 33), (135, 34), (137, 35), (140, 36), (141, 39),
     (141, 42), (143, 44), (140, 40), (138, 37), (135, 34), (132, 33),
     (130, 31)],
    [(-5, 50), (-3, 53), (-5, 56), (-2, 58), (-1, 57), (0, 53), (1, 51),
     (-3, 50), (-5, 50)],
    [(167, -45), (170, -43), (174, -41), (176, -38), (178, -37), (175, -40),
     (172, -43), (168, -46), (167, -45)],
]

# Hotspots: (lon, lat, label) for the day's biggest stories.
HOTSPOTS = [
    (114, 22, "SHENZHEN"), (4, 52, "THE HAGUE"), (-74, 41, "NEW YORK"),
    (34, 45, "CRIMEA"), (35, 32, "GAZA"), (56, 27, "GULF"),
    (90, 24, "DHAKA"), (107, -7, "JAKARTA"), (149, -35, "CANBERRA"),
    (0, 51, "LONDON"), (7, 45, "TURIN"), (127, 37, "SEOUL"),
]


def draw_map(cv, x, y, w, h):
    cv.fill_rect(x, y, w, h, OCEAN)
    # graticule
    for gx in range(x + 60, x + w, 120):
        cv.vline(gx, y, h, (190, 208, 220))
    for gy in range(y + 24, y + h, 24):
        cv.hline(x, gy, w, (190, 208, 220))
    lat_top, lat_bot = 84.0, -60.0

    def proj(lon, lat):
        px = x + (lon + 180.0) / 360.0 * w
        py = y + (lat_top - lat) / (lat_top - lat_bot) * h
        return (int(px), int(py))

    for poly in CONTINENTS:
        cv.poly_fill([proj(lon, lat) for lon, lat in poly], LAND)
        pts = [proj(lon, lat) for lon, lat in poly]
        for i in range(len(pts)):
            cv.line(pts[i][0], pts[i][1], pts[(i + 1) % len(pts)][0],
                    pts[(i + 1) % len(pts)][1], LAND_EDGE)
    for lon, lat, _label in HOTSPOTS:
        cx, cy = proj(lon, lat)
        cv.circle(cx, cy, 6, WHITE)
        cv.circle(cx, cy, 4, RED)


# -------------------------------------------------------- lead illustrations
def draw_summit(cv, x, y, w, h):
    cv.fill_rect(x, y, w, h, (214, 228, 238))
    # three flags on poles: US, China, Russia (simplified)
    pole_x = [x + w // 4 - 20, x + w // 2 - 20, x + 3 * w // 4 - 20]
    cv.fill_rect(pole_x[0], y + 6, 40, 26, (60, 90, 150))      # US blue field
    cv.fill_rect(pole_x[0] + 14, y + 6, 26, 26, (178, 52, 62))  # US stripes hint
    cv.fill_rect(pole_x[1], y + 6, 40, 26, (200, 40, 40))       # China red
    cv.circle(pole_x[1] + 10, y + 14, 3, GOLD)
    cv.circle(pole_x[1] + 20, y + 11, 2, GOLD)
    cv.fill_rect(pole_x[2], y + 6, 40, 26, WHITE)               # Russia tricolour
    cv.fill_rect(pole_x[2], y + 6, 40, 9, (200, 40, 40))
    cv.fill_rect(pole_x[2], y + 23, 40, 9, (40, 80, 160))
    for px0 in pole_x:
        cv.vline(px0 - 2, y + 6, 40, INK)
    # round table with three seats
    cv.fill_rect(x + 18, y + 52, w - 36, 6, (120, 84, 50))
    cv.fill_rect(x + 30, y + 58, 6, 12, (120, 84, 50))
    cv.fill_rect(x + w - 36, y + 58, 6, 12, (120, 84, 50))
    cv.hline(x, y + h - 1, w, RULE)


def draw_court(cv, x, y, w, h):
    cv.fill_rect(x, y, w, h, (226, 220, 205))
    cx = x + w // 2
    cv.vline(cx, y + 8, 44, INK)
    cv.hline(cx - 26, y + 14, 52, INK)
    cv.circle(cx, y + 8, 3, GOLD)
    # left pan
    cv.line(cx - 26, y + 14, cx - 38, y + 32, INK)
    cv.line(cx - 26, y + 14, cx - 14, y + 32, INK)
    cv.hline(cx - 40, y + 32, 26, INK)
    # right pan
    cv.line(cx + 26, y + 14, cx + 14, y + 32, INK)
    cv.line(cx + 26, y + 14, cx + 38, y + 32, INK)
    cv.hline(cx + 14, y + 32, 26, INK)
    # plinth
    cv.fill_rect(cx - 30, y + 54, 60, 5, INK)
    cv.fill_rect(cx - 22, y + 59, 44, 5, (120, 110, 90))
    cv.hline(x, y + h - 1, w, RULE)


def draw_ipo(cv, x, y, w, h):
    cv.fill_rect(x, y, w, h, (214, 232, 220))
    base = y + h - 14
    bars = [12, 18, 16, 26, 34, 46]
    bw = 26
    for i, bh in enumerate(bars):
        bx = x + 16 + i * (bw + 6)
        cv.fill_rect(bx, base - bh, bw, bh, BLUE if i < 5 else RED)
    # rising arrow
    cv.line(x + 14, base - 48, x + w - 16, y + 10, RED)
    cv.line(x + w - 16, y + 10, x + w - 28, y + 12, RED)
    cv.line(x + w - 16, y + 10, x + w - 18, y + 22, RED)
    cv.hline(x, y + h - 1, w, RULE)


ART = {"summit": draw_summit, "court": draw_court, "ipo": draw_ipo}

# ------------------------------------------------------------------- layout
MARGIN = 20
COL_GAP = 14


def build():
    cv = Canvas(W, H, PAPER)

    # --- masthead: navy band, title + date
    cv.fill_rect(0, 0, W, 70, NAVY)
    cv.fill_rect(0, 70, W, 3, GOLD)
    title = "THE WORLD IN ONE DAY"
    tw = text_width(title, 4)
    cv.draw_text((W - tw) // 2, 8, title, 4, WHITE, bold=True)
    date = "THURSDAY 19 NOVEMBER 2026"
    dw = text_width(date, 2)
    cv.draw_text((W - dw) // 2, 46, date, 2, GOLD, bold=True)
    left = "ONE DAY - ONE PAGE"
    cv.draw_text(MARGIN, 48, left, 2, (200, 210, 225))
    right = "36 STORIES - 6 CONTINENTS"
    rw = text_width(right, 2)
    cv.draw_text(W - MARGIN - rw, 48, right, 2, (200, 210, 225))

    # --- day in figures strip
    fy, fh = 73, 43
    cell_w = (W - 2 * MARGIN - 3 * 10) // 4
    for i, (num, label) in enumerate(FIGURES):
        cx0 = MARGIN + i * (cell_w + 10)
        cv.fill_rect(cx0, fy, cell_w, fh, CREAM)
        cv.fill_rect(cx0, fy, cell_w, 2, RED)
        cv.draw_text(cx0 + 8, fy + 4, num, 3, NAVY, bold=True)
        lab_lines = wrap_text(label, cell_w - 16, 2)
        cv.draw_lines(cx0 + 8, fy + 28, lab_lines[:1], 2, GREY, 15)

    # --- world map
    my, mh = 116, 116
    cv.draw_text(MARGIN, my + 2, "WHERE THE DAY HAPPENED", 2, NAVY, bold=True)
    cv.draw_text(W - MARGIN - text_width("RED DOTS: THE DAY'S HOTSPOTS", 2),
                 my + 2, "RED DOTS: THE DAY'S HOTSPOTS", 2, GREY)
    draw_map(cv, MARGIN, my + 18, W - 2 * MARGIN, mh - 18)

    # --- three illustrated leads
    ly, lh = 232, 168
    col_w = (W - 2 * MARGIN - 2 * COL_GAP) // 3
    for i, lead in enumerate(LEADS):
        x0 = MARGIN + i * (col_w + COL_GAP)
        ART[lead["art"]](cv, x0, ly, col_w, 72)
        yy = ly + 78
        cv.draw_text(x0, yy, lead["kicker"], 2, RED, bold=True)
        yy += 16
        head_lines = wrap_text(lead["head"], col_w, 2)
        yy = cv.draw_lines(x0, yy, head_lines[:2], 2, INK, 15, bold=True)
        yy += 3  # at least 3 clear pixels between headline and deck
        deck_lines = wrap_text(lead["deck"], col_w, 2)
        cv.draw_lines(x0, yy, deck_lines[:3], 2, (60, 58, 52), 15)
        if i < 2:
            cv.vline(x0 + col_w + COL_GAP // 2, ly, lh, RULE)

    # --- section divider
    dy = 400
    cv.hline(MARGIN, dy, W - 2 * MARGIN, INK)
    cv.draw_text(MARGIN, dy + 5,
                 "WORLD - POLITICS - ECONOMY - TECH - CLIMATE - SCIENCE - SPORT - CULTURE",
                 2, NAVY, bold=True)
    cv.hline(MARGIN, dy + 20, W - 2 * MARGIN, RULE)

    # --- grid: 33 stories, 3 columns x 11 rows
    gy = 424
    rows = 11
    cell_h = (1000 - gy) // rows
    per_col = 11
    for idx, (head, deck) in enumerate(GRID):
        col = idx // per_col
        row = idx % per_col
        x0 = MARGIN + col * (col_w + COL_GAP)
        y0 = gy + row * cell_h
        head_lines = wrap_text(head, col_w, 2)[:2]
        # line budget: headline + deck together take at most 3 lines
        deck_budget = max(1, 3 - len(head_lines))
        deck_lines = wrap_text(deck, col_w, 2)[:deck_budget]
        yy = cv.draw_lines(x0, y0, head_lines, 2, INK, 15, bold=True)
        yy += 3  # at least 3 clear pixels between headline and deck
        cv.draw_lines(x0, yy, deck_lines, 2, (60, 58, 52), 15)
        if row < rows - 1:
            cv.hline(x0, y0 + cell_h - 6, col_w, (225, 220, 205))
        if col < 2:
            cv.vline(x0 + col_w + COL_GAP // 2, gy, 1000 - gy, (225, 220, 205))

    # --- footer
    cv.hline(0, 1000, W, INK)
    cv.fill_rect(0, 1001, W, 23, NAVY)
    foot = "SOURCES: REUTERS, BBC, CBS, THE GUARDIAN, AL JAZEERA - 19 NOV 2026"
    fw = text_width(foot, 2)
    cv.draw_text((W - fw) // 2, 1008, foot, 2, (210, 218, 230))
    return cv


def main():
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "out")
    os.makedirs(outdir, exist_ok=True)
    cv = build()
    path = os.path.join(outdir, "entry.png")
    size = write_png(path, cv)
    print(f"wrote {path} ({size} bytes)")


if __name__ == "__main__":
    main()
