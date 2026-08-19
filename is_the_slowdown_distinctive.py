"""
is_the_slowdown_distinctive.py
Is the 2024-2026 hiring slowdown actually unusual, or is it what every downturn looks like?

WHY THIS EXISTS
This project argues the 2024-2026 slowdown is not AI-specific on the grounds that
eight of nine sectors slowed hiring and AI exposure does not predict which ones
(r = +0.18, p = 0.64). That argument was asserted without a benchmark. If every
downturn produces a broad, synchronized hiring slowdown that AI exposure fails to
predict, then "broad and unpredicted by AI exposure" is the normal state of the
world and says nothing either way about 2024-2026. And if AI exposure fails to
predict sector slowdowns even in a downturn that was unambiguously concentrated
in technology, then the measure simply cannot detect sector-specific technology
shocks, and its null in 2024-2026 is uninformative rather than exculpatory.

So the same analysis is re-run on every comparable episode since 1990.

THE THREE QUESTIONS

  1. IS BREADTH NORMAL? Count how many of the nine sectors slowed hiring in each
     episode. If it is eight or nine every time, breadth is not evidence.

  2. CAN THE MEASURE EVER DETECT A TECH SHOCK? The 2001 recession is the natural
     test. It was a technology-sector bust, so if AI exposure (or the
     replaceability score, which is a static occupational measure and is being
     used here purely as "how technology-adjacent is this sector's work") does
     not correlate with the 2001 slowdown either, then this class of measure
     cannot detect a concentrated technology shock and the 2024-2026 null cannot
     be read as evidence of absence.

  3. IS "OUTPUT HOLDS WHILE HIRING STOPS" NORMAL? This is the actual claim that
     makes 2024-2026 interesting. In an ordinary recession output falls
     alongside employment. If 2024-2026 is the only episode where sector output
     growth held roughly steady while hiring slowed sharply, then the
     decoupling is distinctive even if the breadth is not, and the project's
     dismissal on breadth grounds was too quick.

EPISODE DATING
Episodes are the recessions and recognized slowdowns since 1990, dated on
calendar years. The comparison window is the three calendar years before the
episode. The current episode is reported twice, because the choice matters and
should be visible: once against 2021-2023 (the uniform three-year rule, but
those years are the post-COVID reopening boom, so the measured slowdown is
inflated) and once against 2013-2019 (the window this project has used
throughout, which avoids the boom but is not the uniform rule).

DATA LIMIT
Sector employment reaches back to 1939 for most sectors and 1990 for finance, so
the employment tests cover all six episodes. BEA real value added by industry
starts in 2005, so the output and productivity tests cover only the last four.

Reads FRED-Data/. Writes is_the_slowdown_distinctive.png.
"""

import os
import glob
import warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats as sp

warnings.filterwarnings("ignore")

DATA = "FRED-Data/"

# sector: (employment files, output spec, AIIE, replaceability)
S = {
    "Information":    (["information_sector_employment_USINFO.csv"],
                       "information_sector_value_added_RVAI.csv", 1.268, 0.325),
    "Finance":        (["finance_insurance_employment_CES5552000001.csv"],
                       "GDPDEFLATE:financial_activities_value_added_VAFI.csv", 1.538, 0.267),
    "ProfBus":        (["professional_business_services_employment_USPBS.csv"],
                       "professional_business_services_value_added_RVAPBS.csv", 0.654, 0.233),
    "Wholesale":      (["wholesale_trade_employment_USWTRADE.csv"],
                       "wholesale_trade_value_added_RVAW.csv", 0.264, 0.207),
    "EducHealth":     (["education_health_employment_USEHS.csv"],
                       "health_care_social_assistance_value_added_RVAHCSA.csv", 0.775, 0.152),
    "Manufacturing":  (["manufacturing_employment_MANEMP.csv"],
                       "manufacturing_value_added_RVAMA.csv", -0.484, 0.138),
    "Transportation": (["transportation_warehousing_employment_CES4300000001.csv",
                        "utilities_employment_CES4422000001.csv"],
                       "transportation_warehousing_value_added_RVAT.csv", -0.342, 0.120),
    "Construction":   (["construction_employment_USCONS.csv"],
                       "construction_value_added_RVAC.csv", -0.997, 0.091),
    "Leisure":        (["leisure_hospitality_employment_USLAH.csv"],
                       "leisure_hospitality_value_added_RVAAERAF.csv", -0.315, 0.088),
}

# label: (pre window, episode window, what it was)
EPISODES = [
    ("1990-91 recession", ("1987", "1989"), ("1990", "1991"), "credit crunch, oil shock"),
    ("2001 dot-com",      ("1997", "2000"), ("2001", "2003"), "TECHNOLOGY-CONCENTRATED bust"),
    ("2008-09 GFC",       ("2004", "2007"), ("2008", "2010"), "financial crisis"),
    ("2015-16 industrial", ("2012", "2014"), ("2015", "2016"), "oil bust, strong dollar"),
    ("2020 COVID",        ("2017", "2019"), ("2020", "2021"), "pandemic"),
    ("2024-26 vs 2021-23", ("2021", "2023"), ("2024", "2026"), "current, uniform 3yr rule"),
    ("2024-26 vs 2013-19", ("2013", "2019"), ("2024", "2026"), "current, this project's window"),
]


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


# year-over-year growth series per sector
EG, OG, PG = {}, {}, {}
for name, (efs, ospec, _, _) in S.items():
    e = esum(efs)
    EG[name] = (e.pct_change(4) * 100).dropna()
    o = real_output(ospec)
    OG[name] = (o.pct_change(4) * 100).dropna()
    df = pd.DataFrame({"o": o, "e": e}).dropna()
    PG[name] = ((df["o"] / df["e"]).pct_change(4) * 100).dropna()


def avg(series, y0, y1):
    x = series.loc[f"{y0}-01-01":f"{y1}-12-31"]
    return x.mean() if len(x) >= 4 else np.nan


rows = []
for label, (p0, p1), (e0, e1), what in EPISODES:
    for name, (_, _, aiie, rep) in S.items():
        de = avg(EG[name], e0, e1) - avg(EG[name], p0, p1)
        do = avg(OG[name], e0, e1) - avg(OG[name], p0, p1)
        dp = avg(PG[name], e0, e1) - avg(PG[name], p0, p1)
        rows.append(dict(episode=label, what=what, sector=name, aiie=aiie, rep=rep,
                         d_emp=de, d_out=do, d_prod=dp,
                         emp_pre=avg(EG[name], p0, p1), emp_ep=avg(EG[name], e0, e1),
                         out_pre=avg(OG[name], p0, p1), out_ep=avg(OG[name], e0, e1)))
R = pd.DataFrame(rows)

print("=" * 106)
print("IS THE 2024-2026 SLOWDOWN DISTINCTIVE? The same analysis run on every episode since 1990")
print("=" * 106)

print("\n" + "-" * 106)
print("QUESTION 1  IS BREADTH NORMAL? How many of nine sectors slowed hiring, each episode")
print("-" * 106 + "\n")
print(f"{'episode':<22}{'what it was':<32}{'slowed':>8}{'mean':>9}{'spread':>9}"
      f"{'worst sector':>18}")
q1 = []
for label, _, _, what in EPISODES:
    sub = R[R.episode == label].dropna(subset=["d_emp"])
    n_slow = int((sub.d_emp < 0).sum())
    worst = sub.loc[sub.d_emp.idxmin(), "sector"]
    q1.append(dict(episode=label, n_slow=n_slow, n=len(sub), mean=sub.d_emp.mean(),
                   sd=sub.d_emp.std(), worst=worst))
    print(f"{label:<22}{what:<32}{str(n_slow) + ' of ' + str(len(sub)):>8}"
          f"{sub.d_emp.mean():>+9.2f}{sub.d_emp.std():>9.2f}{worst:>18}")
Q1 = pd.DataFrame(q1)
print(f"\n  Breadth is the norm: the median episode slowed {Q1.n_slow.median():.0f} of 9 sectors.")
print("  'Eight of nine slowed' is therefore not by itself evidence about the cause.")

print("\n" + "-" * 106)
print("QUESTION 2  CAN THIS CLASS OF MEASURE EVER DETECT A TECHNOLOGY SHOCK?")
print("-" * 106 + "\n")
print("  Correlation of each sector's hiring slowdown with its AI-exposure score, by episode.")
print("  2001 is the test case: it was a technology-concentrated bust, so a measure that")
print("  tracks technology-adjacent work should show a NEGATIVE correlation there (more")
print("  exposed sectors slowing more). If it cannot detect 2001, it cannot clear 2024-2026.\n")
print(f"{'episode':<22}{'r with AIIE':>13}{'p':>8}{'r with replace.':>17}{'p':>8}"
      f"{'Information rank':>18}")
q2 = []
for label, _, _, _ in EPISODES:
    sub = R[R.episode == label].dropna(subset=["d_emp"])
    ra, pa = sp.pearsonr(sub.aiie, sub.d_emp)
    rr, pr = sp.pearsonr(sub.rep, sub.d_emp)
    sub = sub.sort_values("d_emp")
    rank = int(sub.reset_index().index[sub.reset_index().sector == "Information"][0]) + 1
    q2.append(dict(episode=label, ra=ra, pa=pa, rr=rr, pr=pr, rank=rank))
    print(f"{label:<22}{ra:>+13.3f}{pa:>8.3f}{rr:>+17.3f}{pr:>8.3f}"
          f"{str(rank) + ' of ' + str(len(sub)):>18}")
Q2 = pd.DataFrame(q2)
d01 = Q2[Q2.episode == "2001 dot-com"].iloc[0]
print(f"\n  2001, a bust everyone agrees was concentrated in technology:")
print(f"    AIIE          r = {d01.ra:+.3f}, p = {d01.pa:.3f}")
print(f"    replaceability r = {d01.rr:+.3f}, p = {d01.pr:.3f}")
print(f"    Information ranked {int(d01['rank'])} of 9 for size of hiring slowdown")
print("  Read this before reading anything into the 2024-2026 null.")

print("\n" + "-" * 106)
print("QUESTION 3  IS 'OUTPUT HOLDS WHILE HIRING STOPS' NORMAL?")
print("-" * 106 + "\n")
print("  This is the claim that actually makes 2024-2026 interesting. In an ordinary")
print("  downturn, output falls alongside employment. Mean across the nine sectors of the")
print("  change in output growth and the change in employment growth, same windows.")
print("  Output data (BEA real value added) starts 2005, so the first two episodes drop.\n")
print(f"{'episode':<22}{'Δ output gr.':>14}{'Δ employment gr.':>18}{'wedge':>9}"
      f"{'Δ productivity':>16}")
q3 = []
for label, _, _, _ in EPISODES:
    sub = R[R.episode == label]
    if sub.d_out.notna().sum() < 5:
        print(f"{label:<22}{'(no output data before 2005)':>57}")
        continue
    do, de = sub.d_out.mean(), sub.d_emp.mean()
    q3.append(dict(episode=label, do=do, de=de, wedge=do - de, dp=sub.d_prod.mean()))
    print(f"{label:<22}{do:>+14.2f}{de:>+18.2f}{do - de:>+9.2f}{sub.d_prod.mean():>+16.2f}")
Q3 = pd.DataFrame(q3)
cur = Q3[Q3.episode == "2024-26 vs 2013-19"].iloc[0]
past = Q3[~Q3.episode.str.startswith("2024-26")]
print(f"\n  Past downturns with output data (n = {len(past)}): mean change in output growth "
      f"{past.do.mean():+.2f}pp,")
print(f"  mean change in employment growth {past.de.mean():+.2f}pp. Output fell "
      f"{'MORE' if past.do.mean() < past.de.mean() else 'LESS'} than employment.")
print(f"  2024-2026 (vs 2013-2019): output {cur.do:+.2f}pp, employment {cur.de:+.2f}pp, "
      f"wedge {cur.wedge:+.2f}pp.")
print("  A positive wedge means output held up better than hiring. Compare the wedge column.")

print("\n" + "-" * 106)
print("QUESTION 3b  Is Information's decoupling unusual FOR INFORMATION?")
print("-" * 106 + "\n")
print(f"{'episode':<22}{'INFO Δ output':>15}{'INFO Δ emp':>13}{'INFO wedge':>13}"
      f"{'vs 9-sector mean wedge':>25}")
for label, _, _, _ in EPISODES:
    sub = R[R.episode == label]
    i = sub[sub.sector == "Information"]
    if i.d_out.isna().all():
        continue
    i = i.iloc[0]
    mw = (sub.d_out - sub.d_emp).mean()
    print(f"{label:<22}{i.d_out:>+15.2f}{i.d_emp:>+13.2f}{i.d_out - i.d_emp:>+13.2f}"
          f"{(i.d_out - i.d_emp) - mw:>+25.2f}")

print("\n" + "-" * 106)
print("QUESTION 4  IS 2001 ACTUALLY A PRECEDENT FOR 2024-2026, OR ONLY A DIAGNOSTIC?")
print("-" * 106 + "\n")
print("  Question 2 uses 2001 for one purpose only: to show the nine-sector correlation")
print("  cannot detect a single-sector shock. That is a property of the test and does not")
print("  require the two episodes to resemble each other. Whether they DO resemble each")
print("  other is a separate question, and the answer is mostly no. JOLTS begins in")
print("  December 2000, so both episodes are covered on the same margins.\n")


def jolts(stem, margin):
    hits = glob.glob(os.path.join(DATA, f"jolts_{stem}_{margin}_*.csv"))
    d = pd.read_csv(hits[0])
    d.columns = [c.strip() for c in d.columns]
    d[d.columns[0]] = pd.to_datetime(d[d.columns[0]])
    d = d.set_index(d.columns[0])
    return pd.to_numeric(d.iloc[:, 0], errors="coerce").dropna()


gdp_g = (load("real_gdp_GDPC1.csv").pct_change(4) * 100).dropna()
unrate = load("unemployment_rate_UNRATE.csv")
info_e = esum(S["Information"][0])

print("  MACRO BACKDROP, which is where they differ\n")
print(f"    {'':<26}{'2001-2003':>14}{'2024-2026':>14}")
w1, w2 = ("2001-01-01", "2003-12-31"), ("2024-01-01", "2026-12-31")
print(f"    {'mean real GDP growth':<26}{gdp_g.loc[w1[0]:w1[1]].mean():>+13.2f}%"
      f"{gdp_g.loc[w2[0]:w2[1]].mean():>+13.2f}%")
print(f"    {'unemployment, low to high':<26}"
      f"{f'{unrate.loc[w1[0]:w1[1]].min():.1f} to {unrate.loc[w1[0]:w1[1]].max():.1f}%':>14}"
      f"{f'{unrate.loc[w2[0]:w2[1]].min():.1f} to {unrate.loc[w2[0]:w2[1]].max():.1f}%':>14}")
pk1 = info_e.loc["2000-06-01":"2001-06-01"].max()
tr1 = info_e.loc["2003-01-01":"2004-06-01"].min()
pk2 = info_e.loc["2022-06-01":"2023-06-01"].max()
print(f"    {'Information employment':<26}{(tr1/pk1-1)*100:>+13.1f}%{(info_e.iloc[-1]/pk2-1)*100:>+13.1f}%")
print("\n    2001 was an NBER recession with a telecom and dot-com investment collapse behind")
print("    it. 2024-2026 is an expansion. Information is shedding a tenth of its workforce")
print("    without the demand shock that explains 2001, which makes it the harder episode to")
print("    account for, not the easier one.")

print("\n  LABOR-MARKET MECHANISM INSIDE INFORMATION, which is where they are alike\n")
print(f"    {'margin':<12}{'2001':>8}{'2003':>8}{'change':>9}   |{'2019':>8}{'latest 12m':>12}{'change':>9}")
for key, margin in [("openings", "job_openings_rate"), ("hires", "hires_rate"),
                    ("layoffs", "layoffs_rate"), ("quits", "quits_rate")]:
    x = jolts("information_sector", margin)
    a1, b1 = x.loc["2001"].mean(), x.loc["2003"].mean()
    a2, b2 = x.loc["2019"].mean(), x.iloc[-12:].mean()
    print(f"    {key:<12}{a1:>8.2f}{b1:>8.2f}{(b1/a1-1)*100:>+8.0f}%   |{a2:>8.2f}{b2:>12.2f}"
          f"{(b2/a2-1)*100:>+8.0f}%")
lay = jolts("information_sector", "layoffs_rate")
print(f"\n    Layoffs, monthly means: 2001-2003 {lay.loc['2001':'2003'].mean():.2f}, "
      f"2019 {lay.loc['2019'].mean():.2f}, 2025-2026 {lay.loc['2025':'2026'].mean():.2f}")
print(f"    Peaks are essentially tied: {lay.loc['2001':'2003'].max():.2f} "
      f"(Jan 2002) against {lay.loc['2025':'2026'].max():.2f} (Jan 2026).")
jan = lay[lay.index.month == 1]
top10 = lay[lay.index.year != 2020].nlargest(10)
print(f"    These are unadjusted series and January runs high: {int((top10.index.month == 1).sum())}"
      f" of the 10 highest months on record are Januaries. Read means, not peaks.")

print("\n" + "-" * 106)
print("QUESTION 5  HOW MUCH DOES INFORMATION'S RANK ACTUALLY BUY?")
print("-" * 106 + "\n")
print("  The rank table invites an argument worth stating precisely: information sits at")
print("  5th to 8th of nine in every ORDINARY downturn and first in the only two episodes")
print("  anyone would call technology shocks. If that regularity is real, then information")
print("  ranking first is a marker of a sector-specific technology shock rather than of a")
print("  bad economy, and 2024-2026 has no bad economy to appeal to. Three things have to")
print("  hold for that argument to work, and they are tested in turn.\n")

ORD = ["1990-91 recession", "2008-09 GFC", "2015-16 industrial", "2020 COVID"]
TECH = ["2001 dot-com"]

print("  5a. IS THE REGULARITY REAL, or is 'rank' hiding a trivial difference?")
print("      Z-score of each sector's slowdown within its own episode. Negative means the")
print("      sector slowed more than the average sector that episode.\n")
print(f"      {'episode':<22}{'kind':<12}{'INFO z':>9}{'rank':>10}{'gap to 2nd worst':>19}")
zrows = []
for label, _, _, _ in EPISODES:
    sub = R[R.episode == label].dropna(subset=["d_emp"]).sort_values("d_emp")
    z = (sub.d_emp - sub.d_emp.mean()) / sub.d_emp.std()
    iz = float(z[sub.sector == "Information"].iloc[0])
    rank = int(np.where(sub.sector.values == "Information")[0][0]) + 1
    gap = (sub.d_emp.iloc[1] - sub.d_emp.iloc[0]) if rank == 1 else np.nan
    kind = "ordinary" if label in ORD else ("TECH" if label in TECH else "current")
    zrows.append(dict(episode=label, kind=kind, z=iz, rank=rank))
    print(f"      {label:<22}{kind:<12}{iz:>+9.2f}{str(rank) + ' of ' + str(len(sub)):>10}"
          f"{('%+.2fpp' % gap) if rank == 1 else '':>19}")
Z = pd.DataFrame(zrows)
zo = Z[Z.kind == "ordinary"].z
t, p = sp.ttest_1samp(zo, 0)
print(f"\n      Ordinary downturns (n = {len(zo)}): information's mean z = {zo.mean():+.2f}, "
      f"t = {t:+.2f}, p = {p:.3f}")
print(f"      Information is significantly MORE resilient than the average sector in an")
print(f"      ordinary downturn. The four z-scores sit in a tight band ({zo.min():+.2f} to "
      f"{zo.max():+.2f}),")
print(f"      which is what drives the small p despite n = 4; a tight band with four points")
print(f"      is still four points, so treat this as a clear regularity on thin evidence.")
print(f"      Under random ranking, landing in the bottom half all four times has "
      f"p = {(5/9)**4:.3f}.")
zc = float(Z[Z.episode == "2024-26 vs 2013-19"].z.iloc[0])
print(f"      In 2024-2026 information's z is {zc:+.2f}, a swing of {zo.mean() - zc:.2f} standard")
print(f"      deviations away from its own normal-downturn behaviour.")

print("\n  5b. IS 2024-2026 BIGGER THAN INFORMATION'S OWN CYCLICAL SENSITIVITY PREDICTS?")
print("      Rank is ordinal and throws away magnitude. Fit each sector's slowdown against")
print("      the average sector's slowdown across the ORDINARY downturns only, which gives")
print("      that sector's cyclical beta, then ask what 2024-2026 should have looked like.\n")
means = {lab: R[R.episode == lab].d_emp.mean() for lab, _, _, _ in EPISODES}
print(f"      {'sector':<16}{'cyclical beta':>15}{'predicted':>11}{'actual':>9}{'residual':>10}")
res = []
for name in S:
    pts = [(means[lab], R[(R.episode == lab) & (R.sector == name)].d_emp.iloc[0]) for lab in ORD]
    pts = [(x, y) for x, y in pts if np.isfinite(y)]
    if len(pts) < 4:
        continue
    xs, ys = zip(*pts)
    b, a, r_, p_, _ = sp.linregress(xs, ys)
    lab = "2024-26 vs 2013-19"
    act = R[(R.episode == lab) & (R.sector == name)].d_emp.iloc[0]
    pred = a + b * means[lab]
    res.append(dict(sector=name, beta=b, pred=pred, act=act, resid=act - pred))
RES = pd.DataFrame(res).sort_values("resid")
for _, x in RES.iterrows():
    star = "   <-" if x.sector == "Information" else ""
    print(f"      {x.sector:<16}{x.beta:>+15.2f}{x.pred:>+11.2f}{x.act:>+9.2f}{x.resid:>+10.2f}{star}")
inf = RES[RES.sector == "Information"].iloc[0]
print(f"\n      Information's cyclical beta is {inf.beta:+.2f}: it normally moves "
      f"{'LESS' if abs(inf.beta) < 1 else 'MORE'} than the average")
print(f"      sector in a downturn. Given how mild 2024-2026 is by the nine-sector average")
print(f"      ({means['2024-26 vs 2013-19']:+.2f}pp), it was predicted at {inf.pred:+.2f}pp "
      f"and came in at {inf.act:+.2f}pp,")
print(f"      a residual of {inf.resid:+.2f}pp, the {'largest' if RES.iloc[0].sector == 'Information' else 'not the largest'} "
      f"negative miss of the nine.")
print(f"      CAVEAT: four episodes and two parameters. This is indicative, not inference.")

print("\n  5c. THE DISCRIMINATOR: did OUTPUT fall too? This is what separates the two")
print("      rank-first episodes, and it is the whole AI question.\n")
ni = load("information_sector_nominal_gdp_annual_USINFONGSP.csv")
na = load("all_industry_nominal_gdp_annual_USNGSP.csv")
gd = load("gdp_deflator_GDPDEF.csv").resample("YS").mean()
real_i = (ni / gd.reindex(ni.index).interpolate() * 100)
gi = (real_i.pct_change() * 100).dropna()
share = (ni / na * 100)
emp_a = info_e.resample("YS").mean()
prod = (real_i / emp_a.reindex(real_i.index)).pct_change() * 100

print(f"      {'window':<26}{'real output':>13}{'employment':>12}{'productivity':>14}{'share of GDP':>14}")
for lab, a_, b_ in [("1997-2000 (pre-bust)", "1997", "2000"), ("2001-2003 (dot-com)", "2001", "2003"),
                    ("2013-2019 (pre-AI)", "2013", "2019"), ("2024-2025 (current)", "2024", "2025")]:
    eg = (emp_a.pct_change() * 100).loc[f"{a_}-01-01":f"{b_}-12-31"].mean()
    print(f"      {lab:<26}{gi.loc[f'{a_}-01-01':f'{b_}-12-31'].mean():>+12.2f}%{eg:>+11.2f}%"
          f"{prod.loc[f'{a_}-01-01':f'{b_}-12-31'].mean():>+13.2f}%"
          f"{share.loc[f'{a_}-01-01':f'{b_}-12-31'].mean():>13.2f}%")
print("\n      READ THIS BEFORE THE TABLE. The dot-com bust shows the SAME shape: output kept")
print("      growing (+4.26%/yr) while employment fell (-4.19%/yr), giving a productivity")
print("      surge of +8.93%/yr, LARGER than the current +6.48%. 'Output holds while tech")
print("      jobs fall' is therefore not a new phenomenon and not a signature unique to AI.")
print("      This was the hypothesis that would have separated the two episodes, and it fails.")

# validation: this annual series is not BEA real value added, so check it tracks
bea = load("information_sector_value_added_RVAI.csv").resample("YS").mean()
jj = pd.DataFrame({"a": gi, "b": (bea.pct_change() * 100)}).dropna()
rv, pv = sp.pearsonr(jj["a"], jj["b"])
print(f"\n      Series validation. Nominal Information GDP (state accounts) deflated by the")
print(f"      economy-wide GDP deflator, because that is the only consistent series back to")
print(f"      1997. Against BEA real value added where they overlap ({jj.index[0].year}-"
      f"{jj.index[-1].year}, n = {len(jj)}), annual")
print(f"      growth rates correlate r = {rv:+.3f} (p = {pv:.4f}), but the levels differ a lot:")
print(f"      {jj['a'].mean():+.2f}%/yr here against {jj['b'].mean():+.2f}%/yr on BEA real. "
      f"Information's own deflator")
print(f"      falls, so this understates real growth by roughly {jj['b'].mean()-jj['a'].mean():.1f}pp/yr "
      f"in EVERY period shown.")
print(f"      Use these rows to compare periods with each other, not as levels.")

print("\n  5d. THE OVERHANG TEST, which is where the two episodes really do match")
print("      If tech hires faster than its output supports, productivity growth sags, and the")
print("      correction that follows shows up as a productivity spike. Check both episodes\n")
emp_y = info_e.resample("YS").mean()
eg_y = emp_y.pct_change() * 100
prod_y = (real_i / emp_y.reindex(real_i.index)).pct_change() * 100
print(f"      {'window':<28}{'real output':>13}{'employment':>12}{'productivity':>14}")
for lab, x_, y_ in [("1997-2000 boom", "1997", "2000"), ("2001-2003 bust", "2001", "2003"),
                    ("2013-2019 pre-AI norm", "2013", "2019"),
                    ("2020-2022 pandemic boom", "2020", "2022"),
                    ("2023-2025 correction", "2023", "2025")]:
    s_, e_ = f"{x_}-01-01", f"{y_}-12-31"
    print(f"      {lab:<28}{gi.loc[s_:e_].mean():>+12.2f}%{eg_y.loc[s_:e_].mean():>+11.2f}%"
          f"{prod_y.loc[s_:e_].mean():>+13.2f}%")
norm = prod_y.loc["2013-01-01":"2019-12-31"].mean()
print(f"\n      Both corrections are preceded by a hiring boom that outran output. Before the")
print(f"      dot-com bust, productivity growth was {prod_y.loc['1997-01-01':'2000-12-31'].mean():+.2f}%/yr. "
      f"Before this one it was")
print(f"      {prod_y.loc['2020-01-01':'2022-12-31'].mean():+.2f}%/yr, against a 2013-2019 norm of {norm:+.2f}%/yr.")
print(f"      Then both give it back: {prod_y.loc['2001-01-01':'2003-12-31'].mean():+.2f}%/yr "
      f"and {prod_y.loc['2023-01-01':'2025-12-31'].mean():+.2f}%/yr.")
print(f"      An overhang that built up and is now unwinding accounts for the current episode")
print(f"      without invoking AI at all, and it has an exact precedent. That does not prove")
print(f"      AI is absent; it means this evidence cannot separate the two.")

print("\n" + "-" * 106)
print("QUESTION 6  IS THE OVERHANG ACCOUNT ACTUALLY SUFFICIENT? Test when it runs out.")
print("-" * 106 + "\n")
print("  Question 5d showed the overhang pattern matches the dot-com episode in shape. But")
print("  shape is not size. An overhang explanation has a hard implication: unwinding an")
print("  excess of +X% returns the sector TO its trend, not far below it. So date the")
print("  crossing. Fit log employment on 2010-2019, extrapolate, and read the deviation.\n")
tr = info_e.loc["2010-01-01":"2019-12-31"]
tt = np.arange(len(tr))
bb, aa, _, _, _ = sp.linregress(tt, np.log(tr.values))
seg = info_e.loc["2010-01-01":]
DEV = pd.Series((seg.values / np.exp(aa + bb * np.arange(len(seg))) - 1) * 100, index=seg.index)
print(f"      {'date':<12}{'deviation from 2010-2019 trend':>32}")
for dt in ["2019-10-01", "2022-10-01", "2023-10-01", "2024-10-01", "2025-10-01"]:
    print(f"      {dt[:7]:<12}{DEV.asof(pd.Timestamp(dt)):>+31.1f}%")
print(f"      {'latest':<12}{DEV.iloc[-1]:>+31.1f}%")
peak = DEV.loc["2022-01-01":"2023-06-30"].max()
print(f"\n      Peak overhang {peak:+.1f}%. Back to trend by late 2023 "
      f"({DEV.asof(pd.Timestamp('2023-10-01')):+.1f}%).")
print(f"      Then it keeps going: {DEV.iloc[-1]:+.1f}% now, {DEV.iloc[-1]:.1f}pp past a completed")
print("      correction. The pandemic overhang was fully worked off BEFORE the 2024-2026")
print("      decline happened, so it cannot be what is driving that decline.")

d0 = info_e.loc["1990-01-01":"2000-12-31"]
t0 = np.arange(len(d0))
b0, a0, _, _, _ = sp.linregress(t0, np.log(d0.values))
s0 = info_e.loc["1990-01-01":"2005-12-31"]
D0 = pd.Series((s0.values / np.exp(a0 + b0 * np.arange(len(s0))) - 1) * 100, index=s0.index)
print("\n      BUT BENCHMARK THE METHOD BEFORE TRUSTING THE NUMBER. Same procedure on the")
print("      dot-com episode, fitting 1990-2000 and extrapolating:\n")
for dt in ["2000-10-01", "2002-10-01", "2003-10-01", "2005-10-01"]:
    print(f"      {dt[:7]:<12}{D0.asof(pd.Timestamp(dt)):>+31.1f}%")
print(f"\n      It reaches {D0.min():+.1f}% by {D0.idxmin().date()}, which plainly does not mean a quarter")
print("      of tech jobs were displaced. Extrapolating a prior decade's trend forever inflates")
print("      the gap whenever structural growth slows, and 1990s Information growth was")
print("      never going to continue. The LEVEL of the deviation is not trustworthy.")
print("\n      What survives is the TIMING, which does not depend on extrapolating far: the")
print("      excess relative to the 2010s trend was gone by late 2023, and employment fell")
print("      for another two years after that. The overhang account explains 2022-2023 and")
print("      runs out exactly where the period of interest begins. It does not follow that")
print("      AI explains the remainder, only that the overhang does not.")

# ---- chart -------------------------------------------------------------------
fig, axes = plt.subplots(1, 3, figsize=(19, 6.3))
CUR = "2024-26 vs 2013-19"

ax = axes[0]
c = ["#c0392b" if e.startswith("2024-26") else "#1f4e79" for e in Q1.episode]
ax.barh(np.arange(len(Q1)), Q1.n_slow, color=c)
ax.axvline(8, color="black", ls="--", lw=1.5)
ax.set_yticks(np.arange(len(Q1)))
ax.set_yticklabels(Q1.episode, fontsize=8.5)
ax.set_xlabel("sectors that slowed hiring, of 9", fontsize=10)
ax.set_title("1. Breadth is normal\nEvery downturn slows almost every sector",
             fontsize=11.5, fontweight="bold")
ax.grid(True, axis="x", ls="--", alpha=0.35)

ax = axes[1]
x = np.arange(len(Q2)); w = 0.38
ax.bar(x - w/2, Q2.ra, w, label="AIIE", color="#1f4e79")
ax.bar(x + w/2, Q2.rr, w, label="replaceability", color="#c0392b")
ax.axhline(0, color="black", lw=1.1)
for c_ in (-0.666, 0.666):
    ax.axhline(c_, color="darkgreen", ls="--", lw=1.2)
ax.set_xticks(x)
ax.set_xticklabels([e.replace(" vs ", "\nvs ") for e in Q2.episode], fontsize=7.5, rotation=30,
                   ha="right")
ax.set_ylabel("corr(hiring slowdown, AI exposure)", fontsize=10)
ax.set_title("2. Can the measure detect a tech shock?\n2001 is the test. Green lines = p<.05 at n=9",
             fontsize=11.5, fontweight="bold")
ax.legend(fontsize=8.5); ax.grid(True, axis="y", ls="--", alpha=0.35)

ax = axes[2]
ax.axhline(0, color="black", lw=1.0); ax.axvline(0, color="black", lw=1.0)
for _, r in Q3.iterrows():
    col = "#c0392b" if r.episode.startswith("2024-26") else "#1f4e79"
    ax.scatter(r.de, r.do, s=170, color=col, edgecolors="white", linewidths=1.4, zorder=3)
    ax.annotate(r.episode, (r.de, r.do), xytext=(8, 4), textcoords="offset points", fontsize=8.5)
lim = [min(Q3.de.min(), Q3.do.min()) - 1, max(Q3.de.max(), Q3.do.max()) + 1]
ax.plot(lim, lim, ls="--", color="gray", lw=1.4)
ax.text(0.04, 0.94, "above the diagonal =\noutput held up better than hiring",
        transform=ax.transAxes, fontsize=8.5, va="top", color="#7b241c")
ax.set_xlim(lim); ax.set_ylim(lim)
ax.set_xlabel("change in mean sector employment growth (pp)", fontsize=10)
ax.set_ylabel("change in mean sector output growth (pp)", fontsize=10)
ax.set_title("3. Output holds while hiring stops?\nDistance above the diagonal is the wedge",
             fontsize=11.5, fontweight="bold")
ax.grid(True, ls="--", alpha=0.35)

fig.suptitle("Benchmarking the 2024-2026 slowdown against every episode since 1990",
             fontsize=13, fontweight="bold", y=1.02)
plt.tight_layout()
plt.savefig("is_the_slowdown_distinctive.png", dpi=150, bbox_inches="tight")
print("\nChart saved: is_the_slowdown_distinctive.png")
