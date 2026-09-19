"""
section3_core.py
The core specification for Section 3 of PAPER.md, plus the choices that could be
doing the work.

THE CLAIM
The young-worker share of employment falls in AI-exposed occupations after 2022,
within occupation, relative to less-exposed occupations.

    share_it = a_i + d_t + B * ( z(exposure_i) x post_t ) + e_it

share is the age band as a percent of the occupation's 16-64 employment, a_i and
d_t are occupation and year fixed effects, exposure is z-scored across occupations,
post = 1{year >= 2023}, cells are weighted by occupation employment, and standard
errors cluster on occupation.

WHAT IS CHECKED HERE
A referee will ask what happens if you move the cut-off, drop the weights, or let
a few huge occupations carry it. Section 5 already had a claim collapse because a
benchmark was doing the work unexamined, so every discretionary choice in the
baseline is varied here rather than asserted.

  1. EVENT STUDY     year-by-year, 2022 omitted. Is the pre-period flat, and does
                     the effect arrive when generative AI did? This is what
                     established 22-25 rather than 20-24 as the primary band.
  2. POST CUT-OFF    2022 vs 2023 vs 2024.
  3. WEIGHTS         employment weighted vs unweighted.
  4. INFLUENCE       drop the 10 and 25 largest occupations.

Panel construction and the estimator live in entry_panel.py.
Writes section3_core.png.
"""
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from entry_panel import load, fe, z, post_x, stars, BANDS, MEAS, BASE_YEAR, POST

D = load()

def baseline(d, ycol, xcol, post_from=POST, wcol="tot"):
    return fe(d, ycol, post_x(d, [xcol], post_from), wcol)

print("=" * 96)
print("SECTION 3  THE CORE RESULT")
print(f"occupations {D.occ.nunique()}, cells {len(D)}, {D.year.min()}-{D.year.max()}, post = {POST}")
print("=" * 96)
print(f"\n  {'specification':<40}{'coef':>9}{'se':>9}{'t':>7}{'p':>9}")
CORE = {}
for yc, yl in BANDS:
    for xc, xl in MEAS:
        b, se, t, p, G, n = baseline(D, yc, xc)
        CORE[(yc, xc)] = (b[0], se[0], p[0])
        print(f"  {yl + ', ' + xl:<40}{b[0]:>+9.4f}{se[0]:>9.4f}{t[0]:>7.2f}{p[0]:>9.4f} {stars(p[0])}")

print("\n" + "=" * 96)
print("1. EVENT STUDY  year-by-year exposure coefficient, 2022 omitted")
print("=" * 96)
ES = {}
for yc, yl in BANDS:
    yrs = sorted(y for y in D.year.unique() if y != BASE_YEAR)
    zx = z(D["rep_good"].values)
    X = np.column_stack([zx * (D.year.values == y) for y in yrs])
    b, se, t, p, G, n = fe(D, yc, X)
    ES[yc] = (yrs, b, se)
    print(f"\n  {yl}")
    print(f"    {'year':<8}{'coef':>10}{'se':>9}{'95% CI':>20}")
    for i, y in enumerate(yrs):
        mark = "  <- pre" if y < BASE_YEAR else ""
        print(f"    {y:<8}{b[i]:>+10.4f}{se[i]:>9.4f}"
              f"   [{b[i]-1.96*se[i]:+6.3f}, {b[i]+1.96*se[i]:+6.3f}]{mark}")
    pre = [i for i, y in enumerate(yrs) if y < BASE_YEAR]
    wald = sum(abs(b[i] / se[i]) > 1.96 for i in pre)
    print(f"    pre-2022 coefficients significant at 5%: {wald} of {len(pre)}")

print("\n" + "=" * 96)
print("2. POST CUT-OFF  does the result depend on calling 2023 the first AI year?")
print("=" * 96)
print(f"\n  {'':<24}{'22-25':>22}{'20-24':>22}")
for pf in (2022, 2023, 2024):
    row = f"  post from {pf}{'':<12}"
    for yc, _ in BANDS:
        b, se, t, p, G, n = baseline(D, yc, "rep_good", post_from=pf)
        row += f"{b[0]:>+11.4f} ({p[0]:.4f})"
    print(row)

print("\n" + "=" * 96)
print("3. WEIGHTS  employment weighted vs unweighted")
print("=" * 96)
print(f"\n  {'':<24}{'22-25':>22}{'20-24':>22}")
for wcol, lab in [("tot", "employment weighted"), (None, "unweighted")]:
    row = f"  {lab:<24}"
    for yc, _ in BANDS:
        b, se, t, p, G, n = baseline(D, yc, "rep_good", wcol=wcol)
        row += f"{b[0]:>+11.4f} ({p[0]:.4f})"
    print(row)

print("\n" + "=" * 96)
print("4. INFLUENCE  drop the largest occupations")
print("=" * 96)
size = D[D.year == BASE_YEAR].set_index("occ").tot.sort_values(ascending=False)
print(f"\n  {'':<24}{'22-25':>22}{'20-24':>22}")
for k in (0, 10, 25):
    sub = D[~D.occ.isin(size.index[:k])] if k else D
    row = f"  drop top {k:<16}" if k else f"  {'full sample':<24}"
    for yc, _ in BANDS:
        b, se, t, p, G, n = baseline(sub, yc, "rep_good")
        row += f"{b[0]:>+11.4f} ({p[0]:.4f})"
    print(row + f"   [{sub.occ.nunique()} occ]")

# ---- 5. numerator or denominator? (reported in Section 7) ----------------------
print("\n" + "=" * 96)
print("5. IS THE SHARE FALLING BECAUSE YOUNG EMPLOYMENT FELL, OR TOTAL ROSE?")
print("=" * 96)
print("""
  The outcome is a composition, so a falling share is consistent with young
  employment falling, total employment rising, or both. In logs the two components
  sum exactly to the share, so the same specification run on each decomposes it.
  Coefficients are x100, so they read as percent per sd of exposure.""")
L = D.copy()
for c, num in [("l2225", "a22_25"), ("l2024", "a20_24"), ("ltot", "tot")]:
    L[c] = 100 * np.log(L[num].clip(lower=1e-9))
L = L[np.isfinite(L[["l2225", "l2024", "ltot"]].values).all(axis=1)].copy()
L["ldiff"] = L.l2225 - L.ltot
print(f"\n  {'outcome':<40}{'coef':>9}{'se':>9}{'t':>7}{'p':>9}")
for c, lab in [("l2225", "log young employment (22-25)"),
               ("ltot", "log total employment (16-64)"),
               ("ldiff", "difference (= log share)")]:
    b, se, t, p, G, n = fe(L, c, post_x(L, ["rep_good"]))
    print(f"  {lab:<40}{b[0]:>+9.4f}{se[0]:>9.4f}{t[0]:>7.2f}{p[0]:>9.4f} {stars(p[0])}")
print("""
  The share moves significantly; neither component does on its own. The point
  estimates put about two thirds of it on young employment falling, but the panel
  cannot resolve the split. This is the same limit Section 5 finds in the quintile
  aggregates, here on the full continuous panel, and Section 7 carries it.""")

# ---- chart ---------------------------------------------------------------------
fig, ax = plt.subplots(1, 2, figsize=(13.5, 5.2))
for k, (yc, yl) in enumerate(BANDS):
    yrs, b, se = ES[yc]
    xs = list(yrs) + [BASE_YEAR]; bs = list(b) + [0.0]; ss = list(se) + [0.0]
    o = np.argsort(xs); xs = np.array(xs)[o]; bs = np.array(bs)[o]; ss = np.array(ss)[o]
    ax[k].axhspan(-99, 99, xmin=0, xmax=0, color="none")
    ax[k].fill_between(xs, bs - 1.96 * ss, bs + 1.96 * ss, color="#c0392b", alpha=.16)
    ax[k].plot(xs, bs, marker="o", lw=2.2, color="#c0392b")
    ax[k].axhline(0, color="black", lw=1.1)
    ax[k].axvline(BASE_YEAR, color="gray", ls=":", lw=1.4)
    ax[k].set_title(f"{yl}\nexposure x year, {BASE_YEAR} omitted", fontsize=11.5, fontweight="bold")
    ax[k].set_ylabel("pp change in young share per sd of exposure", fontsize=9.5)
    ax[k].grid(True, ls="--", alpha=.35)
    ax[k].set_ylim(min(bs - 1.96 * ss) - .1, max(bs + 1.96 * ss) + .1)
fig.suptitle("Section 3: the young-employment share falls in AI-exposed occupations after 2022",
             fontsize=13, fontweight="bold", y=1.02)
plt.tight_layout(); plt.savefig("section3_core.png", dpi=150, bbox_inches="tight")
print("\nChart saved: section3_core.png")
