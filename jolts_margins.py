"""
jolts_margins.py
WHICH labor-market margin moved, and does AI replaceability predict it?

WHY THIS EXISTS
Every AI test in this project so far has used employment or productivity: a net
headcount number, or output per head. Both are outcomes. Neither can say HOW a
sector got there, and three very different stories produce the same fall in net
employment growth:

    displacement    firms let workers go             -> LAYOFFS rise
    hiring freeze   firms stop backfilling attrition -> OPENINGS fall, layoffs flat
    labor supply    firms want workers, cannot find  -> OPENINGS hold, HIRES fall

Those are observationally identical in the employment series this project has
used, and they mean completely different things. Only the first is AI
displacement in the sense the literature means. The third is the immigration
objection PAPER.md Section 6 flags as untestable.

JOLTS separates them: job openings (labor DEMAND), hires (realized MATCHES),
layoffs and discharges (involuntary separation), quits (voluntary, a proxy for
worker confidence), monthly, per sector.

CORRECTION TO PAPER.md SECTION 6
That section states FRED carries JOLTS detail for only two of the nine sectors
examined here. That is wrong. FRED carries all four rates for all nine sectors,
307 monthly observations each from 2000-12, under the codes mapped in SECTORS
below. The two-sector limitation was a data-collection gap, not a data-
availability one.

TWO METHOD NOTES THAT MATTER
1. These are the UNADJUSTED (JTU) series, because FRED's seasonally adjusted
   (JTS) layoffs series do not exist for six of the nine sectors, which would
   gut the displacement test. Seasonality is handled instead with 12-month
   trailing means, so every window compares a full year against a full year.
   Comparing a Jan-Jun partial year against full-year averages would be a
   seasonal mismatch: January layoffs run high in the unadjusted data, so a
   half-year window manufactures a spike that is not there.
2. The 2021-2023 reopening was its own regime, with an openings boom and a
   collapsed fill rate that had nothing to do with AI. Averaging 2024-2026
   against 2015-2019 blends the unwinding of that boom into the AI window and
   produces the wrong diagnosis. So both a structural comparison (latest 12
   months vs 2015-2019) and a recent one (latest 12 months vs calendar 2023)
   are reported, and the year-by-year path is printed so the direction of
   travel is visible rather than averaged away.

WHAT THIS DOES AND DOES NOT FIX
It does not fix statistical power. The cross-section is still nine industries,
so the critical |r| for p < 0.05 is still 0.666, and a sector-month panel does
not help because replaceability is time-invariant within sector and would be
absorbed by any sector fixed effect, leaving the effective cluster count at 9.
What JOLTS buys is MECHANISM DISCRIMINATION: it rules stories in and out on
sign and pattern, which the employment series cannot do at any sample size.
Read the signs and the sector-by-sector pattern, not the p-values.

Reads FRED-Data/jolts_*.csv. Writes jolts_margins.png.
"""

import os
import glob
import warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats as sp

warnings.filterwarnings("ignore")

DATA     = "FRED-Data/"
BASE     = ("2015-01-01", "2019-12-31")   # clean post-GFC, pre-COVID, pre-AI baseline
MID      = "2023-12-01"                   # end of the reopening regime
ROLL     = 12                             # months, to deseasonalize the unadjusted series

# sector: (jolts file stem, replaceability, AIIE, rate-model standing on employment)
# Standing is from physical-sector-inversion/does_the_lag_solve_it.py: |fit r| >= 0.35
# regressing 1991-2021 employment growth on FFR at lag 9. It marks the sectors
# whose hiring the rate cycle demonstrably does explain. FRED JOLTS industry
# codes are in the third field.
SECTORS = {
    "Information":                ("information_sector",             0.325,  1.268, False, "5100"),
    "Financial Activities":       ("financial_activities",           0.267,  1.538, False, "510099"),
    "Professional & Business":    ("professional_business_services", 0.233,  0.654, False, "540099"),
    "Wholesale Trade":            ("wholesale_trade",                0.207,  0.264, True,  "4200"),
    "Education & Health":         ("education_health",               0.152,  0.775, True,  "6000"),
    "Manufacturing":              ("manufacturing",                  0.138, -0.484, True,  "3000"),
    "Transportation & Utilities": ("transportation_utilities",       0.120, -0.342, True,  "480099"),
    "Construction":               ("construction",                   0.091, -0.997, True,  "2300"),
    "Leisure & Hospitality":      ("leisure_hospitality",            0.088, -0.315, True,  "7000"),
}

MARGINS = {"openings": "job_openings_rate", "hires": "hires_rate",
           "layoffs": "layoffs_rate", "quits": "quits_rate"}


def load(stem, margin):
    hits = glob.glob(os.path.join(DATA, f"jolts_{stem}_{margin}_*.csv"))
    if not hits:
        raise FileNotFoundError(f"no JOLTS file for {stem}/{margin}")
    d = pd.read_csv(hits[0])
    d.columns = [c.strip() for c in d.columns]
    d[d.columns[0]] = pd.to_datetime(d[d.columns[0]])
    d = d.set_index(d.columns[0])
    return pd.to_numeric(d.iloc[:, 0], errors="coerce").dropna()


rows, series = [], {}
for name, (stem, rep, aiie, standing, _) in SECTORS.items():
    rec = dict(sector=name, rep=rep, aiie=aiie, standing=standing)
    s = {}
    for key, margin in MARGINS.items():
        x = load(stem, margin)
        r12 = x.rolling(ROLL).mean()
        s[key] = x
        s[key + "_r12"] = r12
        rec[f"{key}_base"] = x.loc[BASE[0]:BASE[1]].mean()   # 5 whole years, no seasonal bias
        rec[f"{key}_mid"] = r12.loc[MID]                     # 12 months ending Dec 2023
        rec[f"{key}_now"] = r12.iloc[-1]                     # latest complete 12 months
        rec[f"d_{key}"] = rec[f"{key}_now"] - rec[f"{key}_base"]
        rec[f"dr_{key}"] = rec[f"{key}_now"] - rec[f"{key}_mid"]
    fill = (s["hires"] / s["openings"]).rolling(ROLL).mean()
    rec["fill_base"] = (s["hires"] / s["openings"]).loc[BASE[0]:BASE[1]].mean()
    rec["fill_now"] = fill.iloc[-1]
    rec["d_fill"] = rec["fill_now"] - rec["fill_base"]
    s["fill_r12"] = fill
    series[name] = s
    rows.append(rec)

R = pd.DataFrame(rows).sort_values("rep", ascending=False).reset_index(drop=True)
LATEST = series["Information"]["openings_r12"].dropna().index[-1]
WIN = f"{(LATEST - pd.DateOffset(months=11)).strftime('%b %Y')} to {LATEST.strftime('%b %Y')}"

print("=" * 106)
print(f"JOLTS MARGINS   latest 12 months ({WIN})  vs  baseline 2015-2019")
print("=" * 106)
print("\nChange in each rate, percentage points. Sorted by AI replaceability, high to low.\n")
print(f"{'sector':<28}{'rep':>6}{'d openings':>12}{'d hires':>10}{'d layoffs':>11}"
      f"{'d quits':>10}{'d fill':>9}")
for _, x in R.iterrows():
    print(f"{x.sector:<28}{x.rep:>6.3f}{x.d_openings:>+12.2f}{x.d_hires:>+10.2f}"
          f"{x.d_layoffs:>+11.2f}{x.d_quits:>+10.2f}{x.d_fill:>+9.2f}")
print(f"\n{'mean across all nine':<34}{R.d_openings.mean():>+12.2f}{R.d_hires.mean():>+10.2f}"
      f"{R.d_layoffs.mean():>+11.2f}{R.d_quits.mean():>+10.2f}{R.d_fill.mean():>+9.2f}")

print("\n" + "-" * 106)
print("TEST 1  THE DISPLACEMENT TEST. If AI is displacing workers, layoffs rise where")
print("        jobs are most replaceable. This is the test employment data cannot run.")
print("-" * 106 + "\n")
print(f"{'sector':<28}{'rep':>6}{'layoffs 2015-19':>17}{'layoffs now':>13}{'change':>9}   verdict")
for _, x in R.iterrows():
    v = "LAYOFFS UP" if x.d_layoffs > 0.15 else ("flat" if x.d_layoffs > -0.15 else "layoffs DOWN")
    print(f"{x.sector:<28}{x.rep:>6.3f}{x.layoffs_base:>17.2f}{x.layoffs_now:>13.2f}"
          f"{x.d_layoffs:>+9.2f}   {v}")
up = R[R.d_layoffs > 0.15]
print(f"\n  Sectors with materially higher layoffs than pre-AI: {len(up)} of 9"
      f"{' (' + ', '.join(up.sector) + ')' if len(up) else ''}")
print(f"  Mean change across all nine: {R.d_layoffs.mean():+.2f}pp")
print("  A broad AI-displacement story predicts this column is positive and scales with")
print("  replaceability. Read the column and judge directly.")

print("\n" + "-" * 106)
print("TEST 2  Does replaceability predict which margin moved?   (n = 9, |r| > 0.666 for p < .05)")
print("-" * 106 + "\n")
tests = [("d_openings", "labor DEMAND fell"),
         ("d_hires",    "realized hiring fell"),
         ("d_layoffs",  "involuntary separations rose   <- displacement"),
         ("d_quits",    "worker confidence fell"),
         ("d_fill",     "matching got harder            <- labor supply")]
for col, lab in tests:
    r, p = sp.pearsonr(R["rep"], R[col])
    rs, ps = sp.spearmanr(R["rep"], R[col])
    flag = "   SIGNIFICANT" if p < 0.05 else ""
    print(f"  {col:<12} ~ replaceability   r={r:+.3f} p={p:.3f}   rho={rs:+.3f} p={ps:.3f}"
          f"   [{lab}]{flag}")
print("\n  Bonferroni across these 5 tests: p < 0.010 to survive.")

print("\n" + "-" * 106)
print("TEST 3  The reopening regime, and why the window choice matters")
print("-" * 106 + "\n")
print("  Change measured from calendar 2023 (end of the reopening boom) instead of 2015-2019.")
print("  Where the two columns disagree, the 2015-2019 comparison is picking up the boom")
print("  unwinding rather than anything that happened in the AI window.\n")
print(f"{'sector':<28}{'openings vs 15-19':>19}{'vs 2023':>10}   {'fill vs 15-19':>15}{'vs 2023':>10}")
for _, x in R.iterrows():
    print(f"{x.sector:<28}{x.d_openings:>+19.2f}{x.dr_openings:>+10.2f}   "
          f"{x.d_fill:>+15.2f}{x.fill_now - series[x.sector]['fill_r12'].loc[MID]:>+10.2f}")

print("\n" + "-" * 106)
print("TEST 4  The immigration objection, tested rather than flagged")
print("-" * 106 + "\n")
print("  A shrinking labor force means firms post jobs they cannot fill, so hires per")
print("  opening FALLS while openings hold up and layoffs do not rise. Construction and")
print("  leisure are the most immigrant-intensive sectors, so the effect should be")
print("  concentrated there. Path of the fill rate, hires per opening:\n")
print(f"  {'sector':<26}{'2015-19':>9}{'2021-22':>9}{'2023':>8}{'2024':>8}{'2025':>8}{'latest':>9}")
for n in ["Construction", "Leisure & Hospitality", "Manufacturing", "Information"]:
    s = series[n]
    raw = s["hires"] / s["openings"]
    cells = [raw.loc[BASE[0]:BASE[1]].mean(), raw.loc["2021":"2022"].mean(),
             raw.loc["2023"].mean(), raw.loc["2024"].mean(), raw.loc["2025"].mean(),
             s["fill_r12"].iloc[-1]]
    print(f"  {n:<26}" + "".join(f"{c:>9.2f}" if i else f"{c:>9.2f}" for i, c in enumerate(cells)))
print("\n  If the fill rate troughs in 2021-2023 and RECOVERS through 2024-2026, the")
print("  matching problem belongs to the reopening, not to the AI window. Read the path.")

print("\n" + "-" * 106)
print("TEST 5  The rate-standing split")
print("-" * 106 + "\n")
print(f"{'group':<34}{'n':>3}{'d openings':>12}{'d hires':>10}{'d layoffs':>11}{'d quits':>10}")
for lab, sub in [("rate model HAS standing", R[R.standing]),
                 ("rate model has NO standing", R[~R.standing])]:
    print(f"{lab:<34}{len(sub):>3}{sub.d_openings.mean():>+12.2f}{sub.d_hires.mean():>+10.2f}"
          f"{sub.d_layoffs.mean():>+11.2f}{sub.d_quits.mean():>+10.2f}")
ns = R[~R.standing]
print(f"\n  The three rate-orthogonal sectors are exactly the three highest-replaceability")
print(f"  ones ({', '.join(ns.sector)}),")
print(f"  which is the exclusion restriction the physical-sector sub-project established:")
print(f"  monetary policy demonstrably does not drive hiring there, so whatever moved them")
print(f"  is not the rate cycle. Their mean layoffs change is {ns.d_layoffs.mean():+.2f}pp.")

# ---- chart -------------------------------------------------------------------
fig, axes = plt.subplots(2, 2, figsize=(16.5, 11))
COL = {True: "#1f4e79", False: "#c0392b"}

ax = axes[0, 0]
ax.axhline(0, color="black", lw=1.0); ax.axvline(0, color="black", lw=1.0)
for _, x in R.iterrows():
    ax.scatter(x.d_openings, x.d_layoffs, s=60 + 900 * x.rep, color=COL[x.standing],
               alpha=0.75, edgecolors="white", linewidths=1.4, zorder=3)
    ax.annotate(x.sector, (x.d_openings, x.d_layoffs), xytext=(7, 5),
                textcoords="offset points", fontsize=8.5)
ax.text(0.03, 0.96, "above the line = displacement\n(layoffs above pre-AI)",
        transform=ax.transAxes, fontsize=8.5, va="top", color="#7b241c")
ax.text(0.03, 0.06, "lower left = hiring freeze\n(demand withdrawn, nobody fired)",
        transform=ax.transAxes, fontsize=8.5, va="bottom", color="#1a5276")
ax.set_xlabel("change in job openings rate vs 2015-2019 (pp)", fontsize=10)
ax.set_ylabel("change in layoffs & discharges rate vs 2015-2019 (pp)", fontsize=10)
ax.set_title("1. Displacement or freeze?\nMarker size = AI replaceability. Blue = rate model explains it.",
             fontsize=11.5, fontweight="bold")
ax.grid(True, ls="--", alpha=0.35)

ax = axes[0, 1]
labels, rs_, ps_ = [], [], []
for col, lab in tests:
    r, p = sp.pearsonr(R["rep"], R[col])
    labels.append(col.replace("d_", "Δ ")); rs_.append(r); ps_.append(p)
y = np.arange(len(labels))
ax.barh(y, rs_, color=["#c0392b" if p < 0.05 else "#95a5a6" for p in ps_])
ax.axvline(0, color="black", lw=1.0)
for c in (-0.666, 0.666):
    ax.axvline(c, color="darkgreen", ls="--", lw=1.4)
ax.text(0.68, len(labels) - 0.55, "p=.05 at n=9", fontsize=8, color="darkgreen")
ax.set_yticks(y); ax.set_yticklabels(labels, fontsize=9.5); ax.set_xlim(-1, 1)
ax.set_xlabel("correlation with AI replaceability (n = 9)", fontsize=10)
ax.set_title("2. No margin clears the n=9 bar\nPower, not measurement, is the binding constraint",
             fontsize=11.5, fontweight="bold")
ax.grid(True, axis="x", ls="--", alpha=0.35)

ax = axes[1, 0]
for n, c, lw in [("Information", "#c0392b", 2.6), ("Professional & Business", "#e67e22", 2.2),
                 ("Construction", "#1f4e79", 2.2), ("Leisure & Hospitality", "#5dade2", 2.0)]:
    m = series[n]["layoffs_r12"].loc["2013-01-01":]
    ax.plot(m.index, m.values, color=c, lw=lw, label=n)
ax.axvspan(pd.Timestamp("2020-03-01"), pd.Timestamp("2021-12-31"), color="gray",
           alpha=0.16, label="COVID")
ax.axvspan(pd.Timestamp("2024-01-01"), LATEST, color="gold", alpha=0.18, label="the AI window")
ax.set_ylabel("layoffs & discharges rate, 12-month mean (%)", fontsize=10)
ax.set_title("3. Only Information's layoffs are above their pre-AI level\nEverywhere else, firms stopped hiring rather than started firing",
             fontsize=11.5, fontweight="bold")
ax.legend(fontsize=8, loc="upper right"); ax.grid(True, ls="--", alpha=0.35)

ax = axes[1, 1]
for n, c in [("Construction", "#1f4e79"), ("Leisure & Hospitality", "#5dade2"),
             ("Information", "#c0392b"), ("Professional & Business", "#e67e22")]:
    m = series[n]["fill_r12"].loc["2013-01-01":]
    ax.plot(m.index, m.values, color=c, lw=2.2, label=n)
ax.axvspan(pd.Timestamp("2021-01-01"), pd.Timestamp("2023-12-31"), color="mediumpurple",
           alpha=0.15, label="reopening regime")
ax.axvspan(pd.Timestamp("2024-01-01"), LATEST, color="gold", alpha=0.18, label="the AI window")
ax.set_ylabel("hires per job opening, 12-month mean", fontsize=10)
ax.set_title("4. The matching collapse is a 2021-2023 event that is recovering\nIt belongs to the reopening, not to the AI window",
             fontsize=11.5, fontweight="bold")
ax.legend(fontsize=8, loc="upper right"); ax.grid(True, ls="--", alpha=0.35)

fig.suptitle("JOLTS margins: what kind of slowdown was this, and does AI exposure predict it?",
             fontsize=13.5, fontweight="bold", y=1.0)
plt.tight_layout()
plt.savefig("jolts_margins.png", dpi=150, bbox_inches="tight")
print("\nChart saved: jolts_margins.png")
