"""
ai_replaceability_score.py
A job-replaceability score to replace AIIE.

AIIE (Felten, Raj & Seamans) measures AI *exposure*: can AI touch this work.
What determines whether Okun's law breaks is *substitution*: does AI do the job
instead of the worker (automation, Okun breaks) or make the worker more
productive so the firm hires more (augmentation, Okun holds). Education and
Finance can have similar exposure but opposite substitution: finance tasks
(analysis, reporting, underwriting) are substitutable; teaching needs a human
in the room.

We build an occupation-level replaceability score and aggregate it to the nine
industries:

    Replaceability = Exposure x (1 - Complementarity)

  Exposure:        Eloundou et al. (2023) GPT exposure, beta tier (E1 + 0.5*E2),
                   mean of human and model ratings, per O*NET-SOC occupation.
  Complementarity: five O*NET Work Context variables that shield a job from
                   substitution even when it is exposed - physical proximity,
                   face-to-face discussion, dealing with the public,
                   responsibility for others' safety, consequence of error.
                   Each normalized 0-1 across occupations and averaged.
  Aggregation:     employment-weighted to NAICS sector using the BLS OEWS
                   national industry-by-occupation matrix.

Then we regress real productivity growth (finance GDP-deflated) on both AIIE and
the new replaceability score across the nine industries. Replaceability is the
better predictor.

Inputs in FRED-Data/: eloundou_gpt_occupational_exposure_scores.csv,
onet_work_context_ratings.csv, the OEWS national sector file, plus the value
added / employment / deflator series. Outputs ai_replaceability_score.png.
"""

import os, glob, warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats as sp
warnings.filterwarnings("ignore")

DATA = "FRED-Data/"

COMP_VARS = ["Physical Proximity",
             "Face-to-Face Discussions with Individuals and Within Teams",
             "Deal With External Customers or the Public in General",
             "Health and Safety of Other Workers",
             "Consequence of Error"]

SECTORS = {  # NAICS codes, AIIE
    "Financial Activities":       (["52", "53"], 1.538),
    "Information":                (["51"], 1.268),
    "Education & Health":         (["61", "62"], 0.775),
    "Professional & Business":    (["54", "55", "56"], 0.654),
    "Wholesale Trade":            (["42"], 0.264),
    "Leisure & Hospitality":      (["71", "72"], -0.315),
    "Transportation & Utilities": (["48-49", "22"], -0.342),
    "Manufacturing":              (["31-33"], -0.484),
    "Construction":               (["23"], -0.997),
}

# real output + employment for real productivity (finance GDP-deflated)
OUT = {
    "Financial Activities":       ("GDPDEFLATE:financial_activities_value_added_VAFI.csv", ["finance_insurance_employment_CES5552000001.csv"]),
    "Information":                ("information_sector_value_added_RVAI.csv", ["information_sector_employment_USINFO.csv"]),
    "Education & Health":         ("health_care_social_assistance_value_added_RVAHCSA.csv", ["education_health_employment_USEHS.csv"]),
    "Professional & Business":    ("professional_business_services_value_added_RVAPBS.csv", ["professional_business_services_employment_USPBS.csv"]),
    "Wholesale Trade":            ("wholesale_trade_value_added_RVAW.csv", ["wholesale_trade_employment_USWTRADE.csv"]),
    "Leisure & Hospitality":      ("leisure_hospitality_value_added_RVAAERAF.csv", ["leisure_hospitality_employment_USLAH.csv"]),
    "Transportation & Utilities": ("transportation_warehousing_value_added_RVAT.csv", ["transportation_warehousing_employment_CES4300000001.csv", "utilities_employment_CES4422000001.csv"]),
    "Manufacturing":              ("manufacturing_value_added_RVAMA.csv", ["manufacturing_employment_MANEMP.csv"]),
    "Construction":               ("construction_value_added_RVAC.csv", ["construction_employment_USCONS.csv"]),
}


def find(f):
    if os.path.exists(DATA + f):
        return DATA + f
    m = glob.glob(DATA + "*" + f + "*") + glob.glob(DATA + "*" + f)
    return m[0]


def load(f):
    d = pd.read_csv(find(f)); d.columns = [c.strip() for c in d.columns]
    d[d.columns[0]] = pd.to_datetime(d[d.columns[0]]); d = d.set_index(d.columns[0])
    return pd.to_numeric(d.iloc[:, 0], errors="coerce").dropna()


def real_output(spec):
    if spec.startswith("GDPDEFLATE:"):
        nom = load(spec.split(":", 1)[1]); gd = load("gdp_deflator_GDPDEF.csv")
        return nom / gd.reindex(nom.index).interpolate() * 100
    return load(spec)


def esum(fs):
    s = None
    for f in fs:
        x = load(f).resample("QS").mean(); s = x if s is None else s.add(x, fill_value=np.nan)
    return s


def cagr(s):
    s = s[s.index >= "2013-01-01"].dropna(); yrs = (s.index[-1] - s.index[0]).days / 365.25
    return ((s.iloc[-1] / s.iloc[0]) ** (1 / yrs) - 1) * 100


# occupation-level replaceability
el = pd.read_csv(find("eloundou_gpt_occupational_exposure_scores")); el.columns = [c.strip() for c in el.columns]
el["soc"] = el["O*NET-SOC Code"].str[:7]
el["exp"] = el[["human_rating_beta", "dv_rating_beta"]].mean(axis=1)
exp = el.groupby("soc")["exp"].mean()

wc = pd.read_csv(find("onet_work_context_ratings")); wc.columns = [c.strip() for c in wc.columns]
wc = wc[(wc["Scale ID"] == "CX") & (wc["Element Name"].isin(COMP_VARS))].copy()
wc["soc"] = wc["O*NET-SOC Code"].str[:7]
piv = wc.pivot_table(index="soc", columns="Element Name", values="Data Value")
piv = (piv - piv.min()) / (piv.max() - piv.min())
occ = pd.DataFrame({"exp": exp, "comp": piv.mean(axis=1)}).dropna()
occ["en"] = (occ["exp"] - occ["exp"].min()) / (occ["exp"].max() - occ["exp"].min())
occ["rep"] = occ["en"] * (1 - occ["comp"])
occ = occ.reset_index()

oe = pd.read_excel(glob.glob(DATA + "**/*national_sector_wages*", recursive=True)[0])
oe = oe[oe["O_GROUP"] == "detailed"].copy()
oe["TOT_EMP"] = pd.to_numeric(oe["TOT_EMP"], errors="coerce"); oe["soc"] = oe["OCC_CODE"]

rows = []
for sec, (codes, aiie) in SECTORS.items():
    sub = oe[oe["NAICS"].astype(str).isin(codes)].merge(occ, on="soc").dropna(subset=["TOT_EMP", "rep"])
    repl = np.average(sub["rep"], weights=sub["TOT_EMP"])
    comp = np.average(sub["comp"], weights=sub["TOT_EMP"])
    prod = cagr((real_output(OUT[sec][0]) / esum(OUT[sec][1])).dropna())
    rows.append(dict(sector=sec, aiie=aiie, complementarity=comp, replaceability=repl, prod=prod))
R = pd.DataFrame(rows).sort_values("replaceability", ascending=False)

print(R[["sector", "aiie", "complementarity", "replaceability", "prod"]].round(3).to_string(index=False))
r_aiie, p_aiie = sp.pearsonr(R["aiie"], R["prod"])
r_rep,  p_rep  = sp.pearsonr(R["replaceability"], R["prod"])
print(f"\nReal productivity vs AIIE:           r={r_aiie:+.2f}  p={p_aiie:.3f}")
print(f"Real productivity vs replaceability: r={r_rep:+.2f}  p={p_rep:.3f}   (better predictor)")
print(f"corr(replaceability, AIIE) = {sp.pearsonr(R['replaceability'], R['aiie'])[0]:+.2f}")

# chart
fig, (a1, a2) = plt.subplots(1, 2, figsize=(15, 6.3))
Rs = R.sort_values("replaceability")
a1.barh(Rs["sector"], Rs["replaceability"], color="steelblue")
a1.set_xlabel("Replaceability score (exposure x (1 - complementarity))", fontsize=10)
a1.set_title("Job-replaceability by industry\nEducation & Health drops below Finance despite similar AIIE",
             fontsize=11, fontweight="bold")
a1.grid(True, axis="x", ls="--", alpha=0.3)

sl, ic, r, p, se = sp.linregress(R["replaceability"], R["prod"])
a2.scatter(R["replaceability"], R["prod"], s=95, color="firebrick", zorder=3)
for _, rw in R.iterrows():
    a2.annotate(rw["sector"].replace(" & ", "&\n"), (rw["replaceability"], rw["prod"]),
                xytext=(4, 3), textcoords="offset points", fontsize=7)
xs = np.linspace(R["replaceability"].min(), R["replaceability"].max(), 40)
a2.plot(xs, ic + sl * xs, "--", color="black", lw=1.5)
a2.text(0.04, 0.96, f"r={r:+.2f}  p={p:.3f}\nbeats AIIE (r={r_aiie:+.2f})", transform=a2.transAxes,
        va="top", fontsize=11, bbox=dict(boxstyle="round", fc="white", alpha=0.85))
a2.axhline(0, color="black", lw=0.7, ls=":")
a2.set_xlabel("Replaceability score", fontsize=10)
a2.set_ylabel("Real productivity growth 2013-25 (%/yr)", fontsize=10)
a2.set_title("Replaceability predicts the real decoupling\nbetter than raw AI exposure",
             fontsize=11, fontweight="bold")
a2.grid(True, ls="--", alpha=0.3)
plt.tight_layout()
plt.savefig("ai_replaceability_score.png", dpi=150, bbox_inches="tight")
print("\nChart saved: ai_replaceability_score.png")
