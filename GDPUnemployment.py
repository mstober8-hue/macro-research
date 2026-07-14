"""
GDPUnemployment.py
Okun's Law in the AI Era — Aggregate (economy-wide) analysis

Tests whether the historical inverse relationship between the output gap
(how far GDP sits above/below its sustainable potential) and the unemployment
gap (how far unemployment sits above/below its natural rate) has weakened
since Q4 2022 (ChatGPT's public release, used as the AI-era cutoff).

Methodology: gap form of Okun's Law, U_gap = C * Y_gap + intercept, fit on a
rolling 12-quarter (3-year) window so the coefficient C can be tracked over
time rather than assumed constant. COVID quarters (Q2 2020-Q1 2021) are
excluded from all regressions since the pandemic shock was a policy-driven
shutdown, not an organic output-employment relationship.

See README.md for the full plain-language walkthrough of each chart.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats as sp_stats


# ----------------------------------------------------------------
# 1. LOAD DATA — four FRED series, all quarterly except UNRATE
# ----------------------------------------------------------------
DATA_DIR = "FRED-Data/"

gdp = pd.read_csv(DATA_DIR + "GDPC1.csv", parse_dates=["observation_date"])
gdp.columns = ["date", "gdp"]
gdp = gdp.set_index("date")

gdppot = pd.read_csv(DATA_DIR + "GDPPOT.csv", parse_dates=["observation_date"])
gdppot.columns = ["date", "gdppot"]
gdppot = gdppot.set_index("date")

unrate = pd.read_csv(DATA_DIR + "UNRATE.csv", parse_dates=["observation_date"])
unrate.columns = ["date", "unrate"]
unrate = unrate.set_index("date")

nrou = pd.read_csv(DATA_DIR + "NROU.csv", parse_dates=["observation_date"])
nrou.columns = ["date", "nrou"]
nrou = nrou.set_index("date")

# --- Align frequencies: resample monthly unemployment to quarterly ---
# UNRATE is published monthly; averaging the three months in each quarter
# lines it up with the quarterly GDP/NROU series before merging.
unrate_q = unrate.resample("QS").mean()

# Merge on shared dates — inner join keeps only quarters where all four
# series report a value; any gaps at the edges of a series are dropped.
df = gdp.join(gdppot, how="inner").join(unrate_q, how="inner").join(nrou, how="inner").dropna()

# ----------------------------------------------------------------
# 2. COMPUTE OKUN'S LAW GAP VARIABLES
# ----------------------------------------------------------------
# Raw GDP can't be compared across decades (the economy is simply bigger
# now), so both output and unemployment are converted into deviations from
# "normal" — this is the transformation that makes Okun's Law comparable
# across eras.
#
# Output Gap: % deviation of actual GDP from potential GDP.
#   Positive = economy running above sustainable potential (overheating).
#   Negative = economy has slack (resources/workers underutilized).
df["y_gap"] = (df["gdp"] - df["gdppot"]) / df["gdppot"] * 100   # expressed in %

# Unemployment Gap: actual unemployment minus the natural rate (NROU).
#   Positive = more people out of work than the natural-rate baseline.
#   Negative = labor market tighter than normal.
# Under Okun's Law, u_gap should move opposite to y_gap (rising output ->
# falling unemployment gap). That inverse relationship is what every
# regression below is testing for stability.
df["u_gap"] = df["unrate"] - df["nrou"]

print(f"Full dataset: {len(df)} quarters ({df.index[0].date()} – {df.index[-1].date()})\n")
print("=== Gap Variables (first 5 rows) ===")
print(df[["gdp", "gdppot", "y_gap", "unrate", "nrou", "u_gap"]].head().round(4), "\n")

# --- Exclude COVID quarters: Q2 2020 through Q1 2021 ---
# GDP cratered and unemployment spiked because businesses were legally
# closed, not because of any organic output-employment relationship.
# Including these quarters would let the model mistake a policy shock for
# a structural pattern, corrupting every regression below. They're kept
# in df_covid (not deleted) so charts can still show them for transparency.
covid_quarters = pd.date_range("2020-04-01", "2021-01-01", freq="QS")
df_clean = df[~df.index.isin(covid_quarters)].copy()
df_covid  = df[df.index.isin(covid_quarters)].copy()
print(f"After removing COVID quarters (Q2 2020–Q1 2021): {len(df_clean)} quarters remaining\n")


# ===============================================================
# 1. SCATTER: Unemployment vs Real GDP (level view)
# ===============================================================
fig1, ax1 = plt.subplots(figsize=(10, 7))

x_line = np.linspace(df_clean["gdp"].min() / 1000, df_clean["gdp"].max() / 1000, 200)
slope_lv, intercept_lv = np.polyfit(df_clean["gdp"] / 1000, df_clean["unrate"], 1)
ax1.plot(x_line, intercept_lv + slope_lv * x_line, color="steelblue",
         linewidth=1.5, linestyle="--", zorder=2, label="Trend (clean data)")

ax1.scatter(df_clean["gdp"] / 1000, df_clean["unrate"],
            color="steelblue", alpha=0.65, s=40, zorder=3,
            label=f"Normal quarters (n={len(df_clean)})")
ax1.scatter(df_covid["gdp"] / 1000, df_covid["unrate"],
            color="crimson", alpha=0.75, s=45, zorder=4, marker="D",
            label=f"COVID quarters — excluded (n={len(df_covid)})")

ax1.set_xlabel("Real GDP (Trillions of 2017 $)", fontsize=12)
ax1.set_ylabel("Unemployment Rate (%)", fontsize=12)
ax1.set_title("Unemployment vs Real GDP\n(red = COVID quarters Q2 2020–Q1 2021, excluded from analysis)",
              fontsize=13, fontweight="bold")
ax1.legend(fontsize=10)
ax1.grid(True, linestyle="--", alpha=0.4)
plt.tight_layout()
plt.savefig("gdp_unemployment_analysis.png", dpi=150, bbox_inches="tight")
print("Chart 1 saved: gdp_unemployment_analysis.png")


# ===============================================================
# 2. GAP DIVERGENCE: timeline + scatter relationship (2010–present)
# ===============================================================
# Use clean data (COVID quarters excluded) from 2010 onward.
# Insert NaN rows at the COVID dates so matplotlib breaks the line
# instead of drawing a misleading straight connection across the gap.
df_post2010 = df_clean[df_clean.index >= "2010-01-01"].copy()

nan_rows = pd.DataFrame(
    {"y_gap": np.nan, "u_gap": np.nan},
    index=pd.date_range("2020-04-01", "2021-01-01", freq="QS")
)
df_post2010 = pd.concat([df_post2010, nan_rows]).sort_index()

# Era labels for the scatter panel (NaN rows get a label too — filtered out in scatter)
df_post2010["era"] = "2010–2022"
df_post2010.loc[df_post2010.index >= "2022-10-01", "era"] = "Q4 2022–Present"

era_colors = {"2010–2022": "steelblue", "Q4 2022–Present": "darkorange"}

fig2, (ax_time, ax_scat) = plt.subplots(
    2, 1, figsize=(13, 12),
    gridspec_kw={"height_ratios": [1.2, 1]}
)

# ── Top panel: time series ──────────────────────────────────────
ax_time.plot(df_post2010.index, df_post2010["y_gap"],
             color="steelblue", linewidth=2,
             label="Output Gap $Y_{gap}$ (% of potential GDP)")
ax_time.plot(df_post2010.index, df_post2010["u_gap"],
             color="firebrick", linewidth=2,
             label="Unemployment Gap $U_{gap}$ (pp above natural rate)")
ax_time.axhline(0, color="black", linewidth=0.8, linestyle="--")

# Mark COVID exclusion zone
ax_time.axvspan(pd.Timestamp("2020-04-01"), pd.Timestamp("2021-04-01"),
                alpha=0.15, color="crimson", label="COVID quarters excluded")
ax_time.text(pd.Timestamp("2020-07-01"), ax_time.get_ylim()[0] if False else -4.5,
             "COVID\nexcluded", color="crimson", fontsize=8,
             ha="center", va="bottom")

# Shade the post-ChatGPT era
ax_time.axvspan(pd.Timestamp("2022-10-01"), df_post2010.index[-1],
                alpha=0.08, color="gold", label="Post-ChatGPT era (Q4 2022+)")

ax_time.set_ylabel("Gap (percentage points)", fontsize=12)
ax_time.set_title("Output Gap vs Unemployment Gap — 2010 to Present\n"
                  "COVID quarters (Q2 2020–Q1 2021) excluded from analysis",
                  fontsize=13, fontweight="bold")
ax_time.legend(fontsize=10, loc="upper left")
ax_time.grid(True, linestyle="--", alpha=0.4)

# ── Bottom panel: scatter relationship ─────────────────────────
for era, color in era_colors.items():
    sub = df_post2010[df_post2010["era"] == era]
    ax_scat.scatter(sub["y_gap"], sub["u_gap"],
                    color=color, alpha=0.75, s=55, zorder=3, label=era)

# Regression line for each era
for era, color in era_colors.items():
    sub = df_post2010[df_post2010["era"] == era].dropna(subset=["y_gap", "u_gap"])
    if len(sub) < 4:
        continue
    m, b = np.polyfit(sub["y_gap"], sub["u_gap"], 1)
    x_r = np.linspace(sub["y_gap"].min(), sub["y_gap"].max(), 100)
    ax_scat.plot(x_r, m * x_r + b, color=color, linewidth=1.5,
                 linestyle="--", alpha=0.9)

ax_scat.axhline(0, color="black", linewidth=0.8, linestyle="--")
ax_scat.axvline(0, color="black", linewidth=0.8, linestyle="--")
ax_scat.set_xlabel("Output Gap $Y_{gap}$ (% of potential GDP)", fontsize=12)
ax_scat.set_ylabel("Unemployment Gap $U_{gap}$ (pp above natural rate)", fontsize=12)
ax_scat.set_title("Relationship: $Y_{gap}$ vs $U_{gap}$ — Has the Slope Changed?",
                  fontsize=13, fontweight="bold")
ax_scat.legend(fontsize=10)
ax_scat.grid(True, linestyle="--", alpha=0.4)

plt.tight_layout(pad=2.5)
plt.savefig("gap_divergence.png", dpi=150, bbox_inches="tight")
print("Chart 2 saved: gap_divergence.png")

# Print the 2022+ quarters so the divergence is readable
print("\n=== Gap Variables: Q4 2022 – Present ===")
print(df_clean[df_clean.index >= "2022-10-01"][["y_gap", "u_gap"]].round(3).to_string())

# ===============================================================
# 2b. GAP DIVERGENCE — ABSOLUTE VALUE VERSION
#     Both gaps shown as |gap|. Under Okun's Law they should track
#     together in magnitude. A divergence means one is large while
#     the other has collapsed — the decoupling signature.
# ===============================================================
fig2b, (ax_abs, ax_scat2) = plt.subplots(
    2, 1, figsize=(13, 12),
    gridspec_kw={"height_ratios": [1.2, 1]}
)

# ── Top panel: |y_gap| and |u_gap| over time ───────────────────
ax_abs.plot(df_post2010.index, df_post2010["y_gap"].abs(),
            color="steelblue", linewidth=2,
            label="|Output Gap| $|Y_{gap}|$ (% of potential GDP)")
ax_abs.plot(df_post2010.index, df_post2010["u_gap"].abs(),
            color="firebrick", linewidth=2,
            label="|Unemployment Gap| $|U_{gap}|$ (pp from natural rate)")

ax_abs.axvspan(pd.Timestamp("2020-04-01"), pd.Timestamp("2021-04-01"),
               alpha=0.15, color="crimson", label="COVID quarters excluded")
ax_abs.text(pd.Timestamp("2020-07-01"), 0.15,
            "COVID\nexcluded", color="crimson", fontsize=8,
            ha="center", va="bottom")
ax_abs.axvspan(pd.Timestamp("2022-10-01"), df_post2010.index[-1],
               alpha=0.08, color="gold", label="Post-ChatGPT era (Q4 2022+)")

ax_abs.set_ylabel("Absolute Gap (percentage points)", fontsize=12)
ax_abs.set_title("|Output Gap| vs |Unemployment Gap| — 2010 to Present\n"
                 "Divergence = one gap large while the other collapses",
                 fontsize=13, fontweight="bold")
ax_abs.set_ylim(bottom=0)
ax_abs.legend(fontsize=10, loc="upper left")
ax_abs.grid(True, linestyle="--", alpha=0.4)

# ── Bottom panel: scatter of |y_gap| vs |u_gap| by era ─────────
for era, color in era_colors.items():
    sub = df_post2010[df_post2010["era"] == era].dropna(subset=["y_gap", "u_gap"])
    ax_scat2.scatter(sub["y_gap"].abs(), sub["u_gap"].abs(),
                     color=color, alpha=0.75, s=55, zorder=3, label=era)

for era, color in era_colors.items():
    sub = df_post2010[df_post2010["era"] == era].dropna(subset=["y_gap", "u_gap"])
    if len(sub) < 4:
        continue
    m, b = np.polyfit(sub["y_gap"].abs(), sub["u_gap"].abs(), 1)
    x_r = np.linspace(sub["y_gap"].abs().min(), sub["y_gap"].abs().max(), 100)
    ax_scat2.plot(x_r, m * x_r + b, color=color, linewidth=1.5,
                  linestyle="--", alpha=0.9)

ax_scat2.set_xlabel("|Output Gap| $|Y_{gap}|$ (% of potential GDP)", fontsize=12)
ax_scat2.set_ylabel("|Unemployment Gap| $|U_{gap}|$ (pp from natural rate)", fontsize=12)
ax_scat2.set_title("Magnitude Relationship: $|Y_{gap}|$ vs $|U_{gap}|$ — Has It Broken Down?",
                   fontsize=13, fontweight="bold")
ax_scat2.set_xlim(left=0)
ax_scat2.set_ylim(bottom=0)
ax_scat2.legend(fontsize=10)
ax_scat2.grid(True, linestyle="--", alpha=0.4)

plt.tight_layout(pad=2.5)
plt.savefig("gap_divergence_abs.png", dpi=150, bbox_inches="tight")
print("Chart 2b saved: gap_divergence_abs.png")
print()


# ===============================================================
# 2c. OKUN RESIDUAL + QUADRANT SCATTER
#     Chart A: residual from pre-2022 regression over time
#     Chart B: quadrant scatter colored by recency (blue→orange)
# ===============================================================

# Fit the historical Okun relationship on pre-2022 clean data only
pre22 = df_post2010[df_post2010.index < "2022-10-01"].dropna(subset=["y_gap", "u_gap"])
okun_m, okun_b = np.polyfit(pre22["y_gap"], pre22["u_gap"], 1)

# Residual for every quarter: actual U_gap minus what Okun predicts
df_post2010["u_predicted"] = okun_m * df_post2010["y_gap"] + okun_b
df_post2010["okun_resid"]  = df_post2010["u_gap"] - df_post2010["u_predicted"]

fig2c, (ax_resid, ax_quad) = plt.subplots(
    2, 1, figsize=(13, 12),
    gridspec_kw={"height_ratios": [1, 1]}
)

# ── Top panel: residual over time ──────────────────────────────
ax_resid.axhline(0, color="black", linewidth=1.2, linestyle="--", zorder=2)
ax_resid.fill_between(df_post2010.index, df_post2010["okun_resid"], 0,
                      where=df_post2010["okun_resid"] > 0,
                      color="firebrick", alpha=0.4,
                      label="Unemployment higher than Okun predicts (law breaking down)")
ax_resid.fill_between(df_post2010.index, df_post2010["okun_resid"], 0,
                      where=df_post2010["okun_resid"] <= 0,
                      color="steelblue", alpha=0.4,
                      label="Unemployment lower than Okun predicts (law holding)")
ax_resid.plot(df_post2010.index, df_post2010["okun_resid"],
              color="black", linewidth=1.2, zorder=3)

ax_resid.axvspan(pd.Timestamp("2020-04-01"), pd.Timestamp("2021-04-01"),
                 alpha=0.15, color="crimson", label="COVID quarters excluded")
ax_resid.axvspan(pd.Timestamp("2022-10-01"), df_post2010.index[-1],
                 alpha=0.08, color="gold", label="Post-ChatGPT era (Q4 2022+)")

ax_resid.set_ylabel("Okun Residual (pp)\nActual $U_{gap}$ − Predicted $U_{gap}$", fontsize=11)
ax_resid.set_title("Okun's Law Residual — 2010 to Present\n"
                   f"Pre-2022 fit: $U_{{gap}}$ = {okun_m:.3f} × $Y_{{gap}}$ + {okun_b:.3f}",
                   fontsize=13, fontweight="bold")
ax_resid.legend(fontsize=9, loc="lower left")
ax_resid.grid(True, linestyle="--", alpha=0.4)

# ── Bottom panel: quadrant scatter colored by time ─────────────
# Color gradient: earlier quarters = blue, recent = orange
df_quad = df_post2010.dropna(subset=["y_gap", "u_gap"]).copy()
n = len(df_quad)

sc = ax_quad.scatter(df_quad["y_gap"], df_quad["u_gap"],
                     c=range(n), cmap="RdYlBu_r", s=60, zorder=3, alpha=0.85)

# Quadrant shading
ax_quad.axhline(0, color="black", linewidth=1.0, zorder=2)
ax_quad.axvline(0, color="black", linewidth=1.0, zorder=2)
ax_quad.fill_between([-6, 0], [0, 0], [6, 6], alpha=0.04, color="steelblue")  # Q2: law holds
ax_quad.fill_between([0, 6], [-6, -6], [0, 0], alpha=0.04, color="steelblue")  # Q4: law holds
ax_quad.fill_between([0, 6], [0, 0], [6, 6], alpha=0.06, color="firebrick")    # Q1: law broken
ax_quad.fill_between([-6, 0], [-6, -6], [0, 0], alpha=0.06, color="firebrick") # Q3: law broken

# Quadrant labels
xlim = df_quad["y_gap"].abs().max() * 1.15
ylim = df_quad["u_gap"].abs().max() * 1.25
ax_quad.text( xlim * 0.55,  ylim * 0.75, "Q1: Law Broken\n(economy above potential,\nunemployment rising)",
              fontsize=8, color="firebrick", ha="center", style="italic")
ax_quad.text(-xlim * 0.55,  ylim * 0.75, "Q2: Law Holding\n(economy below potential,\nunemployment elevated)",
              fontsize=8, color="steelblue", ha="center", style="italic")
ax_quad.text( xlim * 0.55, -ylim * 0.75, "Q4: Law Holding\n(economy above potential,\nunemployment low)",
              fontsize=8, color="steelblue", ha="center", style="italic")
ax_quad.text(-xlim * 0.55, -ylim * 0.75, "Q3: Law Broken\n(economy below potential,\nunemployment low)",
              fontsize=8, color="firebrick", ha="center", style="italic")

ax_quad.set_xlim(-xlim, xlim)
ax_quad.set_ylim(-ylim, ylim)

# ── Trajectory arrows: connect consecutive post-2022 dots ──────
post22_pts = df_quad[df_quad.index >= "2022-10-01"]
xs = post22_pts["y_gap"].values
ys = post22_pts["u_gap"].values
for i in range(len(xs) - 1):
    ax_quad.annotate("",
        xy=(xs[i + 1], ys[i + 1]),
        xytext=(xs[i], ys[i]),
        arrowprops=dict(arrowstyle="-|>", color="black", lw=1.2,
                        mutation_scale=10))

# Label first and last post-2022 point
ax_quad.annotate(str(post22_pts.index[0].date())[:7],
                 xy=(xs[0], ys[0]), xytext=(xs[0] + 0.1, ys[0] - 0.25),
                 fontsize=7, color="black")
ax_quad.annotate(str(post22_pts.index[-1].date())[:7],
                 xy=(xs[-1], ys[-1]), xytext=(xs[-1] + 0.1, ys[-1] + 0.1),
                 fontsize=7, color="black")

cbar = plt.colorbar(sc, ax=ax_quad, orientation="vertical", pad=0.02)
cbar.set_label("Time (blue = 2010, orange = present)", fontsize=9)
tick_positions = [0, n // 4, n // 2, 3 * n // 4, n - 1]
tick_labels    = [str(df_quad.index[i].year) for i in tick_positions]
cbar.set_ticks(tick_positions)
cbar.set_ticklabels(tick_labels)

ax_quad.set_xlabel("Output Gap $Y_{gap}$ (% of potential GDP)", fontsize=12)
ax_quad.set_ylabel("Unemployment Gap $U_{gap}$ (pp above natural rate)", fontsize=12)
ax_quad.set_title("Quadrant Map: Where Does Each Quarter Land?\n"
                  "Blue/Q2+Q4 = Okun holds  |  Red/Q1+Q3 = Okun broken  |  Arrows = post-2022 trajectory",
                  fontsize=13, fontweight="bold")
ax_quad.grid(True, linestyle="--", alpha=0.3)

plt.tight_layout(pad=2.5)
plt.savefig("gap_okun_residual_quadrant.png", dpi=150, bbox_inches="tight")
print("Chart 2c saved: gap_okun_residual_quadrant.png")
print()


# ===============================================================
# 2d. CALCULUS-BASED PROJECTION: Okun residual to 2030
#     Fit a polynomial to the residual over time (post-2010).
#     First derivative = rate of decoupling.
#     Project forward with 95% confidence band.
# ===============================================================

# Use quarterly Okun residuals from df_post2010 (no NaNs)
df_proj = df_post2010.dropna(subset=["okun_resid"]).copy()

# Convert dates to numeric (quarters since 2010-Q1) for polynomial fitting
t0 = df_proj.index[0]
df_proj["t"] = [(d - t0).days / 91.25 for d in df_proj.index]

t_vals  = df_proj["t"].values
r_vals  = df_proj["okun_resid"].values

# Fit degree-2 polynomial: residual = a*t² + b*t + c
deg   = 2
coeffs = np.polyfit(t_vals, r_vals, deg)
poly   = np.poly1d(coeffs)
dpoly  = poly.deriv()      # first derivative  (rate of change)
d2poly = poly.deriv(2)     # second derivative (acceleration)

# 95% confidence band from residuals of the fit
fit_vals  = poly(t_vals)
residuals = r_vals - fit_vals
sigma     = residuals.std()
z95       = 1.96

print("=== Polynomial Fit: Okun Residual over Time ===")
print(f"  f(t)  = {coeffs[0]:.5f}·t² + {coeffs[1]:.5f}·t + {coeffs[2]:.5f}")
print(f"  f'(t) = {dpoly.coeffs[0]:.5f}·t + {dpoly.coeffs[1]:.5f}  (rate of decoupling)")
print(f"  f''   = {d2poly.coeffs[0]:.5f}  (acceleration — positive = speeding up)")
print(f"  Fit σ = {sigma:.4f} pp")
print()

# Project to 2030-Q4
last_date  = df_proj.index[-1]
proj_dates = pd.date_range(last_date + pd.DateOffset(months=3), "2030-10-01", freq="QS")
proj_t     = np.array([(d - t0).days / 91.25 for d in proj_dates])

proj_mean  = poly(proj_t)
proj_upper = proj_mean + z95 * sigma
proj_lower = proj_mean - z95 * sigma

# Value at key future dates
for yr in [2026, 2027, 2028, 2029, 2030]:
    target = pd.Timestamp(f"{yr}-01-01")
    t_q    = (target - t0).days / 91.25
    val    = poly(t_q)
    drv    = dpoly(t_q)
    print(f"  {yr}: projected residual = {val:+.2f} pp  |  rate = {drv:+.3f} pp/quarter")
print()

# Current rate of change at last observed point
t_now  = t_vals[-1]
rate_now = dpoly(t_now)
print(f"  Current rate of change: {rate_now:+.4f} pp/quarter  ({rate_now*4:+.3f} pp/year)")
print(f"  Acceleration:           {d2poly.coeffs[0]:+.5f} pp/quarter²")
print()

# ── Plot ────────────────────────────────────────────────────────
fig2d, ax_proj = plt.subplots(figsize=(13, 7))

# Historical residual
ax_proj.plot(df_proj.index, r_vals, color="black", linewidth=1.5,
             zorder=4, label="Observed Okun Residual")

# Fitted curve over historical period
t_hist_fine = np.linspace(t_vals[0], t_vals[-1], 300)
d_hist_fine = [t0 + pd.DateOffset(days=int(t * 91.25)) for t in t_hist_fine]
ax_proj.plot(d_hist_fine, poly(t_hist_fine), color="steelblue", linewidth=2,
             linestyle="--", zorder=3, label=f"Polynomial fit (degree {deg})")

# Projection
ax_proj.plot(proj_dates, proj_mean, color="firebrick", linewidth=2.5,
             linestyle="--", zorder=3, label="Projected residual (to 2030)")
ax_proj.fill_between(proj_dates, proj_lower, proj_upper,
                     color="firebrick", alpha=0.15, label="95% confidence band")

# Derivative annotation: draw tangent line at last data point
t_tan   = np.linspace(t_now - 6, t_now + 8, 100)
d_tan   = [t0 + pd.DateOffset(days=int(t * 91.25)) for t in t_tan]
tan_val = poly(t_now) + dpoly(t_now) * (t_tan - t_now)
ax_proj.plot(d_tan, tan_val, color="darkorange", linewidth=1.5,
             linestyle=":", alpha=0.8,
             label=f"Tangent at last obs. (rate = {rate_now:+.3f} pp/qtr)")

# Zero line and annotations
ax_proj.axhline(0, color="black", linewidth=0.8, linestyle="--")
ax_proj.axvspan(pd.Timestamp("2020-04-01"), pd.Timestamp("2021-04-01"),
                alpha=0.12, color="crimson", label="COVID quarters excluded")
ax_proj.axvspan(pd.Timestamp("2022-10-01"), pd.Timestamp(last_date),
                alpha=0.06, color="gold")
ax_proj.axvspan(pd.Timestamp(last_date), pd.Timestamp("2030-12-01"),
                alpha=0.10, color="gold", label="Post-ChatGPT era / projection")

# Annotate 2030 projected value
val_2030 = poly((pd.Timestamp("2030-01-01") - t0).days / 91.25)
ax_proj.annotate(f"2030 projection:\n{val_2030:+.2f} pp\n(±{z95*sigma:.2f})",
                 xy=(pd.Timestamp("2030-01-01"), val_2030),
                 xytext=(pd.Timestamp("2028-01-01"), val_2030 + 0.4),
                 arrowprops=dict(arrowstyle="->", color="firebrick"),
                 fontsize=9, color="firebrick",
                 bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="firebrick", alpha=0.9))

ax_proj.set_xlabel("Quarter", fontsize=12)
ax_proj.set_ylabel("Okun Residual (pp)\nActual $U_{gap}$ − Predicted $U_{gap}$", fontsize=12)
ax_proj.set_title("Okun's Law Breakdown — Polynomial Projection to 2030\n"
                  "Positive residual = unemployment higher than output gap alone predicts",
                  fontsize=13, fontweight="bold")
ax_proj.legend(fontsize=9, loc="upper left")
ax_proj.grid(True, linestyle="--", alpha=0.4)
ax_proj.set_xlim(pd.Timestamp("2010-01-01"), pd.Timestamp("2031-01-01"))

plt.tight_layout()
plt.savefig("okun_projection_2030.png", dpi=150, bbox_inches="tight")
print("Chart 2d saved: okun_projection_2030.png")
print()


# ===============================================================
# 3. ROLLING REGRESSION: Okun's constant C — 2000 to present
#    Window = 12 quarters (3 years), rolling forward 1 quarter
# ----------------------------------------------------------------
# This is the main finding of the script. Rather than fitting one
# regression across all history, C is re-estimated on every trailing
# 12-quarter window so its stability over time is visible.
#
# C = how much u_gap changes per 1pp change in y_gap.
#   C < 0   -> Okun's Law holds (more output, less unemployment).
#   C ~= 0  -> the relationship has weakened.
#   C > 0   -> the relationship has inverted.
#
# The companion rolling correlation (r) is tested against the pre-2022
# historical distribution below to see whether any post-2022 inversion
# is statistically surprising or just short-window noise.
#
# CAVEAT — WINDOWS SPAN THE COVID GAP: the window slides over the
# COVID-excluded dataset, so a "12-quarter" window ending in 2022–2024
# stitches together quarters from before Q2 2020 and after Q1 2021.
# Those windows cover more than 3 calendar years, and the early
# "post-ChatGPT" windows still contain pre-COVID quarters. The r = +0.81
# peak lands late enough that its window is mostly post-rebound data,
# but window composition should be kept in mind when reading the chart.
# ===============================================================
WINDOW = 12   # quarters

df_2000 = df_clean[df_clean.index >= "2000-01-01"].copy()
clean_idx = df_2000.index.tolist()

roll_dates = []
roll_slope = []
roll_r     = []

for i in range(WINDOW, len(clean_idx) + 1):
    window_df = df_2000.iloc[i - WINDOW : i]
    x_w = window_df["y_gap"].values
    y_w = window_df["u_gap"].values
    if np.std(x_w) < 1e-9:
        continue
    s, _ = np.polyfit(x_w, y_w, 1)
    r     = np.corrcoef(x_w, y_w)[0, 1]
    roll_dates.append(clean_idx[i - 1])
    roll_slope.append(s)
    roll_r.append(r)

roll_df = pd.DataFrame({"slope": roll_slope, "r": roll_r}, index=roll_dates)

# ── Historical baseline: all windows BEFORE Q4 2022 ────────────
pre_ai    = roll_df[roll_df.index < "2022-10-01"]["r"]
post_ai   = roll_df[roll_df.index >= "2022-10-01"]["r"]

hist_pos_rate = (pre_ai > 0).mean()       # fraction of pre-AI windows with r > 0
hist_mean     = pre_ai.mean()
hist_std      = pre_ai.std()

print("=== Historical Baseline (2000–Q3 2022) ===")
print(f"  Windows:              {len(pre_ai)}")
print(f"  Mean r:               {hist_mean:.3f}")
print(f"  Std r:                {hist_std:.3f}")
print(f"  % windows with r > 0: {hist_pos_rate*100:.1f}%")
print()

# Probability of each post-AI r value under the historical normal distribution
from scipy import stats as sp_stats
print("=== Post-ChatGPT Windows — Probability Under Historical Normal ===")
print(f"  {'Quarter':<14}  {'r':>7}  {'p(r ≥ observed)':>16}")
for dt, row in post_ai.items():
    p = 1 - sp_stats.norm.cdf(row, loc=hist_mean, scale=hist_std)
    print(f"  {str(dt.date()):<14}  {row:>7.3f}  {p:>15.4f}")
print()

# ── Plot ────────────────────────────────────────────────────────
fig3, (ax3a, ax3b) = plt.subplots(2, 1, figsize=(13, 9), sharex=True)

ax3a.plot(roll_df.index, roll_df["slope"], color="steelblue", linewidth=2)
ax3a.axhline(0, color="black", linewidth=0.8, linestyle="--")
ax3a.axvspan(pd.Timestamp("2022-10-01"), roll_df.index[-1],
             alpha=0.08, color="gold", label="Post-ChatGPT era (Q4 2022+)")
ax3a.set_ylabel("Rolling Okun's Coefficient C\n(ΔU_gap per 1pp Y_gap)", fontsize=11)
ax3a.set_title("Rolling 3-Year Okun's Coefficient (2000–Present) — Is C Decaying?",
               fontsize=13, fontweight="bold")
ax3a.legend(fontsize=10)
ax3a.grid(True, linestyle="--", alpha=0.4)

ax3b.plot(roll_df.index, roll_df["r"], color="firebrick", linewidth=2)
ax3b.axhline(0, color="black", linewidth=0.8, linestyle="--")
ax3b.axvspan(pd.Timestamp("2022-10-01"), roll_df.index[-1],
             alpha=0.08, color="gold")

# Annotate the peak inversion with its probability
peak_idx = post_ai.idxmax()
peak_r   = post_ai.max()
peak_p   = 1 - sp_stats.norm.cdf(peak_r, loc=hist_mean, scale=hist_std)
ax3b.annotate(f"r = {peak_r:.2f}\np(r ≥ this) = {peak_p:.4f}",
              xy=(peak_idx, peak_r),
              xytext=(peak_idx - pd.DateOffset(months=18), peak_r - 0.25),
              arrowprops=dict(arrowstyle="->", color="black"),
              fontsize=9, color="black",
              bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="gray", alpha=0.9))

ax3b.set_ylabel("Rolling Correlation (r)\n+ = law inverted,  − = law holding", fontsize=11)
ax3b.set_xlabel("Quarter (end of window)", fontsize=12)
ax3b.set_ylim(-1.05, 1.05)
ax3b.grid(True, linestyle="--", alpha=0.4)

plt.tight_layout()
plt.savefig("rolling_okuns_coefficient.png", dpi=150, bbox_inches="tight")
print("Chart 3 saved: rolling_okuns_coefficient.png")

print("\n=== Rolling Okun's Coefficient: Last 12 Windows ===")
print(roll_df.tail(12).round(4).to_string())
print()


plt.show()
print("\nAll charts saved.")
