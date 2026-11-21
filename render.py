"""Render the 20 November 2026 world-news poster (1024x1024 PNG).

Reads news.json in this directory and draws a newspaper front page:
navy masthead, one main story panel with a wireframe globe, six
numbered stories in two columns, and a footer band. Pure PIL, no
network, no randomness -- the same input always gives the same bytes.
"""
import json
import math
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 1024, 1024

PAPER = (247, 243, 234)      # warm off-white
NAVY = (16, 32, 64)          # deep navy
GOLD = (198, 148, 52)        # muted gold
INK = (24, 24, 24)           # near-black text
GREY = (92, 92, 92)          # descriptor grey
PANEL = (238, 232, 216)      # main-story panel
RULE = (210, 202, 184)       # hairline rules

SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap; returns a list of lines that fit max_w."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_globe(draw, cx, cy, r):
    """Wireframe globe: outer circle, meridians, parallels, gold tint."""
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=NAVY, width=4)
    for k in range(1, 4):
        x = r * k / 4
        draw.ellipse([cx - x, cy - r, cx + x, cy + r], outline=NAVY, width=2)
    for k in (1, 2, 3):
        y = r * k / 4
        half = int(math.sqrt(max(r * r - y * y, 0)))
        draw.line([cx - half, cy - y, cx + half, cy - y], fill=NAVY, width=2)
        draw.line([cx - half, cy + y, cx + half, cy + y], fill=NAVY, width=2)
    draw.line([cx, cy - r, cx, cy + r], fill=NAVY, width=2)
    draw.arc([cx - r, cy - r, cx + r, cy + r], start=200, end=340,
             fill=GOLD, width=5)


def main():
    with open(os.path.join(HERE, "news.json"), encoding="utf-8") as fh:
        data = json.load(fh)

    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- Masthead -------------------------------------------------------
    d.rectangle([0, 0, W, 148], fill=NAVY)
    f_mast = font(SERIF_B, 52)
    d.text((36, 38), data["masthead"], font=f_mast, fill=(255, 255, 255))
    f_date = font(SANS_B, 20)
    date = data["date"]
    dw = d.textlength(date, font=f_date)
    d.text((W - 36 - dw, 56), date, font=f_date, fill=GOLD)
    d.rectangle([0, 148, W, 156], fill=GOLD)

    # ---- Main story -----------------------------------------------------
    main = data["main"]
    d.rectangle([36, 184, W - 36, 500], fill=PANEL)
    d.rectangle([36, 184, 48, 500], fill=GOLD)
    f_kick = font(SANS_B, 20)
    d.text((72, 204), main["kicker"], font=f_kick, fill=GOLD)
    f_head = font(SERIF_B, 52)
    head_lines = wrap(d, main["headline"], f_head, 560)
    y = 236
    for ln in head_lines:
        d.text((72, y), ln, font=f_head, fill=NAVY)
        y += 62
    f_desc = font(SERIF, 22)
    for ln in wrap(d, main["descriptor"], f_desc, 560):
        d.text((72, y), ln, font=f_desc, fill=INK)
        y += 30
    # globe, right side of the panel
    draw_globe(d, 848, 330, 92)
    # fact chips along the panel bottom
    f_chip = font(SANS_B, 14)
    cx = 72
    cy = 452
    for chip in main["chips"]:
        tw = d.textlength(chip, font=f_chip)
        d.rounded_rectangle([cx, cy, cx + tw + 20, cy + 30],
                            radius=15, outline=NAVY, width=2)
        d.text((cx + 10, cy + 7), chip, font=f_chip, fill=NAVY)
        cx += tw + 30

    # ---- Six numbered stories, two columns -----------------------------
    stories = data["stories"]
    f_num = font(SANS_B, 22)
    f_sh = font(SANS_B, 23)
    f_sd = font(SANS, 18)
    col_x = [36, 532]
    col_w = 456
    row_y = [536, 664, 792]
    for i, st in enumerate(stories):
        x = col_x[i % 2]
        y = row_y[i // 2]
        d.ellipse([x, y, x + 40, y + 40], fill=NAVY)
        num = str(i + 1)
        nw = d.textlength(num, font=f_num)
        d.text((x + 20 - nw / 2, y + 6), num, font=f_num, fill=(255, 255, 255))
        tx = x + 54
        for ln in wrap(d, st["headline"], f_sh, col_w - 54):
            d.text((tx, y), ln, font=f_sh, fill=INK)
            y += 28
        for ln in wrap(d, st["descriptor"], f_sd, col_w - 54):
            d.text((tx, y), ln, font=f_sd, fill=GREY)
            y += 23
        if i % 2 == 0:
            d.line([512, row_y[i // 2] + 8, 512, row_y[i // 2] + 108],
                   fill=RULE, width=2)
    d.line([36, 652, W - 36, 652], fill=RULE, width=2)
    d.line([36, 780, W - 36, 780], fill=RULE, width=2)

    # ---- Footer ---------------------------------------------------------
    d.rectangle([0, 940, W, H], fill=NAVY)
    f_foot = font(SANS_B, 20)
    foot = "20 NOVEMBER 2026  •  SEVEN STORIES  •  THE WORLD TODAY"
    fw = d.textlength(foot, font=f_foot)
    d.text(((W - fw) / 2, 966), foot, font=f_foot, fill=(255, 255, 255))

    out = os.path.join(HERE, "entry.png")
    img.save(out, "PNG")
    print("wrote", out, img.size)


if __name__ == "__main__":
    main()
