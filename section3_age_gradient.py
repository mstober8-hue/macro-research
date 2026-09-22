"""
section3_age_gradient.py
Is the effect specific to young workers, or does it hit every age?

WHY THIS MATTERS
Sections 3 and 4 estimate the exposure effect on the 22-25 and 20-24 shares and
find it robustly negative. On its own that is not evidence of an ENTRY-LEVEL
effect. A share is zero-sum across age bands by construction, so a fall in the
young share is mechanically matched by a rise somewhere else; the question is
whether the pattern has the shape an entry-level story predicts.

Brynjolfsson et al.'s fact (2) makes the claim explicitly: "employment of young
workers (ages 22-25) in AI-exposed occupations now stands 19% below where it would
be had it kept pace with that of their less-exposed peers; experienced workers
show no comparable gap." Unlike their fact (5), this one is testable here on this
paper's own outcome, and it is a claim this paper might CONFIRM rather than reject.

WHAT IS RUN
The Section 3 specification, unchanged, on the share of every non-overlapping age
band in turn. If the entry-level reading is right, the coefficient should be
negative and largest for the youngest band, shrink with age, and turn positive for
older bands, because the shares must sum to one.

Panel construction and the estimator live in entry_panel.py.
Writes section3_age_gradient.png.
"""
import numpy as np, pandas as pd
from scipy import stats as sp
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from entry_panel import load, fe, z, post_x, stars, NONOVERLAP

D = load()
# the non-overlapping bands tile 16-64, so their shares sum to 100 by construction
for b in NONOVERLAP:
    D[f"sh_{b}"] = 100 * D[b] / D.tot
D["sh_a22_25"] = 100 * D.a22_25 / D.tot          # overlapping, reported alongside

LADDER = [("sh_u20", "under 20", 18), ("sh_a20_24", "20-24", 22),
          ("sh_a25", "25", 25), ("sh_a26_30", "26-30", 28),
          ("sh_a31_34", "31-34", 32.5), ("sh_a35p", "35 and over", 45)]

print("=" * 92)
print("IS THE EFFECT SPECIFIC TO YOUNG WORKERS?")
print(f"Section 3 specification on every non-overlapping age band, {D.occ.nunique()} occupations")
print("=" * 92)
print("""
  Shares of the non-overlapping bands sum to 100 by construction, so the
  coefficients must sum to approximately zero across the ladder. The question is
  the SHAPE: an entry-level story predicts the largest negative at the bottom,
  shrinking with age, turning positive at the top.
""")
print(f"  {'age band':<16}{'coef':>10}{'se':>9}{'t':>7}{'p':>9}")
RES = []
for col, lab, mid in LADDER:
    b, se, t, p, G, n = fe(D, col, post_x(D, ["rep_good"]))
    RES.append((lab, mid, b[0], se[0], p[0]))
    print(f"  {lab:<16}{b[0]:>+10.4f}{se[0]:>9.4f}{t[0]:>7.2f}{p[0]:>9.4f} {stars(p[0])}")
print(f"  {'':<16}{'-'*10}")
print(f"  {'sum':<16}{sum(r[2] for r in RES):>+10.4f}   (should be ~0)")

b, se, t, p, G, n = fe(D, "sh_a22_25", post_x(D, ["rep_good"]))
print(f"\n  {'22-25 (overlaps)':<16}{b[0]:>+10.4f}{se[0]:>9.4f}{t[0]:>7.2f}{p[0]:>9.4f} {stars(p[0])}")

# ---- is the gradient monotone where the entry-level story needs it to be? ------
print("\n" + "=" * 92)
print("THE SHAPE")
print("=" * 92)
young = [r for r in RES if r[1] <= 25]
old   = [r for r in RES if r[1] >= 26]
print(f"\n  bands 25 and under : {' '.join(f'{r[2]:+.3f}' for r in young)}")
print(f"  bands 26 and over  : {' '.join(f'{r[2]:+.3f}' for r in old)}")
sig_young = sum(1 for r in young if r[4] < .05)
sig_old   = sum(1 for r in old if r[4] < .05)
print(f"\n  significant at 5%: {sig_young} of {len(young)} young bands,"
      f" {sig_old} of {len(old)} older bands")

# weighted regression of coefficient on band midpoint, a compact gradient test
mids = np.array([r[1] for r in RES]); co = np.array([r[2] for r in RES])
w = 1 / np.array([r[3] for r in RES]) ** 2
X = np.column_stack([np.ones(len(mids)), mids])
XtW = X.T * w
bb = np.linalg.pinv(XtW @ X) @ (XtW @ co)
resid = co - X @ bb
s2 = (w * resid ** 2).sum() / max(len(mids) - 2, 1)
V = s2 * np.linalg.pinv(XtW @ X)
tt = bb[1] / np.sqrt(V[1, 1])
print(f"\n  gradient: coefficient rises {bb[1]:+.5f} per year of age"
      f"  (t = {tt:+.2f}, p = {2*(1-sp.norm.cdf(abs(tt))):.4f})")
print("""
  A positive gradient means the exposure effect moves from negative at the bottom
  of the age distribution toward positive at the top, which is the shape an
  entry-level account predicts and a uniform-shrinkage account does not.""")

# ---- chart ---------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(9.5, 5.4))
labs = [r[0] for r in RES]; co = [r[2] for r in RES]; es = [1.96 * r[3] for r in RES]
cols = ["#c0392b" if c < 0 else "#1f4e79" for c in co]
ax.bar(range(len(co)), co, yerr=es, color=cols, error_kw=dict(lw=1.3, capsize=4))
ax.axhline(0, color="black", lw=1.2)
ax.set_xticks(range(len(labs))); ax.set_xticklabels(labs, fontsize=9)
ax.set_ylabel("pp change in band's employment share per sd of exposure", fontsize=9.5)
ax.set_title("The exposure effect by age: negative at entry, positive above 35",
             fontsize=12.5, fontweight="bold")
ax.grid(True, axis="y", ls="--", alpha=.35)
plt.tight_layout(); plt.savefig("section3_age_gradient.png", dpi=150, bbox_inches="tight")
print("\nChart saved: section3_age_gradient.png")
