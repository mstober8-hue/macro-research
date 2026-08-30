"""
exposure_measure_audit.py
Does the occupation-panel result survive the exposure measure being fixed?

WHY THIS EXISTS
cps_panel_did.py reported that AI-exposed occupations shrank after 2022 at
p = 0.004, with 458 clusters, no pre-trend, and identification from
within-occupation variation. That was written up as the project's first result to
clear 5% comfortably. It does not survive this audit.

THE MEASURE IS BROKEN
The exposure score is rep = exposure x (1 - complementarity), where the
complementarity term is the unweighted mean of EVERY O*NET work-context element.
Work context contains dozens of unrelated items (public speaking, working
outdoors, physical proximity, exposure to weather), so averaging them produces
noise, and multiplying exposure by one minus that noise produces a score with no
clear interpretation. The resulting distribution:

    skewness 11.0, and 86.8% of occupations below 0.01
    p50 = 0.003, p99 = 0.108, max = 0.639

and the ranking it produces is not credible. The four highest-scoring occupations
are credit authorizers, accountants and auditors, surveying and mapping
technicians, and FARMERS, RANCHERS AND AGRICULTURAL MANAGERS. A measure that puts
farmers fourth on AI exposure is not measuring AI exposure.

WHAT THE AUDIT DOES
Re-runs the identical panel regression with three alternative measures that are
all more defensible than the composite: the composite rank-transformed to remove
the skew, the raw Eloundou GPT exposure with no O*NET term at all, and that raw
score rank-transformed. Then a leverage test that drops the highest-scoring
occupations one at a time.

THE RESULT
The finding reverses. With the raw exposure score, or with either rank transform,
the coefficient turns POSITIVE, meaning more exposed occupations grew. Dropping
just two occupations takes the composite result from p = 0.004 to p = 0.163, and
dropping eight flips it to significantly positive.

The p = 0.004 result is therefore an artifact of a mis-specified score and two
occupations, not evidence that AI-exposed occupations shrank.
"""

import os
import re
import sys
import glob
import numpy as np
import pandas as pd
from scipy import stats as sp_stats

HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, "cps_panel_did.py")).read()
exec(compile(src[:src.index("def fe_did")], "panel", "exec"))

W2 = W.merge(OCC[["occ", "en"]], on="occ", how="left")
D = W2[(W2.year >= 2016) & W2.rep.notna() & W2.en.notna()].copy()
D["tot"] = D[["a20_24", "a25_34", "a35p"]].sum(axis=1)
D = D[D.tot > 0].copy()
D["ltot"] = np.log(D.tot)
D["rep_rank"] = D.rep.rank(pct=True)
D["en_rank"] = D.en.rank(pct=True)


def fe(df, xcol, post=2023):
    d = df.copy()
    d["post"] = (d.year >= post).astype(float)
    z = (d[xcol] - d[xcol].mean()) / d[xcol].std()
    od = pd.get_dummies(d.occ, prefix="o", drop_first=True).astype(float)
    yd = pd.get_dummies(d.year, prefix="y", drop_first=True).astype(float)
    X = np.column_stack([np.ones(len(d)), (z * d.post).to_numpy(),
                         od.to_numpy(), yd.to_numpy()])
    y, w = d.ltot.to_numpy(), d.tot.to_numpy()
    sw = np.sqrt(w / w.mean())
    Xw, yw = X * sw[:, None], y * sw
    b, *_ = np.linalg.lstsq(Xw, yw, rcond=None)
    r = yw - Xw @ b
    XtX = np.linalg.pinv(Xw.T @ Xw)
    meat = np.zeros((X.shape[1],) * 2)
    for _, idx in d.groupby("occ").indices.items():
        s = Xw[idx].T @ r[idx]
        meat += np.outer(s, s)
    G = d.occ.nunique()
    V = XtX @ meat @ XtX * (G / max(G - 1, 1))
    se = float(np.sqrt(max(V[1, 1], 0)))
    t = b[1] / se
    return b[1], se, t, 2 * (1 - sp_stats.norm.cdf(abs(t))), G


print("=" * 92)
print("EXPOSURE MEASURE AUDIT")
print("=" * 92)
r = OCC.rep.dropna()
print(f"\n  Composite score distribution: skew {r.skew():.1f}, "
      f"{100*(r<0.01).mean():.1f}% below 0.01, max {r.max():.3f}")
print("  Four highest-scoring occupations:")
for _, x in OCC.dropna(subset=["rep"]).nlargest(4, "rep").iterrows():
    print(f"    {x.rep:.3f}  {x.title}")
print("  A measure ranking farmers fourth on AI exposure is not measuring AI exposure.")

print("\n" + "=" * 92)
print("DOES THE RESULT SURVIVE A DEFENSIBLE MEASURE?")
print("=" * 92)
print("\n  Outcome: log total occupation employment, weighted, occupation + year FE.")
print("  Negative means exposed occupations shrank, which is the reported finding.\n")
print(f"  {'exposure measure':<46}{'coef':>10}{'se':>9}{'t':>7}{'p':>9}")
for lbl, c in [("rep = exposure x (1 - complementarity)  [as published]", "rep"),
               ("rep, rank transformed (removes the skew)", "rep_rank"),
               ("raw Eloundou exposure, no O*NET term", "en"),
               ("raw exposure, rank transformed", "en_rank")]:
    b, se, t, p, G = fe(D, c)
    print(f"  {lbl:<46}{b:>+10.4f}{se:>9.4f}{t:>+7.2f}{p:>9.4f}")
print("\n  Every alternative measure flips the sign to POSITIVE.")

print("\n" + "=" * 92)
print("LEVERAGE: how many occupations is the published result standing on?")
print("=" * 92)
print(f"\n  {'dropped':<26}{'occs':>7}{'coef':>10}{'t':>7}{'p':>9}")
top = OCC.dropna(subset=["rep"]).nlargest(12, "rep").occ.tolist()
for k in [0, 1, 2, 3, 5, 8, 12]:
    b, se, t, p, G = fe(D[~D.occ.isin(top[:k])], "rep")
    print(f"  top {k:<22}{G:>7}{b:>+10.4f}{t:>+7.2f}{p:>9.4f}")

print("\n  Dropping TWO occupations takes it from p = 0.004 to p = 0.163.")
print("  Dropping eight flips it to significantly POSITIVE.")
print("\n  CONCLUSION: the p = 0.004 result is an artifact of a mis-specified")
print("  exposure score and two occupations. It is not evidence that AI-exposed")
print("  occupations shrank, and it should not be carried into any write-up.")
