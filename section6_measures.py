"""
section6_measures.py
Section 6 of PAPER.md: the result depends on which exposure measure you use, and
the disagreement is itself the finding.

THE TWO MEASURES
  TASK-BASED (Eloundou et al. GPT-4 beta). A capability rating: what share of an
  occupation's tasks could a large language model do? Built ex ante from task
  descriptions, so it is not contaminated by what happened to employment.

  REVEALED (Anthropic Economic Index). Where Claude is actually used, from
  conversation transcripts mapped to SOC occupations. Measures deployment rather
  than capability, and carries two problems this section has to confront: it is a
  single 2026 cross-section, dated AFTER the treatment period it would assign, and
  it is a share of conversations rather than a rate per worker.

WHAT IS RUN
  1. WHAT AEI MEASURES  concentration, and whether usage tracks employment at all.
  2. BASELINE           the Section 3 specification under each measure.
  3. HORSE RACE         both measures in the same regression.
  4. AUTOMATION         AEI's own automation-vs-augmentation split.
  5. TIMING             AEI is post-treatment. Does it predict the PRE-2022 path?
                        If it does, it is not clean treatment assignment.

Panel construction and the estimator live in entry_panel.py.
Writes section6_measures.png.
"""
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from entry_panel import load, aei, fe, z, post_x, stars, BANDS, BASE_YEAR, POST

D = load().merge(aei(), on="occ", how="inner")
D = D[D.auto_sh.notna()].copy()
# Per-worker intensity: usage share divided by employment share, logged. The
# employment share uses each occupation's MEAN employment over the panel rather
# than a single base year, so occupations absent in any one year do not become
# NaN and silently break the design matrix.
mean_emp = D.groupby("occ").tot.mean()
D["empsh"] = 100 * D.occ.map(mean_emp / mean_emp.sum())
D["inten"] = np.log((D.use / D.empsh.clip(lower=1e-9)).clip(lower=1e-9))
assert np.isfinite(D[["use", "inten", "auto_use", "auto_sh", "aug_sh", "autonomy"]].values).all(), \
    "non-finite values in a measure; fix before estimating"

print("=" * 98)
print("SECTION 6  THE MEASURES DISAGREE")
print(f"occupations {D.occ.nunique()}, cells {len(D)}, {D.year.min()}-{D.year.max()}")
print("=" * 98)

# ---- 1. what AEI actually measures ---------------------------------------------
print("\n1. WHAT THE REVEALED MEASURE MEASURES")
print("-" * 98)
o = D[D.year == BASE_YEAR].drop_duplicates("occ")
top = o.nlargest(10, "use")
print(f"   top 10 occupations by Claude usage hold {100*top.use.sum()/o.use.sum():.1f}% of all usage")
print(f"   the same 10 occupations hold           {100*top.tot.sum()/o.tot.sum():.1f}% of employment")
print(f"   corr(usage share, occupation employment) = {np.corrcoef(o.use, o.tot)[0,1]:+.3f}")
print(f"   usage share: median {o.use.median():.3f}, mean {o.use.mean():.3f}, max {o.use.max():.2f}")
print("\n   the ten, which are a portrait of one model's user base rather than a map")
print("   of where AI is deployed across the economy:")
_t = (pd.read_csv(__import__("entry_panel").DATA + "occ2010_soc_crosswalk.csv")
        .drop_duplicates("occ").set_index("occ")["title"])
for _, r in top.iterrows():
    print(f"     {r.use:6.2f}% usage  {100*r.tot/o.tot.sum():6.3f}% employment   "
          f"{_t.get(int(r.occ), '?')}")
print("\n   Correlations with the task-based measures:")
for c, lab in [("use", "usage share"), ("inten", "usage per worker (log)"),
               ("auto_sh", "automation share"), ("autonomy", "AI autonomy")]:
    print(f"     {lab:<26} rep_good {np.corrcoef(o.rep_good, o[c])[0,1]:+.3f}"
          f"   en_raw {np.corrcoef(o.en_raw, o[c])[0,1]:+.3f}")

# ---- 2. baseline under each measure --------------------------------------------
print("\n2. THE SECTION 3 SPECIFICATION UNDER EACH MEASURE")
print("-" * 98)
MEASURES = [("rep_good", "task-based, composite"), ("en_raw", "task-based, raw GPT-4 beta"),
            ("use", "revealed, usage share"), ("inten", "revealed, usage per worker"),
            ("auto_use", "revealed, automation-weighted"), ("autonomy", "revealed, AI autonomy")]
R = {}
for ycol, ylab in BANDS:
    print(f"\n   --- {ylab} ---")
    print(f"   {'measure':<34}{'coef':>9}{'se':>9}{'t':>7}{'p':>9}")
    for xc, xl in MEASURES:
        b, se, t, p, G, n = fe(D, ycol, post_x(D, [xc]))
        R[(ycol, xc)] = (b[0], se[0], p[0])
        print(f"   {xl:<34}{b[0]:>+9.4f}{se[0]:>9.4f}{t[0]:>7.2f}{p[0]:>9.4f} {stars(p[0])}")

# ---- 3. horse race -------------------------------------------------------------
print("\n3. HORSE RACE  both measures, same regression")
print("-" * 98)
print(f"\n   {'':<26}{'task-based':>24}{'revealed':>24}")
for ycol, ylab in BANDS:
    for rev in ("use", "inten"):
        b, se, t, p, G, n = fe(D, ycol, post_x(D, ["rep_good", rev]))
        print(f"   {ylab + ' vs ' + rev:<26}{b[0]:>+14.4f} ({p[0]:.3f}){b[1]:>+14.4f} ({p[1]:.3f})")

# ---- 4. automation tilt --------------------------------------------------------
print("\n4. AUTOMATION TILT  AEI's automation-vs-augmentation split")
print("-" * 98)
chk = (D.auto_sh + D.aug_sh)
print(f"   The two shares are exact complements (auto + aug = {chk.min():.2f} to {chk.max():.2f},"
      f" corr = {np.corrcoef(D.auto_sh, D.aug_sh)[0,1]:+.4f}), so only ONE is")
print("   identified. Entering both is degenerate and any split between them is arbitrary.")
print("   The automation share is used alone.")
print("\n   Displacement should load on automation-type usage.")
print(f"\n   {'specification':<40}{'coef':>9}{'se':>9}{'t':>7}{'p':>9}")
for ycol, ylab in BANDS:
    for xs, lab in [(["auto_sh"], "automation share alone"),
                    (["auto_use"], "usage x automation share"),
                    (["rep_good", "auto_sh"], "automation share | task-based")]:
        b, se, t, p, G, n = fe(D, ycol, post_x(D, xs))
        i = len(xs) - 1                      # the automation term is last
        print(f"   {ylab + ', ' + lab:<40}{b[i]:>+9.4f}{se[i]:>9.4f}{t[i]:>7.2f}{p[i]:>9.4f} {stars(p[i])}")

# ---- 5. timing: is the revealed measure clean treatment assignment? -------------
print("\n5. TIMING  AEI is a 2026 cross-section, dated after the treatment period")
print("-" * 98)
print("   A clean treatment assignment should not predict the pre-period. Fake post at")
print("   2018 on 2016-2019 data, each measure in turn.")
PL = D[D.year <= 2019]
print(f"\n   {'measure':<34}{'coef':>9}{'se':>9}{'p':>9}")
for xc, xl in MEASURES:
    b, se, t, p, G, n = fe(PL, "share_2225", post_x(PL, [xc], post_from=2018))
    print(f"   {xl:<34}{b[0]:>+9.4f}{se[0]:>9.4f}{p[0]:>9.4f} {stars(p[0])}")

# ---- chart ---------------------------------------------------------------------
fig, ax = plt.subplots(1, 2, figsize=(14, 5.2))
labs = [m[1] for m in MEASURES]; short = ["task\ncomposite", "task\nraw beta", "AEI\nusage",
                                          "AEI\nper worker", "AEI\nautomation", "AEI\nautonomy"]
cols = ["#1f4e79", "#1f4e79", "#c0392b", "#c0392b", "#c0392b", "#c0392b"]
for k, (ycol, ylab) in enumerate(BANDS):
    v = [R[(ycol, m[0])] for m in MEASURES]
    ax[k].bar(range(len(v)), [x[0] for x in v], yerr=[1.96 * x[1] for x in v],
              color=cols, error_kw=dict(lw=1.2, capsize=3))
    ax[k].axhline(0, color="black", lw=1.1)
    ax[k].set_xticks(range(len(v))); ax[k].set_xticklabels(short, fontsize=8)
    ax[k].set_title(ylab, fontsize=11.5, fontweight="bold")
    ax[k].set_ylabel("pp per sd of measure", fontsize=9.5)
    ax[k].grid(True, axis="y", ls="--", alpha=.35)
fig.suptitle("Section 6: capability predicts the entry-level gap; revealed usage does not",
             fontsize=13, fontweight="bold", y=1.02)
plt.tight_layout(); plt.savefig("section6_measures.png", dpi=150, bbox_inches="tight")
print("\nChart saved: section6_measures.png")
