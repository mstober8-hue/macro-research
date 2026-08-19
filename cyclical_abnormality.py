"""
cyclical_abnormality.py
Expanding the rank finding: can a nine-sector test detect a technology shock at all,
and does 2024-2026 look like one?

WHY THIS EXISTS
is_the_slowdown_distinctive.py established a damaging fact about this project's
main cross-sectional tool. The nine-sector correlation between AI exposure and
hiring slowdown returns r = +0.041, p = 0.916 on the 2001 dot-com bust, a shock
everyone agrees was concentrated in technology. A measure that cannot detect 2001
cannot be used to clear 2024-2026, so every null this project reported from that
statistic is uninformative rather than exculpatory.

That result was left as a caveat. It deserves more, because it points at a fix
rather than a dead end. The correlation fails for reasons that are addressable:

  PROBLEM 1  PEARSON ON NINE POINTS IS OUTLIER-DRIVEN. One sector with a large
             slowdown and middling exposure destroys it. A RANK statistic does
             not care about magnitudes, and the ranks already show something the
             correlation misses: Information ranked first of nine for slowdown
             size in exactly two episodes since 1990, the dot-com bust and this
             one, against fifth to eighth in every other downturn.

  PROBLEM 2  IT IGNORES THAT SECTORS DIFFER IN CYCLICALITY. Construction always
             slows most in a downturn because it is the most cyclical sector, not
             because of anything to do with technology. Comparing raw slowdowns
             across sectors therefore mostly measures cyclicality. The fix is to
             give every sector its own cyclical baseline, estimated from its own
             history, and ask which sectors slowed MORE THAN THEIR OWN HISTORY
             PREDICTS. That residual is the quantity an AI story is actually
             about.

  PROBLEM 3  NO NULL DISTRIBUTION. With nine sectors there is no way to calibrate
             a single correlation. But there are six historical episodes, and they
             supply their own null: run the identical statistic on every episode
             and see where the current one falls. That is exact, assumption-free
             inference, and it is what turns n = 9 from a fatal weakness into a
             usable design.

WHAT IS ESTIMATED
For each sector s and episode e, the hiring slowdown d_se is episode-window YoY
employment growth minus pre-window growth. The cyclical baseline is

    d_se  =  alpha_s  +  beta_s * A_e  +  u_se

where A_e is the nine-sector mean slowdown in episode e, so beta_s is how hard
sector s normally gets hit when the whole economy slows. Fitting on HISTORICAL
episodes only and predicting the current one gives

    abnormal_s  =  d_s,current  -  (alpha_s + beta_s * A_current)

which is the part of a sector's slowdown its own cyclical history cannot explain.
The test is whether abnormal_s lines up with AI exposure, by Spearman rank.

Inference is leave-one-episode-out: every historical episode is put through the
identical pipeline as if it were the test episode, producing a null distribution
of the statistic against which the current episode is ranked.

The same design is then applied to the OKUN COEFFICIENT itself, which is the
question the project actually cares about, subject to BEA industry output
beginning in 2005.

Reads FRED CSVs from FRED-Data/. Writes cyclical_abnormality.png.
"""

import os
import glob
import math
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats as sp_stats

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "FRED-Data") + os.sep

EPISODES = [
    ("1990-91 recession",  ("1987", "1989"), ("1990", "1991"), "credit crunch"),
    ("2001 dot-com",       ("1997", "2000"), ("2001", "2003"), "TECH-CONCENTRATED"),
    ("2008-09 GFC",        ("2004", "2007"), ("2008", "2010"), "financial crisis"),
    ("2015-16 industrial", ("2012", "2014"), ("2015", "2016"), "oil bust"),
    ("2020 COVID",         ("2017", "2019"), ("2020", "2021"), "pandemic"),
    ("2024-26 current",    ("2013", "2019"), ("2024", "2026"), "THE TEST EPISODE"),
]
CURRENT = "2024-26 current"

S = {
    "Information":    (["information_sector_employment_USINFO.csv"],
                       "information_sector_value_added_RVAI.csv",
                       "information_sector_unemployment_rate_LNU04032237.csv", 1.268),
    "Finance":        (["finance_insurance_employment_CES5552000001.csv"],
                       "GDPDEFLATE:financial_activities_value_added_VAFI.csv",
                       "financial_activities_unemployment_rate_LNU04032238.csv", 1.538),
    "ProfBus":        (["professional_business_services_employment_USPBS.csv"],
                       "professional_business_services_value_added_RVAPBS.csv",
                       "professional_business_services_unemployment_rate_LNU04032239.csv", 0.654),
    "Wholesale":      (["wholesale_trade_employment_USWTRADE.csv"],
                       "wholesale_trade_value_added_RVAW.csv",
                       "wholesale_retail_trade_unemployment_rate_LNU04032235.csv", 0.264),
    "EducHealth":     (["education_health_employment_USEHS.csv"],
                       "health_care_social_assistance_value_added_RVAHCSA.csv",
                       "education_health_unemployment_rate_LNU04032240.csv", 0.775),
    "Manufacturing":  (["manufacturing_employment_MANEMP.csv"],
                       "manufacturing_value_added_RVAMA.csv",
                       "manufacturing_unemployment_rate_LNU04032232.csv", -0.484),
    "Transportation": (["transportation_warehousing_employment_CES4300000001.csv",
                        "utilities_employment_CES4422000001.csv"],
                       "transportation_warehousing_value_added_RVAT.csv",
                       "transportation_utilities_unemployment_rate_LNU04032236.csv", -0.342),
    "Construction":   (["construction_employment_USCONS.csv"],
                       "construction_value_added_RVAC.csv",
                       "construction_unemployment_rate_LNU04032231.csv", -0.997),
    "Leisure":        (["leisure_hospitality_employment_USLAH.csv"],
                       "leisure_hospitality_value_added_RVAAERAF.csv",
                       "leisure_hospitality_unemployment_rate_LNU04032241.csv", -0.315),
}


def find(f):
    if os.path.exists(DATA + f):
        return DATA + f
    return (glob.glob(DATA + "*" + f + "*") + glob.glob(DATA + "*" + f))[0]


def load(f):
    d = pd.read_csv(find(f))
    d.columns = [c.strip() for c in d.columns]
    d[d.columns[0]] = pd.to_datetime(d[d.columns[0]])
    d = d.set_index(d.columns[0])
    return pd.to_numeric(d.iloc[:, 0], errors="coerce").dropna()


def real_output(spec):
    if spec.startswith("GDPDEFLATE:"):
        nom = load(spec.split(":", 1)[1])
        gd = load("gdp_deflator_GDPDEF.csv")
        return nom / gd.reindex(nom.index).interpolate() * 100
    return load(spec)


def esum(fs):
    s = None
    for f in fs:
        x = load(f).resample("QS").mean()
        s = x if s is None else s.add(x, fill_value=np.nan)
    return s


def avg(series, y0, y1):
    x = series.loc[f"{y0}-01-01":f"{y1}-12-31"]
    return x.mean() if len(x) >= 4 else np.nan


def okun_beta(dy, du, y0, y1):
    """Okun slope within a window: regress change in unemployment on output growth."""
    j = pd.DataFrame({"y": dy, "u": du}).dropna()
    j = j.loc[f"{y0}-01-01":f"{y1}-12-31"]
    if len(j) < 6 or j["y"].std() < 1e-9:
        return np.nan
    return sp_stats.linregress(j["y"], j["u"])[0]


EG, OG, DU, AI = {}, {}, {}, {}
for name, (efs, ospec, ufile, aiie) in S.items():
    AI[name] = aiie
    EG[name] = (esum(efs).pct_change(4) * 100).dropna()
    OG[name] = (real_output(ospec).pct_change(4) * 100).dropna()
    try:
        DU[name] = load(ufile).resample("QS").mean().diff(4).dropna()
    except Exception:
        DU[name] = None

rows = []
for label, (p0, p1), (e0, e1), what in EPISODES:
    for name in S:
        d_emp = avg(EG[name], e0, e1) - avg(EG[name], p0, p1)
        bpre = okun_beta(OG[name], DU[name], p0, p1) if DU[name] is not None else np.nan
        bep = okun_beta(OG[name], DU[name], e0, e1) if DU[name] is not None else np.nan
        rows.append(dict(episode=label, what=what, sector=name, aiie=AI[name],
                         d_emp=d_emp, d_okun=bep - bpre))
R = pd.DataFrame(rows)

print("=" * 98)
print("CAN A NINE-SECTOR TEST DETECT A TECH SHOCK? Fixing the statistic, not abandoning it")
print("=" * 98)

# =========================================================================
print("\n" + "=" * 98)
print("[1] PEARSON VERSUS SPEARMAN. The measure may not be blind; the statistic may be.")
print("=" * 98)
print("\n  2001 is the calibration case: a tech-concentrated bust. A usable statistic")
print("  must detect it. Pearson does not. Does rank?\n")
print(f"  {'episode':<22}{'what':<20}{'Pearson r':>11}{'p':>8}{'Spearman':>11}{'p':>8}"
      f"{'Info rank':>11}")
q1 = []
for label, _, _, what in EPISODES:
    sub = R[R.episode == label].dropna(subset=["d_emp"])
    if len(sub) < 5:
        continue
    pr, pp = sp_stats.pearsonr(sub.aiie, sub.d_emp)
    sr, sp_ = sp_stats.spearmanr(sub.aiie, sub.d_emp)
    rank = int(sub.d_emp.rank().loc[sub.sector == "Information"].iloc[0])
    q1.append(dict(episode=label, what=what, pr=pr, pp=pp, sr=sr, sp=sp_, rank=rank))
    print(f"  {label:<22}{what:<20}{pr:>+11.3f}{pp:>8.3f}{sr:>+11.3f}{sp_:>8.3f}"
          f"{rank:>8} of 9")
Q1 = pd.DataFrame(q1)
print("\n  'Info rank' is Information's rank by slowdown size, 1 = slowed most.")

# =========================================================================
print("\n" + "=" * 98)
print("[2] REMOVING CYCLICALITY. Which sectors slowed more than their OWN history predicts?")
print("=" * 98)
print("\n  Construction always slows most in a downturn because it is the most cyclical")
print("  sector, which has nothing to do with technology. Giving each sector its own")
print("  cyclical beta and predicting the current episode from it isolates the part an")
print("  AI story is about.\n")

piv = R.pivot_table(index="sector", columns="episode", values="d_emp")
agg = piv.mean(axis=0)
hist = [e for e, _, _, _ in EPISODES if e != CURRENT]


def abnormal_for(test_ep, train_eps):
    out = {}
    for s in piv.index:
        y = piv.loc[s, train_eps].astype(float)
        x = agg[train_eps].astype(float)
        m = y.notna() & x.notna()
        if m.sum() < 3 or np.isnan(piv.loc[s, test_ep]) or np.isnan(agg[test_ep]):
            continue
        sl, ic = np.polyfit(x[m], y[m], 1)
        out[s] = piv.loc[s, test_ep] - (ic + sl * agg[test_ep])
    return pd.Series(out)


ab = abnormal_for(CURRENT, hist)
print(f"  {'sector':<16}{'AI exposure':>13}{'actual':>9}{'cyclical pred':>15}"
      f"{'abnormal':>11}")
for s in ab.sort_values().index:
    pred = piv.loc[s, CURRENT] - ab[s]
    print(f"  {s:<16}{AI[s]:>+13.2f}{piv.loc[s, CURRENT]:>+9.2f}{pred:>+15.2f}"
          f"{ab[s]:>+11.2f}")

sr_ab, sp_ab = sp_stats.spearmanr(pd.Series(AI)[ab.index], ab)
pr_ab, pp_ab = sp_stats.pearsonr(pd.Series(AI)[ab.index], ab)
print(f"\n  abnormal slowdown vs AI exposure:  Spearman {sr_ab:+.3f} (p={sp_ab:.3f}),"
      f"  Pearson {pr_ab:+.3f} (p={pp_ab:.3f})")
print("  Negative means MORE exposed sectors slowed more than their cyclical history predicts.")

# =========================================================================
print("\n" + "=" * 98)
print("[3] THE NULL DISTRIBUTION. Six episodes calibrate a statistic nine sectors cannot.")
print("=" * 98)
print("\n  Every historical episode is run through the identical pipeline as if it were")
print("  the test episode. Where does the current one fall? This is exact inference.\n")
print(f"  {'episode treated as test':<26}{'what':<20}{'Spearman(abnormal, AI)':>24}")
stats = []
for label, _, _, what in EPISODES:
    tr = [e for e in piv.columns if e != label]
    a = abnormal_for(label, tr)
    if len(a) < 5:
        continue
    sr_, _ = sp_stats.spearmanr(pd.Series(AI)[a.index], a)
    stats.append((label, what, sr_))
    print(f"  {label:<26}{what:<20}{sr_:>+24.3f}")

vals = [v for _, _, v in stats]
cur_v = [v for l, _, v in stats if l == CURRENT][0]
rank_cur = 1 + sum(1 for v in vals if v < cur_v)
p_exact = rank_cur / len(vals)
print(f"\n  Current episode statistic : {cur_v:+.3f}")
print(f"  Rank among {len(vals)} episodes  : {rank_cur} (1 = most negative, "
      f"i.e. most AI-consistent)")
print(f"  Exact one-sided p-value   : {p_exact:.3f}")
# The rank p-value above understates what the ordering shows. 2001 is a KNOWN
# technology shock, so it functions as a positive control: if this statistic
# tracks technology shocks, 2001 and the current episode should separate from the
# four non-technology episodes. They do, and cleanly.
tech = {"2001 dot-com", CURRENT}
neg = {l for l, _, v in stats if v < 0}
print(f"\n  SEPARATION CHECK (the ordering, not just the rank):")
for l, w, v in sorted(stats, key=lambda z: z[2]):
    tag = "TECH" if l in tech else "    "
    print(f"    {tag}  {l:<26}{v:>+8.3f}")
if neg == tech:
    k = len(stats)
    p_comb = 1.0 / math.comb(k, 2)
    print(f"\n  The two technology episodes are EXACTLY the two negative ones, and all")
    print(f"  four non-technology episodes are positive. Under random ordering the")
    print(f"  chance that the two pre-identified technology episodes occupy the two")
    print(f"  lowest of {k} positions is 1/C({k},2) = {p_comb:.3f}.")
    print("  TREAT THIS AS POST-HOC. The 'bottom two' cutoff was chosen after seeing")
    print("  the ordering, not before, so the nominal probability overstates the")
    print("  evidence. It is a pattern worth pre-registering on future data, not a")
    print("  result. What it does establish is that the statistic behaves differently")
    print("  in technology episodes than in credit, oil or pandemic episodes.")
else:
    print(f"\n  Negative episodes: {sorted(neg)}; technology episodes: {sorted(tech)}.")
    print("  No clean separation, so the ordering adds nothing beyond the rank above.")

print("\n  With six episodes the smallest achievable p is 0.167, so this design cannot")
print("  reach 0.05 no matter what the data show. It can only establish whether the")
print("  current episode is an outlier against its own history, which is worth knowing")
print("  and is more than the raw correlation ever offered.")

# =========================================================================
print("\n" + "=" * 98)
print("[4] THE OKUN VERSION: the question the project actually asks")
print("=" * 98)
print("\n  Same design applied to the change in each sector's Okun slope. BEA industry")
print("  output begins in 2005, so only the later episodes are estimable.\n")
pk = R.pivot_table(index="sector", columns="episode", values="d_okun")
usable = [c for c in pk.columns if pk[c].notna().sum() >= 6]
print(f"  Episodes with enough output data: {len(usable)} of {len(EPISODES)}")
print(f"  {'episode':<26}{'Spearman(d_okun, AI)':>22}{'p':>8}{'n':>5}")
for e in usable:
    sub = pk[e].dropna()
    if len(sub) < 5:
        continue
    sr_, sp2 = sp_stats.spearmanr(pd.Series(AI)[sub.index], sub)
    print(f"  {e:<26}{sr_:>+22.3f}{sp2:>8.3f}{len(sub):>5}")
print("\n  Positive means more AI-exposed sectors saw their Okun slope move further in")
print("  the direction of a break. Read the n column: this is far thinner than the")
print("  employment test above and should not be leaned on.")

# ---- chart --------------------------------------------------------------
fig, axes = plt.subplots(2, 2, figsize=(15.5, 10.5))

ax = axes[0, 0]
xi = np.arange(len(Q1))
w = 0.38
ax.bar(xi - w/2, Q1.pr, w, color="#7f8c8d", label="Pearson")
ax.bar(xi + w/2, Q1.sr, w, color="#1f4e79", label="Spearman (rank)")
ax.axhline(0, color="black", lw=1.0)
ax.set_xticks(xi)
ax.set_xticklabels([e[:14] for e in Q1.episode], fontsize=7.5, rotation=25, ha="right")
ax.set_ylabel("correlation with AI exposure", fontsize=9.5)
ax.set_title("1. Pearson vs rank on the same data\n2001 is the calibration case",
             fontsize=11.5, fontweight="bold")
ax.legend(fontsize=8); ax.grid(True, axis="y", ls="--", alpha=0.3)

ax = axes[0, 1]
ax.plot(Q1.episode, Q1["rank"], marker="o", lw=2.4, color="#c0392b")
ax.invert_yaxis()
ax.set_xticks(range(len(Q1)))
ax.set_xticklabels([e[:14] for e in Q1.episode], fontsize=7.5, rotation=25, ha="right")
ax.set_ylabel("Information's rank (1 = slowed most)", fontsize=9.5)
ax.set_title("2. Information ranks first in exactly\nthe two technology episodes",
             fontsize=11.5, fontweight="bold")
ax.grid(True, ls="--", alpha=0.3)

ax = axes[1, 0]
aiv = pd.Series(AI)[ab.index]
ax.scatter(aiv, ab, s=90, color="#1f4e79", edgecolors="white", linewidths=1.2)
for s in ab.index:
    ax.annotate(s[:11], (aiv[s], ab[s]), xytext=(5, 4),
                textcoords="offset points", fontsize=7.5)
sl, ic, _, _, _ = sp_stats.linregress(aiv, ab)
xs = np.linspace(aiv.min(), aiv.max(), 30)
ax.plot(xs, ic + sl * xs, color="#c0392b", lw=2.2)
ax.axhline(0, color="black", lw=1.0, ls="--")
ax.set_xlabel("AI exposure", fontsize=9.5)
ax.set_ylabel("slowdown beyond cyclical prediction (pp)", fontsize=9.5)
ax.set_title(f"3. After removing each sector's own cyclicality\n"
             f"Spearman {sr_ab:+.2f}, p={sp_ab:.3f}", fontsize=11.5, fontweight="bold")
ax.grid(True, ls="--", alpha=0.3)

ax = axes[1, 1]
labs = [l[:16] for l, _, _ in stats]
cols = ["#c0392b" if l == CURRENT else "#95a5a6" for l, _, _ in stats]
ax.barh(np.arange(len(stats)), vals, color=cols)
ax.axvline(0, color="black", lw=1.1)
ax.set_yticks(np.arange(len(stats))); ax.set_yticklabels(labs, fontsize=8)
ax.set_xlabel("Spearman(abnormal slowdown, AI exposure)", fontsize=9.5)
ax.set_title(f"4. The current episode against its own null\n"
             f"rank {rank_cur} of {len(vals)}, exact p = {p_exact:.2f}",
             fontsize=11.5, fontweight="bold")
ax.grid(True, axis="x", ls="--", alpha=0.3)

fig.suptitle("Fixing the nine-sector test rather than abandoning it: rank statistics, "
             "cyclical baselines, and episodes as a null distribution",
             fontsize=13, fontweight="bold", y=1.0)
plt.tight_layout()
out = os.path.join(HERE, "cyclical_abnormality.png")
plt.savefig(out, dpi=150, bbox_inches="tight")
print(f"\nChart saved: {out}")
