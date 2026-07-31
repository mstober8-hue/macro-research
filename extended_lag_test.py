"""
extended_lag_test.py
Re-run Phase 4's rate control at the lags where the channel actually operates.

WHY THIS EXISTS
okun_phase2_3.py controls for the Federal Funds Rate at lags of 0, 2 and 4
quarters (`for lag in [0, 2, 4]`) and concludes the industry Okun breakdowns
are not a rate artifact. But physical-sector-inversion/hiring_slowdown.py finds
that the rate-to-hiring channel rises monotonically with the lag and peaks at
8 to 9 quarters (r = -0.74 excluding COVID, n = 75). At the lags Phase 4 tested,
the true correlation is only -0.08 to -0.32.

So Phase 4's rejection of the rate hypothesis was measured with a ruler roughly
half as long as needed, and that applies to EVERY sector, including Information.
"Tech's break survived rate controls" is unestablished in exactly the same way
"the goods sectors were not rates" was unestablished.

This script re-runs the identical specification with lags extended to 6, 8, 9,
10 and 12 quarters, in both the YoY-change and the level form of the rate
variable, and asks what happens to each sector's post-2022 Okun coefficient.

Three possible outcomes, all informative:
  - Information's post-period beta collapses toward zero -> the AI reading was
    a rate artifact.
  - It survives -> tech is doing something rates do not explain, and it has now
    passed a much harder test than before.
  - It shrinks but stays positive -> both mechanisms operate and can be sized.

METHOD (identical to okun_phase2_3.py except for the lag range)
  delta_U = a + b1*(%dY) + b2*(rate control) + e
  YoY (4-quarter) differences computed on the intact series first.
  COVID + rebound (2020 Q2 - 2022 Q1) excluded. Split at Q4 2022.
  Lagging the rate control does NOT cost post-period observations, because
  FEDFUNDS extends back to 1954; n stays at 13 for every lag.

Reads FRED CSVs from FRED-Data/. Writes extended_lag_test.png.
"""

import os
import glob
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats as sp_stats

DATA_DIR = "FRED-Data/"
CUT      = pd.Timestamp("2022-10-01")
EXCLUDE  = pd.date_range("2020-04-01", "2022-01-01", freq="QS")

INDUSTRIES = {
    "Financial Activities":       ("financial_activities_value_added_VAFI.csv",
                                   "financial_activities_unemployment_rate_LNU04032238.csv", 1.538),
    "Information":                ("information_sector_value_added_RVAI.csv",
                                   "information_sector_unemployment_rate_LNU04032237.csv", 1.268),
    "Education & Health":         ("health_care_social_assistance_value_added_RVAHCSA.csv",
                                   "education_health_unemployment_rate_LNU04032240.csv", 0.775),
    "Professional & Business":    ("professional_business_services_value_added_RVAPBS.csv",
                                   "professional_business_services_unemployment_rate_LNU04032239.csv", 0.654),
    "Wholesale Trade":            ("wholesale_trade_value_added_RVAW.csv",
                                   "wholesale_retail_trade_unemployment_rate_LNU04032235.csv", 0.264),
    "Leisure & Hospitality":      ("leisure_hospitality_value_added_RVAAERAF.csv",
                                   "leisure_hospitality_unemployment_rate_LNU04032241.csv", -0.315),
    "Transportation & Utilities": ("transportation_warehousing_value_added_RVAT.csv",
                                   "transportation_utilities_unemployment_rate_LNU04032236.csv", -0.342),
    "Manufacturing":              ("manufacturing_value_added_RVAMA.csv",
                                   "manufacturing_unemployment_rate_LNU04032232.csv", -0.484),
    "Construction":               ("construction_value_added_RVAC.csv",
                                   "construction_unemployment_rate_LNU04032231.csv", -0.997),
}

ORIGINAL_LAGS = [0, 2, 4]
EXTENDED_LAGS = [6, 8, 9, 10, 12]


def find(f):
    p = DATA_DIR + f
    return p if os.path.exists(p) else glob.glob(DATA_DIR + "*" + f)[0]


def load(f):
    d = pd.read_csv(find(f))
    d.columns = [c.strip() for c in d.columns]
    d[d.columns[0]] = pd.to_datetime(d[d.columns[0]])
    d = d.set_index(d.columns[0])
    return pd.to_numeric(d.iloc[:, 0], errors="coerce").dropna()


def build_df(out_f, un_f):
    y = load(out_f)
    u = load(un_f).resample("QS").mean()
    df = pd.DataFrame({"output": y, "unemp": u}).dropna()
    df["pct_dy"]  = df["output"].pct_change(periods=4) * 100
    df["delta_u"] = df["unemp"].diff(periods=4)
    df = df[~df.index.isin(EXCLUDE)]
    return df.dropna(subset=["pct_dy", "delta_u"])


# rate control variables: YoY change and level, at every lag we care about
ffr_q = load("fed_funds_rate_FEDFUNDS.csv").resample("QS").mean()
RATE = pd.DataFrame(index=ffr_q.index)
dffr = ffr_q.diff(periods=4)
for L in ORIGINAL_LAGS + EXTENDED_LAGS:
    RATE[f"dffr_lag{L}"] = dffr.shift(L)
    RATE[f"level_lag{L}"] = ffr_q.shift(L)


def multiple_ols(x, z, y):
    """y = a + b1*x + b2*z. Returns (b1, se_b1, n)."""
    m = ~(np.isnan(x) | np.isnan(z) | np.isnan(y))
    x, z, y = x[m], z[m], y[m]
    n = len(x)
    if n < 4:
        return np.nan, np.nan, n
    A = np.column_stack([np.ones(n), x, z])
    c, _, _, _ = np.linalg.lstsq(A, y, rcond=None)
    resid = y - A @ c
    s2 = np.sum(resid ** 2) / (n - 3)
    try:
        se = np.sqrt(np.diag(s2 * np.linalg.inv(A.T @ A)))[1]
    except np.linalg.LinAlgError:
        se = np.nan
    return c[1], se, n


def simple_ols(x, y):
    m = ~(np.isnan(x) | np.isnan(y))
    x, y = x[m], y[m]
    b, a, r, p, se = sp_stats.linregress(x, y)
    return b, se, len(x)


rows = []
for name, (of, uf, aiie) in INDUSTRIES.items():
    df = build_df(of, uf)
    pre, post = df[df.index < CUT], df[df.index >= CUT]
    rec = {"industry": name, "aiie": aiie}

    b_pre, _, _   = simple_ols(pre["pct_dy"].values, pre["delta_u"].values)
    b_post, _, n0 = simple_ols(post["pct_dy"].values, post["delta_u"].values)
    rec["b_pre_simple"], rec["b_post_simple"], rec["n_post"] = b_pre, b_post, n0

    for form in ["dffr", "level"]:
        for L in ORIGINAL_LAGS + EXTENDED_LAGS:
            col = f"{form}_lag{L}"
            jp = pre.join(RATE[[col]], how="inner").dropna(subset=["pct_dy", "delta_u", col])
            jq = post.join(RATE[[col]], how="inner").dropna(subset=["pct_dy", "delta_u", col])
            bp, _, _  = multiple_ols(jp["pct_dy"].values, jp[col].values, jp["delta_u"].values)
            bq, se, n = multiple_ols(jq["pct_dy"].values, jq[col].values, jq["delta_u"].values)
            rec[f"bpost_{col}"] = bq
            rec[f"n_{col}"] = n
            rec[f"dbeta_{col}"] = bq - bp
    rows.append(rec)

R = pd.DataFrame(rows)

# ---- report ------------------------------------------------------------------
print("=" * 92)
print("EXTENDED-LAG RATE CONTROL:  does the breakdown survive lags where rates actually bite?")
print("=" * 92)
print("\nInformation's post-2022 Okun coefficient (positive = law inverted / broken)\n")
info = R[R.industry == "Information"].iloc[0]
print(f"  {'spec':<26}{'b1_post':>10}{'n':>5}")
print(f"  {'no control (baseline)':<26}{info['b_post_simple']:>+10.3f}{int(info['n_post']):>5}")
for form, lbl in [("dffr", "YoY change in FFR"), ("level", "FFR level")]:
    print(f"\n  --- {lbl} ---")
    for L in ORIGINAL_LAGS + EXTENDED_LAGS:
        tag = "  (Phase 4 tested)" if L in ORIGINAL_LAGS else "  (NEW)"
        print(f"  {f'lag {L}q':<26}{info[f'bpost_{form}_lag{L}']:>+10.3f}"
              f"{int(info[f'n_{form}_lag{L}']):>5}{tag}")

orig_vals = [info[f"bpost_{f}_lag{L}"] for f in ["dffr", "level"] for L in ORIGINAL_LAGS]
ext_vals  = [info[f"bpost_{f}_lag{L}"] for f in ["dffr", "level"] for L in EXTENDED_LAGS]
print(f"\n  Phase 4 lags (0,2,4)   : range {min(orig_vals):+.3f} to {max(orig_vals):+.3f}")
print(f"  Extended lags (6-12)   : range {min(ext_vals):+.3f} to {max(ext_vals):+.3f}")
print(f"  Sign flips negative?   : {'YES' if min(ext_vals) < 0 else 'NO, stays positive throughout'}")

print("\n" + "=" * 92)
print("ALL SECTORS: post-2022 beta under the original vs extended lags (FFR level form)")
print("=" * 92)
print(f"\n{'industry':<28}{'AIIE':>7}{'base':>8}" +
      "".join(f"{f'L{L}':>8}" for L in ORIGINAL_LAGS + EXTENDED_LAGS))
for _, r in R.sort_values("aiie", ascending=False).iterrows():
    print(f"{r.industry:<28}{r.aiie:>+7.2f}{r.b_post_simple:>+8.3f}" +
          "".join(f"{r[f'bpost_level_lag{L}']:>+8.3f}" for L in ORIGINAL_LAGS + EXTENDED_LAGS))

# cross-section at each lag: does AI exposure predict delta-beta once rates are properly controlled?
print("\n" + "=" * 92)
print("CROSS-SECTION: delta-beta ~ AIIE at each lag (positive slope = supports AI hypothesis)")
print("=" * 92 + "\n")
for form, lbl in [("dffr", "YoY change"), ("level", "level")]:
    print(f"  --- rate control = FFR {lbl} ---")
    for L in ORIGINAL_LAGS + EXTENDED_LAGS:
        sub = R[["aiie", f"dbeta_{form}_lag{L}"]].dropna()
        sl, ic, r_, p_, se = sp_stats.linregress(sub["aiie"], sub[f"dbeta_{form}_lag{L}"])
        tag = "(Phase 4)" if L in ORIGINAL_LAGS else "(NEW)    "
        print(f"    lag {L:>2}q  {tag}  r={r_:+.3f}  p={p_:.3f}")

# ---- chart -------------------------------------------------------------------
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16.5, 6.4))
ALL_LAGS = ORIGINAL_LAGS + EXTENDED_LAGS

# panel 1: Information across lags, both forms
ax1.axhline(0, color="black", lw=1.1, ls="--")
ax1.axvspan(-0.4, 4.4, color="gray", alpha=0.13)
ax1.text(2.0, ax1.get_ylim()[1], "", fontsize=8)
for form, c, lbl in [("dffr", "#1f4e79", "control = YoY change in FFR"),
                     ("level", "#c0392b", "control = FFR level")]:
    ax1.plot(ALL_LAGS, [info[f"bpost_{form}_lag{L}"] for L in ALL_LAGS],
             marker="o", lw=2.2, color=c, label=lbl)
ax1.axhline(info["b_post_simple"], color="gray", lw=1.4, ls=":",
            label=f"no rate control ({info['b_post_simple']:+.3f})")
ax1.set_xlabel("lag on the rate control (quarters)", fontsize=10)
ax1.set_ylabel("Information post-2022 Okun coefficient", fontsize=10)
ax1.set_title("Information's break, under rate controls at every lag\n"
              "Shaded = the lags Phase 4 actually tested", fontsize=11.5, fontweight="bold")
ax1.legend(fontsize=8.5); ax1.grid(True, ls="--", alpha=0.35)

# panel 2: cross-section r by lag
ax2.axhline(0, color="black", lw=1.1, ls="--")
ax2.axvspan(-0.4, 4.4, color="gray", alpha=0.13)
for form, c, lbl in [("dffr", "#1f4e79", "control = YoY change in FFR"),
                     ("level", "#c0392b", "control = FFR level")]:
    rr = []
    for L in ALL_LAGS:
        sub = R[["aiie", f"dbeta_{form}_lag{L}"]].dropna()
        rr.append(sp_stats.linregress(sub["aiie"], sub[f"dbeta_{form}_lag{L}"])[2])
    ax2.plot(ALL_LAGS, rr, marker="o", lw=2.2, color=c, label=lbl)
ax2.set_xlabel("lag on the rate control (quarters)", fontsize=10)
ax2.set_ylabel("cross-sectional r:  Δβ ~ AI exposure", fontsize=10)
ax2.set_title("Does AI exposure predict the breakdown\nonce rates are properly controlled?",
              fontsize=11.5, fontweight="bold")
ax2.text(0.03, 0.94, "positive = supports AI hypothesis", transform=ax2.transAxes, fontsize=8.5)
ax2.text(0.03, 0.05, "negative = contradicts it", transform=ax2.transAxes, fontsize=8.5)
ax2.legend(fontsize=8.5, loc="center right"); ax2.grid(True, ls="--", alpha=0.35)

fig.suptitle("Phase 4 re-run: extending the rate control to the lags where the channel actually operates",
             fontsize=13, fontweight="bold", y=1.01)
plt.tight_layout()
plt.savefig("extended_lag_test.png", dpi=150, bbox_inches="tight")
print("\nChart saved: extended_lag_test.png")
