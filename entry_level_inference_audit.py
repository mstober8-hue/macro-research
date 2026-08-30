"""
entry_level_inference_audit.py
Auditing the project's headline result with inference that does not depend on
cluster count.

WHY
The entry-level triple difference is the only affirmative displacement finding in
this project and the load-bearing claim of any paper built on it. It was reported
at p = 0.011 from a bootstrap clustered on SOC major groups. Two things about
that need checking.

  1. THERE ARE ONLY 21 CLUSTERS, and employment is concentrated: the top three
     SOC major groups carry 39% of covered employment, giving a Herfindahl of
     0.081 and roughly 12 EFFECTIVE clusters. The cluster bootstrap is generally
     considered unreliable below about 30, and this is well below that.

  2. THE TWO REPORTED BOOTSTRAPS DISAGREE. The occupation-level bootstrap gives
     one-sided p = 0.056 with a confidence interval spanning zero, while the
     cluster bootstrap gives 0.011. Clustering normally WIDENS intervals; here it
     shifted the distribution instead, which is a symptom of too few clusters
     rather than a more conservative estimate.

THE FIX
Randomization inference. Permute WHICH occupations are high-exposure, holding all
employment data fixed, and recompute the triple difference. This is exact, makes
no distributional assumption, and is valid no matter how few clusters exist. It is
the standard remedy when cluster counts are small.

THE RESULT
Randomization inference reproduces the point estimate exactly (-13.1pp) and gives
one-sided p = 0.056, two-sided p = 0.111. The effect is 1.59 null standard
deviations from zero. It agrees exactly with the occupation bootstrap, and the
cluster bootstrap is the outlier.

The finding is therefore MARGINAL and does not clear 5%. Its supporting structure
remains intact and is not affected by this: the monotone age gradient, the timing
in the AI window rather than the COVID window, the clean placebo, and the
leave-one-occupation-out stability. What changes is that the headline p-value
should be 0.056, not 0.011, and the claim should be stated as suggestive.

Run after cps_within_occupation_age.py, whose construction it reuses.
"""

import numpy as np
import pandas as pd

src = open("cps_within_occupation_age.py").read()
exec(compile(src[:src.index("QP, QB, QT = qpanel")], "audit", "exec"))

QP, QT = qpanel("placebo"), qpanel("test")


def gap_from(F, rv):
    hi = rv >= np.quantile(rv, 0.8)
    return 100 * (F.a2024_1[hi].sum() / F.a2024_0[hi].sum()
                  - F.a2024_1[~hi].sum() / F.a2024_0[~hi].sum())


actual = gap_from(QT, QT.rep.values) - gap_from(QP, QP.rep.values)

emp = QT.groupby(QT.soc.str[:2])["total_0"].sum()
sh = emp / emp.sum()
hhi = float((sh ** 2).sum())

print("=" * 92)
print("INFERENCE AUDIT OF THE ENTRY-LEVEL TRIPLE DIFFERENCE")
print("=" * 92)
print(f"\n  Point estimate                    : {actual:+.1f}pp")
print(f"  SOC major groups (clusters)       : {emp.size}")
print(f"  Top 3 clusters' employment share  : {100*sh.nlargest(3).sum():.1f}%")
print(f"  Herfindahl / effective clusters   : {hhi:.3f} / {1/hhi:.1f}")
print("  Cluster bootstrap needs roughly 30+; this is well below.")

rng = np.random.default_rng(11)
N = 20000
null = np.empty(N)
for i in range(N):
    null[i] = (gap_from(QT, QT.rep.values[rng.permutation(len(QT))])
               - gap_from(QP, QP.rep.values[rng.permutation(len(QP))]))
p2 = float((np.abs(null) >= abs(actual)).mean())
p1 = float((null <= actual).mean())

print(f"\n  Randomization null: mean {null.mean():+.2f}, sd {null.std():.2f}")
print(f"  Effect size in null sd units      : {actual/null.std():+.2f}")
print(f"  Two-sided p                       : {p2:.4f}")
print(f"  One-sided p                       : {p1:.4f}")

print(f"\n  {'method':<36}{'one-sided p':>13}   validity")
print(f"  {'SOC-major cluster bootstrap':<36}{0.0110:>13.4f}   UNRELIABLE at ~12 effective clusters")
print(f"  {'occupation bootstrap':<36}{0.0563:>13.4f}   ignores within-SOC correlation")
print(f"  {'randomization inference':<36}{p1:>13.4f}   exact, valid at any cluster count")

print("\n  VERDICT: the two methods that do not depend on cluster count agree at")
print("  p = 0.056. The cluster bootstrap is the outlier and is the least reliable")
print("  of the three here. The finding is MARGINAL, not significant at 5%.")
print("\n  UNAFFECTED: the monotone age gradient (-13.1 / -2.8 / -0.0 by age band),")
print("  the timing in the AI window rather than the COVID bridge, the clean 2016-2019")
print("  placebo, and leave-one-occupation-out stability of [-14.2, -11.3]pp. Those are")
print("  design features, not p-values, and they are what makes the result credible")
print("  despite falling short of conventional significance.")
