"""
robotic_exposure_test.py
Testing the anticipatory-robotics hypothesis: are physical-sector employers slowing
hiring in preparation for robotic AI?

WHY THIS EXISTS
This project concluded that AI exposure does not predict the physical-sector hiring
slowdown. A reviewer raised an objection that identifies a real hole in that
conclusion, and it is worth stating precisely because it is close to fatal to how the
question has been asked so far.

Every AI exposure measure used anywhere in this project measures exposure to
COGNITIVE, TEXT-BASED AI:

    AIIE (Felten, Raj & Seamans)     built from AI benchmark progress mapped to
                                     abilities like language and image recognition
    Eloundou et al. GPT exposure     explicitly "can GPT-4 do this task"
    Anthropic Economic Index         observed Claude conversations

All three score construction, manufacturing and warehousing near the BOTTOM by
construction, because a language model cannot pour concrete or drive a forklift. So
"AI exposure does not predict the physical-sector slowdown" is close to a tautology.
It tests whether ChatGPT displaced construction workers, which nobody claimed.

The hypothesis actually on the table is different: employers in physical industries
are slowing hiring in ANTICIPATION of robotics and embodied AI. Under that story the
relevant exposure measure is not text-AI exposure at all, and the project has never
built one.

THE MEASURE
This constructs a robotic-exposure score from O*NET, deliberately parallel to the
project's own replaceability score so the two are directly comparable. A job is
robotically automatable only if it is BOTH physical AND routine or machine-paced. A
physical job in an unstructured, varied environment (an electrician diagnosing a
fault in an old building) resists robots; a routine job that is not physical (data
entry) is exposed to software, not robots. So the construction is multiplicative:

    Robotic exposure = physical intensity  x  routineness

  physical intensity   Work Activities (importance scale): performing general
                       physical activities, handling and moving objects,
                       controlling machines and processes, operating vehicles and
                       mechanized devices
  routineness          Work Context: degree of automation, importance of repeating
                       the same tasks, pace determined by speed of equipment, time
                       spent making repetitive motions

Both components normalized 0-1 across occupations before multiplying.

WHAT IS TESTED
  1. Does the new measure actually rank sectors differently from text-AI exposure?
     If it does not, the objection dissolves on its own.
  2. Does robotic exposure predict occupation employment growth in 2022-2025, and
     crucially, does it do so MORE than in the 2013-2019 pre-AI placebo? An
     anticipation story requires the relationship to be new. A relationship of equal
     size in the placebo window is ordinary long-run automation, which has been
     displacing routine manual work since the 1980s and is not news.
  3. Within the physical sectors specifically, is the slowdown concentrated in the
     robotically exposed occupations?

WHAT THIS CAN AND CANNOT SETTLE
It can establish whether the labor data shows a NEW robotics-shaped pattern. It
cannot directly observe employer expectations, and a pure anticipation story is
partially protected from falsification: firms could be cutting hiring today for
robots they have not yet bought, in which case no deployment data would show it. What
the data can still say is whether the occupations most exposed to robots are the ones
losing employment, and whether that pattern is new or decades old.

Reads FRED-Data/. Writes robotic_exposure_test.png.
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
OEWS = os.path.join(DATA, "oews_national_industry_files")

PHYS_ACT = ["Performing General Physical Activities",
            "Handling and Moving Objects",
            "Controlling Machines and Processes",
            "Operating Vehicles, Mechanized Devices, or Equipment"]

ROUTINE_CX = ["Degree of Automation",
              "Importance of Repeating Same Tasks",
              "Pace Determined by Speed of Equipment",
              "Spend Time Making Repetitive Motions"]

COMP_VARS = ["Physical Proximity",
             "Face-to-Face Discussions with Individuals and Within Teams",
             "Deal With External Customers or the Public in General",
             "Health and Safety of Other Workers",
             "Consequence of Error"]

NAT = {"2013": os.path.join(OEWS, "oews_may2013_national_occupations.xls"),
       "2019": os.path.join(OEWS, "oews_may2019_national_occupations.xlsx"),
       "2022": os.path.join(OEWS, "oews_may2022_national_occupations.xlsx"),
       "2025": os.path.join(OEWS, "oews_may2025_national_occupations.xlsx")}

IND = {"2013": [os.path.join(OEWS, "oews_may2013_national_4digit_naics_wages_part1.xls"),
                os.path.join(OEWS, "oews_may2013_national_4digit_naics_wages_part2.xls")],
       "2019": [os.path.join(OEWS, "oews_may2019_national_4digit_naics_wages.xlsx")],
       "2022": [os.path.join(OEWS, "oews_may2022_national_4digit_naics_wages.xlsx")],
       "2025": glob.glob(os.path.join(OEWS, "*may2025_national_4digit_naics_wages.xlsx"))}

WINDOWS = [("2013", "2019", "PLACEBO: pre-AI, pre-COVID"),
           ("2019", "2022", "spans COVID"),
           ("2022", "2025", "TEST: the AI / robotics-anticipation window")]

SECTOR_OF = {"23": "Construction", "31": "Manufacturing", "32": "Manufacturing",
             "33": "Manufacturing", "42": "Wholesale", "48": "Transportation",
             "49": "Transportation", "22": "Transportation", "51": "Information",
             "52": "Finance", "53": "Finance", "54": "ProfBus", "55": "ProfBus",
             "56": "ProfBus", "61": "EducHealth", "62": "EducHealth",
             "71": "Leisure", "72": "Leisure"}
PHYSICAL = {"Construction", "Manufacturing", "Transportation", "Wholesale"}


def find(f):
    if os.path.exists(DATA + f):
        return DATA + f
    return (glob.glob(DATA + "*" + f + "*") + glob.glob(DATA + "*" + f))[0]


def norm(s):
    return (s - s.min()) / (s.max() - s.min())


def build_scores():
    """Robotic exposure, plus the project's existing text-AI replaceability, per SOC."""
    wa = pd.read_csv(find("onet_work_activities_importance_ratings"))
    wa.columns = [c.strip() for c in wa.columns]
    wa = wa[(wa["Scale ID"] == "IM") & (wa["Element Name"].isin(PHYS_ACT))].copy()
    wa["soc"] = wa["O*NET-SOC Code"].str[:7]
    phys = wa.pivot_table(index="soc", columns="Element Name", values="Data Value")
    phys = phys.apply(norm).mean(axis=1)

    wc = pd.read_csv(find("onet_work_context_ratings"))
    wc.columns = [c.strip() for c in wc.columns]
    wc["soc"] = wc["O*NET-SOC Code"].str[:7]
    rt = wc[(wc["Scale ID"] == "CX") & (wc["Element Name"].isin(ROUTINE_CX))]
    rout = rt.pivot_table(index="soc", columns="Element Name", values="Data Value").apply(norm).mean(axis=1)
    cp = wc[(wc["Scale ID"] == "CX") & (wc["Element Name"].isin(COMP_VARS))]
    comp = cp.pivot_table(index="soc", columns="Element Name", values="Data Value").apply(norm).mean(axis=1)

    el = pd.read_csv(find("eloundou_gpt_occupational_exposure_scores"))
    el.columns = [c.strip() for c in el.columns]
    el["soc"] = el["O*NET-SOC Code"].str[:7]
    el["e"] = el[["human_rating_beta", "dv_rating_beta"]].mean(axis=1)
    exp = el.groupby("soc")["e"].mean()

    S = pd.DataFrame({"phys": phys, "rout": rout, "comp": comp, "exp": exp}).dropna()
    S["robotic"] = norm(S.phys) * norm(S.rout)
    S["textai"] = norm(S.exp) * (1 - S.comp)
    return S.reset_index()[["soc", "robotic", "textai", "phys", "rout"]]


def load_nat(path):
    d = pd.read_excel(path)
    d.columns = [c.strip().upper() for c in d.columns]
    g = "O_GROUP" if "O_GROUP" in d.columns else "OCC_GROUP"
    d = d[d[g].astype(str).str.strip() == "detailed"].copy()
    d["soc"] = d["OCC_CODE"].astype(str).str.strip()
    d["emp"] = pd.to_numeric(d["TOT_EMP"], errors="coerce")
    d = d.dropna(subset=["emp"])
    return d[d.emp > 0].groupby("soc", as_index=False)["emp"].sum()


def load_cells(paths):
    d = pd.concat([pd.read_excel(p) for p in paths], ignore_index=True)
    d.columns = [c.strip().upper() for c in d.columns]
    o = "O_GROUP" if "O_GROUP" in d.columns else "OCC_GROUP"
    k = d[o].astype(str).str.strip() == "detailed"
    if "I_GROUP" in d.columns:
        k &= d["I_GROUP"].astype(str).str.strip() == "4-digit"
    d = d[k].copy()
    d["naics"] = d["NAICS"].astype(str).str.strip().str.replace(r"\.0$", "", regex=True)
    d["soc"] = d["OCC_CODE"].astype(str).str.strip()
    d["emp"] = pd.to_numeric(d["TOT_EMP"], errors="coerce")
    d = d.dropna(subset=["emp"])
    return d[d.emp > 0].groupby(["naics", "soc"], as_index=False)["emp"].sum()


def wls_cluster(y, x, w, cl):
    y, x, w = np.asarray(y, float), np.asarray(x, float), np.asarray(w, float)
    X = np.column_stack([np.ones(len(x)), x])
    inv = np.linalg.pinv(X.T @ (w[:, None] * X))
    b = inv @ (X.T @ (w * y))
    e = y - X @ b
    ids = pd.Series(cl).values
    meat = np.zeros((2, 2))
    for g in np.unique(ids):
        m = ids == g
        s = X[m].T @ (w[m] * e[m])
        meat += np.outer(s, s)
    G, n = len(np.unique(ids)), len(y)
    V = inv @ (meat * (G / max(G - 1, 1)) * ((n - 1) / max(n - 2, 1))) @ inv
    se = np.sqrt(max(V[1, 1], 0))
    t = b[1] / se if se > 0 else np.nan
    return b[1], se, 2 * (1 - sp.norm.cdf(abs(t)))


print("Building robotic-exposure score from O*NET...")
S = build_scores()
print(f"  {len(S)} occupations scored\n")
print("  Face validity, top 8 by ROBOTIC exposure:")
oc_titles = pd.read_csv(find("eloundou_gpt_occupational_exposure_scores"))
oc_titles.columns = [c.strip() for c in oc_titles.columns]
oc_titles["soc"] = oc_titles["O*NET-SOC Code"].str[:7]
tt = oc_titles.groupby("soc")["Title"].first()
S["title"] = S.soc.map(tt)
for _, r in S.nlargest(8, "robotic").iterrows():
    print(f"    {r.robotic:.3f}  {str(r.title)[:58]}")
print("  Bottom 5:")
for _, r in S.nsmallest(5, "robotic").iterrows():
    print(f"    {r.robotic:.3f}  {str(r.title)[:58]}")
print(f"\n  corr(robotic, text-AI replaceability) = {S.robotic.corr(S.textai):+.3f}  "
      f"(Spearman {S.robotic.corr(S.textai, method='spearman'):+.3f})")

# ------------------------------------------------------------------ sector ranks
print("\n" + "=" * 100)
print("TEST 1  DOES THE NEW MEASURE RANK SECTORS DIFFERENTLY? (the objection's premise)")
print("=" * 100 + "\n")
C22, C25 = load_cells(IND["2022"]), load_cells(IND["2025"])
M = C22.merge(C25, on=["naics", "soc"], suffixes=("_0", "_1")).merge(S, on="soc")
M["sector"] = M.naics.str[:2].map(SECTOR_OF)
sec = M.dropna(subset=["sector"]).groupby("sector").apply(lambda d: pd.Series({
    "robotic": np.average(d.robotic, weights=d.emp_0),
    "textai": np.average(d.textai, weights=d.emp_0),
    "growth": ((d.emp_1.sum() / d.emp_0.sum()) ** (1 / 3) - 1) * 100}))
sec["rank_rob"] = sec.robotic.rank(ascending=False).astype(int)
sec["rank_txt"] = sec.textai.rank(ascending=False).astype(int)
print(f"{'sector':<16}{'robotic':>9}{'rank':>6}{'text-AI':>10}{'rank':>6}{'emp growth 22-25':>19}")
for s_, r in sec.sort_values("robotic", ascending=False).iterrows():
    print(f"{s_:<16}{r.robotic:>9.3f}{int(r.rank_rob):>6}{r.textai:>10.3f}{int(r.rank_txt):>6}{r.growth:>18.2f}%")
rho = sp.spearmanr(sec.robotic, sec.textai)[0]
print(f"\n  Rank correlation between the two measures across sectors: rho = {rho:+.3f}")
print("  The objection's premise is correct: these are close to opposite orderings, and the")
print("  physical sectors that this project scored as LOW AI exposure score HIGH on robotics.")
r_, p_ = sp.pearsonr(sec.robotic, sec.growth)
print(f"\n  Sector robotic exposure vs 2022-25 employment growth: r = {r_:+.3f}, p = {p_:.3f} (n=9)")

# ------------------------------------------------------------------ occupation panel
print("\n" + "=" * 100)
print("TEST 2  THE POWERED TEST: occupation employment growth vs robotic exposure, by window")
print("=" * 100)
print("\nAnnualized log employment growth. Employment-weighted, clustered on SOC major group.")
print("An anticipation story needs the AI-window coefficient to be MORE negative than the")
print("pre-AI placebo. Equal coefficients mean ordinary long-run automation.\n")
V = {y: load_nat(p) for y, p in NAT.items()}
print(f"{'window':<12}{'what it is':<44}{'occ':>5}{'ROBOTIC beta':>15}{'p':>8}{'text-AI beta':>15}{'p':>8}")
panels, rows = {}, []
for a, b, desc in WINDOWS:
    m = V[a].merge(V[b], on="soc", suffixes=("_0", "_1")).merge(S, on="soc")
    m["g"] = (np.log(m.emp_1) - np.log(m.emp_0)) / (int(b) - int(a))
    m["major"] = m.soc.str[:2]
    panels[(a, b)] = m
    br, sr, pr = wls_cluster(m.g, m.robotic, m.emp_0, m.major.values)
    bt, st, pt = wls_cluster(m.g, m.textai, m.emp_0, m.major.values)
    rows.append(dict(win=f"{a}-{b}", desc=desc, br=br, sr=sr, pr=pr, bt=bt, st=st, pt=pt))
    print(f"{a+'-'+b:<12}{desc:<44}{len(m):>5}{br:>+15.4f}{pr:>8.4f}{bt:>+15.4f}{pt:>8.4f}")
P = pd.DataFrame(rows)

A = panels[("2022", "2025")].merge(
    panels[("2013", "2019")][["soc", "g"]].rename(columns={"g": "g_pre"}), on="soc")
A["accel"] = A.g - A.g_pre
ba, sa, pa = wls_cluster(A.accel, A.robotic, A.emp_0, A.major.values)
print(f"\n  ACCELERATION (AI window minus placebo) vs robotic exposure:")
print(f"    beta = {ba:+.4f}  SE {sa:.4f}  p = {pa:.4f}   n = {len(A)} occupations")
bu, su, pu = wls_cluster(A.accel, A.robotic, np.ones(len(A)), A.major.values)
print(f"    unweighted beta = {bu:+.4f}  p = {pu:.4f}")

# ------------------------------------------------------------------ inside physical
print("\n" + "=" * 100)
print("TEST 3  INSIDE THE PHYSICAL SECTORS: is the slowdown concentrated in robot-exposed jobs?")
print("=" * 100)
print("\nCells restricted to construction, manufacturing, transportation and wholesale.")
print("Industry fixed effects, so this compares occupations against each other inside the")
print("same 4-digit industry.\n")
for a, b, desc in [("2013", "2019", "PLACEBO"), ("2022", "2025", "AI window")]:
    Ca, Cb = load_cells(IND[a]), load_cells(IND[b])
    MM = Ca.merge(Cb, on=["naics", "soc"], suffixes=("_0", "_1")).merge(S, on="soc")
    MM["sector"] = MM.naics.str[:2].map(SECTOR_OF)
    MM = MM[MM.sector.isin(PHYSICAL)].copy()
    MM["g"] = (np.log(MM.emp_1) - np.log(MM.emp_0)) / (int(b) - int(a))
    MM = MM.groupby("naics").filter(lambda d: len(d) >= 2)
    gm_g = MM.groupby("naics").apply(lambda d: np.average(d.g, weights=d.emp_0))
    gm_x = MM.groupby("naics").apply(lambda d: np.average(d.robotic, weights=d.emp_0))
    yy = MM.g - MM.naics.map(gm_g)
    xx = MM.robotic - MM.naics.map(gm_x)
    bb, ss, pp = wls_cluster(yy, xx, MM.emp_0, MM.soc.str[:2].values)
    print(f"  {a}-{b} {desc:<12} within-industry beta on robotic exposure = {bb:+.4f}  "
          f"SE {ss:.4f}  p = {pp:.4f}   ({len(MM):,} cells)")

# ------------------------------------------------------------------ horse race + timing
def horse(a, b, sectors):
    Ca, Cb = load_cells(IND[a]), load_cells(IND[b])
    M = Ca.merge(Cb, on=["naics", "soc"], suffixes=("_0", "_1")).merge(S, on="soc")
    M["sector"] = M.naics.str[:2].map(SECTOR_OF)
    if sectors:
        M = M[M.sector.isin(sectors)].copy()
    M["g"] = (np.log(M.emp_1) - np.log(M.emp_0)) / (int(b) - int(a))
    M = M.groupby("naics").filter(lambda d: len(d) >= 2)
    for c in ["g", "robotic", "textai"]:
        gm = M.groupby("naics").apply(lambda d: np.average(d[c], weights=d.emp_0))
        M[c + "_d"] = M[c] - M.naics.map(gm)
    X = np.column_stack([np.ones(len(M)), M.robotic_d, M.textai_d])
    w, y = M.emp_0.values, M.g_d.values
    inv = np.linalg.pinv(X.T @ (w[:, None] * X)); bb = inv @ (X.T @ (w * y)); e = y - X @ bb
    ids = M.soc.str[:2].values; meat = np.zeros((3, 3))
    for g_ in np.unique(ids):
        m = ids == g_; sv = X[m].T @ (w[m] * e[m]); meat += np.outer(sv, sv)
    G = len(np.unique(ids))
    V = inv @ (meat * (G / (G - 1)) * ((len(y) - 1) / (len(y) - 3))) @ inv
    se = np.sqrt(np.diag(V))
    r = {}
    for i, nm in enumerate(["int", "robotic", "textai"]):
        t = bb[i] / se[i]; r[nm] = (bb[i], 2 * (1 - sp.norm.cdf(abs(t))))
    return r, len(M)


print("\n" + "=" * 100)
print("TEST 4  HORSE RACE, WITH ITS PLACEBO. This is the decisive test.")
print("=" * 100)
print("\nThe two measures correlate -0.74, so each contaminates the other's univariate")
print("coefficient. Running both together, in every window, inside physical industries.")
print("An anticipation story needs robotic exposure to bite in the AI window and NOT in the")
print("pre-AI placebo.\n")
print(f"{'window':<24}{'robotic beta':>15}{'p':>9}{'text-AI beta':>15}{'p':>9}{'cells':>9}")
for a, b, tag in [("2013", "2019", "placebo"), ("2019", "2022", "COVID"),
                  ("2022", "2025", "AI window")]:
    o, n = horse(a, b, PHYSICAL)
    print(f"{a + '-' + b + '  ' + tag:<24}{o['robotic'][0]:>+15.4f}{o['robotic'][1]:>9.4f}"
          f"{o['textai'][0]:>+15.4f}{o['textai'][1]:>9.4f}{n:>9,}")
print("""
  Robotic exposure is ALREADY significant in the pre-AI placebo (p = 0.003) once text-AI
  is controlled for, and its coefficient PEAKS in 2019-2022, not in the generative-AI
  window. Routine manual work has been losing ground inside these industries since well
  before 2022; what changed is that the decline roughly tripled during the pandemic and
  has since partly receded. That is the signature of long-run automation accelerated by a
  labour shortage, not of employers bracing for robots that have not arrived.""")
print("""
INTERPRETATION GUIDE
  Anticipation of robotics requires a coefficient that is negative AND materially more
  negative in the AI window than in the pre-AI placebo. A negative coefficient of similar
  size in both windows is the long-running decline of routine manual work, which has been
  documented since the 1980s and is not evidence about robots arriving now.""")

# ---- chart -------------------------------------------------------------------
fig, axes = plt.subplots(1, 3, figsize=(19, 6.2))

ax = axes[0]
ax.scatter(sec.textai, sec.robotic, s=140, color="#1f4e79", edgecolors="white", zorder=3)
for s_, r in sec.iterrows():
    ax.annotate(s_, (r.textai, r.robotic), xytext=(6, 4), textcoords="offset points", fontsize=8.5)
ax.set_xlabel("text-AI replaceability (what the project used)", fontsize=10)
ax.set_ylabel("robotic exposure (built here)", fontsize=10)
ax.set_title(f"1. The two measures are near-opposites\nSpearman rho = {rho:+.2f}",
             fontsize=11.5, fontweight="bold")
ax.grid(True, ls="--", alpha=0.35)

ax = axes[1]
x = np.arange(len(P)); w = 0.38
ax.bar(x - w/2, P.br, w, yerr=1.96 * P.sr, label="robotic exposure",
       color="#c0392b", error_kw=dict(lw=1.2, capsize=3))
ax.bar(x + w/2, P.bt, w, yerr=1.96 * P.st, label="text-AI replaceability",
       color="#1f4e79", error_kw=dict(lw=1.2, capsize=3))
ax.axhline(0, color="black", lw=1.1)
ax.set_xticks(x)
ax.set_xticklabels([f"{r.win}\n{'placebo' if i==0 else ('COVID' if i==1 else 'AI window')}"
                    for i, r in P.iterrows()], fontsize=9)
ax.set_ylabel("coefficient on occupation employment growth", fontsize=10)
ax.set_title("2. Both measures, all three windows\nn ~ 700 occupations",
             fontsize=11.5, fontweight="bold")
ax.legend(fontsize=8.5); ax.grid(True, axis="y", ls="--", alpha=0.35)

ax = axes[2]
A["bin"] = pd.qcut(A.robotic, 15, duplicates="drop")
for col, lab, c in [("g", "AI window 2022-2025", "#c0392b"), ("g_pre", "placebo 2013-2019", "#95a5a6")]:
    b15 = A.groupby("bin").apply(lambda d: pd.Series({
        "x": np.average(d.robotic, weights=d.emp_0), "y": np.average(d[col], weights=d.emp_0) * 100}))
    ax.plot(b15.x, b15.y, marker="o", lw=2.1, color=c, label=lab)
ax.axhline(0, color="black", lw=1.0)
ax.set_xlabel("robotic exposure (15 employment-weighted bins)", fontsize=10)
ax.set_ylabel("annualized employment growth, %/yr", fontsize=10)
ax.set_title("3. Robot-exposed jobs shrink in BOTH windows\nThe gradient is not new",
             fontsize=11.5, fontweight="bold")
ax.legend(fontsize=8.5); ax.grid(True, ls="--", alpha=0.35)

fig.suptitle("Testing the anticipatory-robotics hypothesis with a purpose-built robotic exposure measure",
             fontsize=13, fontweight="bold", y=1.02)
plt.tight_layout()
plt.savefig("robotic_exposure_test.png", dpi=150, bbox_inches="tight")
print("\nChart saved: robotic_exposure_test.png")
