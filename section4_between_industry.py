"""
section4_between_industry.py
Does the entry-level effect survive industry-by-year fixed effects?

THE OBJECTION
Section 3 carries occupation and year fixed effects. Those absorb anything fixed
about an occupation and anything common to a year. They do NOT absorb an
industry-specific shock in a particular year. If AI-exposed occupations sit
disproportionately in industries that contracted after 2022 for unrelated reasons,
and young workers are more exposed to industry contraction than older ones, the
Section 3 coefficient could be reading industry composition rather than AI
exposure.

Occupation fixed effects do not close this. An occupation's industry mix shifts
over time, and the same occupation in a different industry faces a different
shock.

THE TEST
Re-estimate on occupation-by-industry-by-year cells, adding industry-by-year fixed
effects. Those absorb every sector-level shock in every year, so identification
comes only from comparing occupations against each other WITHIN the same industry
in the same year. If the coefficient survives, the effect is within-industry and
the between-industry channel is not driving it.

Cells are occupation x IND1990 major division x year, from build_cps_panel_ind.py.
Writes section4_between_industry.png.
"""
import os, numpy as np, pandas as pd
from scipy import stats as sp
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from entry_panel import load, z, stars, HERE, POST
from fastfe import _demean

NONOV = ["u20", "a20_24", "a25", "a26_30", "a31_34", "a35p"]

EXP = load().drop_duplicates("occ")[["occ", "rep_good", "en_raw"]]
P = pd.read_csv(os.path.join(HERE, "cps_panel_ind.csv"))
W = (P.pivot_table(index=["occ", "year", "sector"], columns="band",
                   values="emp", aggfunc="sum").fillna(0.0).reset_index()
       .merge(EXP, on="occ", how="inner"))
missing = [c for c in NONOV if c not in W.columns]
assert not missing, f"panel missing bands {missing}"
W["tot"] = W[NONOV].sum(axis=1)
D = W[(W.year >= 2016) & (W.tot > 0) & (W.a22_25 > 0)].copy()
D["share_2225"] = 100 * D.a22_25 / D.tot
D["share_2024"] = 100 * D.a20_24 / D.tot
D["iy"] = D.sector.astype(str) + "_" + D.year.astype(str)

def fe2(d, ycol, xcols, unit, time, post_from=POST):
    """Two-way FE on arbitrary unit and time dimensions, clustered on occupation."""
    post = (d.year.values >= post_from).astype(float)
    X = np.column_stack([z(d[c].values) * post for c in xcols])
    y = d[ycol].values.astype(float)
    w = d.tot.values.astype(float); w = w / w.mean()
    uc, uu = pd.factorize(d[unit].values); tc, tu = pd.factorize(d[time].values)
    M = _demean(np.hstack([X, y.reshape(-1, 1)]), uc, tc, w, len(uu), len(tu))
    Xt, yt = M[:, :-1], M[:, -1]
    inv = np.linalg.pinv(Xt.T @ (w[:, None] * Xt)); b = inv @ (Xt.T @ (w * yt))
    r = yt - Xt @ b
    oc, ou = pd.factorize(d.occ.values)
    meat = np.zeros((Xt.shape[1],) * 2)
    for gi in range(len(ou)):
        m = oc == gi
        if m.any():
            s = Xt[m].T @ (w[m] * r[m]); meat += np.outer(s, s)
    G = len(ou); V = inv @ (meat * (G / max(G - 1, 1))) @ inv
    se = np.sqrt(np.maximum(np.diag(V), 0)); t = b / se
    return b, se, t, 2 * (1 - sp.norm.cdf(np.abs(t))), G, len(d)

print("=" * 96)
print("DOES THE EFFECT SURVIVE INDUSTRY-BY-YEAR FIXED EFFECTS?")
print(f"{D.occ.nunique()} occupations x {D.sector.nunique()} sectors, {len(D):,} cells")
print("=" * 96)
print()
R = {}
for ycol, ylab in [("share_2225", "22-25 (primary)"), ("share_2024", "20-24")]:
    print(f"  --- {ylab} ---")
    print(f"  {'specification':<46}{'coef':>10}{'se':>9}{'t':>7}{'p':>9}")
    for unit, time, lab in [("occ", "year", "occupation + year FE"),
                            ("occ", "iy", "occupation + INDUSTRY-BY-YEAR FE")]:
        b, se, t, p, G, n = fe2(D, ycol, ["rep_good"], unit, time)
        R[(ycol, lab)] = (b[0], se[0], p[0])
        print(f"  {lab:<46}{b[0]:>+10.4f}{se[0]:>9.4f}{t[0]:>7.2f}{p[0]:>9.4f} {stars(p[0])}")
    a = R[(ycol, "occupation + year FE")][0]
    c = R[(ycol, "occupation + INDUSTRY-BY-YEAR FE")][0]
    print(f"  {'':<46}change: {100*(c-a)/abs(a):+.0f}%\n")

print("  Note the occupation+year row here is estimated on occupation-by-industry")
print("  cells, so it will not exactly match Section 3, which uses occupation-by-year")
print("  cells. The comparison that matters is between the two rows above, which run")
print("  on identical cells.\n")

print("  HOW MUCH OF THE VARIATION IS BETWEEN INDUSTRIES?")
tot_var = np.average((D.share_2225 - np.average(D.share_2225, weights=D.tot))**2, weights=D.tot)
sect_mean = D.groupby("sector").apply(
    lambda g: np.average(g.share_2225, weights=g.tot), include_groups=False)
D["_sm"] = D.sector.map(sect_mean)
btw_var = np.average((D._sm - np.average(D.share_2225, weights=D.tot))**2, weights=D.tot)
print(f"    between-sector share of variance in the young share: {100*btw_var/tot_var:.1f}%")

# ---- chart ---------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(8.6, 5.0))
labs = ["occupation\n+ year FE", "occupation\n+ industry-by-year FE"]
x = np.arange(2); w = 0.38
for j, (ycol, ylab, c) in enumerate([("share_2225", "22-25", "#c0392b"),
                                     ("share_2024", "20-24", "#1f4e79")]):
    v = [R[(ycol, "occupation + year FE")], R[(ycol, "occupation + INDUSTRY-BY-YEAR FE")]]
    ax.bar(x + (j - 0.5) * w, [k[0] for k in v], w, yerr=[1.96 * k[1] for k in v],
           color=c, error_kw=dict(lw=1.3, capsize=4), label=ylab)
ax.axhline(0, color="black", lw=1.2)
ax.set_xticks(x); ax.set_xticklabels(labs, fontsize=9.5)
ax.set_ylabel("pp per sd of exposure", fontsize=9.5)
ax.set_title("The effect is within industry, not between",
             fontsize=12.5, fontweight="bold")
ax.legend(fontsize=9); ax.grid(True, axis="y", ls="--", alpha=.35)
plt.tight_layout(); plt.savefig("section4_between_industry.png", dpi=150, bbox_inches="tight")
print("\nChart saved: section4_between_industry.png")
