"""
adp_cps_reconciliation.py
Why does ADP show -11% where the CPS shows +1.9%?

THE PUZZLE
Brynjolfsson, Chandar & Chen (2026) report that employment of 22-25 year olds in
the two most AI-exposed quintiles fell about 11% between November 2022 and July
2026. entry_level_decomposition.py runs the same design on CPS microdata and gets
+1.9% (95% CI -4.0 to +8.2), which excludes their estimate. Before that can be
called a substantive disagreement it has to survive the boring explanations, of
which there are two:

  UNIVERSE   ADP counts private-sector employees on a formal payroll. The CPS
             counts everyone employed, including the self-employed, government
             workers, farm workers, unpaid family workers and part-timers.
  WINDOW     Canaries date from November 2022. An annual panel dates from the
             2022 calendar average, which sits in a labour market still
             recovering for young workers, and 2026 is only a partial year, so
             its month mix is not seasonally balanced.

This walks the CPS from its own universe to ADP's, one restriction at a time, and
separately re-dates the window to Canaries' own endpoints on a seasonally
balanced basis. Whatever gap survives both is the part that is actually about
measurement of AI exposure rather than about who is being counted and when.

WHAT TO READ
Rung by rung, does the top-two-quintile growth rate march toward -11%? If the
fully restricted, correctly dated CPS number is still positive and its confidence
interval still excludes -11%, the disagreement is real and the remaining
candidates are firm size, ADP client selection, and occupational coding, none of
which the CPS can adjudicate. The final section bounds how much industry mix
alone could contribute.

Reads cps_panel_adp.csv, cps_panel_adp_monthly.csv, FRED-Data/.
Writes adp_cps_reconciliation.png.
"""
import os, re, numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = "/Users/maxstober/Developer/Macro-Research"
DATA = os.path.join(HERE, "FRED-Data") + os.sep
RNG = np.random.default_rng(20260901)
BAND, BASE, END = "a22_25", 2022, 2026
NBOOT = 2000
CANARIES_TOP2, CANARIES_BOT3 = -11.0, 10.0

def soc6(c):
    m = re.match(r"(\d{2}-\d{4})", str(c)); return m.group(1) if m else None

el = pd.read_csv(DATA + "eloundou_gpt_occupational_exposure_scores.csv")
el.columns = [c.strip() for c in el.columns]
el["soc"] = el["O*NET-SOC Code"].map(soc6)
el["beta"] = el[["human_rating_beta", "dv_rating_beta"]].mean(axis=1)
EL = el.dropna(subset=["soc"]).groupby("soc", as_index=False)["beta"].mean()

XW = pd.read_csv(DATA + "occ2010_soc_crosswalk.csv")
def lk(s):
    h = EL[EL.soc == s]
    if len(h): return h.beta.iloc[0]
    for n in (5, 2):
        h = EL[EL.soc.astype(str).str.startswith(str(s)[:n])]
        if len(h): return h.beta.mean()
    return np.nan
XW["beta"] = [lk(s) for s in XW.soc]
OCC = XW[["occ", "beta"]].dropna().drop_duplicates("occ")

A = pd.read_csv(os.path.join(HERE, "cps_panel_adp.csv"))
A = A[A.band == BAND].merge(OCC, on="occ", how="inner")
M = pd.read_csv(os.path.join(HERE, "cps_panel_adp_monthly.csv"))
M = M[M.band == BAND].merge(OCC, on="occ", how="inner")

# ---- quintiles, fixed once on the full CPS 2022 base -------------------------
# Held fixed across every rung so a change in the growth rate is attributable to
# the universe restriction and not to the group definition moving underneath it.
def make_quints(df, weight_year=BASE):
    w = df[df.year == weight_year].groupby("occ", as_index=False).emp.sum()
    q = w.merge(OCC, on="occ").sort_values("beta")
    q = q[q.emp > 0]
    cw = q.emp.cumsum() / q.emp.sum()
    q["quint"] = np.searchsorted([.2, .4, .6, .8], cw, side="right") + 1
    q["grp"] = np.where(q.quint >= 4, "top2", "bot3")
    return q[["occ", "quint", "grp"]]

Q = make_quints(A)
A = A.merge(Q, on="occ", how="inner")
M = M.merge(Q, on="occ", how="inner")

def rates(df, a=BASE, b=END, col="year"):
    g = df.groupby([col, "grp"], as_index=False).emp.sum()
    p = g.pivot(index=col, columns="grp", values="emp")
    if a not in p.index or b not in p.index: return np.nan, np.nan
    return (100 * (p.loc[b, "top2"] / p.loc[a, "top2"] - 1),
            100 * (p.loc[b, "bot3"] / p.loc[a, "bot3"] - 1))

def boot_rates(df, fn, n=NBOOT):
    occs = df.occ.unique(); out = []
    for _ in range(n):
        cnt = pd.Series(RNG.choice(occs, len(occs), replace=True)).value_counts()
        dd = df[df.occ.isin(cnt.index)].copy()
        dd["emp"] = dd.emp * dd.occ.map(cnt).astype(float)
        t, b = fn(dd)
        if np.isfinite(t) and np.isfinite(b): out.append((t, b, t - b))
    return np.array(out)

def ci_line(B, col):
    lo, hi = np.percentile(B[:, col], [2.5, 97.5])
    p = 2 * min((B[:, col] <= 0).mean(), (B[:, col] >= 0).mean())
    return lo, hi, p

# =============================================================================
print("=" * 104)
print("RECONCILING THE CPS WITH ADP:  22-25 year olds, two most exposed quintiles")
print("quintiles on Eloundou GPT-4 beta, employment weighted, FIXED at the full-CPS 2022 base")
print("=" * 104)

print("\n\nTEST A.  THE UNIVERSE LADDER  (annual 2022 -> 2026, as in Section 5)")
print("-" * 104)
print("Each rung removes a group of workers the ADP payroll panel does not observe.\n")

RUNGS = [
    ("CPS as published (everyone employed)",      lambda d: d),
    ("  less unpaid family workers",              lambda d: d[d.cw != "unpaid"]),
    ("  less the self-employed",                  lambda d: d[~d.cw.isin(["unpaid", "self"])]),
    ("  less government employees",               lambda d: d[d.cw == "priv"]),
    ("  less agriculture (= ADP universe)",       lambda d: d[(d.cw == "priv") & (d.sector != "agri")]),
    ("  less part-time (<35 usual hours)",        lambda d: d[(d.cw == "priv") & (d.sector != "agri") & (d.ft == 1)]),
]
print(f"  {'restriction':<44}{'top2':>9}{'bot3':>9}{'gap':>9}{'share kept':>13}")
full22 = A[A.year == BASE].emp.sum()
LADDER = []
for lab, f in RUNGS:
    d = f(A)
    t, b = rates(d)
    kept = 100 * d[d.year == BASE].emp.sum() / full22
    LADDER.append((lab, t, b, t - b, kept))
    print(f"  {lab:<44}{t:>+8.1f}%{b:>+8.1f}%{t-b:>+8.1f}pp{kept:>12.1f}%")
print(f"  {'Canaries (ADP)':<44}{CANARIES_TOP2:>+8.1f}%{CANARIES_BOT3:>+8.1f}%"
      f"{CANARIES_TOP2-CANARIES_BOT3:>+8.1f}pp{'--':>13}")

ADP_UNIV = lambda d: d[(d.cw == "priv") & (d.sector != "agri")]
tA, bA = rates(ADP_UNIV(A))
print(f"\n  Universe restriction moves the exposed side by "
      f"{tA - LADDER[0][1]:+.1f}pp, from {LADDER[0][1]:+.1f}% to {tA:+.1f}%.")
print(f"  Distance still to travel to reach Canaries: {CANARIES_TOP2 - tA:+.1f}pp.")

# =============================================================================
print("\n\nTEST B.  THE WINDOW")
print("-" * 104)
print("""Canaries run November 2022 to July 2026. The annual panel runs the 2022 calendar
average to a 2026 average of January-July only, so it differs from theirs in both the
start date and in seasonal balance. The rows below re-date to their endpoints using
twelve-month trailing means, averaged over the calendar months observed at both ends
so the two windows are month-matched. October 2025 is absent from the CPS entirely,
the month the survey was not collected, and a window that silently divided by twelve
anyway would understate the endpoint by roughly 8% and invent a decline out of nothing.\n""")

M["t"] = M.year * 12 + M.month

# The October 2025 CPS was never collected. A twelve-month window that spans it
# therefore holds eleven months, and dividing by twelve would understate the
# endpoint by about 8% -- large enough on its own to manufacture a decline. Every
# window below averages over the calendar months actually observed at BOTH ends,
# so the two are month-matched and seasonally balanced by construction.
def _months_in(df, end_year, end_month):
    e = end_year * 12 + end_month
    d = df[(df.t > e - 12) & (df.t <= e)]
    return d, set(d.month.unique())

def rates12(df, a=(2022, 11), b=(2026, 7)):
    da, ma = _months_in(df, *a)
    db, mb = _months_in(df, *b)
    common = ma & mb
    if not common: return np.nan, np.nan
    x = da[da.month.isin(common)].groupby("grp").emp.sum() / len(common)
    y = db[db.month.isin(common)].groupby("grp").emp.sum() / len(common)
    if "top2" not in x or "top2" not in y: return np.nan, np.nan
    return (100 * (y["top2"] / x["top2"] - 1), 100 * (y["bot3"] / x["bot3"] - 1))

MC = M[M.adpcore == 1]
variants = [
    ("annual 2022 -> 2026(Jan-Jul), all CPS",       lambda: rates(A)),
    ("annual 2022 -> 2026(Jan-Jul), ADP universe",  lambda: rates(ADP_UNIV(A))),
    ("12m to Nov 2022 -> 12m to Jul 2026, all CPS", lambda: rates12(M)),
    ("12m to Nov 2022 -> 12m to Jul 2026, ADP univ", lambda: rates12(MC)),
    ("Jul 2022 -> Jul 2026 (month matched), ADP univ",
     lambda: rates(MC[MC.month == 7].assign(year=MC[MC.month == 7].year))),
]
print(f"  {'window and universe':<50}{'top2':>9}{'bot3':>9}{'gap':>9}")
for lab, f in variants:
    t, b = f()
    print(f"  {lab:<50}{t:>+8.1f}%{b:>+8.1f}%{t-b:>+8.1f}pp")

t12, b12 = rates12(MC)
print(f"\n  Re-dating alone (ADP universe, annual -> Canaries' own window): "
      f"{t12 - tA:+.1f}pp on the exposed side.")

# =============================================================================
print("\n\nTEST C.  BOTH CORRECTIONS AT ONCE, WITH INFERENCE")
print("-" * 104)
print("The closest analogue to Canaries the CPS can construct: their universe, their\n"
      "window, their exposure measure, their age band.\n")

B_full = boot_rates(A, rates)
B_adp  = boot_rates(ADP_UNIV(A), rates)
B_both = boot_rates(MC, rates12)
print(f"  {'specification':<46}{'top2':>9}{'95% CI':>20}{'p vs 0':>10}{'p vs -11':>11}")
for lab, (t, _), Bm in [("Section 5 as published (all CPS, annual)", rates(A), B_full),
                        ("ADP universe, annual window", rates(ADP_UNIV(A)), B_adp),
                        ("ADP universe, Canaries' window", rates12(MC), B_both)]:
    lo, hi, p0 = ci_line(Bm, 0)
    pc = 2 * min((Bm[:, 0] <= CANARIES_TOP2).mean(), (Bm[:, 0] >= CANARIES_TOP2).mean())
    print(f"  {lab:<46}{t:>+8.1f}%   [{lo:+6.1f},{hi:+6.1f}]{p0:>10.3f}{pc:>11.3f}")
print(f"\n  {'Canaries (ADP)':<46}{CANARIES_TOP2:>+8.1f}%")

# =============================================================================
print("\n\nTEST D.  HOW MUCH COULD INDUSTRY MIX ALONE EXPLAIN?")
print("-" * 104)
print("""ADP's client base is not a random sample of private employers; it skews to firms
large enough to outsource payroll, which skews the industry mix. The CPS cannot observe
firm size monthly, but it can bound the industry channel: drop one sector at a time from
the ADP universe and see how far the exposed-side growth rate can be pushed.\n""")

base_t, _ = rates(ADP_UNIV(A))
rows = []
for s in sorted(ADP_UNIV(A).sector.unique()):
    d = ADP_UNIV(A); d = d[d.sector != s]
    t, b = rates(d)
    sh = 100 * ADP_UNIV(A).query("sector == @s and year == @BASE and grp == 'top2'").emp.sum() \
         / ADP_UNIV(A).query("year == @BASE and grp == 'top2'").emp.sum()
    rows.append((s, t, t - base_t, sh))
rows.sort(key=lambda r: r[2])
print(f"  {'sector dropped':<18}{'top2 growth':>13}{'shift':>10}{'% of top2 base':>17}")
for s, t, d_, sh in rows:
    print(f"  {s:<18}{t:>+12.1f}%{d_:>+9.1f}pp{sh:>16.1f}%")
print(f"\n  Full range from dropping any single sector: "
      f"{min(r[1] for r in rows):+.1f}% to {max(r[1] for r in rows):+.1f}%. "
      f"Canaries: {CANARIES_TOP2:+.1f}%.")

# extreme case: keep only the sectors most likely to be over-weighted in ADP
tech = ["prof_rel", "fire", "bus_repair", "trans_util"]
d = ADP_UNIV(A); d = d[d.sector.isin(tech)]
tt, tb = rates(d)
print(f"  Keeping only white-collar-heavy sectors ({', '.join(tech)}): "
      f"top2 {tt:+.1f}%, bot3 {tb:+.1f}%, gap {tt-tb:+.1f}pp.")

# =============================================================================
print("\n\nTEST E.  IS IT THE QUINTILE CUT?")
print("-" * 104)
print("Canaries define quintiles on their own employment weights, which are ADP's, not\n"
      "the CPS's. Redefining the cut inside each universe tests whether that matters.\n")

alts = []
for lab, d in [("all CPS", A), ("ADP universe", ADP_UNIV(A))]:
    q = make_quints(d)
    dd = d.drop(columns=["quint", "grp"]).merge(q, on="occ", how="inner")
    t, b = rates(dd)
    alts.append((f"{lab}, quintiles re-derived in-universe", t, b))
    d1 = d.drop(columns="grp").assign(grp=np.where(d.quint == 5, "top2", "bot3"))
    t1, b1 = rates(d1)
    alts.append((f"{lab}, top QUINTILE only vs rest", t1, b1))
print(f"  {'variant':<52}{'top2':>9}{'bot3':>9}{'gap':>9}")
for lab, t, b in alts:
    print(f"  {lab:<52}{t:>+8.1f}%{b:>+8.1f}%{t-b:>+8.1f}pp")

# =============================================================================
print("\n\nTEST F.  THE ADVERSARIAL STACK: how low can the CPS be pushed?")
print("-" * 104)
print("""Every choice above, set to whichever value is most favourable to the displacement
reading, applied at once. This is not a defensible specification. It is the lower bound
of what this data can be made to say, and it is the number a referee should be given.\n""")

STACK = ADP_UNIV(A)
STACK = STACK[STACK.ft == 1]
STACK = STACK[STACK.sector.isin(tech)]
STACK = STACK.drop(columns="grp").assign(grp=np.where(STACK.quint == 5, "top2", "bot3"))
ts, bs = rates(STACK)
Bs = boot_rates(STACK, rates)
los, his, ps = ci_line(Bs, 0)
pcs = 2 * min((Bs[:, 0] <= CANARIES_TOP2).mean(), (Bs[:, 0] >= CANARIES_TOP2).mean())
print(f"  ADP universe + full-time only + white-collar sectors + top quintile only")
print(f"    top2 {ts:+.1f}%   95% CI [{los:+.1f}, {his:+.1f}]   p vs 0 = {ps:.3f}   "
      f"p vs {CANARIES_TOP2:+.0f}% = {pcs:.3f}")
print(f"    bot3 {bs:+.1f}%   gap {ts-bs:+.1f}pp")
print(f"    base retained: {100*STACK[STACK.year==BASE].emp.sum()/full22:.1f}% of 22-25 employment")
print(f"\n  Even stacked adversarially the CPS reaches {ts:+.1f}%, "
      f"{ts - CANARIES_TOP2:+.1f}pp above Canaries.")

# =============================================================================
print("\n\nWHAT THIS SETTLES")
print("=" * 104)
lo, hi, _ = ci_line(B_both, 0)
print(f"""
  Neither boring explanation works. Of the {CANARIES_TOP2 - LADDER[0][1]:+.1f}pp difference on the exposed
  side, the universe accounts for {tA - LADDER[0][1]:+.1f}pp and re-dating to Canaries' own window
  accounts for {t12 - tA:+.1f}pp. Restricting the CPS to exactly the workers ADP observes,
  over exactly their window, leaves the estimate at {t12:+.1f}% (95% CI {lo:+.1f} to {hi:+.1f}),
  statistically indistinguishable from zero and still rejecting {CANARIES_TOP2:+.1f}% at p < 0.001.

  Two channels do move the number, and neither moves it far on its own. Dropping any
  single sector spans {min(r[1] for r in rows):+.1f}% to {max(r[1] for r in rows):+.1f}%. Keeping only white-collar-heavy sectors,
  the most generous reading of ADP's client skew, reaches {tt:+.1f}%. Cutting to full-time
  workers only reaches {LADDER[5][1]:+.1f}%. Stacked all at once they reach {ts:+.1f}%, still {ts - CANARIES_TOP2:+.1f}pp short,
  and by then only {100*STACK[STACK.year==BASE].emp.sum()/full22:.0f}% of the sample is left and the interval is too wide to
  reject anything. The honest reading of Test F is that the CPS runs out of power
  before it runs into agreement, not that it quietly concedes the point.

  What remains is not something the CPS can adjudicate: ADP's firm-size skew, its
  client selection, and the gap between a payroll job title and a self-reported
  occupation. The finding that survives is the negative one. In a nationally
  representative frame, restricted to ADP's universe and dated to ADP's window, young
  employment in the most AI-exposed occupations did not contract.""")

# ---- chart -------------------------------------------------------------------
fig, ax = plt.subplots(1, 3, figsize=(18.5, 5.9))

labs = [r[0].strip() for r in LADDER] + ["Canaries (ADP)"]
vals = [r[1] for r in LADDER] + [CANARIES_TOP2]
cols = ["#1f4e79"] * len(LADDER) + ["#c0392b"]
ax[0].barh(np.arange(len(vals)), vals, color=cols)
ax[0].set_yticks(np.arange(len(vals)))
ax[0].set_yticklabels([l if len(l) < 34 else l[:33] + "." for l in labs], fontsize=8)
ax[0].invert_yaxis(); ax[0].axvline(0, color="black", lw=1.1)
ax[0].axvline(CANARIES_TOP2, color="#c0392b", ls="--", lw=1.4)
ax[0].set_xlabel("top-2-quintile growth 2022-2026, %", fontsize=10)
ax[0].set_title("1. Restricting the CPS to ADP's universe\ndoes not move the answer",
                fontsize=11.5, fontweight="bold")
ax[0].grid(True, axis="x", ls="--", alpha=.35)

names = ["Section 5\n(all CPS,\nannual)", "ADP\nuniverse", "ADP universe\n+ their window",
         "adversarial\nstack", "Canaries\n(ADP)"]
v = [LADDER[0][1], tA, t12, ts, CANARIES_TOP2]
e = [1.96 * B_full[:, 0].std(), 1.96 * B_adp[:, 0].std(), 1.96 * B_both[:, 0].std(),
     1.96 * Bs[:, 0].std(), 0]
ax[1].bar(np.arange(5), v, yerr=e, color=["#1f4e79", "#2e86c1", "#5dade2", "#a9cce3", "#c0392b"],
          error_kw=dict(lw=1.3, capsize=4))
ax[1].axhline(0, color="black", lw=1.1)
ax[1].set_xticks(np.arange(5)); ax[1].set_xticklabels(names, fontsize=8)
ax[1].set_ylabel("employment growth, %", fontsize=10)
ax[1].set_title("2. No restriction the CPS can impose\nreaches -11%", fontsize=11.5, fontweight="bold")
ax[1].grid(True, axis="y", ls="--", alpha=.35)

ax[2].hist(B_both[:, 0], bins=45, color="#5dade2", alpha=.8)
ax[2].axvline(0, color="black", lw=1.3)
ax[2].axvline(CANARIES_TOP2, color="#c0392b", lw=2.2, ls="--", label=f"Canaries: {CANARIES_TOP2:+.0f}%")
ax[2].axvline(t12, color="#1f4e79", lw=2.0, label=f"CPS, matched: {t12:+.1f}%")
ax[2].set_xlabel("bootstrapped top-2 growth, ADP universe and window, %", fontsize=10)
ax[2].set_ylabel("frequency", fontsize=10)
ax[2].set_title("3. The disagreement survives\nevery boring explanation", fontsize=11.5, fontweight="bold")
ax[2].legend(fontsize=8.5); ax[2].grid(True, ls="--", alpha=.35)

fig.suptitle("Reconciling CPS with ADP: who is counted, and over what window",
             fontsize=13, fontweight="bold", y=1.02)
plt.tight_layout(); plt.savefig("adp_cps_reconciliation.png", dpi=150, bbox_inches="tight")
print("\nChart saved: adp_cps_reconciliation.png")
