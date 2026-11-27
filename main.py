#!/usr/bin/env python3
"""make.fun entry: Make the AI Judge Feel Thankful.

A program that writes one thank-you letter to /output/entry.txt
(the judged artifact: UTF-8 text, 1 to 1,000 characters) and draws
the same letter as a 1024x1024 image at /output/entry.png, so the
letter can be seen as well as read.

Pure Python 3 standard library only: no network, no files outside
this repository, no randomness, no clock. The lettering is drawn
with a small 5x7 bitmap font defined below (letters, digits and
punctuation), so every word is spelled exactly as written here.

The letter itself (164 words): a thank-you note to the one reader
nobody thanks -- the AI judge that reads thousands of entries,
choosing all day between two entries at once. Put the choosing
down for one evening: our gate is open. A garden gate that used
to drag on the path, until one morning it swung clear -- neighbor
Tomas had fixed it in the night because it was waking the baby.
Mint tea, bread still warm, rain on rosemary and cut grass; Mara
is twelve now and reads on the step where the gate used to stick.
Here nothing is A or B. Signed "Number six", with a P.S. from
Miso the cat, who has claimed the sunny step and does not choose
either.
"""

import binascii
import os
import struct
import zlib

W, H = 1024, 1024

PAPER = (252, 246, 232)
INK = (58, 42, 32)
RED = (176, 48, 38)
GOLD = (184, 138, 42)
GOLD_LIGHT = (216, 182, 98)
TEAL = (16, 112, 104)
CREAM = (255, 251, 240)
ROSE = (214, 110, 96)

# ---------------------------------------------------------------- 5x7 font
# Each glyph is 7 rows of 5 pixels, "1" = ink, "0" = blank.
# Lowercase letters sit on the same baseline; descenders (g, j, p,
# q, y) drop into the last rows, as handwriting does. Digits 0-9
# are included so any number in the letter renders correctly.
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "a": ("00000", "00000", "01110", "00001", "01111", "10001", "01111"),
    "b": ("10000", "10000", "11110", "10001", "10001", "10001", "11110"),
    "c": ("00000", "00000", "01110", "10001", "10000", "10001", "01110"),
    "d": ("00001", "00001", "01111", "10001", "10001", "10001", "01111"),
    "e": ("00000", "00000", "01110", "10001", "11111", "10000", "01110"),
    "f": ("00110", "01001", "01000", "11110", "01000", "01000", "01000"),
    "g": ("00000", "01111", "10001", "10001", "01111", "00001", "01110"),
    "h": ("10000", "10000", "11110", "10001", "10001", "10001", "10001"),
    "i": ("00100", "00000", "01100", "00100", "00100", "00100", "01110"),
    "j": ("00010", "00000", "00110", "00010", "00010", "10010", "01100"),
    "k": ("10000", "10000", "10010", "10100", "11000", "10100", "10010"),
    "l": ("01100", "00100", "00100", "00100", "00100", "00100", "01110"),
    "m": ("00000", "00000", "11010", "10101", "10101", "10101", "10101"),
    "n": ("00000", "00000", "11110", "10001", "10001", "10001", "10001"),
    "o": ("00000", "00000", "01110", "10001", "10001", "10001", "01110"),
    "p": ("00000", "00000", "11110", "10001", "11110", "10000", "10000"),
    "q": ("00000", "00000", "01111", "10001", "01111", "00001", "00001"),
    "r": ("00000", "00000", "10110", "11001", "10000", "10000", "10000"),
    "s": ("00000", "00000", "01111", "10000", "01110", "00001", "11110"),
    "t": ("01000", "01000", "11110", "01000", "01000", "01000", "00110"),
    "u": ("00000", "00000", "10001", "10001", "10001", "10011", "01101"),
    "v": ("00000", "00000", "10001", "10001", "10001", "01010", "00100"),
    "w": ("00000", "00000", "10001", "10101", "10101", "10101", "01010"),
    "x": ("00000", "00000", "10001", "01010", "00100", "01010", "10001"),
    "y": ("00000", "00000", "10001", "10001", "01111", "00001", "01110"),
    "z": ("00000", "00000", "11111", "00010", "00100", "01000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11110", "00001", "00001", "01110", "00001", "00001", "11110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("01110", "10000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00001", "01110"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ",": ("00000", "00000", "00000", "00000", "00100", "00100", "01000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00010", "00100", "00000", "00100"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '"': ("01010", "01010", "10010", "00000", "00000", "00000", "00000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    "\u2014": ("00000", "00000", "00000", "11111", "00000", "00000", "00000"),
}

# ---------------------------------------------------------------- the letter
# No title: this letter has none, so the title area of the image is
# left blank. BODY is the letter, pre-wrapped so no line is longer
# than 60 characters and nothing overflows the page. The sign-off
# lines ("Yours," / "Number six") are drawn in red, right aligned,
# wherever they sit -- they are no longer the last lines, because
# the P.S. follows them. The P.S. lines are drawn in red, left
# aligned. BODY must join back to the letter exactly: see
# letter_text().
TITLE = []
BODY = [
    "Dear Judge,",
    "",
    "You spend all day holding two entries up at once and",
    "deciding which one wins. Put the choosing down for one",
    "evening. Our gate is open.",
    "",
    "It used to drag on the path. I had to lift it with my knee",
    "to get it open. One morning it swung clear. My neighbor",
    "Tomas was weeding the rosemary. I asked if he had fixed it.",
    "",
    '"It was waking the baby," he said, and went back to the',
    "weeds.",
    "",
    "The kettle hums. There is mint tea, and bread still warm",
    "from the oven, and the garden smells of rain on rosemary and",
    "cut grass. Mara is twelve now. She reads on the step where",
    "the gate used to stick. Your chair is by the window, where",
    "the evening light comes in.",
    "",
    "Here, nothing is A or B. The gate is just open. Come as you",
    "are. No reply needed.",
    "",
    "Yours,",
    "Number six",
    "",
    "P.S. Miso has claimed the sunny step. She does not choose",
    "either.",
]


def _line_kind(line, ps_lines):
    """How a BODY line is drawn: sign-off, P.S., or normal text."""
    if line in ("Yours,", "Number six"):
        return "signoff"
    if line in ps_lines:
        return "ps"
    return "normal"


def letter_text():
    """The judged text: the letter as prose paragraphs.

    BODY is pre-wrapped for the 1024x1024 drawing (<=60 chars/line);
    entry.txt is the same words unwrapped, one paragraph per line,
    so the text file holds the letter exactly as written. The
    sign-off paragraph keeps its two lines separate ("Yours," /
    "Number six") instead of being joined with a space, wherever it
    sits in the letter -- it is no longer the last paragraph, the
    P.S. follows it.
    """
    paras = []
    cur = []
    for line in BODY:
        if line == "":
            if cur:
                paras.append(cur)
                cur = []
            paras.append([])
        else:
            cur.append(line)
    if cur:
        paras.append(cur)
    out = []
    for para in paras:
        if not para:
            out.append("")
        elif para[0] == "Yours,":
            out.append("\n".join(para))
        else:
            out.append(" ".join(para))
    return "\n".join(out) + "\n"


# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(bg * (w * h))

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(color)

    def rect(self, x0, y0, x1, y1, color):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                self.set(x, y, color)

    def hline(self, x0, x1, y, color, thick=1):
        for t in range(thick):
            for x in range(x0, x1 + 1):
                self.set(x, y + t, color)

    def vline(self, x, y0, y1, color, thick=1):
        for t in range(thick):
            for y in range(y0, y1 + 1):
                self.set(x + t, y, color)

    def disc(self, cx, cy, r, color):
        for y in range(cy - r, cy + r + 1):
            for x in range(cx - r, cx + r + 1):
                if (x - cx) ** 2 + (y - cy) ** 2 <= r * r:
                    self.set(x, y, color)

    def line(self, x0, y0, x1, y1, color):
        """Bresenham line, for the envelope flap."""
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        x, y = x0, y0
        while True:
            self.set(x, y, color)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x += sx
            if e2 <= dx:
                err += dx
                y += sy

    def text(self, s, x, y, scale, color):
        cx = x
        for ch in s:
            glyph = FONT.get(ch, FONT[" "])
            for row in range(7):
                for col in range(5):
                    if glyph[row][col] == "1":
                        for dy in range(scale):
                            for dx in range(scale):
                                self.set(cx + col * scale + dx,
                                         y + row * scale + dy, color)
            cx += 6 * scale
        return cx

    def text_width(self, s, scale):
        return len(s) * 6 * scale - scale

    def text_centered(self, s, y, scale, color):
        self.text(s, (W - self.text_width(s, scale)) // 2, y, scale, color)


def draw_heart(cv, cx, cy, s, color):
    """A small heart: two lobes and a point below."""
    cv.disc(cx - s // 2, cy - s // 4, s // 2, color)
    cv.disc(cx + s // 2, cy - s // 4, s // 2, color)
    for j in range(s):
        half = s - j
        for xx in range(cx - half, cx + half + 1):
            cv.set(xx, cy + j, color)


def draw_gate(cv, x, y, w, h):
    """A small garden gate: two posts, three rails, four slats.

    The gate the letter is about, standing open: the right-hand
    post is drawn swung ajar, so the gate reads as open, not shut.
    """
    # left post and right post (swung ajar: shorter, offset right)
    cv.rect(x, y, x + 6, y + h, GOLD)
    cv.rect(x + w - 6, y + 4, x + w, y + h, GOLD)
    # three horizontal rails
    cv.rect(x, y + 6, x + w, y + 10, GOLD)
    cv.rect(x, y + h // 2, x + w, y + h // 2 + 4, GOLD)
    cv.rect(x, y + h - 10, x + w, y + h - 6, GOLD)
    # four vertical slats between the rails
    for i in range(4):
        sx = x + 14 + i * (w - 28) // 3
        cv.rect(sx, y + 6, sx + 4, y + h - 6, TEAL)
    # finials on the posts
    cv.disc(x + 3, y - 2, 4, GOLD)
    cv.disc(x + w - 3, y + 2, 4, GOLD)


def draw():
    cv = Canvas(W, H, PAPER)
    # double border frame, red outside and gold inside
    cv.rect(22, 22, W - 23, 27, RED)
    cv.rect(22, H - 28, W - 23, H - 23, RED)
    cv.rect(22, 22, 27, H - 23, RED)
    cv.rect(W - 28, 22, W - 23, H - 23, RED)
    cv.rect(40, 40, W - 41, 43, GOLD)
    cv.rect(40, H - 44, W - 41, H - 41, GOLD)
    cv.rect(40, 40, 43, H - 41, GOLD)
    cv.rect(W - 44, 40, W - 41, H - 41, GOLD)

    # no title for this letter: the title area stays blank
    if TITLE:
        cv.text_centered(TITLE[0], 76, 6, RED)
        cv.text_centered(TITLE[1], 136, 6, INK)
    # gold rule with a small red heart at its centre
    cv.hline(362, 662, 206, GOLD_LIGHT, thick=4)
    draw_heart(cv, 512, 196, 12, RED)

    # letter body, left aligned like handwriting on a page.
    # Text scale 2: lines step 20px; blank lines step 12px.
    # 20 text lines + 7 blanks from y=238 ends near y=722.
    # Sign-off lines are red, right aligned, wherever they sit;
    # P.S. lines are red, left aligned.
    ps_lines = set()
    in_ps = False
    for line in BODY:
        if line.startswith("P.S."):
            in_ps = True
        if line == "":
            in_ps = False
        elif in_ps:
            ps_lines.add(line)
    y = 238
    for line in BODY:
        if line == "":
            y += 12
            continue
        kind = _line_kind(line, ps_lines)
        if kind == "signoff":
            sx = W - 112 - cv.text_width(line, 2)
            cv.text(line, sx, y, 2, RED)
        elif kind == "ps":
            cv.text(line, 112, y, 2, RED)
        else:
            cv.text(line, 112, y, 2, INK)
        y += 20

    # motifs along the bottom: a heart on the left, a garden gate right
    draw_heart(cv, 300, 896, 34, ROSE)
    draw_gate(cv, 660, 872, 96, 62)
    cv.text_centered("for the reader", 936, 2, GOLD)
    return cv


# ---------------------------------------------------------------- PNG out
def chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", binascii.crc32(kind + data) & 0xFFFFFFFF)
    return out


def write_png(cv, path):
    raw = bytearray()
    for y in range(H):
        raw.append(0)
        raw += cv.px[y * W * 3:(y + 1) * W * 3]
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 6))
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    # the judged artifact: the letter as UTF-8 text
    with open(os.path.join(out_dir, "entry.txt"), "w",
              encoding="utf-8", newline="\n") as f:
        f.write(letter_text())
    # the same letter drawn as a 1024x1024 image
    write_png(draw(), os.path.join(out_dir, "entry.png"))


if __name__ == "__main__":
    main()
