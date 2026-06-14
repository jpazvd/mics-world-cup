#!/usr/bin/env python3
"""Render the MICS World Cup knockout bracket.

Writes figures/mics_world_cup_bracket.svg and .png (rasterised at 2x).
Tournament data comes from mics_world_cup_sim.simulate(); this script only
lays it out. Run:  python make_bracket.py
"""
from pathlib import Path

from mics_world_cup_sim import simulate, GROUPS, NAME
from _svgkit import (NAVY, CYAN, YELLOW, WHITE, INK, MUTE, GREY, DEEP, MIST, CONNECT,
                     disp, text, rect, circle, line, path, svg_doc, write_figure)

HERE = Path(__file__).resolve().parent
FIG = HERE / "figures"

WIN_BG = CYAN; LOSE_BG = "#F1F6F9"; WIN_FG = WHITE; LOSE_FG = GREY
BW = 182  # match-box width

# round -> (top-y of first match, vertical pitch between matches)
TOP = {"R32": (179, 78), "R16": (218, 156), "QF": (296, 312), "SF": (452, 0)}


def _inorder_r32(qf_id, R16, QF):
    """R32 match ids under one quarterfinal, in top-to-bottom (planar) order."""
    a, b = QF[qf_id]
    return [R16[a][0], R16[a][1], R16[b][0], R16[b][1]]


def _champ_blurb(r):
    champ = r["champ"]; cat = r["cat"]
    rounds, n, _ = r["S"][champ][1]
    m7 = cat[(cat["country"] == NAME.get(champ, champ)) & (cat["round"] == "MICS7")]
    if (m7["status"] == "Data processing / analysis").any(): m7txt = "MICS7 in processing"
    elif len(m7):                                            m7txt = "MICS7 fielded"
    else:                                                    m7txt = "no MICS7 yet"
    return f"{n} surveys · {rounds} rounds · {m7txt}"


def build(r):
    S = r["S"]; R32 = r["R32"]; R16 = r["R16"]; QF = r["QF"]
    w = r["w"]; w16 = r["w16"]; wqf = r["wqf"]
    el = []

    # title
    el.append(text(925, 62, "If World Cups were won on child data", 38, NAVY, bold=True, anchor="middle"))
    el.append(text(925, 94, "The FIFA World Cup 26 bracket, every match decided by MICS programme strength", 17, INK, anchor="middle"))
    el.append(line(40, 116, 1810, 116, CYAN, 3))

    HEAD = ["ROUND OF 32", "ROUND OF 16", "QUARTERFINALS", "SEMIFINAL"]
    for cx, lab in zip((131, 315, 499, 683), HEAD):   el.append(text(cx, 146, lab, 12.5, MUTE, anchor="middle", ls=1.5))
    for cx, lab in zip((1719, 1527, 1335, 1143), HEAD): el.append(text(cx, 146, lab, 12.5, MUTE, anchor="middle", ls=1.5))

    wings = {
        "L": {"cols": {"R32": 40,   "R16": 224,  "QF": 408,  "SF": 592},
              "r32": _inorder_r32(97, R16, QF) + _inorder_r32(98, R16, QF),
              "qf": [97, 98], "r16": [89, 90, 93, 94],
              "sf": (r["sf1"], (wqf[97], wqf[98]))},
        "R": {"cols": {"R32": 1628, "R16": 1436, "QF": 1244, "SF": 1052},
              "r32": _inorder_r32(99, R16, QF) + _inorder_r32(100, R16, QF),
              "qf": [99, 100], "r16": [91, 92, 95, 96],
              "sf": (r["sf2"], (wqf[99], wqf[100]))},
    }

    def box(col_x, top_y, team, winner):
        won = team == winner
        bg, fg = (WIN_BG, WIN_FG) if won else (LOSE_BG, LOSE_FG)
        return [rect(col_x, top_y, BW, 26, bg, rx=5),
                text(col_x + 10, top_y + 19, disp(team), 13.5, fg, bold=won),
                text(col_x + 173, top_y + 19, f"{S[team][0]:.0f}", 12.5, fg, bold=True, anchor="end")]

    def centers(round_key, n):
        top0, pitch = TOP[round_key]
        return [top0 + pitch * i + 28 for i in range(n)]

    for wk, W in wings.items():
        cols = W["cols"]
        for i, m in enumerate(W["r32"]):
            top = TOP["R32"][0] + TOP["R32"][1] * i; a, b = R32[m]
            el += box(cols["R32"], top, a, w[m]); el += box(cols["R32"], top + 28, b, w[m])
        for i, m in enumerate(W["r16"]):
            top = TOP["R16"][0] + TOP["R16"][1] * i; ca, cb = R16[m]
            el += box(cols["R16"], top, w[ca], w16[m]); el += box(cols["R16"], top + 28, w[cb], w16[m])
        for i, m in enumerate(W["qf"]):
            top = TOP["QF"][0] + TOP["QF"][1] * i; ca, cb = QF[m]
            el += box(cols["QF"], top, w16[ca], wqf[m]); el += box(cols["QF"], top + 28, w16[cb], wqf[m])
        sfwin, (a, b) = W["sf"]
        el += box(cols["SF"], TOP["SF"][0], a, sfwin); el += box(cols["SF"], TOP["SF"][0] + 28, b, sfwin)

        # faint elbow connectors: parent i is fed by children 2i and 2i+1
        left = wk == "L"
        for child_key, parent_key, n_parent in (("R32", "R16", 4), ("R16", "QF", 2), ("QF", "SF", 1)):
            cc = centers(child_key, n_parent * 2); pc = centers(parent_key, n_parent)
            cx = cols[child_key] + (BW if left else 0)
            px = cols[parent_key] + (0 if left else BW)
            mid = cx + (1 if left else -1)
            for i in range(n_parent):
                for ch in (cc[2 * i], cc[2 * i + 1]):
                    el.append(path(f"M {cx} {ch} H {mid} V {pc[i]} H {px}", CONNECT, 1.6))

    # final card
    champ, ru, third = r["champ"], r["runner_up"], r["third"]
    rec3 = next(x for x in r["records"] if x[0] == "3rd")
    fourth = rec3[2] if rec3[3] == rec3[1] else rec3[1]
    el.append(rect(793, 382, 264, 196, NAVY, rx=14))
    el.append(rect(817, 476, 216, 40, YELLOW, rx=8))
    el.append(text(925, 416, "FINAL · METLIFE · JULY 19", 12.5, YELLOW, anchor="middle"))
    el.append(text(925, 456, f"{champ.upper()} {S[champ][0]:.0f} – {S[ru][0]:.0f} {ru.upper()}", 24, WIN_FG, bold=True, anchor="middle"))
    el.append(text(925, 503, f"🏆 CHAMPION: {champ.upper()}", 19, NAVY, bold=True, anchor="middle"))
    el.append(text(925, 540, _champ_blurb(r), 11.5, MIST, anchor="middle"))
    el.append(text(925, 560, f"Third place: {disp(third)} {S[third][0]:.0f} – {S[fourth][0]:.0f} {disp(fourth)}", 11.5, MIST, anchor="middle"))

    # group-stage legend
    el.append(text(40, 818, "GROUP STAGE — qualifiers (1st · 2nd · 3rd, * = among best eight thirds)", 14, MUTE))
    best8 = set(r["best8"])
    for i, g in enumerate(GROUPS):
        cx = 51 + 147.5 * i; st = r["standings"][g]
        el.append(circle(cx, 846, 10, NAVY))
        el.append(text(cx, 850, g, 12, WIN_FG, bold=True, anchor="middle"))
        el.append(text(cx + 17, 850, disp(st[0]), 12.5, DEEP, bold=True))
        el.append(text(cx + 17, 869, disp(st[1]), 12, NAVY))
        el.append(text(cx + 17, 887, disp(st[2]) + ("*" if g in best8 else ""), 12, MUTE))

    # footer — reproducibility claim corrected to this script
    el.append(text(40, 916,
        "Simulation: official FIFA World Cup 26 bracket (final draw, 5 Dec 2025); match outcomes decided by MICS programme strength derived from the UNICEF MICS survey catalogue (427 records, MICS1–MICS7):",
        12.5, MUTE))
    el.append(text(40, 934,
        "2 pts per survey + 3 pts per distinct round + bonuses for a MICS7 in the current round, reaching data processing, and fieldwork since 2020. Ties resolved by seeded penalties (seed = 1995, the year MICS began). Reproducible: make_bracket.py. UNICEF · Data & Analytics · June 2026.",
        12.5, MUTE))

    return svg_doc(1850, 968, el)


def main():
    write_figure(FIG, "mics_world_cup_bracket", build(simulate()))


if __name__ == "__main__":
    main()
