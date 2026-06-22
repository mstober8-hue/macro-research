import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats as sp_stats


# ================================================================
# WHY THE DIFFERENCE FORM?
# ----------------------------------------------------------------
# The existing script uses the GAP form of Okun's Law:
#   U_gap = C × Y_gap + ε
# where U_gap = actual minus natural rate, Y_gap = actual minus potential.
#
# That requires a natural rate (NAIRU) and potential output for each
# sector — which the Fed/BEA only publishes at the aggregate level.
#
# The DIFFERENCE form is the standard alternative:
#   ΔU = β × %ΔY + ε
# where ΔU   = quarter-over-quarter change in unemployment rate (pp)
#       %ΔY  = quarter-over-quarter % change in real value added
#
# Interpretation: if output grows 1%, unemployment should fall by β pp.
# Under classic Okun's Law, β ≈ −0.3 to −0.5.
# If β shrinks toward zero post-AI, the sector is producing more output
# without proportionally adding workers — the core hypothesis.
#
# The rolling regression, COVID exclusion, era split (pre/post Q4 2022),
# and chart style all match GDPUnemployment.py exactly.
# ================================================================


# ----------------------------------------------------------------
# 1. LOAD DATA
# ----------------------------------------------------------------
DATA_DIR = "Fred Fed Data /"

# Real Value Added: Information sector (quarterly, billions of chained $)
# High-AI industry — software, cloud, data, media
rvai = pd.read_csv(DATA_DIR + "RVAI.csv", parse_dates=["observation_date"])
rvai.columns = ["date", "rvai"]
rvai = rvai.set_index("date")

# Real Value Added: Leisure & Hospitality (quarterly, billions of chained $)
# Low-AI industry — restaurants, hotels, entertainment
rvaaeraf = pd.read_csv(DATA_DIR + "RVAAERAF.csv", parse_dates=["observation_date"])
rvaaeraf.columns = ["date", "rvaaeraf"]
rvaaeraf = rvaaeraf.set_index("date")

# Unemployment rate: Information sector (monthly, %)
# BLS series LNU04032237 (corrected — LNU04032240 is Education & Health Services)
unemp_info = pd.read_csv(DATA_DIR + "LNU04032237.csv", parse_dates=["observation_date"])
unemp_info.columns = ["date", "u_info"]
unemp_info = unemp_info.set_index("date")

# Unemployment rate: Leisure & Hospitality (monthly, %)
# BLS series LNU04032241
unemp_lh = pd.read_csv(DATA_DIR + "LNU04032241.csv", parse_dates=["observation_date"])
unemp_lh.columns = ["date", "u_lh"]
unemp_lh = unemp_lh.set_index("date")


# ----------------------------------------------------------------
# 2. ALIGN FREQUENCIES — monthly unemployment → quarterly
# ----------------------------------------------------------------
# Unemployment is reported monthly; value added is quarterly.
# We average the three monthly readings within each quarter to get
# one quarterly unemployment rate — same method as GDPUnemployment.py.
# "QS" = quarter-start frequency (Jan, Apr, Jul, Oct).
unemp_info_q = unemp_info.resample("QS").mean()
unemp_lh_q   = unemp_lh.resample("QS").mean()

# Merge into two industry dataframes on shared dates
info = rvai.join(unemp_info_q, how="inner").dropna()
lh   = rvaaeraf.join(unemp_lh_q, how="inner").dropna()

print(f"Information sector:    {len(info)} quarters ({info.index[0].date()} – {info.index[-1].date()})")
print(f"Leisure & Hospitality: {len(lh)} quarters ({lh.index[0].date()} – {lh.index[-1].date()})")
print()


# ----------------------------------------------------------------
# 3. COMPUTE DIFFERENCE-FORM OKUN VARIABLES
# ----------------------------------------------------------------
# %ΔY = percentage change in real value added from prior quarter.
#       pct_change() gives (this - prior) / prior × 100.
#       This is our "output growth" proxy — analogous to Y_gap in the
#       aggregate script but in growth-rate space rather than level space.
#
# ΔU  = arithmetic change in unemployment rate from prior quarter (pp).
#       diff() gives this - prior.
#       This is our "labor market pressure" proxy — analogous to U_gap.
#
# Okun's law predicts: when %ΔY is high (strong growth), ΔU is negative
# (unemployment falls). So the regression slope β should be negative.
# A β drifting toward zero means growth is no longer pulling unemployment down.

info["pct_dy"] = info["rvai"].pct_change() * 100
info["delta_u"] = info["u_info"].diff()

lh["pct_dy"] = lh["rvaaeraf"].pct_change() * 100
lh["delta_u"] = lh["u_lh"].diff()

# Drop the first row (NaN from differencing)
info = info.dropna()
lh   = lh.dropna()

print("=== Information sector — first 5 rows ===")
print(info[["rvai", "pct_dy", "u_info", "delta_u"]].head().round(4))
print()
print("=== Leisure & Hospitality — first 5 rows ===")
print(lh[["rvaaeraf", "pct_dy", "u_lh", "delta_u"]].head().round(4))
print()


# ----------------------------------------------------------------
# 4. EXCLUDE COVID QUARTERS (Q2 2020 – Q1 2021)
# ----------------------------------------------------------------
# Same quarters excluded as GDPUnemployment.py.
# The pandemic shock is so large it dominates any regression that
# includes it and obscures the structural AI signal we're looking for.
covid_quarters = pd.date_range("2020-04-01", "2021-01-01", freq="QS")

info_clean = info[~info.index.isin(covid_quarters)].copy()
lh_clean   = lh[~lh.index.isin(covid_quarters)].copy()

print(f"After removing COVID quarters:")
print(f"  Information:    {len(info_clean)} quarters")
print(f"  Leisure & Hosp: {len(lh_clean)} quarters")
print()


# ================================================================
# CHART 1 — SCATTER: %ΔY vs ΔU by era, both industries side by side
# ----------------------------------------------------------------
# This is the direct industry equivalent of Chart 2 (gap divergence
# scatter) in GDPUnemployment.py.
#
# Each dot is one quarter. X-axis = output growth, Y-axis = change in1
# unemployment. Under Okun's Law the cloud should slope downward (top-lef1t
# to bottom-right). If the post-2022 dots cluster near zero ΔU regardless
# of output growth, the law is weakening in that sector.
#
# ERA SPLIT: same as existing script — Q4 2022 onward is "post-ChatGPT."
# ================================================================

era_colors = {"Pre Q4 2022": "steelblue", "Q4 2022–Present": "darkorange"}

for df_c, sector_name, y_col in [
    (info_clean, "Information (High AI)", "u_info"),
    (lh_clean,   "Leisure & Hospitality (Low AI)", "u_lh"),
]:
    df_c["era"] = "Pre Q4 2022"
    df_c.loc[df_c.index >= "2022-10-01", "era"] = "Q4 2022–Present"

fig1, axes1 = plt.subplots(1, 2, figsize=(15, 7), sharey=False)

for ax, (df_c, sector_name) in zip(axes1, [
    (info_clean, "Information (High AI)"),
    (lh_clean,   "Leisure & Hospitality (Low AI)"),
]):
    for era, color in era_colors.items():
        sub = df_c[df_c["era"] == era]
        ax.scatter(sub["pct_dy"], sub["delta_u"],
                   color=color, alpha=0.75, s=55, zorder=3, label=era)

    # Regression line per era
    for era, color in era_colors.items():
        sub = df_c[df_c["era"] == era].dropna(subset=["pct_dy", "delta_u"])
        if len(sub) < 4:
            continue
        m, b = np.polyfit(sub["pct_dy"], sub["delta_u"], 1)
        x_r = np.linspace(sub["pct_dy"].min(), sub["pct_dy"].max(), 100)
        ax.plot(x_r, m * x_r + b, color=color, linewidth=1.5,
                linestyle="--", alpha=0.9,
                label=f"{era} slope = {m:.3f}")

    ax.axhline(0, color="black", linewidth=0.8, linestyle="--")
    ax.axvline(0, color="black", linewidth=0.8, linestyle="--")
    ax.set_xlabel("% Change in Real Value Added (%ΔY)", fontsize=11)
    ax.set_ylabel("Change in Unemployment Rate (ΔU, pp)", fontsize=11)
    ax.set_title(f"{sector_name}\nOkun's Difference Form: %ΔY vs ΔU",
                 fontsize=12, fontweight="bold")
    ax.legend(fontsize=9)
    ax.grid(True, linestyle="--", alpha=0.4)

plt.suptitle("Industry Okun's Law — Scatter by Era\n"
             "Downward slope = law holds | Flat/upward slope = law breaking down",
             fontsize=13, fontweight="bold", y=1.01)
plt.tight_layout()
plt.savefig("industry_scatter.png", dpi=150, bbox_inches="tight")
print("Chart 1 saved: industry_scatter.png")


# ================================================================
# CHART 2 — ROLLING REGRESSION: Okun's β over time
# ----------------------------------------------------------------
# Same 12-quarter (3-year) rolling window as GDPUnemployment.py.
# For each window we fit: ΔU = β × %ΔY + ε and record β and r.
#
# β (slope): how many pp does unemployment change per 1% of output growth.
#    Classic Okun → β ≈ −0.3 to −0.5.
#    β → 0 means growth no longer moves unemployment.
#
# r (correlation): sign and strength of the relationship.
#    r < 0 → law holds (output up, unemployment down).
#    r > 0 → law inverted (output up, unemployment also up — very anomalous).
#
# Plotting both industries on the same axes makes the divergence visible:
# if high-AI (Information) β decays faster post-2022 than low-AI
# (Leisure & Hospitality), that's evidence AI is the mechanism.
# ================================================================

WINDOW = 12

def rolling_okun(df_c):
    """Return a DataFrame of rolling slope (β) and correlation (r)."""
    idx    = df_c.index.tolist()
    dates, slopes, rs = [], [], []
    for i in range(WINDOW, len(idx) + 1):
        w = df_c.iloc[i - WINDOW : i]
        x = w["pct_dy"].values
        y = w["delta_u"].values
        if np.std(x) < 1e-9:
            continue
        s, _ = np.polyfit(x, y, 1)
        r     = np.corrcoef(x, y)[0, 1]
        dates.append(idx[i - 1])
        slopes.append(s)
        rs.append(r)
    return pd.DataFrame({"slope": slopes, "r": rs}, index=dates)

roll_info = rolling_okun(info_clean)
roll_lh   = rolling_okun(lh_clean)

fig2, (ax2a, ax2b) = plt.subplots(2, 1, figsize=(13, 10), sharex=False)

# ── β (slope) panel ─────────────────────────────────────────────
for roll_df, label, color in [
    (roll_info, "Information (High AI)",         "darkorange"),
    (roll_lh,   "Leisure & Hospitality (Low AI)", "steelblue"),
]:
    ax2a.plot(roll_df.index, roll_df["slope"], color=color,
              linewidth=2, label=label)

ax2a.axhline(0, color="black", linewidth=0.8, linestyle="--")
ax2a.axvspan(pd.Timestamp("2022-10-01"),
             max(roll_info.index[-1], roll_lh.index[-1]),
             alpha=0.08, color="gold", label="Post-ChatGPT era (Q4 2022+)")
ax2a.set_ylabel("Rolling Okun's β\n(ΔU per 1% output growth)", fontsize=11)
ax2a.set_title("Rolling 3-Year Okun's β by Industry — Is High-AI Decaying Faster?",
               fontsize=13, fontweight="bold")
ax2a.legend(fontsize=10)
ax2a.grid(True, linestyle="--", alpha=0.4)

# ── r (correlation) panel ───────────────────────────────────────
for roll_df, label, color in [
    (roll_info, "Information (High AI)",         "darkorange"),
    (roll_lh,   "Leisure & Hospitality (Low AI)", "steelblue"),
]:
    ax2b.plot(roll_df.index, roll_df["r"], color=color,
              linewidth=2, label=label)

ax2b.axhline(0, color="black", linewidth=0.8, linestyle="--")
ax2b.axvspan(pd.Timestamp("2022-10-01"),
             max(roll_info.index[-1], roll_lh.index[-1]),
             alpha=0.08, color="gold")
ax2b.set_ylabel("Rolling Correlation (r)\nr < 0 = law holds | r > 0 = law inverted", fontsize=11)
ax2b.set_xlabel("Quarter (end of 12-quarter window)", fontsize=12)
ax2b.set_ylim(-1.05, 1.05)
ax2b.legend(fontsize=10)
ax2b.grid(True, linestyle="--", alpha=0.4)

plt.tight_layout()
plt.savefig("industry_rolling_okun.png", dpi=150, bbox_inches="tight")
print("Chart 2 saved: industry_rolling_okun.png")


# ================================================================
# CHART 3 — OKUN RESIDUAL over time, both industries
# ----------------------------------------------------------------
# Fit Okun's β on pre-2022 data only (the "historical normal").
# Then for every quarter compute the residual:
#   residual = actual ΔU − predicted ΔU
#
# Predicted ΔU = what Okun's law says unemployment should have done
#               given the output growth that actually occurred.
#
# A POSITIVE residual means unemployment fell LESS than output growth
# would historically have predicted — consistent with AI absorbing
# the output gains without adding workers.
#
# A NEGATIVE residual means unemployment fell MORE than predicted —
# the labor market is tighter than output alone explains.
#
# KEY TEST: if the high-AI sector (Information) runs a persistently
# positive residual post-2022 while low-AI (Leisure) does not,
# that is direct industry-level evidence for the AI hypothesis.
# ================================================================

def fit_pre2022_and_residual(df_c):
    """
    Fit Okun's β on pre-Q4-2022 clean data.
    Return (slope, intercept, df_with_residual).
    """
    pre22 = df_c[df_c.index < "2022-10-01"].dropna(subset=["pct_dy", "delta_u"])
    m, b  = np.polyfit(pre22["pct_dy"], pre22["delta_u"], 1)
    df_out = df_c.copy()
    df_out["u_predicted"] = m * df_out["pct_dy"] + b
    df_out["okun_resid"]  = df_out["delta_u"] - df_out["u_predicted"]
    return m, b, df_out

m_info, b_info, info_resid = fit_pre2022_and_residual(info_clean)
m_lh,   b_lh,   lh_resid   = fit_pre2022_and_residual(lh_clean)

print(f"\n=== Pre-2022 Okun Fit ===")
print(f"  Information:    ΔU = {m_info:.4f} × %ΔY + {b_info:.4f}")
print(f"  Leisure & Hosp: ΔU = {m_lh:.4f}   × %ΔY + {b_lh:.4f}")
print()

# Insert NaN rows at COVID dates so line breaks cleanly (same trick as existing script)
nan_info = pd.DataFrame({"okun_resid": np.nan},
                        index=pd.date_range("2020-04-01", "2021-01-01", freq="QS"))
nan_lh   = pd.DataFrame({"okun_resid": np.nan},
                        index=pd.date_range("2020-04-01", "2021-01-01", freq="QS"))

info_plot = pd.concat([info_resid[["okun_resid"]], nan_info]).sort_index()
lh_plot   = pd.concat([lh_resid[["okun_resid"]],   nan_lh]).sort_index()

fig3, (ax3a, ax3b) = plt.subplots(2, 1, figsize=(13, 11),
                                   gridspec_kw={"height_ratios": [1, 1]})

for ax, df_plot, sector_name, m, b, color in [
    (ax3a, info_plot, "Information (High AI)",         m_info, b_info, "darkorange"),
    (ax3b, lh_plot,   "Leisure & Hospitality (Low AI)", m_lh,   b_lh,   "steelblue"),
]:
    ax.axhline(0, color="black", linewidth=1.2, linestyle="--", zorder=2)
    ax.fill_between(df_plot.index, df_plot["okun_resid"], 0,
                    where=df_plot["okun_resid"] > 0,
                    color="firebrick", alpha=0.4,
                    label="Unemployment higher than Okun predicts")
    ax.fill_between(df_plot.index, df_plot["okun_resid"], 0,
                    where=df_plot["okun_resid"] <= 0,
                    color=color, alpha=0.4,
                    label="Unemployment lower than Okun predicts")
    ax.plot(df_plot.index, df_plot["okun_resid"],
            color="black", linewidth=1.2, zorder=3)

    ax.axvspan(pd.Timestamp("2020-04-01"), pd.Timestamp("2021-04-01"),
               alpha=0.15, color="crimson", label="COVID quarters excluded")
    ax.axvspan(pd.Timestamp("2022-10-01"), df_plot.index[-1],
               alpha=0.08, color="gold", label="Post-ChatGPT era (Q4 2022+)")

    ax.set_ylabel("Okun Residual (pp)\nActual ΔU − Predicted ΔU", fontsize=11)
    ax.set_title(f"{sector_name} — Okun Residual\n"
                 f"Pre-2022 fit: ΔU = {m:.3f} × %ΔY + {b:.3f}",
                 fontsize=12, fontweight="bold")
    ax.legend(fontsize=9, loc="lower left")
    ax.grid(True, linestyle="--", alpha=0.4)

plt.tight_layout(pad=2.5)
plt.savefig("industry_okun_residual.png", dpi=150, bbox_inches="tight")
print("Chart 3 saved: industry_okun_residual.png")

# Print post-2022 residuals for both sectors so you can read them numerically
print("\n=== Post-Q4 2022 Okun Residuals: Information ===")
print(info_resid[info_resid.index >= "2022-10-01"][["pct_dy", "delta_u", "okun_resid"]].round(3).to_string())
print("\n=== Post-Q4 2022 Okun Residuals: Leisure & Hospitality ===")
print(lh_resid[lh_resid.index >= "2022-10-01"][["pct_dy", "delta_u", "okun_resid"]].round(3).to_string())
print()


# ================================================================
# CHART 4 — STATISTICAL COMPARISON: post-AI windows vs historical baseline
# ----------------------------------------------------------------
# Same statistical test as GDPUnemployment.py Chart 3.
# For each sector:
#   - Compute the distribution of rolling r values PRE Q4 2022
#     (mean, std — this is the "historical normal" for that sector)
#   - For each POST Q4 2022 window, ask: how probable is this r
#     under the historical normal distribution?
#   - p value near 0 means the post-AI correlation is extremely
#     unlikely to have come from the same regime — regime change signal.
#
# Doing this for BOTH sectors and comparing is the key test:
# if high-AI shows statistically significant regime change but
# low-AI does not, AI is the most parsimonious explanation.
# ================================================================

print("=" * 60)
for roll_df, sector_name in [
    (roll_info, "Information (High AI)"),
    (roll_lh,   "Leisure & Hospitality (Low AI)"),
]:
    pre_ai  = roll_df[roll_df.index < "2022-10-01"]["r"]
    post_ai = roll_df[roll_df.index >= "2022-10-01"]["r"]

    hist_mean = pre_ai.mean()
    hist_std  = pre_ai.std()

    print(f"\n{sector_name}")
    print(f"  Historical baseline (pre-Q4 2022): mean r = {hist_mean:.3f}, std = {hist_std:.3f}")
    print(f"  {'Quarter':<14}  {'r':>7}  {'p(r ≥ observed)':>16}")
    for dt, r_val in post_ai.items():
        p = 1 - sp_stats.norm.cdf(r_val, loc=hist_mean, scale=hist_std)
        print(f"  {str(dt.date()):<14}  {r_val:>7.3f}  {p:>15.4f}")

print()


# ================================================================
# CHART 5 — INTER-INDUSTRY UNEMPLOYMENT CORRELATION
# ----------------------------------------------------------------
# The logic here is different from everything above. Charts 1–4
# ask: does Okun's Law hold within each sector? This chart asks:
# do the two sectors' unemployment rates MOVE TOGETHER at all?
#
# WHY THIS MATTERS FOR YOUR HYPOTHESIS
# Before AI, both sectors are driven by the same business cycle —
# when a recession hits, unemployment rises in both Information and
# Leisure & Hospitality. That shared cycle produces a strong positive
# correlation (r close to +1).
#
# If AI is specifically disrupting the high-AI sector, the correlation
# should FALL post-2022 — Information unemployment starts moving
# independently because its driver is no longer just the business
# cycle but also AI displacement.
#
# A correlation that was r ≈ 0.8 before and drops to r ≈ 0.2 after
# is a decoupling signal: the two sectors no longer share the same
# unemployment dynamics.
#
# HOW WE COMPUTE IT
# We merge the two quarterly unemployment rate series on shared dates,
# then run a 12-quarter rolling correlation (same window as all other
# rolling regressions in this script and GDPUnemployment.py).
# We also compute full-sample r for pre vs post Q4 2022 and run a
# Fisher Z-test to check whether the difference is statistically
# significant.
#
# Fisher Z-test: converts r to a normally distributed Z score so we
# can test whether r_pre and r_post are significantly different.
#   Z = 0.5 × ln((1+r)/(1−r))  — Fisher (1915) transformation.
# If |Z_pre − Z_post| / SE > 1.96, the difference is significant at 95%.
# ================================================================

# Merge the two quarterly unemployment series on shared dates
u_info_q = unemp_info.resample("QS").mean()
u_lh_q   = unemp_lh.resample("QS").mean()
u_joint   = u_info_q.join(u_lh_q, how="inner").dropna()
u_joint.columns = ["u_info", "u_lh"]

# Exclude COVID quarters (same as everywhere else)
u_joint_clean = u_joint[~u_joint.index.isin(covid_quarters)].copy()

# ── Rolling 12-quarter correlation ──────────────────────────────
roll_corr_dates = []
roll_corr_vals  = []
idx_j = u_joint_clean.index.tolist()

for i in range(WINDOW, len(idx_j) + 1):
    w = u_joint_clean.iloc[i - WINDOW : i]
    r = w["u_info"].corr(w["u_lh"])
    roll_corr_dates.append(idx_j[i - 1])
    roll_corr_vals.append(r)

roll_corr = pd.Series(roll_corr_vals, index=roll_corr_dates)

# ── Pre vs post Q4 2022 full-sample r ───────────────────────────
pre_joint  = u_joint_clean[u_joint_clean.index < "2022-10-01"]
post_joint = u_joint_clean[u_joint_clean.index >= "2022-10-01"]

r_pre, _ = sp_stats.pearsonr(pre_joint["u_info"], pre_joint["u_lh"])
r_post, _ = (sp_stats.pearsonr(post_joint["u_info"], post_joint["u_lh"])
             if len(post_joint) >= 3 else (np.nan, np.nan))

def fisher_z(r):
    r = np.clip(r, -0.9999, 0.9999)
    return 0.5 * np.log((1 + r) / (1 - r))

n_pre  = len(pre_joint)
n_post = len(post_joint)

z_pre  = fisher_z(r_pre)
z_post = fisher_z(r_post) if not np.isnan(r_post) else np.nan

if not np.isnan(z_post):
    se_diff = np.sqrt(1 / (n_pre - 3) + 1 / (n_post - 3))
    z_stat  = (z_pre - z_post) / se_diff
    p_diff  = 2 * (1 - sp_stats.norm.cdf(abs(z_stat)))
else:
    z_stat, p_diff = np.nan, np.nan

print("=== Inter-Industry Unemployment Correlation ===")
print(f"  Pre-Q4 2022  (n={n_pre:3d}):  r = {r_pre:.3f}")
if not np.isnan(r_post):
    print(f"  Post-Q4 2022 (n={n_post:3d}):  r = {r_post:.3f}")
    significance = "SIGNIFICANT — correlation changed" if p_diff < 0.05 else "not significant at 95%"
    print(f"  Fisher Z-test: Z = {z_stat:.3f},  p = {p_diff:.4f}  ({significance})")
print()

# ── Plot: two panels ─────────────────────────────────────────────
fig5, (ax5a, ax5b) = plt.subplots(2, 1, figsize=(13, 10),
                                   gridspec_kw={"height_ratios": [1.2, 1]})

# Top: raw unemployment rates for both sectors over time
# Insert NaN at COVID so the line breaks visually (same trick as existing script)
nan_u  = pd.DataFrame({"u_info": np.nan, "u_lh": np.nan},
                      index=pd.date_range("2020-04-01", "2021-01-01", freq="QS"))
u_plot = pd.concat([u_joint_clean, nan_u]).sort_index()

ax5a.plot(u_plot.index, u_plot["u_info"], color="darkorange",
          linewidth=2, label="Information (High AI)")
ax5a.plot(u_plot.index, u_plot["u_lh"], color="steelblue",
          linewidth=2, label="Leisure & Hospitality (Low AI)")
ax5a.axvspan(pd.Timestamp("2020-04-01"), pd.Timestamp("2021-04-01"),
             alpha=0.15, color="crimson", label="COVID quarters excluded")
ax5a.axvspan(pd.Timestamp("2022-10-01"), u_plot.index[-1],
             alpha=0.08, color="gold", label="Post-ChatGPT era (Q4 2022+)")
ax5a.set_ylabel("Unemployment Rate (%)", fontsize=11)
ax5a.set_title("Unemployment Rates: Information vs Leisure & Hospitality\n"
               "Shared movement = business cycle | Divergence = sector-specific shock",
               fontsize=12, fontweight="bold")
ax5a.legend(fontsize=10)
ax5a.grid(True, linestyle="--", alpha=0.4)

# Bottom: rolling 12-quarter correlation between the two rates
ax5b.plot(roll_corr.index, roll_corr.values, color="black", linewidth=2,
          label="Rolling 12-qtr correlation (r) between sectors")
ax5b.axhline(0, color="black", linewidth=0.8, linestyle="--")
ax5b.axhline(r_pre, color="steelblue", linewidth=1.2, linestyle=":",
             label=f"Pre-2022 full-sample r = {r_pre:.3f}")
if not np.isnan(r_post):
    ax5b.axhline(r_post, color="darkorange", linewidth=1.2, linestyle=":",
                 label=f"Post-2022 full-sample r = {r_post:.3f}  (p={p_diff:.3f})")
ax5b.axvspan(pd.Timestamp("2022-10-01"), roll_corr.index[-1],
             alpha=0.08, color="gold", label="Post-ChatGPT era (Q4 2022+)")
ax5b.set_ylabel("Rolling Correlation (r)\nbetween sector unemployment rates", fontsize=11)
ax5b.set_xlabel("Quarter (end of 12-quarter window)", fontsize=12)
ax5b.set_ylim(-1.05, 1.05)
ax5b.set_title("Rolling Inter-Industry Correlation — Are They Decoupling?\n"
               "r falling post-2022 = sectors no longer share the same unemployment dynamic",
               fontsize=12, fontweight="bold")
ax5b.legend(fontsize=9)
ax5b.grid(True, linestyle="--", alpha=0.4)

plt.tight_layout(pad=2.5)
plt.savefig("industry_unemployment_correlation.png", dpi=150, bbox_inches="tight")
print("Chart 5 saved: industry_unemployment_correlation.png")

print()


# ================================================================
# CHART 6 — OUTPUT GROWTH vs UNEMPLOYMENT: THE DECOUPLING PICTURE
# ----------------------------------------------------------------
# This chart directly captures what you observed: unemployment rates
# move together across sectors, but output diverged — specifically
# in the high-AI (Information) sector post-2022.
#
# PANEL A — Indexed output (both sectors, base = Q4 2019)
#   We set Q4 2019 = 100 for both sectors so they're on the same
#   scale regardless of dollar size. This shows GROWTH, not levels.
#   Under Okun's Law, faster output growth should pull unemployment
#   down more. If Information output surges but its unemployment
#   tracks Leisure & Hospitality's, the law is broken specifically
#   on the output side in the high-AI sector.
#
# PANEL B — Output growth vs unemployment rate, post-2022 only
#   X-axis: cumulative % change in real value added since Q4 2022
#   Y-axis: unemployment rate in that quarter
#   Each dot is one quarter. Under Okun's Law: as output grows,
#   unemployment should fall — downward slope expected.
#   If Information dots are flat (output up, unemployment unchanged)
#   while Leisure & Hospitality dots slope down normally, that IS
#   the AI hypothesis in chart form.
# ================================================================

# ── Base index both output series to Q4 2019 = 100 ──────────────
# Q4 2019 is pre-COVID, pre-AI — a clean baseline.
base_date = pd.Timestamp("2019-10-01")

info_idx = info[["rvai", "u_info"]].copy()
lh_idx   = lh[["rvaaeraf", "u_lh"]].copy()

base_info = info_idx.loc[info_idx.index == base_date, "rvai"]
base_lh   = lh_idx.loc[lh_idx.index == base_date, "rvaaeraf"]

if len(base_info) == 0 or len(base_lh) == 0:
    # Fall back to first shared pre-COVID quarter if Q4 2019 not present
    pre_covid = info_idx[info_idx.index < "2020-01-01"]
    base_info = pre_covid["rvai"].iloc[[-1]]
    base_lh   = lh_idx[lh_idx.index < "2020-01-01"]["rvaaeraf"].iloc[[-1]]
    base_date = pre_covid.index[-1]
    print(f"Note: Q4 2019 not in data, using {base_date.date()} as base.")

info_idx["output_idx"] = info_idx["rvai"]   / base_info.values[0] * 100
lh_idx["output_idx"]   = lh_idx["rvaaeraf"] / base_lh.values[0]   * 100

# Insert NaN at COVID for clean line breaks
nan_idx = pd.DataFrame({"output_idx": np.nan, "u_info": np.nan, "u_lh": np.nan},
                       index=pd.date_range("2020-04-01", "2021-01-01", freq="QS"))

info_plot6 = pd.concat([info_idx[["output_idx", "u_info"]], nan_idx[["output_idx"]]]).sort_index()
lh_plot6   = pd.concat([lh_idx[["output_idx", "u_lh"]],   nan_idx[["output_idx"]]]).sort_index()

# ── Post-2022 output growth vs unemployment for scatter panel ────
# Cumulative output growth since Q4 2022 base
base22_date = pd.Timestamp("2022-10-01")

info_post22 = info_clean[info_clean.index >= base22_date].copy()
lh_post22   = lh_clean[lh_clean.index >= base22_date].copy()

base22_info = info.loc[info.index == base22_date, "rvai"]
base22_lh   = lh.loc[lh.index == base22_date, "rvaaeraf"]

if len(base22_info) > 0:
    info_post22["cum_output_growth"] = (info_post22["rvai"] / base22_info.values[0] - 1) * 100
    lh_post22["cum_output_growth"]   = (lh_post22["rvaaeraf"] / base22_lh.values[0] - 1) * 100
else:
    info_post22["cum_output_growth"] = info_post22["pct_dy"].cumsum()
    lh_post22["cum_output_growth"]   = lh_post22["pct_dy"].cumsum()

# ── Plot ─────────────────────────────────────────────────────────
fig6, (ax6a, ax6b) = plt.subplots(1, 2, figsize=(16, 7))

# Panel A: indexed output over time, with unemployment overlaid on twin axis
ax6a_u = ax6a.twinx()

ax6a.plot(info_plot6.index, info_plot6["output_idx"], color="darkorange",
          linewidth=2.5, label="Information output index (High AI)")
ax6a.plot(lh_plot6.index, lh_plot6["output_idx"], color="steelblue",
          linewidth=2.5, label="Leisure & Hospitality output index (Low AI)")
ax6a.axhline(100, color="black", linewidth=0.8, linestyle="--", alpha=0.5)
ax6a.axvspan(pd.Timestamp("2020-04-01"), pd.Timestamp("2021-04-01"),
             alpha=0.15, color="crimson")
ax6a.axvspan(base22_date, info_plot6.index[-1],
             alpha=0.08, color="gold")
ax6a.text(base22_date + pd.DateOffset(months=1), ax6a.get_ylim()[0] if False else 80,
          "Post-ChatGPT", color="goldenrod", fontsize=8, style="italic")
ax6a.set_ylabel("Real Value Added (Q4 2019 = 100)", fontsize=11, color="black")
ax6a.set_xlabel("Quarter", fontsize=11)
ax6a.set_title("Output Index vs Unemployment Rate\nOutput diverges; unemployment tracks together",
               fontsize=12, fontweight="bold")

# Unemployment on the right axis — both sectors
ax6a_u.plot(info_idx.index, info_idx["u_info"], color="darkorange",
            linewidth=1.5, linestyle=":", alpha=0.7,
            label="Information unemployment rate (right)")
ax6a_u.plot(lh_idx.index, lh_idx["u_lh"], color="steelblue",
            linewidth=1.5, linestyle=":", alpha=0.7,
            label="Leisure & Hosp unemployment rate (right)")
ax6a_u.set_ylabel("Unemployment Rate (%)", fontsize=11, color="gray")
ax6a_u.tick_params(axis="y", labelcolor="gray")

# Combined legend
lines_a,  labels_a  = ax6a.get_legend_handles_labels()
lines_au, labels_au = ax6a_u.get_legend_handles_labels()
ax6a.legend(lines_a + lines_au, labels_a + labels_au, fontsize=8, loc="upper left")
ax6a.grid(True, linestyle="--", alpha=0.4)

# Panel B: scatter — cumulative output growth post-2022 vs unemployment rate
# Dots colored by time (blue = early, orange = late) to show trajectory
n_i = len(info_post22)
n_l = len(lh_post22)

sc_i = ax6b.scatter(info_post22["cum_output_growth"], info_post22["u_info"],
                    c=range(n_i), cmap="Oranges", s=70, zorder=4,
                    label="Information (High AI)", edgecolors="darkorange", linewidths=0.8)
sc_l = ax6b.scatter(lh_post22["cum_output_growth"], lh_post22["u_lh"],
                    c=range(n_l), cmap="Blues", s=70, zorder=4,
                    label="Leisure & Hospitality (Low AI)", edgecolors="steelblue", linewidths=0.8)

# Regression lines for each sector post-2022
for df_p, col, color, label in [
    (info_post22, "u_info", "darkorange", "Info"),
    (lh_post22,   "u_lh",   "steelblue",  "L&H"),
]:
    sub = df_p.dropna(subset=["cum_output_growth", col])
    if len(sub) >= 3:
        m, b = np.polyfit(sub["cum_output_growth"], sub[col], 1)
        x_r  = np.linspace(sub["cum_output_growth"].min(), sub["cum_output_growth"].max(), 100)
        ax6b.plot(x_r, m * x_r + b, color=color, linewidth=1.5, linestyle="--",
                  label=f"{label} slope = {m:.3f} pp per 1% output growth")

ax6b.set_xlabel("Cumulative Output Growth since Q4 2022 (%)", fontsize=11)
ax6b.set_ylabel("Unemployment Rate (%)", fontsize=11)
ax6b.set_title("Post-AI Era: Output Growth vs Unemployment Rate\n"
               "Flat slope = output grew but unemployment didn't fall (Okun broken)",
               fontsize=12, fontweight="bold")
ax6b.legend(fontsize=9)
ax6b.grid(True, linestyle="--", alpha=0.4)

plt.tight_layout()
plt.savefig("industry_output_vs_unemployment.png", dpi=150, bbox_inches="tight")
print("Chart 6 saved: industry_output_vs_unemployment.png")

# Print the post-2022 numbers so you can read the divergence exactly
print("\n=== Post-Q4 2022: Output Growth and Unemployment — Information ===")
print(info_post22[["rvai", "cum_output_growth", "u_info"]].round(2).to_string())
print("\n=== Post-Q4 2022: Output Growth and Unemployment — Leisure & Hospitality ===")
print(lh_post22[["rvaaeraf", "cum_output_growth", "u_lh"]].round(2).to_string())

print()
print("All charts saved.")
plt.show()
