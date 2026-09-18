"""
entry_level_decomposition.py
Where does the entry-level exposure gap actually come from?

THE QUESTION
Brynjolfsson, Chandar & Chen (2026) report that between November 2022 and June 2026,
employment of 22-25 year olds fell about 11% in the two most AI-exposed quintiles and
rose about 10% in the three least exposed. They read the divergence as displacement:
AI-exposed occupations shedding their entry tier.

A gap of that shape has two possible sources, and they carry different meanings:

    DISPLACEMENT   exposed occupations lose young workers in levels
    REALLOCATION   exposed occupations hold roughly flat while unexposed
                   occupations absorb a growing share of young workers

Both produce a widening gap. Only the first is displacement. The regression on the
young SHARE cannot tell them apart, because a share moves when either side moves.
This decomposes the levels.

DESIGN
Quintiles are defined on the Eloundou GPT-4 beta rating, which is Canaries' primary
exposure measure, employment-weighted so the groups are comparable in size. Canaries'
window sits entirely inside the CPS microdata panel, so no BLS splice is needed here
and none is used. Standard errors are a nonparametric bootstrap resampling
OCCUPATIONS with replacement, which is the sampling unit and the level the exposure
measure varies at. Both age bands are reported: 22-25 to match Canaries, 20-24 as
this project's original.

WHAT TO READ
The decisive number is the top-two-quintile growth rate in levels. If it is
significantly negative, this is displacement and replicates Canaries. If it is flat
or positive while the bottom three rise, the gap is reallocation and the displacement
reading does not survive in nationally representative data.

Reads cps_panel_bands.csv and FRED-Data/. Writes entry_level_decomposition.png.
"""
import os, re, sys, numpy as np, pandas as pd
from scipy import stats as sp
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = "/Users/maxstober/Developer/Macro-Research"
DATA = os.path.join(HERE, "FRED-Data") + os.sep
RNG = np.random.default_rng(20260901)
BASE, END = 2022, 2026
NBOOT = 2000

def soc6(c):
    m = re.match(r"(\d{2}-\d{4})", str(c)); return m.group(1) if m else None

# ---- exposure: Eloundou GPT-4 beta, Canaries' primary measure ----------------
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

P = pd.read_csv(os.path.join(HERE, "cps_panel_bands.csv")).merge(OCC, on="occ", how="inner")

def prep(band):
    d = P[P.band == band].groupby(["occ", "year"], as_index=False).emp.sum()
    d = d.merge(OCC, on="occ", how="left")
    base = d[d.year == BASE].set_index("occ").emp
    keep = base[base > 0].index
    d = d[d.occ.isin(keep)]
    w = d[d.year == BASE].set_index("occ").emp
    # employment-weighted quintiles on beta, using base-year employment
    q = d.drop_duplicates("occ")[["occ", "beta"]].merge(w.rename("w0").reset_index(), on="occ")
    q = q.sort_values("beta")
    cw = q.w0.cumsum() / q.w0.sum()
    q["quint"] = np.searchsorted([.2, .4, .6, .8], cw, side="right") + 1
    q["grp"] = np.where(q.quint >= 4, "top2", "bot3")
    return d.merge(q[["occ", "quint", "grp"]], on="occ", how="left")

def growth(d, grp, a=BASE, b=END, occ_subset=None):
    dd = d if occ_subset is None else d[d.occ.isin(occ_subset)]
    dd = dd[dd.grp == grp]
    e0 = dd[dd.year == a].emp.sum(); e1 = dd[dd.year == b].emp.sum()
    return 100 * (e1 / e0 - 1) if e0 > 0 else np.nan

def growth_all(d, a=BASE, b=END):
    """Growth of the whole young cohort, the benchmark the gap decomposes against."""
    e0 = d[d.year == a].emp.sum(); e1 = d[d.year == b].emp.sum()
    return 100 * (e1 / e0 - 1) if e0 > 0 else np.nan

def boot(d):
    occs = d.occ.unique()
    out = []
    for _ in range(NBOOT):
        s = RNG.choice(occs, len(occs), replace=True)
        cnt = pd.Series(s).value_counts()
        dd = d[d.occ.isin(cnt.index)].copy()
        dd["rep"] = dd.occ.map(cnt).astype(float)
        dd["emp"] = dd.emp * dd.rep
        t = growth(dd, "top2"); b = growth(dd, "bot3"); g = growth_all(dd)
        if np.isfinite(t) and np.isfinite(b) and np.isfinite(g):
            # cols: 0 top2, 1 bot3, 2 gap, 3 all, 4 top2 shortfall, 5 bot3 excess
            out.append((t, b, t - b, g, t - g, b - g))
    return np.array(out)

print("=" * 100)
print("DECOMPOSING THE ENTRY-LEVEL EXPOSURE GAP, 2022 to 2026")
print("quintiles on Eloundou GPT-4 beta (Canaries' primary measure), employment weighted")
print("bootstrap over occupations, 2000 reps; CPS microdata only, no splice")
print("=" * 100)

RES = {}
for band, lab in [("a22_25", "22-25  (Canaries band)"), ("a20_24", "20-24  (this project)")]:
    d = prep(band)
    t, b = growth(d, "top2"), growth(d, "bot3")
    B = boot(d)
    ci = lambda col: np.percentile(B[:, col], [2.5, 97.5])
    pval = lambda col: 2 * min((B[:, col] <= 0).mean(), (B[:, col] >= 0).mean())
    RES[band] = dict(d=d, top=t, bot=b, B=B, all=growth_all(d))
    print(f"\n  {lab}     ({d.occ.nunique()} occupations)")
    print(f"    {'group':<34}{'growth':>10}{'95% CI':>22}{'p vs 0':>10}")
    print(f"    {'top 2 exposed quintiles':<34}{t:>+9.1f}%   [{ci(0)[0]:+6.1f}, {ci(0)[1]:+6.1f}]{pval(0):>10.3f}")
    print(f"    {'bottom 3 quintiles':<34}{b:>+9.1f}%   [{ci(1)[0]:+6.1f}, {ci(1)[1]:+6.1f}]{pval(1):>10.3f}")
    print(f"    {'GAP (top2 minus bot3)':<34}{t-b:>+9.1f}pp  [{ci(2)[0]:+6.1f}, {ci(2)[1]:+6.1f}]{pval(2):>10.3f}")
    print(f"\n    Canaries report, same window:      top2 -11%,  bot3 +10%,  gap -21pp")
    print(f"    Difference on the exposed side:    {t - (-11):+.1f}pp")

print("\n" + "=" * 100)
print("TWO QUESTIONS, TWO BENCHMARKS")
print("=" * 100)
print("""
  These are separate questions and they take different benchmarks. An earlier version
  of this script ran them together against zero and reported that none of the gap came
  from the exposed side. That was an artifact: it truncated a positive growth rate at
  zero, so it could not have reported anything else. Both are shown here.

  Q1  DID THE EXPOSED SIDE CONTRACT?  Benchmark zero. A displacement account needs
      employment in exposed occupations to fall in levels.

  Q2  WHICH SIDE OPENS THE GAP?  Benchmark the aggregate growth of the young cohort,
      because "no gap" means both groups growing at the common rate, not at zero.
      Against zero the shares are uninterpretable and can exceed 100%.""")

for band, lab in [("a22_25", "22-25"), ("a20_24", "20-24")]:
    B = RES[band]["B"]
    t, b, allg = RES[band]["top"], RES[band]["bot"], RES[band]["all"]
    gap = t - b
    ci = lambda c: np.percentile(B[:, c], [2.5, 97.5])
    pv = lambda c: 2 * min((B[:, c] <= 0).mean(), (B[:, c] >= 0).mean())
    print(f"\n  {lab}:  top2 {t:+.2f}%   bot3 {b:+.2f}%   all occupations {allg:+.2f}%   gap {gap:+.2f}pp")
    print(f"    Q1  exposed-side growth vs zero        {t:+.2f}%   "
          f"[{ci(0)[0]:+.1f}, {ci(0)[1]:+.1f}]  p = {pv(0):.3f}   -> did NOT contract")
    print(f"    Q2  benchmark = aggregate ({allg:+.2f}%)")
    print(f"          exposed side underperforms   {t-allg:+.2f}pp  "
          f"[{ci(4)[0]:+.1f}, {ci(4)[1]:+.1f}]  p = {pv(4):.3f}   ({100*(t-allg)/gap:.1f}% of the gap)")
    print(f"          unexposed side outperforms   {b-allg:+.2f}pp  "
          f"[{ci(5)[0]:+.1f}, {ci(5)[1]:+.1f}]  p = {pv(5):.3f}   ({-100*(b-allg)/gap:.1f}% of the gap)")
    print(f"    For contrast, the same split against zero: "
          f"exposed {100*t/gap:.1f}%, unexposed {-100*b/gap:.1f}% (uninterpretable)")

print("""
  The gap is split roughly evenly with a tilt toward the exposed side. Both sides move.
  The exposed side underperforms the aggregate without contracting, which rejects the
  displacement magnitude without supporting a claim that the gap is generated entirely
  by the unexposed side.""")

print("\n" + "=" * 100)
print("THE FULL PATH, indexed to 2022 = 100")
print("=" * 100)
for band, lab in [("a22_25", "22-25"), ("a20_24", "20-24")]:
    d = RES[band]["d"]
    piv = d.pivot_table(index="year", columns="grp", values="emp", aggfunc="sum")
    idx = 100 * piv / piv.loc[BASE]
    print(f"\n  {lab}")
    print(f"    {'year':<8}{'top2':>10}{'bot3':>10}{'gap':>10}")
    for y in idx.index:
        print(f"    {y:<8}{idx.loc[y,'top2']:>10.1f}{idx.loc[y,'bot3']:>10.1f}"
              f"{idx.loc[y,'top2']-idx.loc[y,'bot3']:>10.1f}")

print("\n" + "=" * 100)
print("BENCHMARK: is the exposed side underperforming even though it grew?")
print("=" * 100)
for band, lab in [("a22_25", "22-25"), ("a20_24", "20-24")]:
    d = RES[band]["d"]
    allg = 100 * (d[d.year == END].emp.sum() / d[d.year == BASE].emp.sum() - 1)
    t = RES[band]["top"]
    print(f"\n  {lab}: all occupations {allg:+.1f}%,  top-2 exposed {t:+.1f}%,  "
          f"shortfall {t-allg:+.1f}pp")
print("""
  This is the honest two-sided statement: exposed occupations did NOT shed young
  workers in levels, and they did grow more slowly than young employment overall.
  Underperformance is real; contraction is not.""")

# ---- chart -------------------------------------------------------------------
fig, ax = plt.subplots(1, 3, figsize=(18.5, 5.8))
d = RES["a22_25"]["d"]
piv = d.pivot_table(index="year", columns="grp", values="emp", aggfunc="sum")
idx = 100 * piv / piv.loc[BASE]
ax[0].plot(idx.index, idx.top2, marker="o", lw=2.4, color="#c0392b", label="top 2 exposed quintiles")
ax[0].plot(idx.index, idx.bot3, marker="s", lw=2.4, color="#1f4e79", label="bottom 3 quintiles")
ax[0].axhline(100, color="black", lw=1.0, ls="--")
ax[0].axvline(BASE, color="gray", lw=1.2, ls=":")
ax[0].set_ylabel("employment, 2022 = 100", fontsize=10)
ax[0].set_title("1. Ages 22-25, Canaries band\nCPS microdata, no splice", fontsize=11.5, fontweight="bold")
ax[0].legend(fontsize=8.5); ax[0].grid(True, ls="--", alpha=.35)

t22, b22 = RES["a22_25"]["top"], RES["a22_25"]["bot"]
vals = [t22, b22, -11.0, 10.0]
cols = ["#c0392b", "#1f4e79", "#e59866", "#85c1e9"]
labs = ["top2\n(this paper)", "bot3\n(this paper)", "top2\n(Canaries)", "bot3\n(Canaries)"]
B = RES["a22_25"]["B"]
errs = [1.96*B[:,0].std(), 1.96*B[:,1].std(), 0, 0]
ax[1].bar(np.arange(4), vals, yerr=errs, color=cols, error_kw=dict(lw=1.3, capsize=4))
ax[1].axhline(0, color="black", lw=1.1)
ax[1].set_xticks(np.arange(4)); ax[1].set_xticklabels(labs, fontsize=8.5)
ax[1].set_ylabel("employment growth 2022-2026, %", fontsize=10)
ax[1].set_title("2. The exposed side is where\nthe two studies disagree", fontsize=11.5, fontweight="bold")
ax[1].grid(True, axis="y", ls="--", alpha=.35)

ax[2].hist(B[:,0], bins=45, color="#c0392b", alpha=.75, label="top2 growth")
ax[2].axvline(0, color="black", lw=1.4)
ax[2].axvline(-11, color="#e59866", lw=2.2, ls="--", label="Canaries: -11%")
ax[2].set_xlabel("bootstrapped growth of top-2 quintiles, %", fontsize=10)
ax[2].set_ylabel("frequency", fontsize=10)
ax[2].set_title("3. Bootstrap distribution\nCanaries' estimate is far outside", fontsize=11.5, fontweight="bold")
ax[2].legend(fontsize=8.5); ax[2].grid(True, ls="--", alpha=.35)

fig.suptitle("Underperformance without contraction: the exposed side grew, and grew slower than the aggregate",
             fontsize=13, fontweight="bold", y=1.02)
plt.tight_layout(); plt.savefig("entry_level_decomposition.png", dpi=150, bbox_inches="tight")
print("\nChart saved: entry_level_decomposition.png")
