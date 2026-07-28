"""
recency_test.py
Does AI exposure predict the RECENT ACCELERATION in productivity, or only its level?

The corrected cross-section (real_productivity_ai_crosssection.py) shows that
AI exposure and job replaceability predict real productivity growth measured
over 2013-2025. The obvious objection is that this window mostly predates
generative AI, so the result could reflect long-run automation rather than
anything about the 2022+ AI era.

This is the test of that objection. If AI specifically is doing the work, then
exposure should predict not just the LEVEL of productivity growth but the
CHANGE in it: sectors with more replaceable jobs should have accelerated more
after AI arrived, relative to their own pre-AI baseline.

    acceleration_i = productivity growth (2024-2025) - productivity growth (2013-2019)

then regress acceleration on the replaceability score (and on AIIE) across the
nine industries, and check robustness to the choice of baseline and post window.

RESULT: the acceleration test does NOT confirm the AI story. The slope is
positive in every specification tried, but only reaches significance in the
narrowest post window (2025 alone), which is also the most specification-
searched. The level result stays robust (r ~ +0.84, p ~ 0.004). So the
"this could be long-run automation" caveat survives, and the project's AI
claim rests on levels rather than on a discontinuity timed to AI's arrival.

Real terms throughout: finance is deflated with the neutral GDP deflator
(its own BEA deflator is FISIM-broken); the other eight use BEA real value
added. Reads FRED-Data/. Writes recency_test.png.
"""

import os, glob, warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats as sp
warnings.filterwarnings("ignore")

DATA = "FRED-Data/"

# sector: (output spec, employment files, AIIE, replaceability)
S = {
 "Financial Activities":       ("GDPDEFLATE:financial_activities_value_added_VAFI.csv", ["finance_insurance_employment_CES5552000001.csv"], 1.538, 0.267),
 "Information":                ("information_sector_value_added_RVAI.csv", ["information_sector_employment_USINFO.csv"], 1.268, 0.325),
 "Education & Health":         ("health_care_social_assistance_value_added_RVAHCSA.csv", ["education_health_employment_USEHS.csv"], 0.775, 0.152),
 "Professional & Business":    ("professional_business_services_value_added_RVAPBS.csv", ["professional_business_services_employment_USPBS.csv"], 0.654, 0.233),
 "Wholesale Trade":            ("wholesale_trade_value_added_RVAW.csv", ["wholesale_trade_employment_USWTRADE.csv"], 0.264, 0.207),
 "Leisure & Hospitality":      ("leisure_hospitality_value_added_RVAAERAF.csv", ["leisure_hospitality_employment_USLAH.csv"], -0.315, 0.088),
 "Transportation & Utilities": ("transportation_warehousing_value_added_RVAT.csv", ["transportation_warehousing_employment_CES4300000001.csv", "utilities_employment_CES4422000001.csv"], -0.342, 0.120),
 "Manufacturing":              ("manufacturing_value_added_RVAMA.csv", ["manufacturing_employment_MANEMP.csv"], -0.484, 0.138),
 "Construction":               ("construction_value_added_RVAC.csv", ["construction_employment_USCONS.csv"], -0.997, 0.091),
}


def find(f):
    if os.path.exists(DATA + f):
        return DATA + f
    m = glob.glob(DATA + "*" + f + "*") + glob.glob(DATA + "*" + f)
    return m[0]


def load(f):
    d = pd.read_csv(find(f)); d.columns = [c.strip() for c in d.columns]
    d[d.columns[0]] = pd.to_datetime(d[d.columns[0]]); d = d.set_index(d.columns[0])
    return pd.to_numeric(d.iloc[:, 0], errors="coerce").dropna()


def real_output(spec):
    if spec.startswith("GDPDEFLATE:"):
        nom = load(spec.split(":", 1)[1]); gd = load("gdp_deflator_GDPDEF.csv")
        return nom / gd.reindex(nom.index).interpolate() * 100
    return load(spec)


def esum(fs):
    s = None
    for f in fs:
        x = load(f).resample("QS").mean(); s = x if s is None else s.add(x, fill_value=np.nan)
    return s


# per-sector YoY productivity growth series
PG = {}
for name, (ospec, efs, _, _) in S.items():
    df = pd.DataFrame({"o": real_output(ospec), "e": esum(efs)}).dropna()
    PG[name] = ((df["o"] / df["e"]).pct_change(4) * 100).dropna()

REP  = {n: v[3] for n, v in S.items()}
AIIE = {n: v[2] for n, v in S.items()}
avg  = lambda n, a, b: PG[n].loc[a:b].mean()

BASE_A, BASE_B = "2013-01-01", "2019-12-31"
POST_A, POST_B = "2024-01-01", "2026-12-31"

rows = []
for n in S:
    pre  = avg(n, BASE_A, BASE_B)
    mid  = avg(n, "2022-01-01", "2023-12-31")
    post = avg(n, POST_A, POST_B)
    rows.append(dict(sector=n, rep=REP[n], aiie=AIIE[n], pre=pre, mid=mid, post=post, accel=post - pre))
R = pd.DataFrame(rows).sort_values("rep", ascending=False)

print("Real productivity growth by period (avg YoY, %/yr), sorted by replaceability")
print(R[["sector", "rep", "pre", "mid", "post", "accel"]].round(2).to_string(index=False))

print("\nMain test (baseline 2013-2019 vs post 2024-2025):")
for col, lab in [("aiie", "AIIE"), ("rep", "Replaceability")]:
    r, p = sp.pearsonr(R[col], R["accel"])
    print(f"  acceleration ~ {lab:<15} r={r:+.3f}  p={p:.3f}")
for col, lab in [("aiie", "AIIE"), ("rep", "Replaceability")]:
    r, p = sp.pearsonr(R[col], R["post"])
    print(f"  2024-25 LEVEL ~ {lab:<14} r={r:+.3f}  p={p:.3f}")

print("\nRobustness of the acceleration test (~ replaceability):")
SPECS = [("2013-01-01", "2019-12-31", "2024-01-01", "2026-12-31"),
         ("2015-01-01", "2019-12-31", "2024-01-01", "2026-12-31"),
         ("2013-01-01", "2019-12-31", "2023-01-01", "2026-12-31"),
         ("2010-01-01", "2019-12-31", "2024-01-01", "2026-12-31"),
         ("2013-01-01", "2019-12-31", "2025-01-01", "2026-12-31")]
rob = []
for a0, a1, b0, b1 in SPECS:
    acc = [avg(n, b0, b1) - avg(n, a0, a1) for n in S]
    x = [REP[n] for n in S]
    r, p = sp.pearsonr(x, acc); rs, ps = sp.spearmanr(x, acc)
    rob.append((f"{a0[:4]}-{a1[:4]} -> {b0[:4]}-{b1[:4]}", r, p, rs, ps))
    print(f"  base {a0[:4]}-{a1[:4]}  post {b0[:4]}-{b1[:4]}:  r={r:+.3f} p={p:.3f}   spearman={rs:+.3f} p={ps:.3f}")
print("\nVerdict: positive in every spec, but significant only in the narrowest")
print("post window. The acceleration test does not independently confirm the AI story.")

# ---- chart: level (robust) vs acceleration (not) ----
fig, (a1, a2) = plt.subplots(1, 2, figsize=(15, 6.3))
for ax, col, ylab, title in [
    (a1, "post", "Real productivity growth 2024-25 (%/yr)",
     "LEVEL: replaceability predicts it\n(robust)"),
    (a2, "accel", "Acceleration: 2024-25 minus 2013-19 (pp)",
     "ACCELERATION: it does not, reliably\n(the recency test fails)")]:
    sl, ic, r, p, se = sp.linregress(R["rep"], R[col])
    ax.scatter(R["rep"], R[col], s=95, color="steelblue" if col == "post" else "firebrick", zorder=3)
    for _, rw in R.iterrows():
        ax.annotate(rw["sector"].replace(" & ", "&\n"), (rw["rep"], rw[col]),
                    xytext=(4, 3), textcoords="offset points", fontsize=7)
    xs = np.linspace(R["rep"].min(), R["rep"].max(), 40)
    ax.plot(xs, ic + sl * xs, "--", color="black", lw=1.5)
    verdict = "SUPPORTS AI" if p < 0.05 else "NOT SIGNIFICANT"
    ax.text(0.04, 0.96, f"r={r:+.2f}  p={p:.3f}\n{verdict}", transform=ax.transAxes, va="top",
            fontsize=11, bbox=dict(boxstyle="round", fc="white", alpha=0.85))
    ax.axhline(0, color="black", lw=0.7, ls=":")
    ax.set_xlabel("Job-replaceability score", fontsize=10)
    ax.set_ylabel(ylab, fontsize=10)
    ax.set_title(title, fontsize=11, fontweight="bold")
    ax.grid(True, ls="--", alpha=0.3)
fig.suptitle("The recency test: AI-replaceable sectors have higher productivity growth,\n"
             "but they did not reliably accelerate more after AI arrived",
             fontsize=13, fontweight="bold")
plt.tight_layout(rect=[0, 0, 1, 0.90])
plt.savefig("recency_test.png", dpi=150, bbox_inches="tight")
print("\nChart saved: recency_test.png")
