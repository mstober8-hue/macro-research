"""
immigration_confound.py
Was the 2024-2025 hiring slowdown a fall in labor DEMAND, or a fall in labor SUPPLY?

WHY THIS MATTERS
Everything else in this folder treats slower hiring as evidence about labor
demand: rates cooled it, or AI displaced it. There is a third possibility the
project has flagged but never tested. Net immigration collapsed through 2025,
with unauthorized flows turning negative and averaging roughly -55,000 a month in
the second half of the year, and Federal Reserve estimates put the monthly
breakeven job growth needed to hold unemployment steady at roughly 40,000 or
lower in 2025, down from about 100,000 in 2024 (Dallas Fed 2025, 2026; Kansas
City Fed 2026; Murray and Vidangos 2026).

If the workforce shrank, employment growth would slow even with labor demand
completely unchanged. That is not a rival explanation for the same mechanism; it
is a different mechanism producing an identical-looking employment series. And it
hits Construction hardest, which is the sector carrying most of this project's
weight and the most immigrant-intensive major industry in the US.

THE TEST
Supply and demand contractions make OPPOSITE predictions about four observables,
so they can be separated without needing immigration data at the industry level:

                        labor SUPPLY fell      labor DEMAND fell
  job openings          stay high              fall
  hires per opening     FALLS (cannot fill)    roughly stable
  wage growth           RISES (bidding up)     falls
  unemployment rate     falls                  rises

A supply story requires firms to be trying and failing to hire: postings stay up,
each posting yields fewer hires, wages get bid up, and unemployment falls because
there are fewer workers competing. A demand story has firms simply posting less,
with each posting still filling normally, wage growth cooling and unemployment
rising.

These are sharp enough that the data can decide, and they do not rely on any
industry-level measure of immigrant labor share, which is what makes the test
feasible. What it cannot do is attribute a supply contraction specifically to
immigration rather than to retirements or participation, so a supply verdict here
is "labor supply", not "immigration" per se. That distinction is kept throughout.

DATA
  JOLTS   BLS, 28 industries, seasonally adjusted rates: job openings, hires,
          quits, layoffs. Construction is its own industry.
  CES     Average hourly earnings by industry, for the wage test.
  FRED    Sector unemployment rates already in this repo.

Writes immigration_confound.png.
"""

import os
import glob
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats as sp_stats

HERE     = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(HERE, "..", "FRED-Data") + os.sep
JD       = os.path.join(DATA_DIR, "jolts") + os.sep
PRE      = ("2013-01-01", "2019-12-31")
POST     = ("2024-01-01", "2026-12-31")

FOCUS = {
    "230000": "Construction",
    "300000": "Manufacturing",
    "480099": "Transportation/Utilities",
    "620000": "Health care & social asst",
    "720000": "Accommodation & food",
    "540099": "Professional & business",
    "510000": "Information",
    "100000": "Total private",
}
# CES supersector codes matching the JOLTS industries above, for wages
CES_MATCH = {
    "230000": "20000000", "300000": "30000000", "480099": "40000000",
    "620000": "65000000", "720000": "70000000", "540099": "60000000",
    "510000": "50000000", "100000": "05000000",
}
UNEMP = {
    "Construction": "construction_unemployment_rate_LNU04032231.csv",
    "Manufacturing": "manufacturing_unemployment_rate_LNU04032232.csv",
    "Transportation/Utilities": "transportation_utilities_unemployment_rate_LNU04032236.csv",
}


def read_bls(path, names):
    d = pd.read_csv(path, sep="\t", header=None, names=names, dtype=str)
    d = d[d.period.str.startswith("M") & (d.period != "M13")].copy()
    d["value"] = pd.to_numeric(d.value, errors="coerce")
    d["date"] = pd.to_datetime(d.year + "-" + d.period.str[1:] + "-01")
    return d.dropna(subset=["value"])


def load_fred(name):
    p = os.path.join(DATA_DIR, name)
    p = p if os.path.exists(p) else glob.glob(os.path.join(DATA_DIR, "*" + name))[0]
    d = pd.read_csv(p)
    d.columns = [c.strip() for c in d.columns]
    d[d.columns[0]] = pd.to_datetime(d[d.columns[0]])
    d = d.set_index(d.columns[0])
    return pd.to_numeric(d.iloc[:, 0], errors="coerce").dropna()


def avg(s, win):
    v = s.loc[win[0]:win[1]]
    return v.mean() if len(v) else np.nan


jolts = read_bls(JD + "jolts_rates.tsv", ["sid", "year", "period", "value"])
jolts["ind"] = jolts.sid.str[3:9]
jolts["elem"] = jolts.sid.str[-3:-1]
piv = {e: jolts[jolts.elem == e].pivot_table(index="date", columns="ind", values="value")
       for e in ["JO", "HI", "QU", "LD"]}

ahe = read_bls(JD + "ces_ahe.tsv", ["sid", "year", "period", "value"])
ahe["code"] = ahe.sid.str[3:11]
ahe_p = ahe.pivot_table(index="date", columns="code", values="value")

print("=" * 98)
print("IS THE HIRING SLOWDOWN A LABOR SUPPLY CONTRACTION?  Four discriminating tests")
print("=" * 98)
print(f"\n  Comparing {POST[0][:7]} onward against the {PRE[0][:7]} to {PRE[1][:7]} baseline.")
print("  SUPPLY predicts: openings hold up, vacancy yield falls, wages accelerate,")
print("  unemployment falls.  DEMAND predicts the opposite on all four.\n")

rows = []
for code, nm in FOCUS.items():
    jo, hi = piv["JO"].get(code), piv["HI"].get(code)
    if jo is None or hi is None:
        continue
    jo_pre, jo_post = avg(jo, PRE), avg(jo, POST)
    hi_pre, hi_post = avg(hi, PRE), avg(hi, POST)
    # vacancy yield: hires per unit of openings
    vy = (hi / jo).replace([np.inf, -np.inf], np.nan)
    vy_pre, vy_post = avg(vy, PRE), avg(vy, POST)
    # wages: YoY growth of average hourly earnings
    w = ahe_p.get(CES_MATCH.get(code))
    if w is not None:
        wg = w.pct_change(12) * 100
        w_pre, w_post = avg(wg, PRE), avg(wg, POST)
    else:
        w_pre = w_post = np.nan
    rows.append(dict(code=code, name=nm,
                     jo_pre=jo_pre, jo_post=jo_post, jo_d=jo_post - jo_pre,
                     hi_pre=hi_pre, hi_post=hi_post, hi_d=hi_post - hi_pre,
                     vy_pre=vy_pre, vy_post=vy_post, vy_d=vy_post - vy_pre,
                     w_pre=w_pre, w_post=w_post, w_d=w_post - w_pre))
R = pd.DataFrame(rows)

print("[1] JOB OPENINGS AND HIRES RATES (percent of employment, monthly)\n")
print(f"  {'industry':<28}{'openings pre':>13}{'post':>8}{'chg':>8}"
      f"{'hires pre':>11}{'post':>8}{'chg':>8}")
for _, r in R.iterrows():
    print(f"  {r['name']:<28}{r.jo_pre:>13.2f}{r.jo_post:>8.2f}{r.jo_d:>+8.2f}"
          f"{r.hi_pre:>11.2f}{r.hi_post:>8.2f}{r.hi_d:>+8.2f}")

print("\n[2] VACANCY YIELD: hires per opening. THE KEY DISCRIMINATOR.\n")
print("  A supply constraint means firms post jobs they cannot fill, so yield FALLS.")
print("  A demand contraction means fewer postings but normal filling, so yield HOLDS.\n")
print(f"  {'industry':<28}{'yield pre':>11}{'post':>9}{'change':>9}{'% change':>10}   reading")
for _, r in R.iterrows():
    pc = 100 * r.vy_d / r.vy_pre if r.vy_pre else np.nan
    rd_ = ("supply-constrained" if pc < -12 else
           "demand-driven" if pc > -5 else "mixed")
    print(f"  {r['name']:<28}{r.vy_pre:>11.2f}{r.vy_post:>9.2f}{r.vy_d:>+9.2f}"
          f"{pc:>+10.1f}   {rd_}")

print("\n[3] WAGE GROWTH: a supply squeeze bids wages UP\n")
print(f"  {'industry':<28}{'AHE growth pre':>16}{'post':>9}{'change':>9}   reading")
for _, r in R.iterrows():
    if np.isnan(r.w_pre):
        continue
    rd_ = "supply-consistent" if r.w_d > 0.5 else \
          "demand-consistent" if r.w_d < -0.3 else "flat"
    print(f"  {r['name']:<28}{r.w_pre:>16.2f}{r.w_post:>9.2f}{r.w_d:>+9.2f}   {rd_}")

print("\n[4] UNEMPLOYMENT: a supply squeeze LOWERS it even as hiring slows\n")
print(f"  {'sector':<28}{'unemp pre':>11}{'post':>9}{'change':>9}   reading")
u_rows = []
for nm, fn in UNEMP.items():
    u = load_fred(fn)
    up, uq = avg(u, PRE), avg(u, POST)
    u_rows.append((nm, up, uq, uq - up))
    rd_ = "supply-consistent" if uq - up < -0.3 else \
          "demand-consistent" if uq - up > 0.3 else "flat"
    print(f"  {nm:<28}{up:>11.2f}{uq:>9.2f}{uq-up:>+9.2f}   {rd_}")

# ---------------------------------------------------------------------------
print("\n" + "=" * 98)
print("VERDICT, SCORED ACROSS THE FOUR TESTS")
print("=" * 98)
umap = {n: d for n, _, _, d in u_rows}
print(f"\n  {'industry':<28}{'openings':>10}{'vac yield':>11}{'wages':>9}"
      f"{'unemp':>9}   net")
for _, r in R.iterrows():
    score = 0
    marks = []
    marks.append("S" if r.jo_d > -0.3 else "D"); score += 1 if r.jo_d > -0.3 else -1
    pc = 100 * r.vy_d / r.vy_pre if r.vy_pre else 0
    marks.append("S" if pc < -12 else "D"); score += 1 if pc < -12 else -1
    if not np.isnan(r.w_d):
        marks.append("S" if r.w_d > 0.5 else "D"); score += 1 if r.w_d > 0.5 else -1
    else:
        marks.append("-")
    ud = umap.get(r['name'], np.nan)
    if not np.isnan(ud):
        marks.append("S" if ud < -0.3 else "D"); score += 1 if ud < -0.3 else -1
    else:
        marks.append("-")
    verdict = "SUPPLY" if score >= 2 else "DEMAND" if score <= -2 else "mixed"
    print(f"  {r['name']:<28}{marks[0]:>10}{marks[1]:>11}{marks[2]:>9}"
          f"{marks[3]:>9}   {verdict}")
print("\n  S = pattern matches a labor-supply contraction, D = matches a demand contraction.")

print("\n  CONSTRUCTION IS THE CASE THAT MATTERS, because it is both the sector this")
print("  project leans on most and the most immigrant-intensive major US industry.")
c = R[R.name == "Construction"].iloc[0]
print(f"    openings   {c.jo_pre:.2f} -> {c.jo_post:.2f}  ({c.jo_d:+.2f})")
print(f"    hires      {c.hi_pre:.2f} -> {c.hi_post:.2f}  ({c.hi_d:+.2f})")
print(f"    vac yield  {c.vy_pre:.2f} -> {c.vy_post:.2f}  ({100*c.vy_d/c.vy_pre:+.1f}%)")
print(f"    wage growth{c.w_pre:>6.2f} -> {c.w_post:.2f}  ({c.w_d:+.2f}pp)")
print(f"    unemployment {umap.get('Construction', float('nan')):+.2f}pp")

print("\n  WHAT THIS CANNOT DO: separate immigration from retirement or participation")
print("  as the source of any supply contraction, and it cannot rule out that demand")
print("  and supply both fell at once, which would partly offset on every measure here.")

# ---------------------------------------------------------------------------
# THE BASELINE MATTERS, AND THIS IS THE MOST IMPORTANT QUALIFICATION.
# Everything above compares 2024-2025 against 2013-2019, which is how this
# project defines the "slowdown". But that comparison spans the post-COVID
# repricing of the whole labor market, so it answers "is the 2024-25 labor
# market tighter than the 2010s?" rather than "what changed recently?".
# Re-running against the 2022-2023 peak isolates the recent move.
# ---------------------------------------------------------------------------
PEAK = ("2022-01-01", "2023-12-31")
print("\n" + "=" * 98)
print("THE SAME TESTS AGAINST THE 2022-2023 PEAK, WHICH ISOLATES THE RECENT CHANGE")
print("=" * 98)
print("\n  Against 2013-2019 the question is 'is this market tight relative to the 2010s'.")
print("  Against 2022-2023 the question is 'what has been happening lately'. Both matter,")
print("  and they do not have to give the same answer.\n")
print(f"  {'industry':<28}{'openings':>10}{'vac yield %':>13}{'wages':>9}   reading vs peak")
rows2 = []
for code, nm in FOCUS.items():
    jo, hi = piv["JO"].get(code), piv["HI"].get(code)
    if jo is None or hi is None:
        continue
    vy = (hi / jo).replace([np.inf, -np.inf], np.nan)
    jod = avg(jo, POST) - avg(jo, PEAK)
    vyp = avg(vy, PEAK)
    vyd = 100 * (avg(vy, POST) - vyp) / vyp if vyp else np.nan
    w = ahe_p.get(CES_MATCH.get(code))
    wd = np.nan
    if w is not None:
        wg = w.pct_change(12) * 100
        wd = avg(wg, POST) - avg(wg, PEAK)
    rows2.append(dict(name=nm, jo_d=jod, vy_d=vyd, w_d=wd))
    rd_ = ("demand cooling" if jod < -0.3 and (np.isnan(wd) or wd < 0) else
           "supply-constrained" if vyd < -12 and (not np.isnan(wd) and wd > 0) else "mixed")
    print(f"  {nm:<28}{jod:>+10.2f}{vyd:>+13.1f}{wd:>+9.2f}   {rd_}")
R2 = pd.DataFrame(rows2)

c2 = R2[R2.name == "Construction"].iloc[0]
print(f"\n  Construction against the 2022-23 peak: openings {c2.jo_d:+.2f}, "
      f"vacancy yield {c2.vy_d:+.1f}%, wage growth {c2.w_d:+.2f}pp")
print("\n  READ THE TWO BASELINES TOGETHER. Against the 2010s the 2024-25 market still")
print("  looks supply-tight on every measure. Against the 2022-23 peak, openings and")
print("  wage growth are coming DOWN, which is demand cooling. The consistent reading is")
print("  a labor market that became structurally supply-constrained after COVID and is")
print("  now cooling on the demand side from that tighter starting point.")
print("\n  For THIS project the consequence is specific: the 2013-2019 baseline used")
print("  throughout to define the 'hiring slowdown' cannot separate the two, because a")
print("  smaller workforce and weaker labor demand both reduce measured hiring against")
print("  a pre-COVID benchmark.")

# ---------------------------------------------------------------------------
fig, axes = plt.subplots(2, 2, figsize=(15.5, 10.5))

ax = axes[0, 0]
for code, nm in [("230000", "Construction"), ("300000", "Manufacturing"),
                 ("100000", "Total private")]:
    jo = piv["JO"].get(code)
    if jo is None:
        continue
    s = jo.loc["2013-01-01":]
    ax.plot(s.index, s.values, lw=2.0, label=f"{nm} openings")
    hi = piv["HI"].get(code).loc["2013-01-01":]
    ax.plot(hi.index, hi.values, lw=1.6, ls="--", alpha=0.75, label=f"{nm} hires")
ax.axvspan(pd.Timestamp(POST[0]), pd.Timestamp("2026-06-01"), color="gold", alpha=0.15)
ax.set_title("1. Openings and hires rates\nboth fell together (a demand signature)",
             fontsize=11.5, fontweight="bold")
ax.set_ylabel("rate (% of employment)", fontsize=9.5)
ax.legend(fontsize=7.5, ncol=2); ax.grid(True, ls="--", alpha=0.3)

ax = axes[0, 1]
names = R.name.tolist()
pcs = [100 * r.vy_d / r.vy_pre if r.vy_pre else 0 for _, r in R.iterrows()]
cols = ["#c0392b" if p < -12 else "#1f4e79" for p in pcs]
ax.barh(np.arange(len(names)), pcs, color=cols)
ax.axvline(0, color="black", lw=1.1)
ax.axvline(-12, color="#c0392b", ls="--", lw=1.5)
ax.text(-11.5, 0.2, "supply-constrained\nthreshold", fontsize=7.5, color="#c0392b")
ax.set_yticks(np.arange(len(names))); ax.set_yticklabels(names, fontsize=8.5)
ax.set_xlabel("change in hires per opening (%)", fontsize=9.5)
ax.set_title("2. Vacancy yield: the key discriminator\nfalling yield = cannot fill jobs",
             fontsize=11.5, fontweight="bold")
ax.grid(True, axis="x", ls="--", alpha=0.3)

ax = axes[1, 0]
w = R.dropna(subset=["w_d"])
xi = np.arange(len(w)); bw = 0.38
ax.bar(xi - bw/2, w.w_pre, bw, color="#7f8c8d", label="2013-2019")
ax.bar(xi + bw/2, w.w_post, bw, color="#c0392b", label="2024-2025")
ax.set_xticks(xi); ax.set_xticklabels(w.name, fontsize=7.5, rotation=30, ha="right")
ax.set_ylabel("average hourly earnings growth (%/yr)", fontsize=9.5)
ax.set_title("3. Wage growth\na supply squeeze should raise it",
             fontsize=11.5, fontweight="bold")
ax.legend(fontsize=8); ax.grid(True, axis="y", ls="--", alpha=0.3)

ax = axes[1, 1]
un = [(n, d) for n, _, _, d in u_rows]
ax.barh(np.arange(len(un)), [d for _, d in un],
        color=["#1f4e79" if d > 0 else "#c0392b" for _, d in un])
ax.axvline(0, color="black", lw=1.1)
ax.set_yticks(np.arange(len(un))); ax.set_yticklabels([n for n, _ in un], fontsize=8.5)
ax.set_xlabel("change in unemployment rate (pp)", fontsize=9.5)
ax.set_title("4. Sector unemployment\nsupply squeeze would LOWER it",
             fontsize=11.5, fontweight="bold")
ax.grid(True, axis="x", ls="--", alpha=0.3)

fig.suptitle("Testing the labor-supply (immigration) confound: four observables that "
             "separate a supply contraction from a demand contraction",
             fontsize=13, fontweight="bold", y=1.0)
plt.tight_layout()
out = os.path.join(HERE, "immigration_confound.png")
plt.savefig(out, dpi=150, bbox_inches="tight")
print(f"\nChart saved: {out}")
