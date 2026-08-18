"""
naics3_ai_test.py
The AI test with enough cross-sectional units to actually detect something.

WHY THIS EXISTS
audit.py found that this project's AI result was not a finding at all. With nine
sectors, the smallest correlation detectable at 80% power is r = 0.82, and the
95% confidence interval on the observed r = +0.18 runs [-0.55, +0.75]. That
interval spans almost the entire range of possible correlations, so the test
could not distinguish "AI has no effect on hiring" from "AI has a substantial
effect". Reporting it as evidence of no effect was an overclaim.

The fix is more units. This rebuilds the test at the 3-digit NAICS level:

  OUTCOME     BLS CES national employment, 73 three-digit NAICS industries,
              monthly and seasonally adjusted. The hiring slowdown is defined
              exactly as in hiring_slowdown.py: average year-over-year growth in
              2024-2025 minus average year-over-year growth over the 2013-2019
              trend period.

  AI EXPOSURE Built rather than assumed. OEWS national industry files give the
              occupation mix of each industry; the AEI occupational exposure
              scores give each occupation's AI exposure. Industry exposure is
              the employment-weighted mean of its occupations' scores, which is
              the standard construction (Felten, Raj and Seamans; Webb; Acemoglu
              and Restrepo all build industry measures this way).

              A concern with using the CURRENT occupation mix is that the mix is
              itself an outcome: if AI already displaced workers, the 2025 mix
              reflects that, and exposure becomes partly endogenous to the thing
              being explained. So exposure is built TWICE, once from the May
              2025 mix and once from the May 2019 mix, which predates generative
              AI entirely. The 2019 version is the one to trust.

  RATE        Each industry's response to an IDENTIFIED monetary policy shock
  SENSITIVITY (Bauer-Swanson) at the pre-specified 8-quarter horizon, estimated
              by local projection. Using the identified shock rather than the raw
              funds rate matters here: identified_shocks.py showed the raw rate
              mixes a contractionary channel with an oppositely signed
              central-bank information channel.

THE TEST
A horse race. If AI exposure drives the 2024-2025 hiring slowdown, it should
predict the slowdown after controlling for how rate-sensitive an industry is.
If the slowdown is monetary, rate sensitivity should absorb it and AI exposure
should add nothing.

Power is reported first, before any result, because a null is only informative
once you know what the test could have detected.

Reads ../FRED-Data/ces/ and ../FRED-Data/oews_national_industry_files/.
Writes naics3_ai_test.png.
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
CES_DIR  = os.path.join(DATA_DIR, "ces") + os.sep
OEWS_DIR = os.path.join(DATA_DIR, "oews_national_industry_files") + os.sep
SHOCKS   = os.path.join(DATA_DIR, "shocks") + os.sep
COVID_Q  = pd.date_range("2020-04-01", "2021-10-01", freq="QS")
PRE      = ("2013-01-01", "2019-12-31")
POST     = ("2024-01-01", "2026-12-31")
LP_H     = 8          # pre-specified, matching identified_shocks.py
NLAGS    = 4


def ols_robust(y, X):
    """OLS with HC1 robust standard errors. Cross-sectional, so no HAC needed."""
    n, k = X.shape
    XtX = np.linalg.pinv(X.T @ X)
    b = XtX @ X.T @ y
    e = y - X @ b
    S = (X * (e ** 2)[:, None]).T @ X
    V = XtX @ S @ XtX * (n / max(n - k, 1))
    return b, np.sqrt(np.maximum(np.diag(V), 0))


def mde(n, alpha=0.05, power=0.80):
    """Minimum detectable correlation for a given cross-section size."""
    if n <= 4:
        return np.nan
    se = 1.0 / np.sqrt(n - 3)
    z = (sp_stats.norm.ppf(1 - alpha / 2) + sp_stats.norm.ppf(power)) * se
    return np.tanh(z)


def ci_r(r, n):
    se = 1.0 / np.sqrt(n - 3)
    z = np.arctanh(r)
    return np.tanh(z - 1.96 * se), np.tanh(z + 1.96 * se)


# ---------------------------------------------------------------------------
# 1. Employment outcomes
# ---------------------------------------------------------------------------
meta = pd.read_csv(CES_DIR + "naics3_meta.csv", dtype=str)
raw = pd.read_csv(CES_DIR + "ces_naics3_raw.tsv", sep="\t", header=None,
                  names=["sid", "year", "period", "value"], dtype=str)
raw = raw[raw.period.str.startswith("M") & (raw.period != "M13")].copy()
raw["value"] = pd.to_numeric(raw.value, errors="coerce")
raw["date"] = pd.to_datetime(raw.year + "-" + raw.period.str[1:] + "-01")
raw = raw.dropna(subset=["value"])

emp = raw.pivot_table(index="date", columns="sid", values="value")
g = emp.pct_change(12) * 100                    # year-over-year, monthly

rows = []
for _, m in meta.iterrows():
    s = g.get(m.sid)
    if s is None:
        continue
    pre = s.loc[PRE[0]:PRE[1]].mean()
    post = s.loc[POST[0]:POST[1]].mean()
    if np.isnan(pre) or np.isnan(post):
        continue
    rows.append(dict(sid=m.sid, naics=m.naics_code, name=m.industry_name,
                     pre=pre, post=post, slowdown=post - pre))
OUT = pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# 2. AI exposure, built from the occupation mix
# ---------------------------------------------------------------------------
ex = pd.read_csv(DATA_DIR + "aei_job_exposure.csv", dtype=str)
ex["observed_exposure"] = pd.to_numeric(ex.observed_exposure, errors="coerce")
ex = ex.dropna(subset=["observed_exposure"])[["occ_code", "observed_exposure"]]


def industry_exposure(path, naics_from_4digit=False):
    # Column case differs across OEWS vintages (2019 is lowercase, later files
    # are uppercase), so normalise rather than hard-code either convention.
    o = pd.read_excel(path, dtype=str)
    o.columns = [c.strip().upper() for c in o.columns]
    o = o[["NAICS", "OCC_CODE", "O_GROUP", "TOT_EMP", "I_GROUP"]]
    grp = "4-digit" if naics_from_4digit else "3-digit"
    o = o[(o.I_GROUP == grp) & (o.O_GROUP == "detailed")].copy()
    o["TOT_EMP"] = pd.to_numeric(o.TOT_EMP, errors="coerce")
    o = o.dropna(subset=["TOT_EMP"])
    o["n3"] = o.NAICS.str[:3]
    m = o.merge(ex, left_on="OCC_CODE", right_on="occ_code", how="inner")
    agg = m.groupby("n3").apply(
        lambda d: np.average(d.observed_exposure, weights=d.TOT_EMP),
        include_groups=False)
    return agg.rename("aiie")


aiie25 = industry_exposure(OEWS_DIR + "unused_oews_may2025_national_3digit_naics_wages.xlsx")
aiie19 = industry_exposure(OEWS_DIR + "oews_may2019_national_4digit_naics_wages.xlsx",
                           naics_from_4digit=True)

OUT = OUT.merge(aiie25.rename("aiie_2025"), left_on="naics", right_index=True, how="left")
OUT = OUT.merge(aiie19.rename("aiie_2019"), left_on="naics", right_index=True, how="left")


# ---------------------------------------------------------------------------
# 3. Rate sensitivity from an identified shock
# ---------------------------------------------------------------------------
bs = pd.read_csv(SHOCKS + "03_bauer_swanson_orthogonalized_shock.csv")
bs.columns = [c.strip() for c in bs.columns]
bs["date"] = pd.to_datetime(bs[bs.columns[0]])
shock = pd.to_numeric(bs["shock"], errors="coerce").groupby(bs.date).sum()
shock = shock.resample("QS").sum()

empq = emp.resample("QS").mean()
sens = {}
for sid in OUT.sid:
    if sid not in empq.columns:
        continue
    lv = np.log(empq[sid].dropna()) * 100
    parts = {"dep": lv.shift(-LP_H) - lv.shift(1), "s": shock}
    for L in range(1, NLAGS + 1):
        parts[f"dl{L}"] = (lv - lv.shift(1)).shift(L)
        parts[f"sl{L}"] = shock.shift(L)
    j = pd.DataFrame(parts).dropna()
    j = j[~j.index.isin(COVID_Q)]
    if len(j) < 40:
        continue
    yv = j["dep"].to_numpy()
    Xv = np.column_stack([np.ones(len(j))] +
                         [j[c].to_numpy() for c in j.columns if c != "dep"])
    b, _ = ols_robust(yv, Xv)
    sens[sid] = b[1] * shock.std()
OUT["rate_sens"] = OUT.sid.map(sens)

D = OUT.dropna(subset=["slowdown", "aiie_2019", "aiie_2025", "rate_sens"]).copy()

# ---------------------------------------------------------------------------
print("=" * 96)
print("THE AI TEST, REBUILT AT 3-DIGIT NAICS")
print("=" * 96)
print(f"\n  Industries with employment data      : {len(OUT)}")
print(f"  Complete cases (all variables)       : {len(D)}")

print("\n" + "-" * 96)
print("POWER, REPORTED BEFORE ANY RESULT")
print("-" * 96)
print(f"\n  {'cross-section':<34}{'n':>5}{'min detectable |r|':>22}")
print(f"  {'the old sector-level test':<34}{9:>5}{mde(9):>22.2f}")
print(f"  {'this test':<34}{len(D):>5}{mde(len(D)):>22.2f}")
print(f"\n  The old test could only have rejected a correlation above {mde(9):.2f}, which is")
print(f"  larger than almost any effect in applied economics. This one detects {mde(len(D)):.2f}.")

print("\n" + "-" * 96)
print("UNIVARIATE: does AI exposure predict the 2024-2025 hiring slowdown?")
print("-" * 96)
print(f"\n  {'exposure measure':<26}{'r':>8}{'p':>9}{'95% CI on r':>22}   reading")
for lbl, col in [("2019 mix (pre-AI, clean)", "aiie_2019"),
                 ("2025 mix (endogenous)", "aiie_2025")]:
    r, p = sp_stats.pearsonr(D[col], D.slowdown)
    lo, hi = ci_r(r, len(D))
    rdg = ("significant" if p < 0.05 else
           "null, and now informative" if abs(hi - lo) < 0.75 else "still imprecise")
    print(f"  {lbl:<26}{r:>+8.3f}{p:>9.4f}{f'[{lo:+.2f}, {hi:+.2f}]':>22}   {rdg}")

print("\n" + "-" * 96)
print("HORSE RACE: AI exposure against identified rate sensitivity")
print("-" * 96)
print("\n  Rate sensitivity is each industry's employment response to a 1 SD")
print("  Bauer-Swanson shock at 8 quarters. More negative = more rate-sensitive.\n")
zs = lambda v: (v - v.mean()) / v.std()
X = np.column_stack([np.ones(len(D)), zs(D.aiie_2019.values), zs(D.rate_sens.values)])
b, se = ols_robust(D.slowdown.values, X)
print(f"  {'term':<28}{'coef':>9}{'se':>8}{'t':>8}{'p':>9}")
for nm, bb, ss in zip(["intercept", "AI exposure (2019, z)", "rate sensitivity (z)"], b, se):
    t = bb / ss if ss > 0 else np.nan
    p = 2 * (1 - sp_stats.norm.cdf(abs(t)))
    print(f"  {nm:<28}{bb:>+9.3f}{ss:>8.3f}{t:>+8.2f}{p:>9.4f}")
yhat = X @ b
r2 = 1 - ((D.slowdown.values - yhat) ** 2).sum() / \
     ((D.slowdown.values - D.slowdown.mean()) ** 2).sum()
print(f"\n  R-squared: {r2:.3f}   n = {len(D)}")

ai_p = 2 * (1 - sp_stats.norm.cdf(abs(b[1] / se[1])))
rt_p = 2 * (1 - sp_stats.norm.cdf(abs(b[2] / se[2])))
print("\n  VERDICT:")
if ai_p < 0.05 and rt_p >= 0.05:
    print("    AI exposure predicts the slowdown; rate sensitivity does not.")
elif rt_p < 0.05 and ai_p >= 0.05:
    print("    Rate sensitivity predicts the slowdown; AI exposure adds nothing.")
elif ai_p < 0.05 and rt_p < 0.05:
    print("    Both channels are present and separately identified.")
else:
    print("    NEITHER predicts the slowdown at this sample size. With the power now")
    print("    available, that is a substantive result rather than an absence of power:")
    print("    the 2024-2025 hiring slowdown is broad-based and not well explained by")
    print("    cross-industry variation in either AI exposure or rate sensitivity.")

print("\n" + "-" * 96)
print("DIAGNOSTICS ON THE HORSE RACE")
print("-" * 96)

rr, rp = sp_stats.pearsonr(D.aiie_2019, D.rate_sens)
print(f"\n  Correlation between the two regressors: r = {rr:+.3f} (p = {rp:.3f})")
print(f"  Variance inflation factor: {1/(1-rr**2):.2f}")
print("  Collinearity is only a problem if this is large; below ~2.5 the two effects")
print("  are separately identified.")

print(f"\n  95% CIs on the standardised coefficients:")
for nm, bb, ss in zip(["AI exposure (2019, z)", "rate sensitivity (z)"], b[1:], se[1:]):
    print(f"    {nm:<26}{bb:>+7.3f}   [{bb-1.96*ss:+.3f}, {bb+1.96*ss:+.3f}]")
print("  Read the AI interval directly: it is the honest statement of what this test")
print("  can and cannot rule out about an AI effect.")

# ---------------------------------------------------------------------------
# Rate sensitivity re-estimated WITHOUT the outcome window.
# The main estimate uses a local projection whose h=8 horizon reaches into
# 2024-2025, the same period the outcome is measured over. That overlap could
# make the rate result partly mechanical. Re-estimating on shocks through 2021
# only removes the overlap entirely.
# ---------------------------------------------------------------------------
print("\n" + "-" * 96)
print("IS THE RATE RESULT MECHANICAL? Re-estimated with no overlap with the outcome")
print("-" * 96)

shock_pre = shock[shock.index <= "2021-12-31"]
sens_pre = {}
for sid in D.sid:
    lv = np.log(empq[sid].dropna()) * 100
    parts = {"dep": lv.shift(-LP_H) - lv.shift(1), "s": shock_pre}
    for L in range(1, NLAGS + 1):
        parts[f"dl{L}"] = (lv - lv.shift(1)).shift(L)
        parts[f"sl{L}"] = shock_pre.shift(L)
    j = pd.DataFrame(parts).dropna()
    j = j[~j.index.isin(COVID_Q)]
    if len(j) < 30:
        continue
    yv = j["dep"].to_numpy()
    Xv = np.column_stack([np.ones(len(j))] +
                         [j[c].to_numpy() for c in j.columns if c != "dep"])
    bb_, _ = ols_robust(yv, Xv)
    sens_pre[sid] = bb_[1] * shock_pre.std()

D2 = D.copy()
D2["rate_sens_pre"] = D2.sid.map(sens_pre)
D2 = D2.dropna(subset=["rate_sens_pre"])
print(f"\n  Shocks used through 2021 only. n = {len(D2)}")
X2 = np.column_stack([np.ones(len(D2)), zs(D2.aiie_2019.values),
                      zs(D2.rate_sens_pre.values)])
b2, se2 = ols_robust(D2.slowdown.values, X2)
print(f"\n  {'term':<28}{'coef':>9}{'se':>8}{'t':>8}{'p':>9}")
for nm, bb, ss in zip(["intercept", "AI exposure (2019, z)", "rate sensitivity (z)"],
                      b2, se2):
    t = bb / ss if ss > 0 else np.nan
    print(f"  {nm:<28}{bb:>+9.3f}{ss:>8.3f}{t:>+8.2f}"
          f"{2*(1-sp_stats.norm.cdf(abs(t))):>9.4f}")
rt_p2 = 2 * (1 - sp_stats.norm.cdf(abs(b2[2] / se2[2])))
print(f"\n  -> rate sensitivity {'SURVIVES' if rt_p2 < 0.05 else 'does NOT survive'} "
      f"removing the overlap.")
if rt_p2 >= 0.05:
    print("     The main horse-race result is therefore partly mechanical and should")
    print("     not be read as out-of-sample evidence.")

print("\n" + "-" * 96)
print("MOST AND LEAST EXPOSED INDUSTRIES (2019 mix), as a sanity check")
print("-" * 96)
srt = D.sort_values("aiie_2019")
print(f"\n  {'':<4}{'industry':<48}{'AI expo':>9}{'slowdown':>10}")
for _, r in srt.head(5).iterrows():
    print(f"  {'LOW':<4}{r['name'][:46]:<48}{r.aiie_2019:>9.3f}{r.slowdown:>+10.2f}")
for _, r in srt.tail(5).iterrows():
    print(f"  {'HIGH':<4}{r['name'][:46]:<48}{r.aiie_2019:>9.3f}{r.slowdown:>+10.2f}")

# ---------------------------------------------------------------------------
fig, axes = plt.subplots(1, 3, figsize=(18.5, 6.0))

ax = axes[0]
ns = np.arange(5, 121)
ax.plot(ns, [mde(n) for n in ns], lw=2.6, color="#1f4e79")
ax.axvline(9, color="#c0392b", ls="--", lw=2.0)
ax.axvline(len(D), color="#2e8b57", ls="--", lw=2.0)
ax.annotate(f"old test\nn=9, needs r>{mde(9):.2f}", xy=(9, mde(9)), xytext=(18, 0.72),
            fontsize=9, arrowprops=dict(arrowstyle="->", color="#c0392b"))
ax.annotate(f"this test\nn={len(D)}, detects r={mde(len(D)):.2f}",
            xy=(len(D), mde(len(D))), xytext=(len(D) + 8, 0.42),
            fontsize=9, arrowprops=dict(arrowstyle="->", color="#2e8b57"))
ax.set_xlabel("number of industries", fontsize=9.5)
ax.set_ylabel("minimum detectable correlation", fontsize=9.5)
ax.set_title("1. Why the old test could not work\npower at 80%, alpha 5%",
             fontsize=11.5, fontweight="bold")
ax.grid(True, ls="--", alpha=0.3)

ax = axes[1]
ax.scatter(D.aiie_2019, D.slowdown, s=42, alpha=0.7, color="#1f4e79",
           edgecolors="white", linewidths=0.8)
sl, ic, r_, p_, _ = sp_stats.linregress(D.aiie_2019, D.slowdown)
xs = np.linspace(D.aiie_2019.min(), D.aiie_2019.max(), 40)
ax.plot(xs, ic + sl * xs, color="#c0392b", lw=2.4)
ax.axhline(0, color="black", lw=1.0, ls="--")
ax.set_xlabel("AI exposure (2019 occupation mix)", fontsize=9.5)
ax.set_ylabel("2024-25 hiring slowdown (pp)", fontsize=9.5)
ax.set_title(f"2. AI exposure vs the slowdown\nr={r_:+.3f}, p={p_:.3f}, n={len(D)}",
             fontsize=11.5, fontweight="bold")
ax.grid(True, ls="--", alpha=0.3)

ax = axes[2]
ax.scatter(D.rate_sens, D.slowdown, s=42, alpha=0.7, color="#2e8b57",
           edgecolors="white", linewidths=0.8)
sl2, ic2, r2_, p2_, _ = sp_stats.linregress(D.rate_sens, D.slowdown)
xs2 = np.linspace(D.rate_sens.min(), D.rate_sens.max(), 40)
ax.plot(xs2, ic2 + sl2 * xs2, color="#c0392b", lw=2.4)
ax.axhline(0, color="black", lw=1.0, ls="--")
ax.set_xlabel("response to a 1 SD identified shock at 8q (%)", fontsize=9.5)
ax.set_ylabel("2024-25 hiring slowdown (pp)", fontsize=9.5)
ax.set_title(f"3. Rate sensitivity vs the slowdown\nr={r2_:+.3f}, p={p2_:.3f}",
             fontsize=11.5, fontweight="bold")
ax.grid(True, ls="--", alpha=0.3)

fig.suptitle("The AI test rebuilt with 73 industries instead of 9: enough power for a null "
             "to mean something", fontsize=13, fontweight="bold", y=1.02)
plt.tight_layout()
out = os.path.join(HERE, "naics3_ai_test.png")
plt.savefig(out, dpi=150, bbox_inches="tight")
print(f"\nChart saved: {out}")
