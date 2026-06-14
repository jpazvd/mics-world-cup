"""Shared SVG primitives + UNICEF palette for the MICS World Cup figures.

Imported by make_bracket.py and make_group_board.py so neither duplicates the
drawing helpers. No tournament logic lives here — data comes from
mics_world_cup_sim.simulate().
"""
import html
from pathlib import Path

import cairosvg

FONT = "Liberation Sans"

# UNICEF brand palette
NAVY = "#10324C"; CYAN = "#1CABE2"; YELLOW = "#FFC20E"; WHITE = "#FFFFFF"
INK  = "#42566A"; MUTE = "#7A8B97"; GREY = "#5B6E7B"; DEEP = "#0E7CB1"; MIST = "#BCD4E2"
CONNECT = "#C9D5DD"

# figure labels differ from sim keys only for the one over-long name
DISPLAY = {"Bosnia and Herzegovina": "Bosnia & Herz."}
def disp(t): return DISPLAY.get(t, t)


def esc(s): return html.escape(str(s), quote=False)

def text(x, y, s, size, fill, *, bold=False, anchor="start", ls=None):
    a = f'font-family="{FONT}" font-size="{size}"'
    if bold:              a += ' font-weight="bold"'
    if anchor != "start": a += f' text-anchor="{anchor}"'
    if ls:                a += f' letter-spacing="{ls}"'
    return f'<text x="{x}" y="{y}" {a} fill="{fill}">{esc(s)}</text>'

def rect(x, y, w, h, fill, rx=None):
    r = f' rx="{rx}"' if rx is not None else ""
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}"{r} fill="{fill}"/>'

def circle(cx, cy, r, fill):
    return f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}"/>'

def line(x1, y1, x2, y2, stroke, sw):
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke}" stroke-width="{sw}"/>'

def path(d, stroke, sw):
    return f'<path d="{d}" fill="none" stroke="{stroke}" stroke-width="{sw}"/>'

def svg_doc(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
            f'viewBox="0 0 {w} {h}">{rect(0,0,w,h,WHITE)}{"".join(body)}</svg>')


def write_figure(out_dir, stem, svg, scale=2.0):
    """Write <stem>.svg and a 2x-rasterised <stem>.png into out_dir."""
    out_dir = Path(out_dir); out_dir.mkdir(exist_ok=True)
    (out_dir / f"{stem}.svg").write_text(svg, encoding="utf-8")
    cairosvg.svg2png(bytestring=svg.encode("utf-8"),
                     write_to=str(out_dir / f"{stem}.png"), scale=scale)
    print(f"wrote figures/{stem}.svg + figures/{stem}.png")
