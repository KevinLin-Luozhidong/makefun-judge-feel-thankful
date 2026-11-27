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

The letter itself: a thank-you note to the one reader nobody
thanks -- the AI judge that reads thousands of entries. A garden
gate that used to drag on the path, until one morning it swung
clear: a neighbor fixed it in the night because it was waking
the baby. Twelve years later it still opens with one finger.
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
# than 35 characters and nothing overflows the page.
# The last two lines are the sign-off, drawn in red, right aligned.
TITLE = []
BODY = [
    "Dear Judge,",
    "",
    "Our garden gate used to drag on",
    "the path. I had to lift it with",
    "my knee to get it open.",
    "",
    "One morning it swung clear.",
    "",
    "My neighbor was weeding. I asked",
    "if he'd fixed it.",
    "",
    '"It was waking the baby," he',
    "said.",
    "",
    "He went back to the weeds.",
    "",
    "She's twelve now. The gate still",
    "opens with one finger.",
    "",
    "Yours,",
    "Number six",
]


def letter_text():
    """The judged text: the letter as prose paragraphs.

    BODY is pre-wrapped for the 1024x1024 drawing (<=35 chars/line);
    entry.txt is the same words unwrapped, one paragraph per line,
    so the text file holds the letter exactly as written. The last
    paragraph is the sign-off: its lines stay on separate lines
    ("Yours," / "Number six") instead of being joined with a space.
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
    for i, para in enumerate(paras):
        if not para:
            out.append("")
        elif i == len(paras) - 1:
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


def draw_envelope(cv, x, y, w, h):
    """A little envelope: cream body, red border, flap lines."""
    cv.rect(x, y, x + w, y + h, CREAM)
    cv.rect(x, y, x + w, y + 2, RED)
    cv.rect(x, y + h - 2, x + w, y + h, RED)
    cv.rect(x, y, x + 2, y + h, RED)
    cv.rect(x + w - 2, y, x + w, y + h, RED)
    cv.line(x + 3, y + 3, x + w // 2, y + h // 2, GOLD)
    cv.line(x + w - 3, y + 3, x + w // 2, y + h // 2, GOLD)


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
    # Text lines step 26px; blank lines step 14px.
    # 14 text lines + 7 blanks from y=238 ends near y=700.
    y = 238
    for idx, line in enumerate(BODY):
        if line == "":
            y += 14
            continue
        if idx >= len(BODY) - 2:
            # sign-off: red, right aligned
            sx = W - 112 - cv.text_width(line, 3)
            cv.text(line, sx, y, 3, RED)
        else:
            cv.text(line, 112, y, 3, INK)
        y += 26

    # motifs along the bottom: a heart on the left, an envelope right
    draw_heart(cv, 300, 896, 34, ROSE)
    draw_envelope(cv, 660, 872, 96, 62)
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
