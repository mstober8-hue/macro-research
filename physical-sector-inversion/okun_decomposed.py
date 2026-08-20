"""
okun_decomposed.py
Does any of the timing work actually bear on Okun's Law? Decomposing the question.

THE CHALLENGE THIS ANSWERS
The timing mechanism (unemployment responds to a rate shock before output does)
was invented to explain why the measured Okun correlation flipped sign. But it
tests how output and unemployment each respond to a MONETARY SHOCK, and infers
their relationship to each other from that. It is two steps removed from Okun's
Law, and it failed on its own terms in timing_stress_test.py.

The direct question was answerable the whole time. Okun's Law is a chain:

    output  ->  employment  ->  unemployment

The first link is labour demand: does more output mean more jobs. The second is
an accounting identity that depends on the labour force, since unemployment is
unemployed/labour force and a displaced worker who exits the labour force never
appears in it. Okun's Law as normally measured collapses both links into one
coefficient, so when it moves, either link could be responsible.

okun_employment_form.py showed the second link is compromised here: seven of nine
sectors lost employment while their unemployment rate ALSO fell, which requires
labour-force exit. The natural next hypothesis is that the whole "Okun inversion"
is an artifact of that, and that the output-employment relationship is intact.

THAT HYPOTHESIS IS WRONG, AND THIS SCRIPT SHOWS WHY.
Measured on employment instead of unemployment, the inversion is not weaker. It
is STRONGER, and it is unambiguous. Employment is a headcount, not a rate, so it
cannot be distorted by labour-force exit at all. Whatever is happening is a break
in the output-to-employment link itself, which is the labour-demand link, not a
measurement problem in the unemployment statistic.

WHAT IS MEASURED
  Unemployment form  corr(output growth, 4q change in unemployment), 12q rolling.
                     Normal is NEGATIVE. Inversion means it goes POSITIVE.
  Employment form    corr(output growth, employment growth), 12q rolling.
                     Normal is POSITIVE. A break means it goes toward zero or
                     NEGATIVE, i.e. output rising while employment falls.

Reads FRED CSVs from ../FRED-Data/. Writes okun_decomposed.png.
"""

import os
import glob
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "FRED-Data") + os.sep
W = 12

SEC = {
    "Construction": ("construction_value_added_RVAC.csv",
                     "construction_unemployment_rate_LNU04032231.csv",
                     ["construction_employment_USCONS.csv"], "#1f3b73"),
    "Manufacturing": ("manufacturing_value_added_RVAMA.csv",
                      "manufacturing_unemployment_rate_LNU04032232.csv",
                      ["manufacturing_employment_MANEMP.csv"], "#3f7cac"),
    "Transportation": ("transportation_warehousing_value_added_RVAT.csv",
                       "transportation_utilities_unemployment_rate_LNU04032236.csv",
                       ["transportation_warehousing_employment_CES4300000001.csv",
                        "utilities_employment_CES4422000001.csv"], "#6fb0d6"),
}


def rd(n):
    p = DATA + n if os.path.exists(DATA + n) else glob.glob(DATA + "*" + n)[0]
    d = pd.read_csv(p)
    d.columns = [c.strip() for c in d.columns]
    d[d.columns[0]] = pd.to_datetime(d[d.columns[0]])
    d = d.set_index(d.columns[0])
    return pd.to_numeric(d.iloc[:, 0], errors="coerce").dropna()


def roll(a, b):
    d = pd.DataFrame({"a": a, "b": b}).dropna()
    idx = d.index.tolist()
    o = {}
    for i in range(W, len(idx) + 1):
        w = d.iloc[i - W:i]
        if w.a.std() > 1e-9 and w.b.std() > 1e-9:
            o[idx[i - 1]] = np.corrcoef(w.a, w.b)[0, 1]
    return pd.Series(o)


print("=" * 96)
print("DECOMPOSING OKUN: output -> employment -> unemployment")
print("=" * 96)
print("\n  Okun's Law chains two links. The first is labour demand (does output growth")
print("  mean job growth). The second is an accounting step through the labour force.")
print("  Measuring only the unemployment version cannot tell you which link moved.\n")
print("  Unemployment form: normal NEGATIVE, inversion means POSITIVE.")
print("  Employment form:   normal POSITIVE, break means NEGATIVE.\n")

res = {}
print(f"  {'sector':<16}{'form':<7}{'2013-19':>10}{'2024-26':>10}{'extreme':>10}   broke?")
for nm, (of, uf, efs, _) in SEC.items():
    y = (rd(of).pct_change(4) * 100).dropna()
    u = rd(uf).resample("QS").mean().diff(4).dropna()
    e = None
    for f in efs:
        x = rd(f).resample("QS").mean()
        e = x if e is None else e.add(x, fill_value=np.nan)
    eg = (e.pct_change(4) * 100).dropna()
    ru, re_ = roll(y, u), roll(y, eg)
    res[nm] = (ru, re_)
    a1, a2, a3 = ru.loc["2013":"2019"].mean(), ru.loc["2024":"2026"].mean(), ru.loc["2024":"2026"].max()
    b1, b2, b3 = re_.loc["2013":"2019"].mean(), re_.loc["2024":"2026"].mean(), re_.loc["2024":"2026"].min()
    print(f"  {nm:<16}{'unemp':<7}{a1:>+10.3f}{a2:>+10.3f}{a3:>+10.3f}   "
          f"{'YES' if a3 > 0 else 'no'}")
    print(f"  {'':<16}{'emp':<7}{b1:>+10.3f}{b2:>+10.3f}{b3:>+10.3f}   "
          f"{'YES' if b3 < 0 else 'no'}")

print("\n  THE RESULT. The inversion is present in BOTH forms, and the employment form")
print("  is the more extreme of the two in every sector. Employment is a headcount,")
print("  not a rate, so labour-force exit cannot touch it. The break is therefore in")
print("  the output-to-EMPLOYMENT link, which is labour demand, and is not an artifact")
print("  of how unemployment is measured.")
print("\n  Output growing while employment falls is the literal description of")
print("  labour-saving change. That does not identify AI as the cause: it is equally")
print("  the description of automation, offshoring, or a capital-labour substitution")
print("  of any kind. What it does rule out is the reading that nothing real happened")
print("  to the output-labour relationship.")

print("\n  CAVEATS. The 2013-2019 baseline correlation in employment form is only")
print("  +0.09 to +0.27, so the relationship was weak to begin with and the move to")
print("  -0.5 or lower is a large swing from a low base. A 12-quarter rolling window")
print("  over 2024-2026 is roughly 8 usable windows, and why_in_sync.py showed the")
print("  unemployment-form inversion reverses at 20-quarter windows. The employment")
print("  form has not been tested at longer windows here and should be before it is")
print("  leaned on.")

fig, axes = plt.subplots(1, 3, figsize=(18, 5.8))
for i, (nm, (ru, re_)) in enumerate(res.items()):
    ax = axes[i]
    ax.axhline(0, color="black", lw=1.1)
    a = ru.loc["2010":]
    b = re_.loc["2010":]
    ax.plot(a.index, a.values, lw=2.3, color="#c0392b",
            label="unemployment form (normal < 0)")
    ax.plot(b.index, b.values, lw=2.3, color="#1f4e79",
            label="employment form (normal > 0)")
    ax.axvspan(pd.Timestamp("2024-01-01"), b.index[-1], color="gold", alpha=0.15)
    ax.set_title(nm, fontsize=12, fontweight="bold")
    ax.set_ylim(-1.05, 1.05)
    if i == 0:
        ax.set_ylabel("rolling 12q correlation", fontsize=9.5)
        ax.legend(fontsize=8, loc="lower left")
    ax.grid(True, ls="--", alpha=0.3)
fig.suptitle("The inversion is not an unemployment artifact: it is larger in employment form, "
             "which labour-force exit cannot distort", fontsize=13, fontweight="bold", y=1.02)
plt.tight_layout()
out = os.path.join(HERE, "okun_decomposed.png")
plt.savefig(out, dpi=150, bbox_inches="tight")
print(f"\nChart saved: {out}")
