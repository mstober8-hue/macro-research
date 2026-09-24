"""
section6_facts_4_6.py
Canaries' facts (4) and (6), tested on CPS flows and outgoing-rotation earnings.

FACT (4)  "It operates primarily through reduced hiring of young workers rather
          than increased separations."
FACT (6)  "Adjustment is occurring through employment rather than base
          compensation."

Both are mechanism claims and neither is testable on employment stocks, which is
why earlier sections could not reach them. build_cps_flows.py links individuals
across consecutive months on CPSIDP to construct hires and separations, and pulls
EARNWEEK / HOURWAGE from the outgoing rotation groups with their own weight.

SPECIFICATION
The Section 3 specification, unchanged: two-way occupation and year fixed effects,
z-scored exposure interacted with post-2022, employment weighted, occupation
clustered. Only the outcome changes.

  fact (4)   hire rate   = 100 x hires / (hires + stayers)
             sep rate    = 100 x separations / (separations + stayers)
  fact (6)   log weekly earnings, log hourly wage

WHAT WOULD CONFIRM EACH
Fact (4) predicts a negative exposure coefficient on the young hire rate and no
positive coefficient on the young separation rate. Fact (6) predicts no negative
exposure coefficient on pay: if adjustment runs through employment, prices should
not move.

Writes section6_facts_4_6.png.
"""
import numpy as np, pandas as pd
from scipy import stats as sp
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from entry_panel import load, fe, z, post_x, stars, HERE
import os

BANDS = [("a22_25", "22-25 (their band)"), ("a20_24", "20-24"),
         ("a26_30", "26-30"), ("a31_34", "31-34"), ("a35p", "35+")]

EXP = load().drop_duplicates("occ")[["occ", "rep_good", "en_raw"]]

# ---- fact (4): flows ------------------------------------------------------------
F = pd.read_csv(os.path.join(HERE, "cps_flows.csv")).merge(EXP, on="occ", how="inner")
F = F[(F.year >= 2016) & (F.year <= 2026)].copy()
F["emp_t"] = F.hires + F.stayers
F["emp_p"] = F.seps + F.stayers
F = F[(F.emp_t > 0) & (F.emp_p > 0)].copy()
F["hire_rate"] = 100 * F.hires / F.emp_t
F["sep_rate"] = 100 * F.seps / F.emp_p
F["tot"] = F.emp_t

print("=" * 96)
print("FACT (4): DOES THE EFFECT RUN THROUGH HIRING RATHER THAN SEPARATIONS?")
print("=" * 96)
print("""
  Their claim: "It operates primarily through reduced hiring of young workers
  rather than increased separations." Confirmation needs the hire-rate coefficient
  negative for the young and the separation-rate coefficient NOT positive.
""")
R4 = {}
for outcome, olab in [("hire_rate", "HIRE RATE"), ("sep_rate", "SEPARATION RATE")]:
    print(f"  {olab}")
    print(f"    {'age band':<22}{'coef':>10}{'se':>9}{'t':>7}{'p':>9}{'mean':>9}")
    for b, lab in BANDS:
        d = F[F.band == b]
        if len(d) < 200: continue
        co, se, t, p, G, n = fe(d, outcome, post_x(d, ["rep_good"]))
        R4[(outcome, b)] = (co[0], se[0], p[0])
        mu = np.average(d[outcome], weights=d.tot)
        print(f"    {lab:<22}{co[0]:>+10.4f}{se[0]:>9.4f}{t[0]:>7.2f}{p[0]:>9.4f} "
              f"{stars(p[0]):<4}{mu:>7.2f}")
    print()

# net flow: the margin that has to reconcile with the stock result in Section 3
print("  NET FLOW (hire rate minus separation rate)")
print(f"    {'age band':<22}{'coef':>10}{'se':>9}{'t':>7}{'p':>9}")
F["net_rate"] = F.hire_rate - F.sep_rate
for b, lab in BANDS:
    d = F[F.band == b]
    if len(d) < 200: continue
    co, se, t, p, G, n = fe(d, "net_rate", post_x(d, ["rep_good"]))
    R4[("net_rate", b)] = (co[0], se[0], p[0])
    print(f"    {lab:<22}{co[0]:>+10.4f}{se[0]:>9.4f}{t[0]:>7.2f}{p[0]:>9.4f} {stars(p[0])}")
print("""
  Read this carefully. The net is negative for the young, which is the sign the
  Section 3 stock result requires, but it is not significant at any age. What IS
  significant is the separation side, and it is significant at four of five bands
  rather than only the young ones.

  Two things follow, and the second is awkward for this paper rather than for
  theirs. Fact (4)'s specific claim, reduced hiring with separations unchanged,
  does not hold here: the hire-rate point estimates are positive and the
  separation-rate estimates are positive and mostly significant. And the flow
  results carry no age gradient, while the stock results in Section 3.6 carry a
  sharp one. A mechanism visible in stocks but not in the flows that generate them
  is a tension this paper cannot resolve, and Section 8 records it as such.
""")

# ---- do the flows CONTRADICT the stocks, or merely fail to resolve them? --------
# A net-flow estimate that is insignificant is not evidence against the stock
# result unless the flow design could have detected the flow the stock result
# implies. This computes the implied value and checks it against the interval.
print("=" * 96)
print("RECONCILIATION: is the flow null a contradiction or a power failure?")
print("=" * 96)
print("""
  A stock coefficient of b pp per sd on a band whose base share is s, accumulated
  over a 48-month window, implies a monthly net-flow gap of 100*(b/s)/48. If that
  implied value sits inside the observed flow interval, the two results agree and
  the flow design simply cannot resolve the difference.
""")
from entry_panel import NONOVERLAP
DD = load()
for bb in NONOVERLAP: DD[f"sh_{bb}"] = 100 * DD[bb] / DD.tot
DD["sh_a22_25"] = 100 * DD.a22_25 / DD.tot
F["net_rate"] = F.hire_rate - F.sep_rate
print(f"  {'band':<10}{'stock':>10}{'base':>9}{'REQUIRED':>11}{'OBSERVED':>11}"
      f"{'95% CI':>20}{'agrees':>9}")
for bb, colname in [("a20_24", "sh_a20_24"), ("a22_25", "sh_a22_25"),
                    ("a26_30", "sh_a26_30"), ("a31_34", "sh_a31_34"),
                    ("a35p", "sh_a35p")]:
    sc, _, _, _, _, _ = fe(DD, colname, post_x(DD, ["rep_good"]))
    share = 100 * DD[DD.year == 2022][bb].sum() / DD[DD.year == 2022].tot.sum()
    req = 100 * (sc[0] / share) / 48
    d = F[F.band == bb]
    co, se, t, p, G, n = fe(d, "net_rate", post_x(d, ["rep_good"]))
    lo, hi = co[0] - 1.96 * se[0], co[0] + 1.96 * se[0]
    print(f"  {bb:<10}{sc[0]:>+10.3f}{share:>8.1f}%{req:>+11.4f}{co[0]:>+11.4f}"
          f"   [{lo:+6.3f},{hi:+6.3f}]{'YES' if lo <= req <= hi else 'NO':>9}")
print("""
  The implied value falls inside the interval at every band, and for 22-25 the
  observed estimate is 91% of the required magnitude. The flows agree with the
  stocks; they are too imprecise to confirm the gradient. Note why the gradient is
  hard to see in flows: the 35+ band holds 63% of employment, so its large stock
  coefficient implies a monthly flow gap of only +0.021, well inside noise. The
  whole implied flow gradient spans about 0.12pp against standard errors of 0.04
  to 0.16.
""")

# ---- fact (6): earnings, at the PERSON level -----------------------------------
# Cell means do not work here. The ORG subsample is a quarter of records, so
# occupation x year x narrow age band cells held a median of 4 observations and
# two-way fixed effects on those means produced coefficients of order 1e11. The
# regression runs on the 1.0M person records instead.
E = pd.read_csv(os.path.join(HERE, "cps_earnings.csv")).merge(EXP, on="occ", how="inner")
E = E[(E.year >= 2016) & (E.year <= 2026)].copy()
# trim implausible reports at the bottom; the top is a genuine topcode, left alone
E.loc[E.earnweek < 50, "earnweek"] = np.nan
E.loc[E.hourwage < 2, "hourwage"] = np.nan
E["lew"] = 100 * np.log(E.earnweek)
E["lhw"] = 100 * np.log(E.hourwage)
E["tot"] = E.ewt

print("=" * 96)
print("FACT (6): DOES ADJUSTMENT RUN THROUGH EMPLOYMENT RATHER THAN PAY?")
print("=" * 96)
print("""
  Their claim: "Adjustment is occurring through employment rather than base
  compensation." Confirmation needs NO negative exposure coefficient on pay.
  Person-level regression on outgoing-rotation records, occupation and year fixed
  effects, ORG-weighted, clustered on occupation. Coefficients are x100 log
  points, so they read as percent per sd of exposure.
""")
R6 = {}
for outcome, olab in [("lew", "LOG WEEKLY EARNINGS"), ("lhw", "LOG HOURLY WAGE")]:
    print(f"  {olab}")
    print(f"    {'age band':<22}{'coef':>10}{'se':>9}{'t':>7}{'p':>9}{'records':>10}")
    for b, lab in BANDS:
        d = E[(E.band == b) if b != "a22_25" else (E.is2225 == True)]
        d = d[np.isfinite(d[outcome])]
        if len(d) < 2000: continue
        co, se, t, p, G, n = fe(d, outcome, post_x(d, ["rep_good"]))
        R6[(outcome, b)] = (co[0], se[0], p[0])
        print(f"    {lab:<22}{co[0]:>+10.4f}{se[0]:>9.4f}{t[0]:>7.2f}{p[0]:>9.4f} "
              f"{stars(p[0]):<4}{n:>9,}")
    print()

# ---- chart ----------------------------------------------------------------------
fig, ax = plt.subplots(1, 2, figsize=(13.5, 5.2))
for k, (outs, title, R) in enumerate(
        [([("hire_rate", "hire rate"), ("sep_rate", "separation rate")],
          "Fact (4): hiring vs separations", R4),
         ([("lew", "log weekly earnings"), ("lhw", "log hourly wage")],
          "Fact (6): pay", R6)]):
    x = np.arange(len(BANDS)); w = 0.38
    for j, (o, olab) in enumerate(outs):
        vals = [R.get((o, b), (np.nan, np.nan, np.nan)) for b, _ in BANDS]
        ax[k].bar(x + (j - 0.5) * w, [v[0] for v in vals], w,
                  yerr=[1.96 * v[1] if np.isfinite(v[1]) else 0 for v in vals],
                  color=["#c0392b", "#1f4e79"][j], error_kw=dict(lw=1.1, capsize=3),
                  label=olab)
    ax[k].axhline(0, color="black", lw=1.1)
    ax[k].set_xticks(x); ax[k].set_xticklabels([l for _, l in BANDS], fontsize=8)
    ax[k].set_title(title, fontsize=11.5, fontweight="bold")
    ax[k].legend(fontsize=8.5); ax[k].grid(True, axis="y", ls="--", alpha=.35)
ax[0].set_ylabel("pp per sd of exposure", fontsize=9.5)
ax[1].set_ylabel("percent per sd of exposure", fontsize=9.5)
fig.suptitle("Facts (4) and (6) in nationally representative data",
             fontsize=13, fontweight="bold", y=1.02)
plt.tight_layout(); plt.savefig("section6_facts_4_6.png", dpi=150, bbox_inches="tight")
print("Chart saved: section6_facts_4_6.png")
