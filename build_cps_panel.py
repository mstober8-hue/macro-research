"""
build_cps_panel.py
Parse the IPUMS CPS basic-monthly extract into an occupation-by-year panel.

WHY A PANEL RATHER THAN MORE OF THE SAME
entry_level_inference_audit.py established that the headline triple difference is
marginal (randomization p = 0.056 one-sided) and, crucially, that its noise is NOT
sampling error. Restricting to progressively larger and better-measured
occupations does not shrink the permutation null at all (8.11 -> 8.43 -> 9.47pp).
The dispersion is genuine cross-occupation variation in young-employment growth.

That has a direct consequence: simply having millions of individual records
instead of 218 published cells does not fix the power problem, because the null is
set by how many OCCUPATIONS there are and how much they truly differ, not by how
precisely each is measured.

What does fix it is differencing that heterogeneity out. In a panel of
occupation-by-year cells with OCCUPATION FIXED EFFECTS, permanent differences
between occupations are absorbed and the identifying variation becomes movement
WITHIN an occupation over time. The 8.26pp null spread is exactly what fixed
effects remove.

This is what the microdata is for, and specifically what OCC2010 is for. Plain OCC
changes coding in 2020, mid-window, which is why the published-table analysis had
to use two disjoint periods that cannot be directly compared. OCC2010 is
harmonized across that break, so a continuous 2016-2026 panel becomes possible and
with it an event study that shows a pre-trend instead of one before-and-after
contrast.

OUTPUT
cps_panel.csv, one row per (OCC2010, year, age band), with weighted employment.
Age bands are 20-24 (entry), 25-34, and 35+ (incumbents), matching the published
analysis so the two can be compared directly.
"""

import gzip
import os
import numpy as np
import pandas as pd

SRC = os.path.expanduser("~/Downloads/cps_00001.dat.gz")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cps_panel.csv")

# Column positions from the DDI codebook, converted to 0-indexed slices.
COLS = {
    "YEAR": (0, 4), "MONTH": (9, 11), "WTFINL": (38, 52), "AGE": (89, 91),
    "SEX": (91, 92), "EMPSTAT": (98, 100), "OCC2010": (105, 109),
    "IND": (112, 116), "CLASSWKR": (116, 118), "EDUC": (121, 124),
}
EMPLOYED = {10, 12}          # at work, and has job not at work
CHUNK = 500_000


def age_band(a):
    return np.where(a < 20, "u20",
           np.where(a < 25, "a20_24",
           np.where(a < 35, "a25_34", "a35p")))


acc = {}
months = {}
n_read = n_kept = 0
with gzip.open(SRC, "rt") as fh:
    while True:
        lines = fh.readlines(CHUNK * 140)
        if not lines:
            break
        arr = np.array(lines)
        n_read += len(arr)

        def col(name, dtype=float):
            s, e = COLS[name]
            v = np.array([ln[s:e] for ln in arr])
            v = np.char.strip(v)
            v[v == ""] = "0"
            return v.astype(dtype)

        emp = col("EMPSTAT", int)
        age = col("AGE", int)
        keep = np.isin(emp, list(EMPLOYED)) & (age >= 16) & (age <= 64)
        if not keep.any():
            continue
        yr = col("YEAR", int)[keep]
        occ = col("OCC2010", int)[keep]
        wt = col("WTFINL", float)[keep] / 10000.0   # 4 implied decimals
        ab = age_band(age[keep])
        n_kept += keep.sum()

        mo = col("MONTH", int)[keep]
        df = pd.DataFrame({"occ": occ, "year": yr, "band": ab, "w": wt})
        g = df.groupby(["occ", "year", "band"], sort=False)["w"].sum()
        for k, v in g.items():
            acc[k] = acc.get(k, 0.0) + v
        for y, m in set(zip(yr.tolist(), mo.tolist())):
            months.setdefault(y, set()).add(m)

print(f"records read   : {n_read:,}")
print(f"records kept   : {n_kept:,}  (employed, age 16-64)")

P = (pd.Series(acc).rename("emp").reset_index()
     .rename(columns={"level_0": "occ", "level_1": "year", "level_2": "band"}))
P = P[P.occ > 0]

# WTFINL is a MONTHLY population weight. Summing across the months of a year
# counts every person once per month, inflating employment by the number of
# months surveyed. Dividing by that count converts the total into an average
# monthly employment level, which is what CES and the published tables report.
mcount = {y: len(ms) for y, ms in months.items()}
P["months"] = P.year.map(mcount)
P["emp"] = P.emp / P.months
print("\nmonths of data per year:",
      ", ".join(f"{y}:{mcount[y]}" for y in sorted(mcount)))
P.drop(columns=["months"]).to_csv(OUT, index=False)

print(f"\npanel cells    : {len(P):,}")
print(f"occupations    : {P.occ.nunique():,}")
print(f"years          : {P.year.min()} to {P.year.max()}")
print(f"total weighted employment, 2024: "
      f"{P[P.year == 2024].emp.sum()/1e6:.1f}M  (CPS employed 16-64; "
      f"published CPS level is about 160M)")
print(f"\nwritten: {OUT}")

w = P.pivot_table(index=["occ", "year"], columns="band", values="emp",
                  aggfunc="sum").fillna(0).reset_index()
print("\nsanity: national age composition by year (share of employment)")
tot = w.groupby("year")[["a20_24", "a25_34", "a35p"]].sum()
tot["share_20_24"] = 100 * tot.a20_24 / tot.sum(axis=1)
print(tot[["share_20_24"]].round(2).to_string())
