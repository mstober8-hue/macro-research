"""
section4_rate_confound.py
Does exposure-correlated interest-rate sensitivity explain the entry-level result?

WHY THIS TEST
Section 7.1 names this as the paper's most likely unmeasured confounder, and it is
not a generic worry here. Part 4 of this project finds that one common factor
explains 72% of sector hiring over the same window and tracks the fed funds rate at
an 8-9 quarter lag, and concludes that monetary policy, not AI, drove most of the
aggregate output-to-jobs break. If AI-exposed occupations are also concentrated in
rate-sensitive industries, the Section 3 estimate could be measuring the tightening
rather than AI. Brynjolfsson et al. run this control in ADP and report the
divergence survives; this runs it here.

DESIGN
1. INDUSTRY SENSITIVITY. For each of 73 NAICS-3 industries, regress annual
   employment growth on the annual change in the fed funds rate at lags 0-3 and sum
   the coefficients. The sum is the cumulative response of that industry's
   employment to a one-point tightening. Estimated on 1990-2019 ONLY, so the
   treatment window cannot contaminate the measure.

2. OCCUPATION EXPOSURE. Map industry sensitivity onto occupations through the OEWS
   May 2022 industry-by-occupation employment matrix: an occupation's rate exposure
   is the employment-weighted mean sensitivity of the industries it works in.

3. HORSE RACE. Add rate exposure x post to the Section 3 specification. If AI
   exposure is really rate sensitivity, the AI coefficient should collapse.

Panel construction and the estimator live in entry_panel.py.
Writes section4_rate_confound.png.
"""
import re, numpy as np, pandas as pd
from scipy import stats as sp
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from entry_panel import load, fe, z, post_x, stars, BANDS, DATA, POST

FIT_MAX = 2019            # sensitivity estimated pre-COVID, pre-treatment
NLAG    = 3

# ---- 1. industry employment sensitivity to the fed funds rate ------------------
ces = pd.read_csv(DATA + "ces/ces_naics3_raw.tsv", sep="\t", header=None,
                  names=["sid", "year", "month", "emp"])
ces["emp"] = pd.to_numeric(ces.emp.astype(str).str.strip(), errors="coerce")
ces = ces[ces.month.astype(str).str.startswith("M")]
ces["m"] = ces.month.astype(str).str[1:].astype(int)
ces = ces[ces.m <= 12].dropna(subset=["emp"])
meta = pd.read_csv(DATA + "ces/naics3_meta.csv")

# Identified shocks, NOT the raw funds rate. A first version of this script
# regressed industry employment growth on the change in the fed funds rate and
# produced a measure on which "Construction of buildings" ranked 69th of 73 for
# rate sensitivity, with a strongly POSITIVE coefficient. That is simultaneity:
# the Fed raises rates because the economy is booming, so the raw rate change is
# procyclical and the regression recovers how procyclical an industry is rather
# than how rate-sensitive it is. Bauer-Swanson is orthogonalized to macro news,
# which is the fix; Jarocinski-Karadi's pure policy shock is the robustness check.
def annual_shock(fname):
    d = pd.read_csv(DATA + "shocks/" + fname)
    d["year"] = pd.to_datetime(d.date).dt.year
    return d.groupby("year", as_index=False).shock.sum()

SHOCKS = {"bauer_swanson": "03_bauer_swanson_orthogonalized_shock.csv",
          "jarocinski_karadi": "04_jarocinski_karadi_pure_mp_shock.csv"}

ann_base = ces.groupby(["sid", "year"], as_index=False).emp.mean()
ann_base["g"] = 100 * ann_base.groupby("sid").emp.pct_change()

def sensitivity(fname):
    SH = annual_shock(fname)
    ann = ann_base.merge(SH, on="year", how="inner")
    out = []
    for sid, g in ann.groupby("sid"):
        g = g.sort_values("year").copy()
        for L in range(NLAG + 1):
            g[f"d{L}"] = g.shock.shift(L)
        f = g[(g.year >= 1990) & (g.year <= FIT_MAX)].dropna(
            subset=["g"] + [f"d{L}" for L in range(NLAG + 1)])
        if len(f) < 15:
            continue
        X = np.column_stack([np.ones(len(f))] + [f[f"d{L}"].values for L in range(NLAG + 1)])
        b = np.linalg.lstsq(X, f.g.values, rcond=None)[0]
        out.append({"sid": sid, "sens": b[1:].sum(), "n": len(f)})
    return pd.DataFrame(out).merge(meta, on="sid", how="left")

SENS = sensitivity(SHOCKS["bauer_swanson"])
SENS["naics3"] = SENS.naics_code.astype(str).str[:3]

# Validation gate. Construction is the textbook rate-sensitive industry; if the
# measure does not put it in the sensitive half, the measure is wrong and nothing
# downstream should be believed.
_c = SENS[SENS.industry_name.astype(str).str.contains("Construction of buildings", case=False, na=False)]
_rank = (SENS.sens < _c.sens.iloc[0]).sum() + 1 if len(_c) else None

print("=" * 96)
print("DOES INTEREST-RATE SENSITIVITY EXPLAIN THE ENTRY-LEVEL RESULT?")
print("=" * 96)
print(f"\n1. INDUSTRY SENSITIVITY  cumulative employment response to a contractionary shock")
print(f"   Bauer-Swanson orthogonalized shock, distributed lag 0-{NLAG} years,")
print(f"   fitted 1990-{FIT_MAX}, {len(SENS)} industries")
print(f"\n   VALIDATION: 'Construction of buildings' ranks {_rank} of {len(SENS)} most sensitive"
      f"  ({'PASS' if _rank and _rank <= len(SENS)//2 else 'FAIL'})")
print(f"\n   most rate-sensitive (employment falls most):")
for _, r in SENS.nsmallest(6, "sens").iterrows():
    print(f"     {r.sens:+7.3f}  {str(r.industry_name)[:52]}")
print(f"   least rate-sensitive:")
for _, r in SENS.nlargest(4, "sens").iterrows():
    print(f"     {r.sens:+7.3f}  {str(r.industry_name)[:52]}")

# ---- 2. push sensitivity onto occupations via the OEWS matrix ------------------
ow = pd.read_excel(DATA + "oews_national_industry_files/oews_may2022_national_4digit_naics_wages.xlsx")
ow.columns = [c.strip().upper() for c in ow.columns]
og = "O_GROUP" if "O_GROUP" in ow.columns else "OCC_GROUP"
ow = ow[ow[og].astype(str).str.strip().str.lower() == "detailed"].copy()
ow["emp"] = pd.to_numeric(ow.TOT_EMP, errors="coerce")
ow["naics3"] = ow.NAICS.astype(str).str.replace(r"\D", "", regex=True).str[:3]
ow["soc"] = ow.OCC_CODE.astype(str).str.extract(r"(\d{2}-\d{4})")[0]
ow = ow.dropna(subset=["emp", "soc"])
ow = ow.merge(SENS[["naics3", "sens"]], on="naics3", how="inner")
occ_sens = (ow.assign(w=ow.emp * ow.sens).groupby("soc")
              .apply(lambda g: g.w.sum() / g.emp.sum(), include_groups=False)
              .rename("rate_sens").reset_index())
print(f"\n2. OCCUPATION RATE EXPOSURE  via OEWS May 2022, {len(occ_sens)} SOC occupations matched")

XW = pd.read_csv(DATA + "occ2010_soc_crosswalk.csv")
def lk(s):
    h = occ_sens[occ_sens.soc == s]
    if len(h): return h.rate_sens.iloc[0]
    for k in (5, 2):
        h = occ_sens[occ_sens.soc.astype(str).str.startswith(str(s)[:k])]
        if len(h): return h.rate_sens.mean()
    return np.nan
XW["rate_sens"] = [lk(s) for s in XW.soc]
RS = XW[["occ", "rate_sens"]].dropna().drop_duplicates("occ")

D = load().merge(RS, on="occ", how="inner")
o = D.drop_duplicates("occ")
print(f"   merged panel: {D.occ.nunique()} occupations, {len(D)} cells")
print(f"   corr(AI exposure, rate sensitivity) = {np.corrcoef(o.rep_good, o.rate_sens)[0,1]:+.3f}"
      f"   [raw beta: {np.corrcoef(o.en_raw, o.rate_sens)[0,1]:+.3f}]")

# ---- 3. horse race -------------------------------------------------------------
print("\n3. HORSE RACE  AI exposure against rate sensitivity")
print("-" * 96)
print(f"\n   {'specification':<46}{'coef':>9}{'se':>9}{'t':>7}{'p':>9}")
R = {}
for ycol, ylab in BANDS:
    for xs, lab, idx in [(["rep_good"], "AI exposure alone", 0),
                         (["rate_sens"], "rate sensitivity alone", 0),
                         (["rep_good", "rate_sens"], "AI exposure | rate sensitivity", 0),
                         (["rep_good", "rate_sens"], "rate sensitivity | AI exposure", 1),
                         (["rep_good", "rate_sens", "jobzone", "lwage"], "AI exposure | rate + educ + wage", 0)]:
        b, se, t, p, G, n = fe(D.dropna(subset=xs), ycol, post_x(D.dropna(subset=xs), xs))
        R[(ycol, lab)] = (b[idx], se[idx], p[idx])
        print(f"   {ylab + ', ' + lab:<46}{b[idx]:>+9.4f}{se[idx]:>9.4f}{t[idx]:>7.2f}{p[idx]:>9.4f} {stars(p[idx])}")
    print()

# ---- chart ---------------------------------------------------------------------
fig, ax = plt.subplots(1, 2, figsize=(13.5, 5.0))
labs = ["AI exposure alone", "AI exposure | rate sensitivity", "AI exposure | rate + educ + wage"]
short = ["AI alone", "AI | rate", "AI | rate\n+ educ + wage"]
for k, (ycol, ylab) in enumerate(BANDS):
    v = [R[(ycol, l)] for l in labs]
    ax[k].bar(range(3), [x[0] for x in v], yerr=[1.96 * x[1] for x in v],
              color="#1f4e79", error_kw=dict(lw=1.3, capsize=4))
    ax[k].axhline(0, color="black", lw=1.1)
    ax[k].axhline(v[0][0], color="gray", ls=":", lw=1.3)
    ax[k].set_xticks(range(3)); ax[k].set_xticklabels(short, fontsize=8.5)
    ax[k].set_title(ylab, fontsize=11.5, fontweight="bold")
    ax[k].set_ylabel("pp per sd of exposure", fontsize=9.5)
    ax[k].grid(True, axis="y", ls="--", alpha=.35)
fig.suptitle("Interest-rate sensitivity does not account for the entry-level result",
             fontsize=13, fontweight="bold", y=1.02)
plt.tight_layout(); plt.savefig("section4_rate_confound.png", dpi=150, bbox_inches="tight")
print("Chart saved: section4_rate_confound.png")
