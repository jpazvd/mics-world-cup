#!/usr/bin/env python3
"""Render the MICS coverage group board ("The other league table").

Writes figures/wc26_mics_group_board.svg and .png (rasterised at 2x).
Tournament/coverage data comes from mics_world_cup_sim.simulate(); this script
only lays it out. Run:  python make_group_board.py
"""
from pathlib import Path

from mics_world_cup_sim import simulate, GROUPS, NAME
from _svgkit import (NAVY, CYAN, YELLOW, WHITE, INK, MUTE, GREY,
                     disp, text, rect, circle, line, svg_doc, write_figure)

HERE = Path(__file__).resolve().parent
FIG = HERE / "figures"

# survey-count -> tile fill (0, 1-2, 3-4, 5-6, 7)
TILE = ["#EEF3F6", "#C8E9F8", "#7FCBEE", "#2FA8DC", "#0E7CB1"]
TILE0_FG = "#6B7C88"


def _coverage(r):
    """Per-nation (survey count, has-MICS7) over the 48 World Cup nations."""
    cat = r["cat"]; S = r["S"]; out = {}
    for g in GROUPS:
        for t in GROUPS[g]:
            key = NAME.get(t, t)
            n = int(S[t][1][1])
            has_m7 = len(cat[(cat["country"] == key) & (cat["round"] == "MICS7")]) > 0
            out[t] = (n, has_m7)
    return out


def _bucket(n):
    if n <= 0: return TILE[0], TILE0_FG
    if n <= 2: return TILE[1], NAVY
    if n <= 4: return TILE[2], NAVY
    if n <= 6: return TILE[3], WHITE
    return TILE[4], WHITE


def build(r):
    cov = _coverage(r)
    el = []
    el.append(text(56, 86, "The other league table", 40, NAVY, bold=True))
    el.append(text(56, 122, "MICS coverage across the 48 nations at the FIFA World Cup 26", 19, INK))
    el.append(line(56, 146, 1144, 146, CYAN, 3))

    n_part = sum(1 for v in cov.values() if v[0] >= 1)
    n_surv = sum(v[0] for v in cov.values())
    n_m7 = sum(1 for v in cov.values() if v[1])
    el.append(text(56, 192, str(n_part), 36, CYAN, bold=True))
    el.append(text(130, 192, "of 48 nations participate in MICS", 16, NAVY))
    el.append(text(480, 192, str(n_surv), 36, CYAN, bold=True))
    el.append(text(554, 192, "MICS surveys since 1995", 16, NAVY))
    el.append(text(811, 192, str(n_m7), 36, CYAN, bold=True))
    el.append(text(863, 192, "with a MICS7 in the current round", 16, NAVY))

    col_x = [66, 343.5, 621, 898.5]
    dot_cy = [248, 488, 728]
    TW = 235.5
    for i, g in enumerate(GROUPS):
        cl = col_x[i % 4]; cy = dot_cy[i // 4]; dot_cx = cl + 88
        el.append(text(cl + 4, cy + 6, "GROUP", 14, MUTE))
        el.append(circle(dot_cx, cy, 14, NAVY))
        el.append(text(dot_cx, cy + 6, g, 16, WHITE, bold=True, anchor="middle"))
        for k, t in enumerate(GROUPS[g]):
            ty = cy + 18 + 42 * k
            n, has_m7 = cov[t]
            fill, fg = _bucket(n)
            el.append(rect(cl, ty, TW, 35, fill, rx=7))
            el.append(text(cl + 12, ty + 24, disp(t), 15.5, fg))
            if n > 0:
                el.append(text(cl + TW - 14, ty + 24, str(n), 15.5, fg, anchor="end"))
            if has_m7:
                el.append(circle(cl + TW - 34, ty + 17.5, 5, YELLOW))

    # legend strip
    el.append(text(56, 966, "MICS surveys per nation, 1995–2026", 15, GREY))
    for j, sx in enumerate((346, 436, 526, 616, 706)):
        el.append(rect(sx, 951, 34, 20, TILE[j], rx=5))
    for sx, lab in zip((388, 478, 568, 658, 748), ("0", "1–2", "3–4", "5–6", "7")):
        el.append(text(sx, 966, lab, 14, GREY))
    el.append(circle(802, 960, 5.5, YELLOW))
    el.append(text(814, 966, "MICS7 in the current round", 14, GREY))

    el.append(text(56, 1004,
        "Source: UNICEF MICS survey catalogue (427 records, MICS1–MICS7) joined to the FIFA World Cup 26 final field. Numbers in tiles are catalogue survey records per nation,",
        12.5, MUTE))
    el.append(text(56, 1022,
        "including subnational and special-population surveys. Amber dot: a MICS7 in the current round (incl. one on hold). UNICEF · Data & Analytics · June 2026.",
        12.5, MUTE))

    return svg_doc(1200, 1124, el)


def main():
    write_figure(FIG, "wc26_mics_group_board", build(simulate()))


if __name__ == "__main__":
    main()
