"""
build_cps_panel_adp.py
Rebuild the entry-level CPS panel with the dimensions that separate the CPS
universe from the ADP payroll universe, so the two can be reconciled.

WHY
Brynjolfsson, Chandar & Chen (2026) measure employment in ADP payroll microdata:
private-sector employees on the formal payroll of firms that use ADP. The CPS
counts every employed person, including the self-employed, government workers,
farm workers, unpaid family workers and part-timers. If the two studies disagree
about what happened to young workers in AI-exposed occupations, the first thing
to rule out is that they are simply counting different people.

This emits the same (occupation x year x age band) cells as cps_panel_bands.csv,
but split by class of worker, industry sector and full-time status, so the panel
can be walked from the CPS universe toward the ADP universe one restriction at
a time. Nothing here is a new sample; it is the same records, sliced.

Outputs
  cps_panel_adp.csv          (occ, year, band, cw, sector, ft, emp)
  cps_panel_adp_monthly.csv  (occ, year, month, band, adpcore, emp)

The monthly file exists because Canaries date their window from November 2022,
while an annual panel dates it from the 2022 calendar average. Early 2022 was
still a recovering labour market for young workers, so the two baselines are not
the same number and the difference belongs in the reconciliation.

Column meanings for the annual file:
  cw     : priv | gov | self | unpaid   (CLASSWKR)
  sector : coarse IND1990 group
  ft     : 1 if usual hours >= 35, else 0 (997 "hours vary" counted as full-time)

Regenerate with the same IPUMS extract used by build_cps_panel_bands.py.
"""
import gzip, os, numpy as np, pandas as pd

SRC = os.path.expanduser("~/Downloads/cps_00001.dat.gz")
OUT = "cps_panel_adp.csv"
OUT_M = "cps_panel_adp_monthly.csv"
COLS = {"YEAR": (0, 4), "MONTH": (9, 11), "WTFINL": (38, 52), "AGE": (89, 91),
        "EMPSTAT": (98, 100), "OCC2010": (105, 109), "IND1990": (109, 112),
        "CLASSWKR": (116, 118), "UHRSWORKT": (118, 121)}
EMPLOYED = {10, 12}
CHUNK = 500_000

# IND1990 -> coarse sector. Bounds follow the IPUMS IND1990 category blocks.
SECT = [(10, 32, "agri"), (40, 50, "mining"), (60, 60, "constr"),
        (100, 392, "mfg"), (400, 472, "trans_util"), (500, 571, "wholesale"),
        (580, 691, "retail"), (700, 712, "fire"), (721, 760, "bus_repair"),
        (761, 791, "personal"), (800, 810, "entertain"), (812, 893, "prof_rel"),
        (900, 932, "pubadm")]
def sector_of(v):
    out = np.full(v.shape, "other", dtype=object)
    for lo, hi, name in SECT:
        out[(v >= lo) & (v <= hi)] = name
    return out

def cw_of(v):
    out = np.full(v.shape, "other", dtype=object)
    out[(v >= 10) & (v <= 14)] = "self"
    out[(v >= 20) & (v <= 23)] = "priv"
    out[(v >= 24) & (v <= 28)] = "gov"
    out[v == 29] = "unpaid"
    return out

acc, accm, months = {}, {}, {}
n_read = n_kept = 0
with gzip.open(SRC, "rt") as fh:
    while True:
        lines = fh.readlines(CHUNK * 140)
        if not lines:
            break
        arr = np.array(lines); n_read += len(arr)

        def col(name, dtype=float):
            s, e = COLS[name]
            v = np.char.strip(np.array([ln[s:e] for ln in arr]))
            v[v == ""] = "0"
            return v.astype(dtype)

        emp = col("EMPSTAT", int); age = col("AGE", int)
        keep = np.isin(emp, list(EMPLOYED)) & (age >= 20) & (age <= 25)
        if not keep.any():
            continue
        yr = col("YEAR", int)[keep]; occ = col("OCC2010", int)[keep]
        wt = col("WTFINL", float)[keep] / 10000.0
        a = age[keep]; mo = col("MONTH", int)[keep]
        sec = sector_of(col("IND1990", int)[keep])
        cw = cw_of(col("CLASSWKR", int)[keep])
        uh = col("UHRSWORKT", int)[keep]
        ft = ((uh >= 35) & (uh != 999)).astype(int)   # 997 "hours vary" -> full time
        ft[uh == 997] = 1
        n_kept += keep.sum()

        # ADP universe: private-sector payroll employees, non-farm, non-government
        core = ((cw == "priv") & (sec != "agri") & (sec != "pubadm")).astype(int)

        for band, mask in [("a20_24", (a >= 20) & (a <= 24)),
                           ("a22_25", (a >= 22) & (a <= 25))]:
            if not mask.any():
                continue
            df = pd.DataFrame({"occ": occ[mask], "year": yr[mask], "cw": cw[mask],
                               "sector": sec[mask], "ft": ft[mask], "w": wt[mask]})
            g = df.groupby(["occ", "year", "cw", "sector", "ft"], sort=False)["w"].sum()
            for k, v in g.items():
                key = (k[0], k[1], band, k[2], k[3], k[4])
                acc[key] = acc.get(key, 0.0) + v

            dm = pd.DataFrame({"occ": occ[mask], "year": yr[mask], "month": mo[mask],
                               "core": core[mask], "w": wt[mask]})
            for k, v in dm.groupby(["occ", "year", "month", "core"], sort=False)["w"].sum().items():
                key = (k[0], k[1], k[2], band, k[3])
                accm[key] = accm.get(key, 0.0) + v
        for y, m in set(zip(yr.tolist(), mo.tolist())):
            months.setdefault(y, set()).add(m)

print(f"records read : {n_read:,}\nrecords kept : {n_kept:,}")
P = pd.DataFrame([(k[0], k[1], k[2], k[3], k[4], k[5], v) for k, v in acc.items()],
                 columns=["occ", "year", "band", "cw", "sector", "ft", "emp"])
P = P[P.occ > 0]
P["emp"] = P.emp / P.year.map({y: len(ms) for y, ms in months.items()})
P.to_csv(OUT, index=False)
print(f"wrote {OUT}: {len(P):,} rows, {P.occ.nunique()} occupations, "
      f"years {P.year.min()}-{P.year.max()}")
M = pd.DataFrame([(*k, v) for k, v in accm.items()],
                 columns=["occ", "year", "month", "band", "adpcore", "emp"])
M = M[M.occ > 0]
M.to_csv(OUT_M, index=False)
print(f"wrote {OUT_M}: {len(M):,} rows, months {M.year.min()}-{M.year.max()}, "
      f"last month {M[M.year == M.year.max()].month.max()} of {M.year.max()}")

chk = P[P.band == "a22_25"].groupby("cw").emp.sum() / P[P.band == "a22_25"].year.nunique()
print("\naverage 22-25 employment by class of worker, millions/yr")
for k, v in chk.sort_values(ascending=False).items():
    print(f"  {k:<8}{v/1e6:>8.2f}   ({100*v/chk.sum():.1f}%)")
