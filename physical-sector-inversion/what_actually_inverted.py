"""
what_actually_inverted.py
Going deeper: what is actually driving the goods-sector Okun inversion?

The sub-project established that Construction, Manufacturing, Transportation
and Wholesale inverted in 2024-2025, that the inversions survive every
interest-rate control, and that the fiscal hypothesis does not explain them
(fiscal_control.py). This script asks the next question: what IS happening?

Three tests, each one narrowing the answer.

TEST 1 - How big is the inversion, really?
    An inverted correlation is not the same as a large economic effect. This
    compares each sector's rolling correlation r against its actual Okun slope
    beta (pp of unemployment per 1% output growth), and against how much
    unemployment varied at all.

    Result: the betas are tiny (+/-0.06 to +/-0.19) and unemployment variance
    collapsed (Construction sd 1.00 -> 0.22). The inversion is a real sign
    flip on very small movements, not a large economic dislocation.

TEST 2 - Jobs lost, or labor force grown?
    Unemployment can rise because employment falls or because the labor force
    grows faster than hiring. Decomposing with sector headcount shows it is
    the employment side: hiring growth collapsed in all four goods sectors
    while real output growth held up.

TEST 3 - Is that "output up, jobs flat" shape AI-specific?
    This is the shape attributed to AI in the Information sector. Measuring
    productivity acceleration and employment slowdown across all nine sectors
    shows it is not AI-specific at all: 8 of 9 sectors slowed hiring, the mean
    slowdown is about -1.8pp, and AI exposure does not predict which sectors
    slowed (r=+0.18, p=0.64).

CONCLUSION: the goods-sector inversion and the tech "AI signature" look like
the same economy-wide 2024-2025 hiring slowdown viewed in different sectors,
rather than two separate mechanisms. The goods sectors are not a fiscal story
and the tech sector is not obviously an AI story; both are sitting inside a
broad hiring freeze.

Reads FRED CSVs from ../FRED-Data/. Writes what_actually_inverted.png.
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

PRE  = ("2013-01-01", "2019-12-31")
POST = ("2024-01-01", "2026-12-31")


def find(f):
    p = os.path.join(DATA_DIR, f)
    if os.path.exists(p):
        return p
    return glob.glob(os.path.join(DATA_DIR, "*" + f))[0]


def load(f):
    d = pd.read_csv(find(f))
    d.columns = [c.strip() for c in d.columns]
    d[d.columns[0]] = pd.to_datetime(d[d.columns[0]])
    d = d.set_index(d.columns[0])
    return pd.to_numeric(d.iloc[:, 0], errors="coerce").dropna()


def emp_sum(files):
    """Some sectors need two employment series added together."""
    s = None
    for f in files:
        x = load(f).resample("QS").mean()
        s = x if s is None else s.add(x, fill_value=np.nan)
    return s


# real output, employment file(s), unemployment file, AIIE, group
SECTORS = {
    "Construction":            ("construction_value_added_RVAC.csv",
                                ["construction_employment_USCONS.csv"],
                                "construction_unemployment_rate_LNU04032231.csv", -0.997, "goods"),
    "Manufacturing":           ("manufacturing_value_added_RVAMA.csv",
                                ["manufacturing_employment_MANEMP.csv"],
                                "manufacturing_unemployment_rate_LNU04032232.csv", -0.484, "goods"),
    "Transportation & Util":   ("transportation_warehousing_value_added_RVAT.csv",
                                ["transportation_warehousing_employment_CES4300000001.csv",
                                 "utilities_employment_CES4422000001.csv"],
                                "transportation_utilities_unemployment_rate_LNU04032236.csv", -0.342, "goods"),
    "Leisure & Hospitality":   ("leisure_hospitality_value_added_RVAAERAF.csv",
                                ["leisure_hospitality_employment_USLAH.csv"],
                                "leisure_hospitality_unemployment_rate_LNU04032241.csv", -0.315, "other"),
    "Wholesale":               ("wholesale_trade_value_added_RVAW.csv",
                                ["wholesale_trade_employment_USWTRADE.csv"],
                                "wholesale_retail_trade_unemployment_rate_LNU04032235.csv", 0.264, "goods"),
    "Professional & Business": ("professional_business_services_value_added_RVAPBS.csv",
                                ["professional_business_services_employment_USPBS.csv"],
                                "professional_business_services_unemployment_rate_LNU04032239.csv", 0.654, "high-AI"),
    "Education & Health":      ("health_care_social_assistance_value_added_RVAHCSA.csv",
                                ["education_health_employment_USEHS.csv"],
                                "education_health_unemployment_rate_LNU04032240.csv", 0.775, "other"),
    "Information":             ("information_sector_value_added_RVAI.csv",
                                ["information_sector_employment_USINFO.csv"],
                                "information_sector_unemployment_rate_LNU04032237.csv", 1.268, "high-AI"),
    "Financial Activities":    (None,  # nominal VAFI, deflated below
                                ["finance_insurance_employment_CES5552000001.csv"],
                                "financial_activities_unemployment_rate_LNU04032238.csv", 1.538, "high-AI"),
}

# Finance output is nominal (VAFI) and its BEA deflator is FISIM-contaminated,
# so deflate with the neutral GDP deflator (same choice as the finance folder).
gdpdef   = load("gdp_deflator_GDPDEF.csv")
fin_nom  = load("financial_activities_value_added_VAFI.csv")
FIN_REAL = fin_nom / gdpdef.reindex(fin_nom.index).interpolate() * 100

GOODS = [k for k, v in SECTORS.items() if v[4] == "goods"]

rows = []
for name, (out_f, emp_fs, un_f, aiie, grp) in SECTORS.items():
    out = FIN_REAL if out_f is None else load(out_f)
    emp = emp_sum(emp_fs)
    un  = load(un_f).resample("QS").mean()

    df = pd.DataFrame({"o": out, "e": emp, "u": un}).dropna()
    df["dy"] = df["o"].pct_change(4) * 100          # real output growth
    df["eg"] = df["e"].pct_change(4) * 100          # employment growth
    df["du"] = df["u"].diff(4)                      # change in unemployment rate
    df["pg"] = (df["o"] / df["e"]).pct_change(4) * 100   # productivity growth
    d = df.dropna()

    pre, post = d.loc[PRE[0]:PRE[1]], d.loc[POST[0]:POST[1]]
    rows.append(dict(
        sector=name, aiie=aiie, grp=grp,
        beta_pre=np.polyfit(pre["dy"], pre["du"], 1)[0],
        beta_post=np.polyfit(post["dy"], post["du"], 1)[0],
        r_pre=np.corrcoef(pre["dy"], pre["du"])[0, 1],
        r_post=np.corrcoef(post["dy"], post["du"])[0, 1],
        sd_pre=pre["du"].std(), sd_post=post["du"].std(),
        dy_pre=pre["dy"].mean(), dy_post=post["dy"].mean(),
        eg_pre=pre["eg"].mean(), eg_post=post["eg"].mean(),
        pg_pre=pre["pg"].mean(), pg_post=post["pg"].mean(),
    ))

R = pd.DataFrame(rows)
R["emp_slowdown"]  = R["eg_post"] - R["eg_pre"]
R["prod_accel"]    = R["pg_post"] - R["pg_pre"]
G = R[R.grp == "goods"]

# ---- TEST 1 -----------------------------------------------------------------
print("=" * 82)
print("TEST 1 - How big is the inversion? (correlation flip vs economic size)")
print("=" * 82)
print(f"\n{'sector':<24}{'r pre':>8}{'r post':>8}{'beta pre':>10}{'beta post':>11}{'sd(dU) pre':>12}{'sd(dU) post':>12}")
for _, r in G.iterrows():
    print(f"{r.sector:<24}{r.r_pre:>+8.2f}{r.r_post:>+8.2f}{r.beta_pre:>+10.3f}"
          f"{r.beta_post:>+11.3f}{r.sd_pre:>12.2f}{r.sd_post:>12.2f}")
print("\n  The correlations flip hard, but beta stays within +/-0.19pp per 1% output growth,")
print("  and unemployment variation shrank. A real sign flip on small movements.")

# ---- TEST 2 -----------------------------------------------------------------
print("\n" + "=" * 82)
print("TEST 2 - Jobs lost, or labor force grown? (goods sectors)")
print("=" * 82)
print(f"\n{'sector':<24}{'realY 13-19':>13}{'realY 24-25':>13}{'emp 13-19':>12}{'emp 24-25':>12}")
for _, r in G.iterrows():
    print(f"{r.sector:<24}{r.dy_pre:>+13.2f}{r.dy_post:>+13.2f}{r.eg_pre:>+12.2f}{r.eg_post:>+12.2f}")
print("\n  Output growth largely held up. Employment growth collapsed in every one.")
print("  The inversion is an employment-side event, not an output collapse.")

# ---- TEST 3 -----------------------------------------------------------------
print("\n" + "=" * 82)
print("TEST 3 - Is 'output up, jobs flat' AI-specific? (all nine sectors)")
print("=" * 82)
print(f"\n{'sector':<24}{'AIIE':>7}{'emp 13-19':>11}{'emp 24-25':>11}{'slowdown':>10}{'prod accel':>12}")
for _, r in R.sort_values("aiie").iterrows():
    print(f"{r.sector:<24}{r.aiie:>+7.2f}{r.eg_pre:>+11.2f}{r.eg_post:>+11.2f}"
          f"{r.emp_slowdown:>+10.2f}{r.prod_accel:>+12.2f}")

n_slow = int((R.emp_slowdown < 0).sum())
sl, ic, r_s, p_s, se = sp_stats.linregress(R["aiie"], R["emp_slowdown"])
sl2, ic2, r_a, p_a, se2 = sp_stats.linregress(R["aiie"], R["prod_accel"])
print(f"\n  sectors with a hiring slowdown : {n_slow} of 9   (mean {R.emp_slowdown.mean():+.2f}pp)")
print(f"  hiring slowdown  ~ AIIE : r={r_s:+.3f}  p={p_s:.3f}")
print(f"  productivity accel ~ AIIE : r={r_a:+.3f}  p={p_a:.3f}")
print("\n  AI exposure predicts neither. The hiring slowdown is economy-wide.")

# ---- chart ------------------------------------------------------------------
fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(19, 6.2))

# panel 1: correlation flip vs beta
x = np.arange(len(G)); w = 0.36
ax1.bar(x - w/2, G["r_pre"], w, color="#7fa8c9", label="pre (2013-19)")
ax1.bar(x + w/2, G["r_post"], w, color="#c0392b", label="post (2024-25)")
ax1.plot(x - w/2, G["beta_pre"], "o", color="black", ms=7, label="beta (economic size)")
ax1.plot(x + w/2, G["beta_post"], "o", color="black", ms=7)
ax1.axhline(0, color="black", lw=0.9)
ax1.set_xticks(x)
ax1.set_xticklabels([s.replace(" & ", "&\n").replace(" ", "\n", 1) for s in G["sector"]], fontsize=8)
ax1.set_ylabel("correlation r  /  beta", fontsize=10)
ax1.set_title("1. The flip is in the correlation,\nnot in the economic magnitude",
              fontsize=11, fontweight="bold")
ax1.legend(fontsize=8); ax1.grid(True, axis="y", ls="--", alpha=0.35)

# panel 2: output held, employment collapsed
x2 = np.arange(len(G))
ax2.bar(x2 - w/2, G["dy_post"] - G["dy_pre"], w, color="#4c8fb3", label="change in real output growth")
ax2.bar(x2 + w/2, G["eg_post"] - G["eg_pre"], w, color="#e08e45", label="change in employment growth")
ax2.axhline(0, color="black", lw=0.9)
ax2.set_xticks(x2)
ax2.set_xticklabels([s.replace(" & ", "&\n").replace(" ", "\n", 1) for s in G["sector"]], fontsize=8)
ax2.set_ylabel("change 2024-25 vs 2013-19 (pp)", fontsize=10)
ax2.set_title("2. Output growth mostly held.\nHiring is what collapsed.", fontsize=11, fontweight="bold")
ax2.legend(fontsize=8); ax2.grid(True, axis="y", ls="--", alpha=0.35)

# panel 3: slowdown vs AI exposure
colors = {"goods": "#1f4e79", "high-AI": "#c0392b", "other": "gray"}
for _, r in R.iterrows():
    ax3.scatter(r.aiie, r.emp_slowdown, s=95, color=colors[r.grp], zorder=3)
    ax3.annotate(r.sector.replace(" & ", "&\n"), (r.aiie, r.emp_slowdown),
                 xytext=(4, 3), textcoords="offset points", fontsize=7)
xs = np.linspace(R["aiie"].min() - 0.2, R["aiie"].max() + 0.2, 50)
ax3.plot(xs, ic + sl * xs, "--", color="firebrick", lw=1.6)
ax3.axhline(0, color="black", lw=0.8, ls=":")
ax3.text(0.04, 0.06, f"r={r_s:+.2f}  p={p_s:.2f}\nAI exposure does not\npredict who slowed",
         transform=ax3.transAxes, fontsize=9,
         bbox=dict(boxstyle="round", fc="white", alpha=0.85))
ax3.set_xlabel("AI exposure (AIIE)", fontsize=10)
ax3.set_ylabel("hiring slowdown, 2024-25 vs 2013-19 (pp)", fontsize=10)
ax3.set_title("3. 8 of 9 sectors slowed hiring.\nIt is economy-wide, not AI-specific.",
              fontsize=11, fontweight="bold")
ax3.grid(True, ls="--", alpha=0.35)

fig.suptitle("What actually inverted: a small sign flip on top of an economy-wide hiring slowdown",
             fontsize=13, fontweight="bold", y=1.01)
plt.tight_layout()
out = os.path.join(HERE, "what_actually_inverted.png")
plt.savefig(out, dpi=150, bbox_inches="tight")
print(f"\nChart saved: {out}")
