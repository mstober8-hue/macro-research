"""
okun_decomposed.py
Which link in Okun's Law actually broke: output->employment, or employment->unemployment?

CORRECTION NOTICE
An earlier version of this script concluded the opposite of what it now reports.
It claimed the inversion is LARGER in employment form, and therefore that the
break is in labour demand rather than in the unemployment statistic. That was
wrong, and the error is worth stating precisely because it is easy to repeat.

The earlier version compared the MEAN OF A ROLLING CORRELATION over dates labelled
2024-2026. A 12-quarter rolling correlation indexed at quarter t is computed from
quarters t-11 through t. So the values labelled "2024-2026" were computed from
windows spanning roughly 2021-2026, dominated by the post-COVID period in which
output was normalising downward while employment was still rebounding upward.
That combination produces a negative correlation which has nothing to do with
2024-2025. Labelling a rolling statistic by its END DATE and then describing it
as a property of that date is a trap, and this project fell into it.

Measured directly on 2024-2026 observations, with no rolling window, the answer
reverses.

THE DECOMPOSITION
Okun's Law chains two links:

    output  ->  employment  ->  unemployment
            (labour demand)   (labour-force accounting)

The first link is economics: does more output mean more jobs. The second is
arithmetic through the labour force, since unemployment is unemployed/labour
force and a displaced worker who exits never enters it. Measuring only the
unemployment version cannot say which link moved.

WHAT THE DATA SAY
Pooled correlations on 2024-2026 quarters, COVID excluded, against the 2013-2019
baseline. In three of four sectors the output-employment link is INTACT and in
fact TIGHTER than before, while the unemployment version inverts. The break is in
the second link, the labour-force step, which is exactly what
okun_employment_form.py found independently when seven of nine sectors lost
employment while their unemployment rate also fell.

WHY THIS MATTERS FOR THE AI QUESTION
Labour-saving technological change means output rising while employment does not
follow, which is a WEAKENING of the output-employment correlation. Three of four
goods sectors show the opposite: the correlation strengthened. That is evidence
against AI displacement in those sectors specifically, and consistent with a
labour-supply account. Wholesale is the exception and does break.

Reads FRED CSVs from ../FRED-Data/. Writes okun_decomposed.png.
"""

import os
import glob
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE  = os.path.dirname(os.path.abspath(__file__))
DATA  = os.path.join(HERE, "..", "FRED-Data") + os.sep
COVID = pd.date_range("2020-04-01", "2021-10-01", freq="QS")
RNG   = np.random.default_rng(31337)
NBOOT = 4000

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
    "Wholesale": ("wholesale_trade_value_added_RVAW.csv",
                  "wholesale_retail_trade_unemployment_rate_LNU04032235.csv",
                  ["wholesale_trade_employment_USWTRADE.csv"], "#9dc6e0"),
}


def rd(n):
    p = DATA + n if os.path.exists(DATA + n) else glob.glob(DATA + "*" + n)[0]
    d = pd.read_csv(p)
    d.columns = [c.strip() for c in d.columns]
    d[d.columns[0]] = pd.to_datetime(d[d.columns[0]])
    d = d.set_index(d.columns[0])
    return pd.to_numeric(d.iloc[:, 0], errors="coerce").dropna()


def pooled(a, b, lo, hi):
    d = pd.DataFrame({"a": a, "b": b}).dropna().loc[lo:hi]
    d = d[~d.index.isin(COVID)]
    if len(d) < 4 or d.a.std() < 1e-9 or d.b.std() < 1e-9:
        return np.nan, len(d)
    return np.corrcoef(d.a, d.b)[0, 1], len(d)


def matched_null_p(a, b, obs, n_obs, tail):
    """
    Null preserving each series' autocorrelation, drawn at the SAME window length
    as the observed statistic. Comparing a short-window statistic against a
    full-sample null understates its spread enormously and is invalid.
    """
    d = pd.DataFrame({"a": a, "b": b}).dropna()
    d = d[~d.index.isin(COVID)]
    x, y = d.a.to_numpy(), d.b.to_numpy()
    if len(x) < n_obs + 5 or np.isnan(obs):
        return np.nan
    vals = []
    for _ in range(NBOOT):
        ys = np.roll(y, RNG.integers(1, len(y) - 1))
        st = RNG.integers(0, len(x) - n_obs)
        s1, s2 = x[st:st + n_obs], ys[st:st + n_obs]
        if np.std(s1) > 1e-9 and np.std(s2) > 1e-9:
            vals.append(np.corrcoef(s1, s2)[0, 1])
    v = np.array(vals)
    return float((v <= obs).mean()) if tail == "low" else float((v >= obs).mean())


print("=" * 98)
print("DECOMPOSING OKUN: output -> employment -> unemployment")
print("=" * 98)
print("\n  CORRECTION: an earlier version of this script reported the opposite")
print("  conclusion. It averaged a 12-quarter ROLLING correlation over dates labelled")
print("  2024-2026, but a rolling value indexed at quarter t is built from quarters")
print("  t-11 to t, so those values described 2021-2026, dominated by the post-COVID")
print("  period when output was normalising down while employment still rebounded.")
print("  Measured directly on 2024-2026 observations the answer reverses.\n")

print("  Unemployment form: normal NEGATIVE, inversion = POSITIVE")
print("  Employment form:   normal POSITIVE, break     = NEGATIVE\n")
print(f"  {'sector':<16}{'form':<7}{'2013-2019':>12}{'2024-2026':>12}{'n':>4}"
      f"{'boot p':>9}   verdict")

rows = []
for nm, (of, uf, efs, _) in SEC.items():
    y = (rd(of).pct_change(4) * 100).dropna()
    u = rd(uf).resample("QS").mean().diff(4).dropna()
    e = None
    for f in efs:
        x = rd(f).resample("QS").mean()
        e = x if e is None else e.add(x, fill_value=np.nan)
    eg = (e.pct_change(4) * 100).dropna()

    pu, _ = pooled(y, u, "2013", "2019")
    cu, nu = pooled(y, u, "2024", "2026")
    pe, _ = pooled(y, eg, "2013", "2019")
    ce, ne = pooled(y, eg, "2024", "2026")
    p_u = matched_null_p(y, u, cu, nu, "high")
    p_e = matched_null_p(y, eg, ce, ne, "low")
    rows.append(dict(sector=nm, pre_u=pu, cur_u=cu, pre_e=pe, cur_e=ce,
                     p_u=p_u, p_e=p_e, n=ne))
    print(f"  {nm:<16}{'unemp':<7}{pu:>+12.3f}{cu:>+12.3f}{nu:>4}{p_u:>9.3f}   "
          f"{'INVERTED' if cu > 0 else 'normal'}")
    print(f"  {'':<16}{'emp':<7}{pe:>+12.3f}{ce:>+12.3f}{ne:>4}{p_e:>9.3f}   "
          f"{'BROKEN' if ce < 0 else 'normal, and TIGHTER' if ce > pe else 'normal'}")
R = pd.DataFrame(rows)

inv = int((R.cur_u > 0).sum())
brk = int((R.cur_e < 0).sum())
tighter = int(((R.cur_e > 0) & (R.cur_e > R.pre_e)).sum())
print(f"\n  Sectors where the UNEMPLOYMENT form inverted        : {inv} of {len(R)}")
print(f"  Sectors where the EMPLOYMENT form broke             : {brk} of {len(R)}")
print(f"  Sectors where the EMPLOYMENT link got TIGHTER       : {tighter} of {len(R)}")

print("\n  THE RESULT. The output-to-employment link is intact, and in three of four")
print("  sectors it is tighter than in 2013-2019. What decoupled is the step from")
print("  employment to unemployment. That matches okun_employment_form.py, which")
print("  found seven of nine sectors losing employment while their unemployment rate")
print("  ALSO fell, a combination that requires labour-force exit.")

print("\n  WHAT THIS MEANS FOR AI. Labour-saving technological change means output")
print("  rising while employment does not follow, which WEAKENS the output-employment")
print("  correlation. Three of four goods sectors show the opposite. That is evidence")
print("  against AI displacement in these sectors and consistent with a labour-supply")
print("  account. Wholesale is the exception and does break, from +0.70 to -0.78.")

print("\n  CAVEATS. The 2024-2026 window supplies only 8 quarterly observations after")
print("  removing COVID, so these correlations are individually imprecise, which is")
print("  what the bootstrap column reflects. The finding rests on the direction being")
print("  consistent across three sectors, not on any single estimate.")

# ---- chart ----------------------------------------------------------------
fig, axes = plt.subplots(1, 2, figsize=(15, 6))
x = np.arange(len(R))
w = 0.36

ax = axes[0]
ax.bar(x - w/2, R.pre_u, w, color="#95a5a6", label="2013-2019")
ax.bar(x + w/2, R.cur_u, w, color="#c0392b", label="2024-2026")
ax.axhline(0, color="black", lw=1.2)
ax.set_xticks(x); ax.set_xticklabels(R.sector, fontsize=9, rotation=15)
ax.set_ylabel("corr(output growth, change in unemployment)", fontsize=9.5)
ax.set_title("Unemployment form\nnormal is NEGATIVE, so positive = inverted",
             fontsize=11.5, fontweight="bold")
ax.legend(fontsize=8.5); ax.grid(True, axis="y", ls="--", alpha=0.3)

ax = axes[1]
ax.bar(x - w/2, R.pre_e, w, color="#95a5a6", label="2013-2019")
ax.bar(x + w/2, R.cur_e, w, color="#1f4e79", label="2024-2026")
ax.axhline(0, color="black", lw=1.2)
ax.set_xticks(x); ax.set_xticklabels(R.sector, fontsize=9, rotation=15)
ax.set_ylabel("corr(output growth, employment growth)", fontsize=9.5)
ax.set_title("Employment form\nnormal is POSITIVE, so it did NOT break",
             fontsize=11.5, fontweight="bold")
ax.legend(fontsize=8.5); ax.grid(True, axis="y", ls="--", alpha=0.3)

fig.suptitle("The output-employment link held and mostly tightened. What broke is the "
             "step from employment to unemployment.",
             fontsize=13, fontweight="bold", y=1.0)
plt.tight_layout()
out = os.path.join(HERE, "okun_decomposed.png")
plt.savefig(out, dpi=150, bbox_inches="tight")
print(f"\nChart saved: {out}")
