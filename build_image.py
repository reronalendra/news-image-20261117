"""Draw the 17 November 2026 world-news infographic (1024x1024 PNG).

All artwork is original vector-style drawing with Pillow primitives:
no photos, no copied images. Stories were verified against reporting
dated 17 November 2026 (see SOURCES in the footer of the image).

Revision: facts, layout and code fixes from the Argon review (round 1).
- Card 6 tag corrected to UK / WEST BANK (sanctions are about West Bank
  settlements, not Gaza); card 4 headline softened to talks at APEC.
- Body text is bounded by the remaining vertical space inside each card;
  anything that does not fit raises an error instead of being cut silently.
- The output path is derived from this file's location and fonts are
  searched in several well-known locations instead of one absolute path.

Revision (round 2): icon artwork rescaled to fit inside the 88 px icon
discs (round 1 shrank the discs but kept the old icon coordinates, so
bridge/tanker/gavel/aid artwork poked through the circle outlines).
fit_lines() now also validates pixel width, and the SOURCE divider/text
are centred in the card footer.
"""
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
OUT = Path(__file__).resolve().parent / "entry.png"

NAVY = (15, 42, 68)
NAVY2 = (23, 63, 99)
PAPER = (248, 246, 238)
INK = (24, 28, 34)
MUTED = (90, 96, 104)
RED = (178, 34, 34)
GOLD = (201, 162, 39)
WHITE = (255, 255, 255)
SOURCES_COL = (185, 205, 225)

# Font candidates, in order. DejaVu ships with most Linux distros; the
# macOS / Windows entries are fallbacks for other machines. If none is
# found we fail with a clear message instead of crashing deep in Pillow.
FONT_CANDIDATES_BOLD = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf",
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "/Library/Fonts/Arial Bold.ttf",
    "C:/Windows/Fonts/arialbd.ttf",
]
FONT_CANDIDATES_REGULAR = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/TTF/DejaVuSans.ttf",
    "/System/Library/Fonts/Supplemental/Arial.ttf",
    "/Library/Fonts/Arial.ttf",
    "C:/Windows/Fonts/arial.ttf",
]


def find_font(bold):
    candidates = FONT_CANDIDATES_BOLD if bold else FONT_CANDIDATES_REGULAR
    for path in candidates:
        if Path(path).exists():
            return path
    raise RuntimeError(
        "No usable font found. Searched: " + ", ".join(candidates)
        + ". Install DejaVu Sans or place a TTF font in one of these paths."
    )


FB = find_font(bold=True)
FR = find_font(bold=False)


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, width):
    """Wrap text by pixel width. One word per line at minimum; a single
    word wider than `width` is kept whole (callers validate the result)."""
    lines = []
    for para in text.split("\n"):
        words = para.split()
        if not words:
            lines.append("")
            continue
        cur = ""
        for w in words:
            trial = (cur + " " + w).strip()
            if draw.textlength(trial, font=fnt) <= width:
                cur = trial
            else:
                if cur:
                    lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)
    return lines


def fit_lines(lines, max_lines, what, draw=None, fnt=None, width=None):
    """Fail loudly instead of silently dropping text that does not fit.

    When draw/fnt/width are given, also fail if any single line (or a
    single word kept whole by wrap()) is wider than `width` pixels.
    """
    if len(lines) > max_lines:
        raise ValueError(
            f"{what}: {len(lines)} lines do not fit in {max_lines} allowed "
            f"lines: {' / '.join(lines)}"
        )
    if draw is not None and fnt is not None and width is not None:
        for line in lines:
            w = draw.textlength(line, font=fnt)
            if w > width:
                raise ValueError(
                    f"{what}: line too wide ({w:.0f}px > {width}px): {line!r}"
                )
    return lines


def draw_bridge(d, cx, cy, col):
    # suspension bridge: towers rising above the deck, main cable arcing
    # between the tower tops, suspenders, deck, and water ripples below.
    # Rescaled (round 2) to fit inside the 88 px icon disc: every point
    # stays within ~37 px of the centre (disc inner radius 41 px).
    d.line([(cx - 28, cy - 22), (cx - 28, cy + 14)], fill=col, width=4)
    d.line([(cx + 28, cy - 22), (cx + 28, cy + 14)], fill=col, width=4)
    d.line([(cx - 28, cy - 18), (cx + 28, cy - 18)], fill=col, width=3)
    d.arc([cx - 28, cy - 18, cx + 28, cy + 14], 180, 360, fill=col, width=4)
    d.line([(cx - 14, cy - 16), (cx - 14, cy + 14)], fill=col, width=3)
    d.line([(cx, cy - 19), (cx, cy + 14)], fill=col, width=3)
    d.line([(cx + 14, cy - 16), (cx + 14, cy + 14)], fill=col, width=3)
    d.line([(cx - 32, cy + 14), (cx + 32, cy + 14)], fill=col, width=5)
    d.line([(cx - 28, cy + 22), (cx - 18, cy + 18), (cx - 8, cy + 22),
            (cx + 2, cy + 18), (cx + 12, cy + 22), (cx + 22, cy + 18),
            (cx + 28, cy + 22)], fill=col, width=3)
    d.line([(cx - 20, cy + 30), (cx - 8, cy + 27), (cx + 4, cy + 30),
            (cx + 16, cy + 27), (cx + 20, cy + 30)], fill=col, width=3)


def draw_tanker(d, cx, cy, col):
    # long tanker hull with stern superstructure, mast, and a small
    # blast starburst marking the mine/drone strike. Rescaled (round 2)
    # to fit inside the 88 px icon disc: every point within ~35 px
    # of the centre (disc inner radius 41 px).
    d.polygon([(cx - 29, cy - 2), (cx + 29, cy - 2), (cx + 23, cy + 11),
               (cx - 23, cy + 11)], fill=col)
    d.rectangle([cx - 26, cy - 15, cx - 11, cy - 2], fill=col)
    d.line([(cx - 18, cy - 21), (cx - 18, cy - 15)], fill=col, width=3)
    d.line([(cx + 17, cy - 2), (cx + 17, cy + 11)], fill=col, width=3)
    bx, by = cx + 19, cy - 19
    for ang in range(0, 360, 45):
        x = bx + int(7 * math.cos(math.radians(ang)))
        y = by + int(7 * math.sin(math.radians(ang)))
        d.line([(bx, by), (x, y)], fill=col, width=2)
    d.line([(cx - 30, cy + 17), (cx - 15, cy + 17), (cx - 8, cy + 21),
            (cx + 8, cy + 17), (cx + 30, cy + 17)], fill=col, width=3)
    d.line([(cx - 23, cy + 24), (cx + 23, cy + 24)], fill=col, width=3)


def draw_virus(d, cx, cy, col):
    d.ellipse([cx - 18, cy - 18, cx + 18, cy + 18], fill=col)
    for ang in range(0, 360, 45):
        x = cx + int(24 * math.cos(math.radians(ang)))
        y = cy + int(24 * math.sin(math.radians(ang)))
        d.ellipse([x - 5, y - 5, x + 5, y + 5], fill=col)
    d.ellipse([cx - 8, cy - 8, cx - 1, cy - 1], fill=WHITE)
    d.ellipse([cx + 3, cy + 2, cx + 9, cy + 8], fill=WHITE)


def draw_handshake(d, cx, cy, col):
    # three leaders: three heads above three shoulders, joined.
    # Kept compact (round 2) so the outer heads stay inside the 88 px
    # icon disc: farthest ink ~38 px from the centre (inner radius 41 px).
    for dx in (-24, 0, 24):
        d.ellipse([cx + dx - 10, cy - 25, cx + dx + 10, cy - 5], fill=col)
        d.pieslice([cx + dx - 12, cy - 2, cx + dx + 12, cy + 26],
                   180, 360, fill=col)
    d.line([(cx - 24, cy + 26), (cx + 24, cy + 26)], fill=col, width=4)


def draw_gavel(d, cx, cy, col):
    # gavel: head as a rotated rectangle (axis -45 deg), handle passing
    # through the head centre at +45 deg, round sound block below.
    # Rescaled (round 2) to fit inside the 88 px icon disc: head
    # corners stay within ~35 px of the centre (disc inner radius 41 px).
    ux, uy = math.cos(math.radians(-45)), math.sin(math.radians(-45))
    vx, vy = -uy, ux  # perpendicular: (0.707, 0.707)
    hx, hy = cx - 5, cy - 12  # head centre
    hl, hw = 22, 9  # head half-length / half-width
    corners = [
        (hx - hl * ux - hw * vx, hy - hl * uy - hw * vy),
        (hx + hl * ux - hw * vx, hy + hl * uy - hw * vy),
        (hx + hl * ux + hw * vx, hy + hl * uy + hw * vy),
        (hx - hl * ux + hw * vx, hy - hl * uy + hw * vy),
    ]
    d.polygon(corners, fill=col)
    d.line([(hx, hy), (hx + 34 * vx, hy + 34 * vy)], fill=col, width=7)
    d.ellipse([cx - 17, cy + 20, cx + 17, cy + 28], fill=col)


def draw_aid(d, cx, cy, col):
    # first-aid box; the lid line is pulled in (round 2) so it stays
    # inside the 88 px icon disc (ends at ~37 px from the centre).
    d.rectangle([cx - 28, cy - 18, cx + 28, cy + 22], fill=col)
    d.rectangle([cx - 6, cy - 10, cx + 6, cy + 14], fill=WHITE)
    d.rectangle([cx - 16, cy - 2, cx + 16, cy + 6], fill=WHITE)
    d.line([(cx - 28, cy - 22), (cx + 28, cy - 22)], fill=col, width=4)


ICONS = {
    "bridge": draw_bridge,
    "tanker": draw_tanker,
    "virus": draw_virus,
    "leaders": draw_handshake,
    "gavel": draw_gavel,
    "aid": draw_aid,
}

# (tag, accent, icon, headline, body, key-stat big, key-stat label, source)
STORIES = [
    ("EUROPE  •  WAR", (178, 34, 34), "bridge",
     "BRIDGES UNDER FIRE",
     "Ukraine struck the Kerch bridge to Crimea, while Russian missiles "
     "hit two Dnipro bridges and energy sites in Kyiv, cutting heat, "
     "water and power.",
     "2 BRIDGES", "HIT IN KYIV", "REUTERS • BBC"),
    ("MIDDLE EAST  •  CONFLICT", (146, 90, 18), "tanker",
     "TANKERS & DRONES AT HORMUZ",
     "Iran fired drones at a US radar base in Bahrain, and tankers were "
     "hit by mines near the Strait of Hormuz. A third US carrier arrived.",
     "3RD", "US CARRIER IN REGION", "AL JAZEERA • REUTERS"),
    ("USA  •  HEALTH", (27, 120, 88), "virus",
     "US LOSES MEASLES-FREE STATUS",
     "After 26 years, officials revoked US elimination status as measles "
     "spread nonstop for 12 months, with 5,412 CDC cases in 2026.",
     "5,412", "US CASES IN 2026", "CDC • AP"),
    ("ASIA  •  DIPLOMACY", (23, 63, 99), "leaders",
     "XI, TRUMP & PUTIN TALKS AT APEC",
     "China confirmed the three leaders will hold talks in Shenzhen on "
     "Thursday 19 November, on the sidelines of the APEC summit.",
     "19 NOV", "SHENZHEN • APEC", "REUTERS • AP"),
    ("FRANCE  •  JUSTICE", (94, 64, 140), "gavel",
     "DEPARDIEU ACCEPTS CONVICTION",
     "Actor Gérard Depardieu dropped his appeal against his 2025 "
     "sexual-assault conviction and apologised to the victims.",
     "2025", "CONVICTION FINAL", "AP • BBC"),
    ("UK  •  WEST BANK", (30, 110, 60), "aid",
     "UK SANCTIONS SETTLEMENT FIRMS",
     "Britain sanctioned eight Israeli firms linked to West Bank "
     "settlements, as Western states urged Israel to open Gaza aid "
     "crossings.",
     "8 FIRMS", "SANCTIONED BY UK", "BBC • REUTERS"),
]


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- header ----
    d.rectangle([0, 0, W, 148], fill=NAVY)
    d.rectangle([0, 148, W, 154], fill=GOLD)
    d.text((32, 16), "THE WORLD IN ONE DAY  •  TUESDAY",
           font=font(FB, 21), fill=(180, 200, 220))
    d.text((30, 42), "17 NOVEMBER 2026", font=font(FB, 66), fill=WHITE)
    d.text((32, 116), "Six stories that defined the day — in one picture.",
           font=font(FR, 20), fill=(180, 200, 220))

    # ---- story grid: 3 cols x 2 rows ----
    margin, gap = 16, 13
    pw = (W - 2 * margin - 2 * gap) // 3
    ph = 345
    top0 = 168
    for i, (tag, accent, icon, head, body, stat_big, stat_label,
            source) in enumerate(STORIES):
        r, c = divmod(i, 3)
        x = margin + c * (pw + gap)
        y = top0 + r * (ph + gap)
        d.rectangle([x, y, x + pw, y + ph], fill=WHITE,
                    outline=(200, 198, 188), width=2)
        d.rectangle([x, y, x + pw, y + 34], fill=accent)
        d.text((x + 12, y + 7), tag, font=font(FB, 16), fill=WHITE)
        # icon disc (88 px) on the left, key-stat callout on the right
        d.ellipse([x + 14, y + 44, x + 102, y + 132], fill=(238, 240, 244),
                  outline=accent, width=3)
        ICONS[icon](d, x + 58, y + 88, accent)
        d.text((x + 116, y + 52), stat_big, font=font(FB, 26), fill=accent)
        if d.textlength(stat_big, font=font(FB, 26)) > pw - 130:
            raise ValueError(
                f"card {i + 1} key-stat big too wide: {stat_big!r}")
        sl = fit_lines(wrap(d, stat_label, font(FB, 13), pw - 130),
                       2, f"card {i + 1} key-stat label",
                       d, font(FB, 13), pw - 130)
        sy = y + 90
        for line in sl:
            d.text((x + 116, sy), line, font=font(FB, 13), fill=INK)
            sy += 17
        # headline below the icon row
        hl = fit_lines(wrap(d, head, font(FB, 23), pw - 24),
                       3, f"card {i + 1} headline",
                       d, font(FB, 23), pw - 24)
        hy = y + 140
        for line in hl:
            d.text((x + 14, hy), line, font=font(FB, 23), fill=INK)
            hy += 26
        # body, bounded by the space left above the source line
        bl = wrap(d, body, font(FR, 16), pw - 28)
        by = hy + 8
        max_body = max(0, (y + ph - 34 - by) // 21)
        bl = fit_lines(bl, max_body, f"card {i + 1} body",
                       d, font(FR, 16), pw - 28)
        for line in bl:
            d.text((x + 14, by), line, font=font(FR, 16), fill=(52, 58, 66))
            by += 21
        # source line with a thin divider at the card bottom
        # (divider and text centred in the card footer: line at -28,
        # text at -22, so the 11 px text sits evenly in the footer strip)
        d.line([(x + 14, y + ph - 28), (x + pw - 14, y + ph - 28)],
               fill=(210, 208, 198), width=1)
        d.text((x + 14, y + ph - 22), "SOURCE: " + source,
               font=font(FB, 11), fill=MUTED)

    # ---- footer strip ----
    fy = top0 + 2 * ph + gap + 12
    d.rectangle([0, fy, W, H], fill=NAVY2)
    d.text((32, fy + 12), "ALSO ON 17 NOVEMBER",
           font=font(FB, 19), fill=GOLD)
    ticker = ("Japan scrambled jets after suspected Russian aircraft entered "
              "its airspace  •  The EU hit Temu with DSA charges over "
              "illegal product sales  •  Markets fell ahead of Nvidia "
              "results.")
    tl = fit_lines(wrap(d, ticker, font(FR, 17), W - 64), 3, "ticker",
                   d, font(FR, 17), W - 64)
    ty = fy + 42
    for line in tl:
        d.text((32, ty), line, font=font(FR, 17), fill=WHITE)
        ty += 23
    d.text((32, H - 30),
           "Sources (17 Nov 2026): Reuters, AP, BBC, The Guardian, "
           "Al Jazeera; data via US CDC & PAHO.",
           font=font(FR, 14), fill=SOURCES_COL)

    img.save(OUT, "PNG", optimize=True)
    print("saved", OUT)


if __name__ == "__main__":
    main()
