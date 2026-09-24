"""
build_cps_flows.py
Build occupation-by-year HIRING and SEPARATION flows from the CPS, plus an
earnings panel, from the cps_00002 extract.

WHY
Brynjolfsson, Chandar & Chen's fact (4) is that the young-employment divergence
"operates primarily through reduced hiring of young workers rather than increased
separations", and fact (6) is that "adjustment is occurring through employment
rather than base compensation". Neither is testable on employment stocks. Flows
need individuals linked across consecutive months; compensation needs the
outgoing-rotation earnings variables and their own weight.

HOW THE LINKING WORKS
The CPS uses a 4-8-4 rotation: a household is in sample for 4 months, out for 8,
back for 4. Month-in-sample (MISH) 1-3 and 5-7 are followed by an observation the
NEXT month; MISH 4 and 8 are not. Linking is on CPSIDP, the longitudinal person
identifier. Standard practice is to verify the link on age and sex, because
CPSIDP can mismatch across household composition changes; mismatched pairs are
dropped rather than kept.

DEFINITIONS, on consecutive month pairs (t-1, t)
  HIRE        not employed at t-1, employed at t, occupation recorded at t
  SEPARATION  employed at t-1, not employed at t, occupation recorded at t-1
  STAYER      employed both months
Occupation is attributed to the job held in the employed month, so a hire counts
toward the occupation entered and a separation toward the occupation left.

EARNINGS
EARNWEEK and HOURWAGE are collected only in the outgoing rotation groups (MISH 4
and 8), identified here by ELIGORG. They carry EARNWT, NOT WTFINL; using the
wrong weight is a standard error in this literature and the script asserts the
distinction rather than trusting it.

Writes cps_flows.csv (occ x year x band: hires, separations, stayers) and
cps_earnings.csv (occ x year x band: weekly earnings, hourly wage, ORG-weighted).
"""
import gzip, os, numpy as np, pandas as pd

SRC = os.path.expanduser("~/Downloads/cps_00002.dat.gz")
COLS = {"YEAR": (0, 4), "MONTH": (9, 11), "MISH": (36, 37), "WTFINL": (41, 55),
        "CPSIDP": (55, 69), "AGE": (97, 99), "SEX": (99, 100),
        "EMPSTAT": (106, 108), "OCC2010": (113, 117), "EARNWT": (132, 142),
        "HOURWAGE": (142, 147), "PAIDHOUR": (147, 148), "EARNWEEK": (148, 156),
        "ELIGORG": (156, 157)}
EMPLOYED = {10, 12}
CHUNK = 400_000

def band(a):
    return np.where(a < 20, "u20",
           np.where(a <= 24, "a20_24",
           np.where(a == 25, "a25",
           np.where(a <= 30, "a26_30",
           np.where(a <= 34, "a31_34", "a35p")))))

def band2225(a):
    return (a >= 22) & (a <= 25)

print(f"reading {SRC}")
keep_cols = ["YEAR", "MONTH", "MISH", "WTFINL", "CPSIDP", "AGE", "SEX", "EMPSTAT",
             "OCC2010", "EARNWT", "HOURWAGE", "PAIDHOUR", "EARNWEEK", "ELIGORG"]
parts = []
n_read = 0
with gzip.open(SRC, "rt") as fh:
    while True:
        lines = fh.readlines(CHUNK * 170)
        if not lines:
            break
        arr = np.array(lines); n_read += len(arr)
        d = {}
        for c in keep_cols:
            s, e = COLS[c]
            v = np.char.strip(np.array([ln[s:e] for ln in arr]))
            v[v == ""] = "0"
            d[c] = v.astype(float if c in ("WTFINL", "EARNWT", "HOURWAGE", "EARNWEEK") else np.int64)
        df = pd.DataFrame(d)
        df = df[(df.AGE >= 16) & (df.AGE <= 64)]
        parts.append(df)
P = pd.concat(parts, ignore_index=True)
del parts
print(f"records read {n_read:,}; aged 16-64 {len(P):,}")

P["t"] = P.YEAR * 12 + P.MONTH
P["emp"] = P.EMPSTAT.isin(EMPLOYED)
P["wt"] = P.WTFINL / 10000.0
P["ewt"] = P.EARNWT / 10000.0

# ---- FLOWS: link consecutive months on CPSIDP -----------------------------------
L = P[P.CPSIDP > 0][["CPSIDP", "t", "emp", "AGE", "SEX", "OCC2010", "wt", "MISH"]]
cur = L.copy(); prv = L.copy()
prv["t"] = prv.t + 1                      # prv now aligns to the FOLLOWING month
M = cur.merge(prv, on=["CPSIDP", "t"], suffixes=("", "_p"))
before = len(M)
# verify the link: age must be stable within a year, sex must match
M = M[(M.SEX == M.SEX_p) & (M.AGE - M.AGE_p).between(0, 1)]
print(f"linked month pairs {before:,}; surviving age/sex verification {len(M):,} "
      f"({100*len(M)/max(before,1):.1f}%)")

M["hire"] = (~M.emp_p) & M.emp
M["sep"] = M.emp_p & (~M.emp)
M["stay"] = M.emp_p & M.emp
# attribute to the occupation of the employed month
M["occ"] = np.where(M.emp, M.OCC2010, M.OCC2010_p)
M["age_use"] = np.where(M.emp, M.AGE, M.AGE_p)
M["band"] = band(M.age_use.values)
M["is2225"] = band2225(M.age_use.values)
M = M[(M.occ > 0) & (M.hire | M.sep | M.stay)]

rows = []
for key, g in M.groupby(["occ", "YEAR" if "YEAR" in M else "t"]):
    pass  # placeholder replaced below
M["year"] = (M.t - 1) // 12
F = (M.groupby(["occ", "year", "band"])
       .apply(lambda g: pd.Series({"hires": (g.wt * g.hire).sum(),
                                   "seps": (g.wt * g.sep).sum(),
                                   "stayers": (g.wt * g.stay).sum()}), include_groups=False)
       .reset_index())
F2 = (M[M.is2225].groupby(["occ", "year"])
        .apply(lambda g: pd.Series({"hires": (g.wt * g.hire).sum(),
                                    "seps": (g.wt * g.sep).sum(),
                                    "stayers": (g.wt * g.stay).sum()}), include_groups=False)
        .reset_index())
F2["band"] = "a22_25"
F = pd.concat([F, F2], ignore_index=True)
F.to_csv("cps_flows.csv", index=False)
print(f"wrote cps_flows.csv: {len(F):,} rows, {F.occ.nunique()} occupations, "
      f"years {F.year.min()}-{F.year.max()}")

# ---- EARNINGS: outgoing rotation groups, emitted as MICRODATA ------------------
# Two things an earlier version of this block got wrong, both recorded because the
# first produced nonsense and the second hid it.
#
# HOURWAGE carries two implied decimals and its not-in-universe code is 99999,
# i.e. 999.99. A top-code check written against 999 instead of 99999 discards
# every wage above $9.99, which left a "wage distribution" running from $3.53 to
# $9.59. EARNWEEK was unaffected: its top code is 2884.61 and no NIU sentinel
# appears in the data.
#
# The ORG subsample is about a quarter of records, so occupation x year x narrow
# age band cells are far too thin for cell means: the median cell held 4
# observations and two-way fixed effects on those means blew up numerically.
# Microdata is emitted instead and the regression runs at the person level.
E = P[(P.ELIGORG == 1) & P.emp & (P.OCC2010 > 0)].copy()
assert E.ewt.sum() > 0, "EARNWT is empty; earnings analysis needs the ORG weight"
print(f"\nORG-eligible employed records {len(E):,} "
      f"({100*len(E)/len(P[P.emp]):.1f}% of employed records)")
E["earnweek"] = np.where((E.EARNWEEK > 0) & (E.EARNWEEK < 99999999),
                         E.EARNWEEK / 100.0, np.nan)
E["hourwage"] = np.where((E.HOURWAGE > 0) & (E.HOURWAGE < 99999),
                         E.HOURWAGE / 100.0, np.nan)
E["band"] = band(E.AGE.values)
E["is2225"] = band2225(E.AGE.values)
OUT = E[["OCC2010", "YEAR", "band", "is2225", "earnweek", "hourwage", "ewt"]].rename(
    columns={"OCC2010": "occ", "YEAR": "year"})
OUT = OUT[np.isfinite(OUT.earnweek) | np.isfinite(OUT.hourwage)]
OUT.to_csv("cps_earnings.csv", index=False)
ew = OUT.earnweek.dropna(); hw = OUT.hourwage.dropna()
print(f"wrote cps_earnings.csv: {len(OUT):,} person records, {OUT.occ.nunique()} occupations")
print(f"  weekly earnings n={len(ew):,}  median ${ew.median():.2f}  range ${ew.min():.2f}-${ew.max():.2f}")
print(f"  hourly wage     n={len(hw):,}  median ${hw.median():.2f}  range ${hw.min():.2f}-${hw.max():.2f}")
