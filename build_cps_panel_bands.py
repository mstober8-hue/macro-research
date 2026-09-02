"""
build_cps_panel_bands.py
Rebuild the IPUMS CPS panel with the age bands Brynjolfsson, Chandar & Chen use,
alongside this project's original bands, so the two can be compared directly.

WHY
This project's panel uses 20-24 as "entry level". Canaries (Aug 2026) uses 22-25,
and reports separate bands 26-30, 31-34, 35-40, 41-49, 50+. The 20-21 year olds in
this project's band are disproportionately students and part-time workers, which is
the most obvious referee objection to a direct comparison. This produces both.

Output: cps_panel_bands.csv, one row per (OCC2010, year, band), weighted employment.
Bands: a20_24 (this project), a22_25 (Canaries entry), a26_30, a31_34, a35p, u20.
Note the first two OVERLAP by construction; use one or the other, never both.
"""
import gzip, os, numpy as np, pandas as pd

SRC = os.path.expanduser("~/Downloads/cps_00001.dat.gz")
OUT = "cps_panel_bands.csv"
COLS = {"YEAR": (0, 4), "MONTH": (9, 11), "WTFINL": (38, 52), "AGE": (89, 91),
        "EMPSTAT": (98, 100), "OCC2010": (105, 109)}
EMPLOYED = {10, 12}
CHUNK = 500_000

acc, months = {}, {}
n_read = n_kept = 0
with gzip.open(SRC, "rt") as fh:
    while True:
        lines = fh.readlines(CHUNK * 140)
        if not lines: break
        arr = np.array(lines); n_read += len(arr)
        def col(name, dtype=float):
            s, e = COLS[name]
            v = np.char.strip(np.array([ln[s:e] for ln in arr]))
            v[v == ""] = "0"
            return v.astype(dtype)
        emp = col("EMPSTAT", int); age = col("AGE", int)
        keep = np.isin(emp, list(EMPLOYED)) & (age >= 16) & (age <= 64)
        if not keep.any(): continue
        yr = col("YEAR", int)[keep]; occ = col("OCC2010", int)[keep]
        wt = col("WTFINL", float)[keep] / 10000.0
        a = age[keep]; mo = col("MONTH", int)[keep]; n_kept += keep.sum()

        # Emit each record into every band it belongs to. a20_24 and a22_25 overlap.
        for band, mask in [("u20",    a < 20),
                           ("a20_24", (a >= 20) & (a <= 24)),
                           ("a22_25", (a >= 22) & (a <= 25)),
                           ("a26_30", (a >= 26) & (a <= 30)),
                           ("a31_34", (a >= 31) & (a <= 34)),
                           ("a35p",   a >= 35)]:
            if not mask.any(): continue
            df = pd.DataFrame({"occ": occ[mask], "year": yr[mask], "w": wt[mask]})
            for (o, y), v in df.groupby(["occ", "year"], sort=False)["w"].sum().items():
                acc[(o, y, band)] = acc.get((o, y, band), 0.0) + v
        for y, m in set(zip(yr.tolist(), mo.tolist())):
            months.setdefault(y, set()).add(m)

print(f"records read : {n_read:,}\nrecords kept : {n_kept:,}")
P = (pd.Series(acc).rename("emp").reset_index()
     .rename(columns={"level_0": "occ", "level_1": "year", "level_2": "band"}))
P = P[P.occ > 0]
P["months"] = P.year.map({y: len(ms) for y, ms in months.items()})
P["emp"] = P.emp / P.months
P.drop(columns="months").to_csv(OUT, index=False)
print(f"wrote {OUT}: {len(P):,} rows, {P.occ.nunique()} occupations, "
      f"years {P.year.min()}-{P.year.max()}")
for b in ["a20_24", "a22_25", "a35p"]:
    print(f"  {b}: {P[P.band==b].emp.sum()/P[P.band==b].year.nunique()/1e6:.2f}M avg/yr")
