"""
generate_results_csv.py
Compiles all numerical results from the Okun's Law / AI Era research project
into a single comprehensive CSV with multiple labelled sections.
"""

import numpy as np
import pandas as pd
from scipy import stats as sp_stats
import csv, io

# ── helpers ──────────────────────────────────────────────────────────────────

def stars(p):
    if np.isnan(p):   return ""
    if p < 0.001:     return "***"
    if p < 0.01:      return "**"
    if p < 0.05:      return "*"
    if p < 0.10:      return "."
    return ""

def t_to_p(t, df):
    if np.isnan(t) or df <= 0: return np.nan
    return 2 * sp_stats.t.sf(abs(t), df=df)

def ci(coef, se, df, level=0.95):
    if np.isnan(se) or df <= 0: return np.nan, np.nan
    t_cr = sp_stats.t.ppf((1 + level) / 2, df=df)
    return coef - t_cr * se, coef + t_cr * se

def fmt(x, d=4):
    if pd.isna(x): return ""
    return f"{x:.{d}f}"

def fmtpct(x, d=1):
    if pd.isna(x): return ""
    return f"{x:.{d}f}%"


# ── load raw data ─────────────────────────────────────────────────────────────

BASE = "/Users/maxstober/Developer/Macro Research /"

p2  = pd.read_csv(BASE + "phase2_results.csv")
bt  = pd.read_csv(BASE + "btos_beta1_table.csv")
rk  = pd.read_csv(BASE + "btos_sector_ranking.csv")

SPECS = ["simple", "rc_lag0", "rc_lag2", "rc_lag4", "rc_level", "rc_dev_rolling"]
SPEC_LABELS = {
    "simple":          "Simple Okun (no rate control)",
    "rc_lag0":         "Rate Control: ΔFFR (lag 0)",
    "rc_lag2":         "Rate Control: ΔFFR (lag 2Q)",
    "rc_lag4":         "Rate Control: ΔFFR (lag 4Q)",
    "rc_level":        "Rate Control: FFR level",
    "rc_dev_rolling":  "Rate Control: FFR dev from rolling mean",
}
INDUSTRIES = p2["industry"].tolist()


# ── cross-section OLS ─────────────────────────────────────────────────────────

def cross_section_ols(x, y):
    mask = ~(np.isnan(x) | np.isnan(y))
    xm, ym = x[mask], y[mask]
    n = int(mask.sum())
    if n < 4:
        return dict(slope=np.nan, intercept=np.nan, se=np.nan, t=np.nan,
                    p=np.nan, r=np.nan, ci_lo=np.nan, ci_hi=np.nan, n=n)
    slope, intercept, r, p, se = sp_stats.linregress(xm, ym)
    df_t = n - 2
    t_cr = sp_stats.t.ppf(0.975, df=df_t)
    return dict(slope=slope, intercept=intercept, se=se,
                t=slope/se, p=p, r=r,
                ci_lo=slope - t_cr*se, ci_hi=slope + t_cr*se, n=n)


# ── Section builder ───────────────────────────────────────────────────────────

rows = []   # list of lists; blank list = blank row

def header(title):
    rows.append([])
    rows.append([f"=== {title.upper()} ==="])
    rows.append([])

def subheader(title):
    rows.append(["--- " + title + " ---"])

def row(*cells):
    rows.append(list(cells))

def blank():
    rows.append([])


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 1 — STUDY DESIGN
# ─────────────────────────────────────────────────────────────────────────────

header("Section 1 — Study Design and Constants")
row("Parameter", "Value", "Notes")
row("Dependent variable", "ΔU (pp)", "YoY change in sector unemployment rate, not seasonally adjusted")
row("Output variable", "%ΔY", "YoY % change in sector real GDP (BEA, chained 2017$)")
row("Differencing horizon", "4 quarters", "YoY to remove seasonality; diffs computed BEFORE dropping rows")
row("AI era cutoff", "Q4 2022", "ChatGPT launch (November 2022)")
row("Pre-period", "1990 Q1 – 2022 Q3", "Approximate; varies slightly by industry data availability")
row("Post-period", "2022 Q4 – 2025 Q4", "n=13 quarters")
row("COVID exclusion", "Q2 2020 – Q1 2022", "8 quarters dropped from both pre and post analysis")
row("Δβ1 sign convention", "Δβ1 = β1_post − β1_pre", "Positive = Okun coefficient weakened (less negative post-AI)")
row("Significance threshold", "Bonferroni-corrected p < 0.01", "5 distinct specs tested; family-wise α = 0.05 → per-test α = 0.01")
blank()
row("Specifications", "", "")
for s, lbl in SPEC_LABELS.items():
    row(s, lbl)
blank()
row("Industries (9)", "AIIE Score", "Felten/Raj/Seamans 2023 AI exposure index")
for _, r_ in p2.iterrows():
    row(r_["industry"], fmt(r_["aiie"], 3))

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 2 — SIMPLE OKUN, ALL INDUSTRIES
# ─────────────────────────────────────────────────────────────────────────────

header("Section 2 — Simple Okun's Law (ΔU = α + β1·%ΔY): Pre vs Post Summary")
row("Industry", "AIIE",
    "β1 Pre", "SE Pre", "t Pre", "p Pre", "Sig", "n Pre", "R² Pre",
    "β1 Post", "SE Post", "t Post", "p Post", "Sig", "n Post", "R² Post",
    "Δβ1", "Δβ1 magnitude", "Interpretation")

for _, r_ in p2.iterrows():
    ind  = r_["industry"]
    aiie = r_["aiie"]
    b1_pre  = r_["beta1_simple_pre"]
    se1_pre = r_["se1_simple_pre"]
    n_pre   = int(r_["n_simple_pre"])
    r2_pre  = r_["r2_simple_pre"]
    df_pre  = n_pre - 2
    t_pre   = b1_pre / se1_pre if se1_pre else np.nan
    p_pre   = t_to_p(t_pre, df_pre)

    b1_post  = r_["beta1_simple_post"]
    se1_post = r_["se1_simple_post"]
    n_post   = int(r_["n_simple_post"])
    r2_post  = r_["r2_simple_post"]
    df_post  = n_post - 2
    t_post   = b1_post / se1_post if se1_post else np.nan
    p_post   = t_to_p(t_post, df_post)

    db = r_["delta_beta1_simple"]

    if abs(db) > 0.2:      interp = "Large breakdown"
    elif abs(db) > 0.1:    interp = "Moderate breakdown"
    elif abs(db) > 0.05:   interp = "Small shift"
    else:                  interp = "Stable"
    if db < 0:             interp = interp.replace("breakdown", "strengthening")

    row(ind, fmt(aiie,3),
        fmt(b1_pre), fmt(se1_pre), fmt(t_pre,2), fmt(p_pre,3), stars(p_pre), n_pre, fmt(r2_pre,3),
        fmt(b1_post), fmt(se1_post), fmt(t_post,2), fmt(p_post,3), stars(p_post), n_post, fmt(r2_post,3),
        fmt(db,4), fmt(abs(db),4), interp)

blank()
subheader("Significance codes:  *** p<0.001  ** p<0.01  * p<0.05  . p<0.10")

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 3 — Δβ1 MATRIX: ALL INDUSTRIES × ALL 6 SPECS
# ─────────────────────────────────────────────────────────────────────────────

header("Section 3 — Δβ1 Matrix: All Industries × All 6 Specifications")
subheader("Δβ1 = β1_post − β1_pre  (positive = Okun weakened post-Q4-2022)")
blank()

# Header row
hdr = ["Industry", "AIIE"] + [s for s in SPECS] + ["Mean Δβ1 (6 specs)", "Min Δβ1", "Max Δβ1", "All positive?"]
row(*hdr)

for _, r_ in p2.iterrows():
    vals = [r_[f"delta_beta1_{s}"] for s in SPECS]
    mean_db = np.mean(vals)
    all_pos = "YES" if all(v > 0 for v in vals) else "NO"
    row(r_["industry"], fmt(r_["aiie"],3),
        *[fmt(v,4) for v in vals],
        fmt(mean_db,4), fmt(min(vals),4), fmt(max(vals),4), all_pos)

blank()
subheader("Sorted by mean Δβ1 descending (largest breakdown first)")
sorted_p2 = p2.copy()
sorted_p2["mean_db"] = sorted_p2[[f"delta_beta1_{s}" for s in SPECS]].mean(axis=1)
sorted_p2 = sorted_p2.sort_values("mean_db", ascending=False)

hdr2 = ["Rank", "Industry", "AIIE"] + [f"Δβ1 ({s})" for s in SPECS] + ["Mean Δβ1"]
row(*hdr2)
for rank, (_, r_) in enumerate(sorted_p2.iterrows(), 1):
    vals = [r_[f"delta_beta1_{s}"] for s in SPECS]
    row(rank, r_["industry"], fmt(r_["aiie"],3), *[fmt(v,4) for v in vals], fmt(r_["mean_db"],4))

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 4 — FULL COEFFICIENT TABLE (β1, β2, SE, t, p, CI, R², n) ALL SPECS
# ─────────────────────────────────────────────────────────────────────────────

header("Section 4 — Full Coefficient Tables: β1 (%ΔY) and β2 (Rate Control) for Every Industry × Spec")
subheader("k = number of regressors incl. intercept (2 for simple, 3 for rate-control specs)")
blank()

for spec in SPECS:
    subheader(f"Spec: {spec}  —  {SPEC_LABELS[spec]}")
    is_simple = (spec == "simple")
    k = 2 if is_simple else 3

    row("Industry", "Period", "n", "df", "R²",
        "β1 (%ΔY)", "SE(β1)", "t(β1)", "p(β1)", "Sig", "95% CI_lo(β1)", "95% CI_hi(β1)",
        "β2 (Rate ctrl)", "SE(β2)", "t(β2)", "p(β2)", "Sig (β2)")

    for _, r_ in p2.iterrows():
        for period in ["pre", "post"]:
            b1  = r_[f"beta1_{spec}_{period}"]
            se1 = r_[f"se1_{spec}_{period}"]
            n_  = int(r_[f"n_{spec}_{period}"])
            r2_ = r_[f"r2_{spec}_{period}"]
            df_ = n_ - k
            t1  = b1 / se1 if se1 and not np.isnan(se1) else np.nan
            p1  = t_to_p(t1, df_)
            lo1, hi1 = ci(b1, se1, df_)

            if not is_simple:
                b2  = r_[f"beta2_{spec}_{period}"]
                se2 = r_[f"se2_{spec}_{period}"]
                t2  = b2 / se2 if se2 and not np.isnan(se2) else np.nan
                p2_ = t_to_p(t2, df_)
            else:
                b2 = se2 = t2 = p2_ = np.nan

            row(r_["industry"], period, n_, df_, fmt(r2_,3),
                fmt(b1), fmt(se1), fmt(t1,2), fmt(p1,3), stars(p1), fmt(lo1), fmt(hi1),
                fmt(b2), fmt(se2), fmt(t2,2) if not np.isnan(t2) else "",
                fmt(p2_,3) if not np.isnan(p2_) else "", stars(p2_))
        blank()

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 5 — AI EXPOSURE MEASURES
# ─────────────────────────────────────────────────────────────────────────────

header("Section 5 — AI Exposure Measures: AIIE Scores and BTOS Adoption Rates")
blank()
row("Industry", "AIIE Score", "AIIE Rank", "BTOS AI Adoption %", "BTOS Rank",
    "Rank Difference (AIIE − BTOS)", "BTOS n_obs (biweekly panels)")

for _, r_ in rk.iterrows():
    btos_row = bt[bt["Industry"] == r_["Industry"]].iloc[0]
    row(r_["Industry"],
        fmt(r_["AIIE"],3),
        int(r_["AIIE_rank"]),
        fmt(r_["BTOS_pct"],2),
        int(r_["BTOS_rank"]),
        fmt(r_["rank_diff"],0),
        int(btos_row["BTOS_n_obs"]))

blank()
subheader("Spearman rank correlation: AIIE ranking vs BTOS adoption ranking")
aiie_ranks = rk["AIIE_rank"].values
btos_ranks = rk["BTOS_rank"].values
rho, rho_p = sp_stats.spearmanr(aiie_ranks, btos_ranks)
row("Spearman ρ", fmt(rho,3), "p-value", fmt(rho_p,3), "Interpretation",
    "Strong agreement" if rho > 0.8 else "Moderate agreement")
blank()
subheader("Note: AIIE = Felten/Raj/Seamans (2023) theoretical AI occupational exposure score.")
subheader("BTOS = Census Bureau Business Trends and Outlook Survey Q7 (used AI in past 2 weeks).")
subheader("BTOS sector-level data available from Nov 2025 onward; averaged across 14 biweekly panels.")
subheader("ρ=0.917 closes off 'AIIE measured the wrong thing' objection — both measures agree on sector ranking.")

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 6 — CROSS-SECTIONAL REGRESSION: Δβ1 ~ AIIE and Δβ1 ~ BTOS
# ─────────────────────────────────────────────────────────────────────────────

header("Section 6 — Cross-Sectional Regression: Δβ1 vs AI Exposure Measures")
subheader("OLS: Δβ1_i = α + γ·AI_i + ε_i  across 9 industries")
subheader("Positive γ (slope) would mean higher AI exposure → larger Okun breakdown.")
subheader("Bonferroni-corrected threshold: p < 0.01 for 5 non-simple specs.")
blank()

row("Spec", "Spec Description", "AI Measure", "n",
    "Slope γ", "SE(γ)", "t(γ)", "p(γ)", "Sig", "95% CI_lo", "95% CI_hi",
    "r (Pearson)", "Intercept", "SE(Intercept)", "Direction vs hypothesis")

aiie_scores = bt["AIIE"].values
btos_pcts   = bt["BTOS_pct"].values

for spec in SPECS:
    db_vals = bt[f"dbeta1_{spec}"].values
    for measure, x in [("AIIE", aiie_scores), ("BTOS %", btos_pcts)]:
        res = cross_section_ols(x, db_vals)
        direction = ("SUPPORTS AI hypothesis (slope > 0)"
                     if res["slope"] > 0
                     else "CONTRADICTS AI hypothesis (slope < 0)")
        row(spec, SPEC_LABELS[spec], measure, res["n"],
            fmt(res["slope"],4), fmt(res["se"],4), fmt(res["t"],2), fmt(res["p"],3),
            stars(res["p"]), fmt(res["ci_lo"],4), fmt(res["ci_hi"],4),
            fmt(res["r"],3), fmt(res["intercept"],4), "",
            direction)

blank()
subheader("Expected result under 'AI breaks Okun' hypothesis: γ > 0 (higher AI exposure → larger Δβ1)")
subheader("Actual result: slope is negative in most specs for both measures → contradicts simple AI story")

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 7 — Δβ1 RAW DATA BY INDUSTRY × SPEC (long format, for scatter plots)
# ─────────────────────────────────────────────────────────────────────────────

header("Section 7 — Δβ1 Raw Data by Industry × Spec (Long Format)")
row("Industry", "AIIE", "AIIE_Rank", "BTOS_pct", "BTOS_Rank", "Spec", "Δβ1",
    "β1_pre", "SE_pre", "t_pre", "p_pre", "Sig_pre",
    "β1_post", "SE_post", "t_post", "p_post", "Sig_post")

for _, r_ in p2.iterrows():
    ind  = r_["industry"]
    aiie = r_["aiie"]
    rk_row  = rk[rk["Industry"] == ind].iloc[0]
    bt_row  = bt[bt["Industry"] == ind].iloc[0]
    aiie_rank = int(rk_row["AIIE_rank"])
    btos_pct  = bt_row["BTOS_pct"]
    btos_rank = int(rk_row["BTOS_rank"])

    for spec in SPECS:
        is_simple = (spec == "simple")
        k = 2 if is_simple else 3
        db = r_[f"delta_beta1_{spec}"]

        b1_pre  = r_[f"beta1_{spec}_pre"]
        se1_pre = r_[f"se1_{spec}_pre"]
        n_pre   = int(r_[f"n_{spec}_pre"])
        df_pre  = n_pre - k
        t1_pre  = b1_pre / se1_pre if se1_pre else np.nan
        p1_pre  = t_to_p(t1_pre, df_pre)

        b1_post  = r_[f"beta1_{spec}_post"]
        se1_post = r_[f"se1_{spec}_post"]
        n_post   = int(r_[f"n_{spec}_post"])
        df_post  = n_post - k
        t1_post  = b1_post / se1_post if se1_post else np.nan
        p1_post  = t_to_p(t1_post, df_post)

        row(ind, fmt(aiie,3), aiie_rank, fmt(btos_pct,2), btos_rank, spec, fmt(db,4),
            fmt(b1_pre), fmt(se1_pre), fmt(t1_pre,2), fmt(p1_pre,3), stars(p1_pre),
            fmt(b1_post), fmt(se1_post), fmt(t1_post,2), fmt(p1_post,3), stars(p1_post))

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 8 — INFORMATION SECTOR OVERHANG TEST
# ─────────────────────────────────────────────────────────────────────────────

header("Section 8 — Information Sector: Overhang-Correction Hypothesis Test")
subheader("ΔU = α + β1·(%ΔY) + β2·(ΔFFR) + β3·(Overhang or ΔOverhang)")
subheader("Hypothesis: 2020-21 overhiring correction explains post-2022 Okun breakdown")
subheader("M3 = Overhang level (% above trend); M4 = ΔOverhang QoQ (rate of correction)")
blank()

# All results from the info_overhang.py run
overhang_data = {
    # (model, period): {param: (coef, se, t, p, ci_lo, ci_hi), n, df, r2}
    # Pre-period
    ("M1", "pre"):  {
        "n":2, "df":57, "r2":0.113,
        "params": {
            "intercept": (0.5982, 0.3777, 1.58, 0.1188, -0.158, 1.355),
            "%ΔY":       (-0.1339, 0.0497, -2.69, 0.0093, -0.233, -0.034),
        }},
    ("M2", "pre"):  {
        "n":59, "df":56, "r2":0.314,
        "params": {
            "intercept": (0.3486, 0.3406, 1.02, 0.3105, -0.334, 1.031),
            "%ΔY":       (-0.0981, 0.0450, -2.18, 0.0335, -0.188, -0.008),
            "ΔFFR":      (-0.6917, 0.1705, -4.06, 0.0002, -1.033, -0.350),
        }},
    ("M3", "pre"):  {
        "n":59, "df":55, "r2":0.325,
        "params": {
            "intercept": (0.2506, 0.3563, 0.70, 0.4849, -0.463, 0.965),
            "%ΔY":       (-0.1004, 0.0451, -2.23, 0.0301, -0.191, -0.010),
            "ΔFFR":      (-0.6679, 0.1725, -3.87, 0.0003, -1.014, -0.322),
            "Overhang":  (0.0286, 0.0301, 0.95, 0.3476, -0.032, 0.089),
        }},
    ("M4", "pre"):  {
        "n":59, "df":55, "r2":0.436,
        "params": {
            "intercept":  (-0.4406, 0.3867, -1.14, 0.2594, -1.215, 0.334),
            "%ΔY":        (-0.0157, 0.0476, -0.33, 0.7429, -0.111, 0.080),
            "ΔFFR":       (-0.3204, 0.1896, -1.69, 0.0967, -0.700, 0.060),
            "ΔOverhang":  (-1.1839, 0.3433, -3.45, 0.0011, -1.872, -0.496),
        }},
    # Post-period
    ("M1", "post"): {
        "n":13, "df":11, "r2":0.088,
        "params": {
            "intercept": (-0.6918, 1.2621, -0.55, 0.5946, -3.470, 2.086),
            "%ΔY":       (0.1804, 0.1754, 1.03, 0.3260, -0.206, 0.567),
        }},
    ("M2", "post"): {
        "n":13, "df":10, "r2":0.261,
        "params": {
            "intercept": (-0.4814, 1.1992, -0.40, 0.6966, -3.153, 2.191),
            "%ΔY":       (0.1863, 0.1656, 1.12, 0.2871, -0.183, 0.555),
            "ΔFFR":      (-0.2386, 0.1558, -1.53, 0.1566, -0.586, 0.109),
        }},
    ("M3", "post"): {
        "n":13, "df":9, "r2":0.263,
        "params": {
            "intercept": (-0.4429, 1.2920, -0.34, 0.7396, -3.366, 2.480),
            "%ΔY":       (0.1630, 0.2403, 0.68, 0.5145, -0.380, 0.707),
            "ΔFFR":      (-0.1434, 0.6966, -0.21, 0.8415, -1.719, 1.432),
            "Overhang":  (-0.0607, 0.4318, -0.14, 0.8913, -1.037, 0.916),
        }},
    ("M4", "post"): {
        "n":13, "df":9, "r2":0.388,
        "params": {
            "intercept":  (-0.8367, 1.1796, -0.71, 0.4961, -3.505, 1.832),
            "%ΔY":        (0.1504, 0.1611, 0.93, 0.3749, -0.214, 0.515),
            "ΔFFR":       (-0.3321, 0.1644, -2.02, 0.0741, -0.704, 0.040),
            "ΔOverhang":  (-0.8487, 0.6216, -1.37, 0.2053, -2.255, 0.557),
        }},
}

row("Model", "Period", "n", "df", "R²", "Parameter",
    "Coef", "SE", "t", "p", "Sig", "95% CI_lo", "95% CI_hi",
    "Predicted sign", "Sign correct?")

MODEL_LABELS = {
    "M1": "M1: Simple Okun",
    "M2": "M2: Okun + ΔFFR",
    "M3": "M3: Okun + ΔFFR + Overhang level",
    "M4": "M4: Okun + ΔFFR + ΔOverhang QoQ",
}

PREDICTED_SIGN = {
    "intercept": "any",
    "%ΔY":       "negative",
    "ΔFFR":      "negative",
    "Overhang":  "positive (M3: excess stock → more unemp)",
    "ΔOverhang": "negative (M4: faster correction → more unemp)",
}

def sign_correct(param, coef):
    pred = PREDICTED_SIGN.get(param, "any")
    if pred == "any":    return "N/A"
    if "negative" in pred: return "YES" if coef < 0 else "NO"
    if "positive" in pred: return "YES" if coef > 0 else "NO"
    return "N/A"

for (model, period), spec_data in overhang_data.items():
    n_, df_, r2_ = spec_data["n"], spec_data["df"], spec_data["r2"]
    first = True
    for param, (coef, se, t, p, lo, hi) in spec_data["params"].items():
        row(MODEL_LABELS[model] if first else "",
            period if first else "",
            n_ if first else "", df_ if first else "", fmt(r2_,3) if first else "",
            param, fmt(coef,4), fmt(se,4), fmt(t,2), fmt(p,3), stars(p), fmt(lo,4), fmt(hi,4),
            PREDICTED_SIGN.get(param, "any"), sign_correct(param, coef))
        first = False
    blank()

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 9 — COLLINEARITY DIAGNOSTICS (overhang test)
# ─────────────────────────────────────────────────────────────────────────────

header("Section 9 — Collinearity Diagnostics: Information Overhang Test (Post-2022)")
blank()

subheader("Pearson Correlations Among Regressors (post-2022, n=13)")
row("Variable A", "Variable B", "r", "p-value", "Interpretation")
row("Overhang level", "ΔFFR",  "+0.948", "0.000", "Near-perfect collinearity — both decline monotonically post-2022")
row("Overhang level", "%ΔY",   "-0.197", "0.520", "Low correlation")
row("ΔFFR",           "%ΔY",   "+0.023", "0.940", "Low correlation")
blank()

subheader("Variance Inflation Factors (VIF = 1/(1-R²_j), R²_j from regressing each var on others)")
row("Model", "Regressor", "VIF", "Flagged?", "Implication")
row("M3 (Overhang level)", "pct_dy",     "1.90", "No",       "Acceptable")
row("M3 (Overhang level)", "delta_ffr",  "18.05","YES (>5)", "SE inflated ~4x; β estimate unreliable")
row("M3 (Overhang level)", "overhang",   "18.77","YES (>5)", "SE inflated ~4x; β estimate unreliable")
row("M4 (ΔOverhang QoQ)", "pct_dy",     "1.03", "No",       "Excellent — differencing resolved collinearity")
row("M4 (ΔOverhang QoQ)", "delta_ffr",  "1.21", "No",       "Excellent")
row("M4 (ΔOverhang QoQ)", "delta_overhang","1.24","No",      "Excellent")
blank()

subheader("Overhang Variable Summary (Information sector)")
row("Metric", "Value")
row("Overhang at AI cutoff (Q4 2022)", "+6.13% above trend")
row("Overhang latest (Q4 2025)", "-4.68% below trend")
row("ΔOverhang QoQ range (post-2022)", "-1.89% to +0.04% per quarter")
row("Trend: monotonically declining post-2022 → collinear with ΔFFR (also declining)")

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 10 — β1 STABILITY TABLE (key diagnostic for overhang test)
# ─────────────────────────────────────────────────────────────────────────────

header("Section 10 — β1 (%ΔY) Stability Across Models: Information Sector")
subheader("Key diagnostic: does β1 (Okun coefficient) move when overhang controls added?")
subheader("If overhang explains the breakdown, β1 should return toward pre-period value when controlled.")
blank()

row("Period", "Model", "Spec", "β1 (%ΔY)", "Δ from M2", "SE", "p",
    "β3 (Overhang/ΔOverhang)", "β3 p", "VIF (overhang var)", "Verdict")

pre_m2_b1  = -0.0981
post_m2_b1 =  0.1863

for model, b1, b3, b3p, vif, verdict_text in [
    ("M1 (no controls)",        -0.1339, None,    None,  None, "baseline — pre-period"),
    ("M2 (+ΔFFR)",              -0.0981, None,    None,  None, "benchmark for pre-period"),
    ("M3 (+ΔFFR + Overhang)",   -0.1004, +0.0286, 0.348, 18.77, "β1 barely moves; β3 wrong sign; VIF=19"),
    ("M4 (+ΔFFR + ΔOverhang)",  -0.0157, -1.1839, 0.001,  1.24, "β1 collapses — ΔOverhang absorbs Okun in pre-period"),
]:
    db = fmt(b1 - pre_m2_b1, 4) if model != "M1 (no controls)" else "N/A"
    row("Pre-2022", model, "Info-sector",
        fmt(b1,4), db if "M1" not in model else "",
        "", "",
        fmt(b3,4) if b3 is not None else "", fmt(b3p,3) if b3p is not None else "",
        fmt(vif,2) if vif is not None else "", verdict_text)

blank()
for model, b1, b3, b3p, vif, verdict_text in [
    ("M1 (no controls)",        +0.1804, None,    None,  None, "baseline post-period"),
    ("M2 (+ΔFFR)",              +0.1863, None,    None,  None, "benchmark — Okun INVERTED post-AI"),
    ("M3 (+ΔFFR + Overhang)",   +0.1630, -0.0607, 0.891, 18.77, "β1 barely moves (−0.023); β3 wrong sign; VIF=19 ← impaired"),
    ("M4 (+ΔFFR + ΔOverhang)",  +0.1504, -0.8487, 0.205,  1.24, "β1 barely moves (−0.036); β3 right sign but p=0.205 ← CLEAN TEST"),
]:
    db = fmt(b1 - post_m2_b1, 4) if "M1" not in model else ""
    row("Post-2022", model, "Info-sector",
        fmt(b1,4), db,
        "", "",
        fmt(b3,4) if b3 is not None else "", fmt(b3p,3) if b3p is not None else "",
        fmt(vif,2) if vif is not None else "", verdict_text)

blank()
subheader("CONCLUSION: β1 remains +0.150 to +0.186 in all post-period models.")
subheader("The overhiring-correction hypothesis does NOT explain Information's Okun breakdown.")
subheader("The clean test (M4, VIF≈1.2) confirms: right sign on ΔOverhang, p=0.205, β1 barely moves.")

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 11 — R² CHANGE ACROSS MODELS
# ─────────────────────────────────────────────────────────────────────────────

header("Section 11 — R² Progression Across Models (Information Sector)")
blank()
row("Period", "M1 (Simple)", "M2 (+ΔFFR)", "M3 (+Overhang)", "M4 (+ΔOverhang)",
    "M2-M1 gain", "M3-M2 gain", "M4-M2 gain",
    "Notes")
row("Pre-2022",  "0.113", "0.314", "0.325", "0.436",
    "+0.201", "+0.011", "+0.122",
    "M4 adds substantial R² in pre-period (ΔOverhang historically important)")
row("Post-2022", "0.088", "0.261", "0.263", "0.388",
    "+0.173", "+0.002", "+0.127",
    "M3 adds almost nothing; M4 adds 0.127 but β3 not significant (n=13)")

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 12 — BTOS DATA AVAILABILITY NOTE
# ─────────────────────────────────────────────────────────────────────────────

header("Section 12 — BTOS Data Availability and Methodology Notes")
blank()
row("Topic", "Finding")
row("BTOS core AI question start", "September 2023 (national level)")
row("BTOS Dec 2023-Feb 2024 supplement", "Sector-level AI data POOLED across 6 biweekly panels — single cross-section per sector; not biweekly time series")
row("BTOS core question end (national)", "August 2024 — not available in standard download files as sector-level")
row("BTOS sector-level AI data (continuous)", "Begins November 2025 (period 202524) — 14 biweekly panels available as of Q1 2026")
row("Data gap", "February 2024 – October 2025 (20 months) — no sector-level AI adoption data publicly available")
row("Files checked", "National.xlsx (Q1-Q9, Q11-Q24), Sector.xlsx (Q3-Q23, Q24), Subsector.xlsx (Q3-Q23, Q24)")
row("AI question code", "Question ID = 7 (Q7: 'Did this business use AI in the past two weeks?') — Yes responses by sector")
row("BTOS panel approach verdict", "Infeasible with available public data — 20-month gap precludes continuous panel identification")
row("BTOS approach used", "Cross-sectional: average sector-level AI adoption rate (Nov 2025–May 2026) as static exposure measure")
row("AIIE-BTOS validation", "Spearman ρ = 0.917, p = 0.001 — 2021 theoretical exposure score closely matches 2025 self-reported adoption")
row("Cross-section result", "Negative slope Δβ1 ~ AIIE and Δβ1 ~ BTOS% in most specs — contradicts 'AI causes Okun breakdown' story")

# ─────────────────────────────────────────────────────────────────────────────
# WRITE OUTPUT
# ─────────────────────────────────────────────────────────────────────────────

outpath = BASE + "results_comprehensive.csv"
with open(outpath, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    for r_ in rows:
        writer.writerow(r_)

print(f"Written: {outpath}")
print(f"Total rows: {len(rows)}")

# Also print a quick summary count per section
section_count = sum(1 for r_ in rows if r_ and str(r_[0]).startswith("=== "))
print(f"Sections: {section_count}")
