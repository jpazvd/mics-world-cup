#!/usr/bin/env python3
"""The MICS World Cup 26 — official FIFA bracket, catalogue-derived strength.

Strength per nation (from mics_surveys_catalogue.csv, 427 records):
  +2 per survey record  +3 per distinct round (time-series depth)
  +2 if a MICS7 is in the current round  +1 stage bonus if that MICS7 has
  reached data processing  +1 if latest fieldwork year >= 2020 (recency)
Group stage: round robin, higher strength wins (3 pts); equal = draw.
Standings tiebreak: strength, then distinct rounds, then seeded lots.
Best 8 thirds ranked by (points, strength); slotted into the official
third-place positions by constraint matching (FIFA Annex C logic).
Knockouts: higher strength advances; exact ties go to "penalties"
(seeded RNG, seed=1995 — the year MICS began).
"""
import pandas as pd, numpy as np, json, itertools, re
from pathlib import Path

rng = np.random.default_rng(1995)
HERE = Path(__file__).resolve().parent
cat = pd.read_csv(HERE / "data" / "mics_surveys_catalogue.csv")
assert len(cat) == 427, "Row count changed — re-baseline before simulating"

NAME = {"South Korea":"-","Ivory Coast":"Cote d'Ivoire","Cape Verde":"-",
        "DR Congo":"Congo DR","Bosnia and Herzegovina":"Bosnia & Herzegovina",
        "Türkiye":"Turkiye","England":"-","Scotland":"-","Curacao":"-","Haiti":"-",
        "Japan":"-","Australia":"-","Jordan":"-","Brazil":"-","Colombia":"-",
        "Ecuador":"-","New Zealand":"-","South Africa":"-","France":"-","Spain":"-",
        "Germany":"-","Portugal":"-","Netherlands":"-","Belgium":"-","Switzerland":"-",
        "Austria":"-","Norway":"-","Sweden":"-","Czechia":"-","United States":"-",
        "Canada":"-"}

GROUPS = {"A":["Mexico","South Africa","South Korea","Czechia"],
          "B":["Canada","Switzerland","Qatar","Bosnia and Herzegovina"],
          "C":["Brazil","Morocco","Haiti","Scotland"],
          "D":["United States","Paraguay","Australia","Türkiye"],
          "E":["Germany","Curacao","Ivory Coast","Ecuador"],
          "F":["Netherlands","Japan","Tunisia","Sweden"],
          "G":["Belgium","Egypt","Iran","New Zealand"],
          "H":["Spain","Cape Verde","Saudi Arabia","Uruguay"],
          "I":["France","Senegal","Norway","Iraq"],
          "J":["Argentina","Algeria","Austria","Jordan"],
          "K":["Portugal","Uzbekistan","Colombia","DR Congo"],
          "L":["England","Croatia","Ghana","Panama"]}

def first_year(y):
    m = re.match(r"(\d{4})", str(y)); return int(m.group(1)) if m else 0

def strength(team):
    key = NAME.get(team, team)
    sub = cat[cat["country"] == key]
    if sub.empty: return 0.0, (0,0,0)
    n = len(sub); rounds = sub["round"].nunique()
    m7 = sub[sub["round"]=="MICS7"]
    m7_bonus = 2 if len(m7) else 0
    stage = 1 if (m7["status"]=="Data processing / analysis").any() else 0
    recent = 1 if sub["year"].map(first_year).max() >= 2020 else 0
    return 2*n + 3*rounds + m7_bonus + stage + recent, (rounds, n, first_year(sub["year"].max()))

S = {t: strength(t) for g in GROUPS.values() for t in g}

# ---- group stage ----------------------------------------------------------
standings = {}
for g, teams in GROUPS.items():
    pts = {t: 0 for t in teams}
    for a, b in itertools.combinations(teams, 2):
        if S[a][0] > S[b][0]: pts[a] += 3
        elif S[b][0] > S[a][0]: pts[b] += 3
        else: pts[a] += 1; pts[b] += 1
    order = sorted(teams, key=lambda t: (pts[t], S[t][0], S[t][1], rng.random()), reverse=True)
    standings[g] = order
    print(f"Group {g}: " + " | ".join(f"{i+1}.{t} ({pts[t]}pts, s={S[t][0]:.0f})" for i, t in enumerate(order)))

W  = {g: standings[g][0] for g in GROUPS}
RU = {g: standings[g][1] for g in GROUPS}
third_rank = sorted(GROUPS, key=lambda g: (S[standings[g][2]][0], rng.random()), reverse=True)
best8 = third_rank[:8]
print("\nBest 8 thirds (groups):", best8, "->", [standings[g][2] for g in best8])

# ---- official Round of 32 (FIFA final-draw bracket) ----------------------
SLOTS = {74:"ABCDF", 77:"CDFGH", 79:"CEFHI", 80:"EHIJK", 81:"BEFIJ", 82:"AEHIJ", 85:"EFGIJ", 87:"DEIJL"}
def assign(slots, thirds):                       # backtracking match (Annex C logic)
    if not slots: return {}
    m, rest = slots[0], slots[1:]
    for g in [g for g in thirds if g in SLOTS[m]]:
        sub = assign(rest, [x for x in thirds if x != g])
        if sub is not None: sub[m] = g; return sub
    return None
T = assign(sorted(SLOTS), best8); assert T, "No valid third-place allocation"

R32 = {73:(RU["A"],RU["B"]), 74:(W["E"],standings[T[74]][2]), 75:(W["F"],RU["C"]),
       76:(W["C"],RU["F"]), 77:(W["I"],standings[T[77]][2]), 78:(RU["E"],RU["I"]),
       79:(W["A"],standings[T[79]][2]), 80:(W["L"],standings[T[80]][2]),
       81:(W["D"],standings[T[81]][2]), 82:(W["G"],standings[T[82]][2]),
       83:(RU["K"],RU["L"]), 84:(W["H"],RU["J"]), 85:(W["B"],standings[T[85]][2]),
       86:(W["J"],RU["H"]), 87:(W["K"],standings[T[87]][2]), 88:(RU["D"],RU["G"])}

def play(a, b, label):
    ka, kb = (S[a][0],)+S[a][1], (S[b][0],)+S[b][1]
    if ka == kb:
        win = a if rng.random() < 0.5 else b
        print(f"{label}: {a} vs {b} -> {win} (on penalties)")
    else:
        win = a if ka > kb else b
        print(f"{label}: {a} ({S[a][0]:.0f}) vs {b} ({S[b][0]:.0f}) -> {win}")
    return win

print("\n-- Round of 32 --")
w = {m: play(*R32[m], f"M{m}") for m in sorted(R32)}
print("\n-- Round of 16 --")
R16 = {89:(74,77),90:(73,75),91:(76,78),92:(79,80),93:(83,84),94:(81,82),95:(86,88),96:(85,87)}
w16 = {m: play(w[a], w[b], f"M{m}") for m,(a,b) in R16.items()}
print("\n-- Quarterfinals --")
QF = {97:(89,90),98:(93,94),99:(91,92),100:(95,96)}
wqf = {m: play(w16[a], w16[b], f"M{m}") for m,(a,b) in QF.items()}
print("\n-- Semifinals --")
sf1 = play(wqf[97], wqf[98], "SF1 (Dallas)")
sf2 = play(wqf[99], wqf[100], "SF2 (Atlanta)")
print("\n-- Third place (Miami) --")
losers = [t for t in (wqf[97],wqf[98],wqf[99],wqf[100]) if t not in (sf1,sf2)]
third = play(losers[0], losers[1], "3rd")
print("\n-- FINAL, MetLife Stadium, July 19 --")
champ = play(sf1, sf2, "FINAL")
print(f"\n*** MICS WORLD CUP CHAMPION: {champ} ***")
