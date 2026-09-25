"""
build_cps_panel_ind.py
Occupation x INDUSTRY x year panel of employment by age band, from the cps_00002
extract, so the Section 3 specification can be re-run with industry-by-year fixed
effects.

WHY
Section 3 carries occupation and year fixed effects. That absorbs anything fixed
about an occupation and anything common to a year, but not an industry-specific
shock in a particular year. If AI-exposed occupations happen to sit in industries
that shrank after 2022 for unrelated reasons, and young workers are more sensitive
to industry contraction than older ones, the exposure coefficient could be picking
up industry composition rather than exposure.

Occupation fixed effects do NOT rule this out. An occupation's industry mix can
shift over time, and the same occupation in a different industry faces a different
shock. The test is to add industry-by-year fixed effects, which requires cells at
the occupation-by-industry level.

INDUSTRY GROUPING
IND1990 has roughly 230 categories, which at occupation x industry x year x age
band would be mostly empty cells. Industries are grouped to the 13 IND1990 major
divisions, which keeps cells populated while still absorbing sector-level shocks.

Writes cps_panel_ind.csv.
"""
import gzip, os, numpy as np, pandas as pd

SRC = os.path.expanduser("~/Downloads/cps_00002.dat.gz")
COLS = {"YEAR": (0, 4), "WTFINL": (41, 55), "AGE": (97, 99),
        "EMPSTAT": (106, 108), "OCC2010": (113, 117), "IND1990": (117, 120)}
EMPLOYED = {10, 12}
CHUNK = 400_000

# IND1990 major divisions
CUTS  = [0, 40, 60, 100, 400, 500, 580, 700, 721, 761, 800, 812, 900, 1000]
NAMES = ["agriculture", "mining", "construction", "manufacturing", "transport_utils",
         "wholesale", "retail", "fire", "business_repair", "personal_svc",
         "entertainment", "professional", "public_admin"]

def band(a):
    return np.where(a < 20, "u20",
           np.where(a <= 24, "a20_24",
           np.where(a == 25, "a25",
           np.where(a <= 30, "a26_30",
           np.where(a <= 34, "a31_34", "a35p")))))

acc = {}
n_read = n_kept = 0
with gzip.open(SRC, "rt") as fh:
    while True:
        lines = fh.readlines(CHUNK * 170)
        if not lines:
            break
        arr = np.array(lines); n_read += len(arr)
        def col(name, dtype=np.int64):
            s, e = COLS[name]
            v = np.char.strip(np.array([ln[s:e] for ln in arr]))
            v[v == ""] = "0"
            return v.astype(dtype)
        emp = col("EMPSTAT"); age = col("AGE"); ind = col("IND1990")
        keep = np.isin(emp, list(EMPLOYED)) & (age >= 16) & (age <= 64) & (ind > 0)
        if not keep.any():
            continue
        n_kept += keep.sum()
        yr = col("YEAR")[keep]; occ = col("OCC2010")[keep]
        wt = col("WTFINL", float)[keep] / 10000.0
        a = age[keep]; ig = np.digitize(ind[keep], CUTS) - 1
        sect = np.array(NAMES, dtype=object)[np.clip(ig, 0, len(NAMES) - 1)]
        bb = band(a)
        # 22-25 overlaps 20-24, emitted separately
        df = pd.DataFrame({"occ": occ, "year": yr, "sector": sect, "band": bb, "w": wt})
        for (o, y, sc, b), v in df.groupby(["occ", "year", "sector", "band"], sort=False)["w"].sum().items():
            acc[(o, y, sc, b)] = acc.get((o, y, sc, b), 0.0) + v
        m = (a >= 22) & (a <= 25)
        if m.any():
            d2 = pd.DataFrame({"occ": occ[m], "year": yr[m], "sector": sect[m], "w": wt[m]})
            for (o, y, sc), v in d2.groupby(["occ", "year", "sector"], sort=False)["w"].sum().items():
                acc[(o, y, sc, "a22_25")] = acc.get((o, y, sc, "a22_25"), 0.0) + v

P = (pd.Series(acc).rename("emp").reset_index()
       .rename(columns={"level_0": "occ", "level_1": "year",
                        "level_2": "sector", "level_3": "band"}))
P.to_csv("cps_panel_ind.csv", index=False)
print(f"records read {n_read:,}; employed 16-64 with industry {n_kept:,}")
print(f"wrote cps_panel_ind.csv: {len(P):,} rows, {P.occ.nunique()} occupations, "
      f"{P.sector.nunique()} sectors, years {P.year.min()}-{P.year.max()}")
