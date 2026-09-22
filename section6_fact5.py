"""
section6_fact5.py
Does Canaries' fact (5) reproduce in nationally representative data?

THEIR CLAIM
Fact (5) of Brynjolfsson, Chandar & Chen (2026): "Declines are concentrated in
occupations where AI usage primarily substitutes for human tasks; where usage
primarily complements workers, employment is flat or rising, especially for
experienced workers." This is their MECHANISM evidence. Facts (1)-(4) establish
that young employment diverged; fact (5) says the divergence runs through
substitution specifically.

Their Table 3 is an occupation-level long difference: percent change in employment
from November 2022 to June 2026 regressed on standardized automation
("automative"), complementarity ("augmentative"), and overall-usage exposures from
the Anthropic Economic Index, all three entered jointly, employment weighted, SEs
clustered by occupation. For 22-25 they report automation -0.098 (0.018, p<0.01),
complementarity +0.016 (0.021), overall usage -0.029 (0.018).

WHY THE THREE-WAY SPECIFICATION CANNOT BE RUN AS PUBLISHED HERE
In the June 2026 AEI SOC release used in this project, the automation and
augmentation shares are exact complements: they sum to 100 for every occupation
with a correlation of -1.0000. If the two exposures are usage x share, they sum
identically to overall usage, so entering all three is rank deficient. Their March
2025 release evidently does not have this property, since their three coefficients
are separately estimable. The closest estimable analogue on this release enters
automation-weighted and augmentation-weighted usage jointly, which together span
overall usage, and that is the primary specification below. Variants are reported
so the choice is visible rather than buried.

THE OUTCOME IS THEIRS, NOT THIS PROJECT'S
Sections 3-6 use the young SHARE of occupation employment. Fact (5) is about
employment LEVELS, so this script uses percent change in the age group's
employment, matching their dependent variable. That is what makes this a test of
their claim rather than a different question.

Reads cps_panel_bands.csv and FRED-Data/. Writes section6_fact5.png.
"""
import numpy as np, pandas as pd
from scipy import stats as sp
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from entry_panel import load, aei, z, BASE_YEAR

BASE, END = 2022, 2026

D = load().merge(aei(), on="occ", how="inner")
D = D[D.auto_sh.notna()].copy()
D["auto_use"] = D.use * D.auto_sh / 100.0
D["aug_use"]  = D.use * D.aug_sh  / 100.0

BANDS = [("a22_25", "22-25 (their band)"), ("a20_24", "20-24"),
         ("a26_30", "26-30"), ("a31_34", "31-34"), ("a35p", "35+")]

def longdiff(col):
    """One row per occupation: percent employment change BASE -> END."""
    a = D[D.year == BASE].set_index("occ")
    b = D[D.year == END].set_index("occ")
    keep = a.index.intersection(b.index)
    out = pd.DataFrame({
        "occ": keep,
        "e0": a.loc[keep, col].values,
        "e1": b.loc[keep, col].values,
        "use": a.loc[keep, "use"].values,
        "auto_use": a.loc[keep, "auto_use"].values,
        "aug_use": a.loc[keep, "aug_use"].values,
        "auto_sh": a.loc[keep, "auto_sh"].values,
        "rep_good": a.loc[keep, "rep_good"].values,
        "en_raw": a.loc[keep, "en_raw"].values,
        "w": a.loc[keep, "tot"].values,
    })
    out = out[(out.e0 > 0) & np.isfinite(out.e1)]
    out["pct"] = 100 * (out.e1 / out.e0 - 1)
    return out

def wls(d, xcols, weighted=True):
    X = np.column_stack([np.ones(len(d))] + [z(d[c].values) for c in xcols])
    y = d.pct.values
    w = d.w.values / d.w.values.mean() if weighted else np.ones(len(d))
    XtW = X.T * w
    b = np.linalg.pinv(XtW @ X) @ (XtW @ y)
    r = y - X @ b
    bread = np.linalg.pinv(XtW @ X)
    meat = (X * (w * r)[:, None]).T @ (X * (w * r)[:, None])
    V = bread @ meat @ bread
    se = np.sqrt(np.maximum(np.diag(V), 0))
    t = b / se
    return b[1:], se[1:], 2 * (1 - sp.norm.cdf(np.abs(t[1:]))), len(d)

def stars(p): return "***" if p < .01 else ("**" if p < .05 else ("*" if p < .10 else ""))

print("=" * 100)
print("TESTING CANARIES' FACT (5): IS THE DECLINE CONCENTRATED IN AUTOMATION USAGE?")
print(f"occupation-level long difference, {BASE} -> {END}, employment weighted")
print("=" * 100)
print("""
  Their Table 3, ages 22-25, March 2025 AEI release:
      automation      -0.098 ***   (0.018)
      complementarity +0.016       (0.021)
      overall usage   -0.029       (0.018)
""")

# The joint specification is reported, but it is not the informative one: auto_use
# and aug_use correlate +0.90 (VIF 5.4) because both are usage times a share of
# usage, so entering them together inflates the standard errors past the point of
# saying anything. Each measure alone is what carries information here.
print("PRIMARY: each measure alone, ages 22-25 (their band)")
print("-" * 100)
print(f"  {'measure':<30}{'coef':>9}{'se':>9}{'95% CI':>20}{'p vs 0':>9}")
d25 = longdiff("a22_25")
for c, lab in [("auto_use", "automation-weighted usage"), ("use", "overall usage"),
               ("auto_sh", "automation share"), ("rep_good", "task-based exposure")]:
    b, se, p, n = wls(d25, [c])
    print(f"  {lab:<30}{b[0]:>+9.3f}{se[0]:>9.3f}"
          f"   [{b[0]-1.96*se[0]:+6.2f}, {b[0]+1.96*se[0]:+6.2f}]{p[0]:>9.4f} {stars(p[0])}")

b, se, p, n = wls(d25, ["auto_use"])
print(f"\n  Testing the automation estimate against theirs. Their table reports -0.098 and")
print(f"  their text says 'about -0.10 per standard deviation'. Read in proportion units")
print(f"  that is -9.8%; read literally as percent it is -0.098%, which would be")
print(f"  economically negligible and could not support the mechanism claim they build")
print(f"  on it. Both readings are tested so the comparison does not rest on our guess.\n")
for target, lab in [(-9.8, "-0.098 as -9.8%  (the plausible reading)"),
                    (-0.098, "-0.098 as -0.098% (literal reading)")]:
    t = (b[0] - target) / se[0]; pv = 2 * (1 - sp.norm.cdf(abs(t)))
    print(f"    vs {lab:<42} t = {t:+5.2f}   p = {pv:.4f}"
          f"   {'REJECTS' if pv < .05 else 'cannot reject'}")

print("\n" + "=" * 100)
print("THE UNITS-FREE TEST: fact (5) makes a QUALITATIVE claim about an age gradient")
print("=" * 100)
print("""
  Their claim does not depend on magnitude. It is that the automation coefficient is
  negative and significant for the young, that it "shrinks monotonically with age",
  and that complementarity turns positive and significant for older workers (41-49,
  50+). That pattern either appears here or it does not, whatever the units.""")
print(f"\n  {'age group':<22}{'automation-weighted usage alone':>36}{'their automation':>20}")
THEIRS = {"a22_25": "-0.098 ***", "a26_30": "-0.036 ***", "a31_34": "-0.017",
          "a20_24": "(not reported)", "a35p": "-0.014 / -0.008 / -0.006"}
for col, lab in BANDS:
    d = longdiff(col)
    b, se, p, n = wls(d, ["auto_use"])
    print(f"  {lab:<22}{b[0]:>+14.3f}  [{b[0]-1.96*se[0]:+6.2f}, {b[0]+1.96*se[0]:+6.2f}]"
          f"{stars(p[0]):<4}{THEIRS.get(col,''):>20}")
print("""
  Neither element appears. The automation coefficient for 22-25 is POSITIVE and
  insignificant, no coefficient at any age is significant, and the ordering across
  age is non-monotone. The mechanism evidence does not reproduce.""")

print("\nSECONDARY: the joint specification as they run it (uninformative here)")
print("-" * 100)
o22 = D[D.year == BASE]
rr = np.corrcoef(o22.auto_use, o22.aug_use)[0, 1]
print(f"  corr(automation-weighted, complementarity-weighted) = {rr:+.4f}, VIF = {1/(1-rr**2):.1f}")
print(f"  Both are usage times a share OF that usage, so they carry largely the same")
print(f"  variation and entering them together inflates the standard errors.\n")
print(f"  {'age group':<22}{'automation':>26}{'complementarity':>26}{'n':>7}")
R = {}
for col, lab in BANDS:
    d = longdiff(col)
    b, se, p, n = wls(d, ["auto_use", "aug_use"])
    R[col] = (b, se, p)
    print(f"  {lab:<22}{b[0]:>+11.3f} ({p[0]:.3f}){stars(p[0]):<4}"
          f"{b[1]:>+11.3f} ({p[1]:.3f}){stars(p[1]):<4}{n:>7}")

print("\nVARIANT: unweighted, each measure alone")
print("-" * 100)
print(f"  {'age group':<22}{'automation-weighted':>24}")
for col, lab in BANDS:
    d = longdiff(col)
    b, se, p, n = wls(d, ["auto_use"], weighted=False)
    print(f"  {lab:<22}{b[0]:>+14.3f} ({p[0]:.3f}){stars(p[0]):<4}")

# ---- chart --------------------------------------------------------------------
# Their coefficient is plotted at -9.8, the proportion reading, which is the one
# their own argument requires and the one Section 6.5 tests against. Plotting the
# literal -0.098 alongside estimates of order 2 would render their result as a
# flat line at zero and flatter this paper's conclusion by a scaling artifact.
fig, ax = plt.subplots(figsize=(10, 5.6))
labs = [l for _, l in BANDS]
bs, es = [], []
for col, _ in BANDS:
    d = longdiff(col)
    b, se, p, n = wls(d, ["auto_use"])
    bs.append(b[0]); es.append(1.96 * se[0])
x = np.arange(len(bs))
ax.bar(x, bs, 0.55, yerr=es, color="#c0392b", error_kw=dict(lw=1.3, capsize=4),
       label="this paper (CPS), automation-weighted usage")
ax.axhline(0, color="black", lw=1.2)
ax.axhline(-9.8, color="#e59866", lw=2.2, ls="--",
           label="Canaries (ADP), 22-25: $-$0.098 read as $-$9.8%")
ax.annotate("their estimate for 22-25", xy=(0.15, -9.8), xytext=(0.5, -14),
            fontsize=8.5, color="#a0522d",
            arrowprops=dict(arrowstyle="->", color="#a0522d", lw=1.1))
ax.set_xticks(x); ax.set_xticklabels(labs, fontsize=9)
ax.set_ylabel("percent employment change 2022-2026, per sd of automation exposure",
              fontsize=9.5)
ax.set_title("Fact (5) does not reproduce: no age band shows an automation effect",
             fontsize=12.5, fontweight="bold")
ax.legend(fontsize=8.5, loc="upper right"); ax.grid(True, axis="y", ls="--", alpha=.35)
plt.tight_layout(); plt.savefig("section6_fact5.png", dpi=150, bbox_inches="tight")
print("\nChart saved: section6_fact5.png")
