"""
does_okun_break_in_recessions.py
Does Okun's Law always break in the goods sectors during a downturn?

WHY THIS EXISTS
The obvious deflating objection to this whole sub-project: maybe the 2024-2025
goods-sector inversion is nothing, because Okun's Law always comes apart in
construction, manufacturing and transportation when the economy turns down.
These are the most cyclical sectors in the economy. If their output-unemployment
correlation flips sign in every recession, then the 2024-2025 flip needs no
special explanation, and the long rate lag documented elsewhere in this folder is
an elaborate answer to a question that was never puzzling.

That objection is entirely testable and has never been tested here. This does it.

METHOD
Rolling 12-quarter correlation between year-over-year sector real output growth
and the year-over-year change in the sector unemployment rate. Okun's Law working
means a NEGATIVE correlation: output up, unemployment down. An inversion is a
positive correlation. The rolling series is then summarised inside four windows.

Two statistics are reported per window, the MEAN correlation and the SHARE of
quarters with a positive correlation. Deliberately not the maximum: a maximum
rises mechanically with the number of windows observed, so comparing the max over
a seven-year calm period against the max over a two-year recession is rigged
toward finding inversions in the longer window. An earlier cut of this test used
the max and produced a misleading table.

BEA real value added by industry starts in 2005, so the sample covers the GFC,
COVID, the 2013-2019 expansion as a calm benchmark, and the current episode.
COVID quarters are deliberately NOT excluded, because the question here is
precisely what downturns do.

RESULT: THE OBJECTION IS BACKWARDS
Okun's Law does not break in these sectors during recessions. It works better
than usual:

    window              Construction     Manufacturing   Transportation
    GFC 2008-2010          -0.90             -0.90            -0.84
    COVID 2020-2021        -0.74             -0.86            -0.90
    calm 2013-2019         +0.13             -0.15            -0.10
    2024-2026 current      +0.58             +0.30            +0.03

Across both recessions in the sample, in all three sectors, not one quarter shows
a positive correlation. Zero of 51. A sharp downturn drives output and
unemployment hard in opposite directions at the same time, which is Okun's Law
operating at full strength. The relationship is cyclically activated: it is
tightest exactly when the cycle is loudest.

WHAT THAT DOES AND DOES NOT BUY THIS SUB-PROJECT
It removes the deflating objection. The current inversion is not the ordinary
behaviour of goods sectors in a downturn, and it is happening in an expansion
rather than a recession, so a recession-based dismissal does not work.

It does not make the inversion large. The calm 2013-2019 benchmark is the honest
comparison, not the recessions, because the present period resembles a calm
expansion far more than it resembles 2008. Against that benchmark, construction
and manufacturing are both clearly outside their normal ranges, each by the same
+0.44 (construction +0.58 against a calm mean of +0.13, manufacturing +0.30
against -0.15). Transportation is not distinguishable from calm-period noise at
all (+0.03 against -0.10), so the "three sectors moved together" framing rests on
two of them. In calm periods these
correlations wander across zero routinely, 36 to 61 percent of quarters positive
depending on the sector.

That is consistent with what `why_in_sync.py` already found by a different route,
that the inversion reverses at a 20-quarter window and should be treated as a
short-window artifact. The hiring slowdown remains the durable finding; the
inversion remains thin; and the reason it is thin is not that recessions always
produce inversions, because they demonstrably do not.

Reads FRED CSVs from ../FRED-Data/. Writes does_okun_break_in_recessions.png.
"""

import os
import glob
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE     = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(HERE, "..", "FRED-Data") + os.sep
WIN      = 12   # quarters

SECTORS = {
    "Construction":   ("construction_value_added_RVAC.csv",
                       "construction_unemployment_rate_LNU04032231.csv"),
    "Manufacturing":  ("manufacturing_value_added_RVAMA.csv",
                       "manufacturing_unemployment_rate_LNU04032232.csv"),
    "Transportation": ("transportation_warehousing_value_added_RVAT.csv",
                       "transportation_utilities_unemployment_rate_LNU04032236.csv"),
}

WINDOWS = [
    ("GFC 2008-2010",     "2008-01-01", "2010-12-31", "recession"),
    ("COVID 2020-2021",   "2020-01-01", "2021-12-31", "recession"),
    ("calm 2013-2019",    "2013-01-01", "2019-12-31", "expansion"),
    ("2024-2026 current", "2024-01-01", "2026-12-31", "current"),
]


def find(f):
    p = os.path.join(DATA_DIR, f)
    return p if os.path.exists(p) else glob.glob(os.path.join(DATA_DIR, "*" + f))[0]


def load(f):
    d = pd.read_csv(find(f))
    d.columns = [c.strip() for c in d.columns]
    d[d.columns[0]] = pd.to_datetime(d[d.columns[0]])
    d = d.set_index(d.columns[0])
    return pd.to_numeric(d.iloc[:, 0], errors="coerce").dropna()


rolls = {}
for name, (of, uf) in SECTORS.items():
    y = (load(of).pct_change(4) * 100).dropna()
    u = load(uf).resample("QS").mean().diff(4).dropna()
    j = pd.DataFrame({"y": y, "u": u}).dropna()
    rolls[name] = j["y"].rolling(WIN).corr(j["u"]).dropna()

print("=" * 100)
print("DOES OKUN'S LAW ALWAYS BREAK IN THE GOODS SECTORS DURING A DOWNTURN?")
print("=" * 100)
print(f"\nRolling {WIN}-quarter corr(sector output growth, change in sector unemployment).")
print("Okun's Law working = NEGATIVE. Inversion = POSITIVE.")
print("Mean and share-positive are reported because both are comparable across windows of")
print("different length. A maximum is not, and would favour finding inversions in the")
print("longest window by construction.\n")

print(f"{'window':<20}{'kind':<11}" + "".join(f"{n:>22}" for n in SECTORS))
print(f"{'':<31}" + "".join(f"{'mean    %pos     n':>22}" for _ in SECTORS))
rows = []
for lab, a, b, kind in WINDOWS:
    line = ""
    for name in SECTORS:
        s = rolls[name].loc[a:b]
        rows.append(dict(window=lab, kind=kind, sector=name,
                         mean=s.mean(), pos=(s > 0).mean(), n=len(s)))
        line += f"{s.mean():>+11.2f}{(s > 0).mean() * 100:>8.0f}%{len(s):>4}" if len(s) \
            else f"{'n/a':>22}"
    print(f"{lab:<20}{kind:<11}{line}")
T = pd.DataFrame(rows)

rec = T[T.kind == "recession"]
print(f"\n  Across both recessions, all three sectors: {int((rec.pos * rec.n).sum())} of "
      f"{int(rec.n.sum())} quarters show a positive correlation.")
print("  Okun's Law does not break in these sectors during a recession. It works BEST then.")
print("  A sharp downturn drives output and unemployment hard in opposite directions at the")
print("  same time, which is the law operating at full strength. So the current inversion")
print("  cannot be dismissed as what goods sectors normally do in a slump, and it is")
print("  happening in an expansion in any case.")

print("\n  The honest benchmark is the CALM period, not the recessions, because 2024-2026")
print("  resembles an expansion far more than it resembles 2008:\n")
calm = T[T.window == "calm 2013-2019"].set_index("sector")
cur = T[T.window == "2024-2026 current"].set_index("sector")
print(f"    {'sector':<16}{'calm mean':>11}{'current mean':>14}{'gap':>8}   verdict")
for name in SECTORS:
    gap = cur.loc[name, "mean"] - calm.loc[name, "mean"]
    v = ("clearly outside calm range" if gap > 0.35 else
         "modestly outside" if gap > 0.15 else "not distinguishable from calm noise")
    print(f"    {name:<16}{calm.loc[name, 'mean']:>+11.2f}{cur.loc[name, 'mean']:>+14.2f}"
          f"{gap:>+8.2f}   {v}")
print("\n  In calm periods these correlations wander across zero routinely "
      f"({calm.pos.min()*100:.0f} to {calm.pos.max()*100:.0f}% of")
print("  quarters positive). Construction and manufacturing are both clearly outside")
print("  their own calm ranges, by the same +0.44; transportation is not, so the 'three")
print("  sectors moved together' framing really rests on two of them.")
print("  This matches what why_in_sync.py found by a different route: the inversion is a")
print("  short-window artifact, and the hiring slowdown is the durable finding.")

# ---- chart -------------------------------------------------------------------
fig, axes = plt.subplots(1, 2, figsize=(17, 6.3))

ax = axes[0]
COLS = {"Construction": "#1f4e79", "Manufacturing": "#c0392b", "Transportation": "#e67e22"}
for name, r in rolls.items():
    ax.plot(r.index, r.values, lw=2.0, color=COLS[name], label=name)
ax.axhline(0, color="black", lw=1.2)
for lab, a, b, kind in WINDOWS:
    if kind == "recession":
        ax.axvspan(pd.Timestamp(a), pd.Timestamp(b), color="gray", alpha=0.22)
ax.axvspan(pd.Timestamp("2024-01-01"), pd.Timestamp("2026-12-31"), color="gold", alpha=0.20)
ax.text(pd.Timestamp("2009-01-01"), 0.88, "recessions", fontsize=9, color="dimgray")
ax.text(pd.Timestamp("2024-02-01"), 0.88, "now", fontsize=9, color="#7b241c")
ax.set_ylabel(f"rolling {WIN}q corr(output growth, Δ unemployment)", fontsize=10)
ax.set_title("Okun's Law is TIGHTEST in recessions, not broken by them\n"
             "Shaded grey = recessions. Every one drives the correlation hard negative.",
             fontsize=11.5, fontweight="bold")
ax.legend(fontsize=9, loc="lower left"); ax.grid(True, ls="--", alpha=0.35)

ax = axes[1]
labs = [w[0] for w in WINDOWS]
x = np.arange(len(labs)); w_ = 0.26
for i, name in enumerate(SECTORS):
    vals = [T[(T.window == l) & (T.sector == name)]["mean"].iloc[0] for l in labs]
    ax.bar(x + (i - 1) * w_, vals, w_, label=name, color=COLS[name])
ax.axhline(0, color="black", lw=1.2)
ax.set_xticks(x); ax.set_xticklabels([l.replace(" ", "\n", 1) for l in labs], fontsize=9)
ax.set_ylabel("mean rolling correlation", fontsize=10)
ax.set_title("The right comparison for now is the calm expansion\n"
             "Construction and Manufacturing clear it; Transportation does not",
             fontsize=11.5, fontweight="bold")
ax.legend(fontsize=9); ax.grid(True, axis="y", ls="--", alpha=0.35)

fig.suptitle("Testing the deflating objection: does Okun's Law always break in goods sectors "
             "when the economy turns down?", fontsize=13, fontweight="bold", y=1.02)
plt.tight_layout()
out = os.path.join(HERE, "does_okun_break_in_recessions.png")
plt.savefig(out, dpi=150, bbox_inches="tight")
print(f"\nChart saved: {out}")
