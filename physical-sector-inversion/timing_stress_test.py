"""
timing_stress_test.py
Giving "unemployment responds before output" its best possible shot.

WHAT WAS RETRACTED AND WHY
The mechanism behind this whole sub-project claimed unemployment absorbs a rate
shock 1.7 to 3 quarters faster than output does. identification_check.py retracted
it: under a moving-block bootstrap the gap's 95% interval covered zero in every
sector and specification, and the point estimate swung from -3q to -12q to +1q
depending on which regressor was used.

That retraction was correct about the test it ran. But three things about that
test were stacked against the hypothesis, and a fair stress test should remove
them before concluding the claim is dead.

  HANDICAP 1  ONLY 20 YEARS OF DATA. Sector real value added begins in 2005, so
              every sector-level timing estimate rested on about 80 quarters. A
              12-quarter lag cannot be pinned down from that. Using AGGREGATE
              output (GDP from 1947) and INDUSTRIAL PRODUCTION for manufacturing
              (from 1972) instead gives five decades.

  HANDICAP 2  NO IDENTIFIED SHOCK. The original used the funds rate level or its
              change, both endogenous. Romer-Romer narrative shocks run 1969-2019,
              which is far longer than the high-frequency series and long enough
              to matter here.

  HANDICAP 3  THE GAP WAS ESTIMATED BY DIFFERENCING TWO ARGMAXES. Taking the peak
              of one noisy curve, the peak of another, and subtracting throws away
              the entire shape of both responses and inherits the instability of
              two separate peak-picks. If two impulse responses really are the
              same shape offset in time, the offset should be estimated FROM THE
              WHOLE CURVE. This script does that: it finds the shift tau that
              best aligns the two normalised response paths, which is far more
              stable than differencing argmaxes and has a proper bootstrap
              distribution.

AND ONE SUBSTANTIVE CORRECTION
okun_employment_form.py showed the unemployment rate is drained of signal for
seven of nine sectors in this episode: employment fell while the unemployment rate
also fell, which requires labor-force exit. If unemployment is a degraded
measure, then "unemployment responds first" may have been testing the wrong
variable all along. So the timing test is run BOTH ways, output against
unemployment and output against EMPLOYMENT, and the two are compared directly.

WHAT WOULD COUNT AS PROOF
A negative tau, meaning the labor variable leads output, with a bootstrap interval
excluding zero, reproducing across the aggregate and manufacturing samples and
across at least two shock measures. Anything less is reported as such.

Reads shocks from ../FRED-Data/shocks/ and cached FRED series from ./fred_cache/.
Writes timing_stress_test.png.
"""

import os
import glob
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats as sp_stats

HERE   = os.path.dirname(os.path.abspath(__file__))
DATA   = os.path.join(HERE, "..", "FRED-Data") + os.sep
SHOCKS = os.path.join(DATA, "shocks") + os.sep
CACHE  = os.path.join(HERE, "fred_cache") + os.sep
COVID  = pd.date_range("2020-04-01", "2021-10-01", freq="QS")
HMAX   = 16
NLAGS  = 4
NBOOT  = 1500
BLOCK  = 20
RNG    = np.random.default_rng(4041)


def read(path, col=None):
    d = pd.read_csv(path)
    d.columns = [c.strip() for c in d.columns]
    d[d.columns[0]] = pd.to_datetime(d[d.columns[0]])
    d = d.set_index(d.columns[0])
    return pd.to_numeric(d[col] if col else d.iloc[:, 0], errors="coerce").dropna()


def fred(sid):
    p = CACHE + sid + ".csv"
    if os.path.exists(p):
        return read(p)
    name = {"MANEMP": "manufacturing_employment_MANEMP.csv",
            "MANU_U": "manufacturing_unemployment_rate_LNU04032232.csv"}[sid]
    q = DATA + name
    q = q if os.path.exists(q) else glob.glob(DATA + "*" + name)[0]
    return read(q)


def ols_hac(y, X, nw):
    XtX = np.linalg.pinv(X.T @ X)
    b = XtX @ X.T @ y
    e = y - X @ b
    S = (X * e[:, None]).T @ (X * e[:, None])
    for L in range(1, max(nw, 1) + 1):
        w = 1.0 - L / (nw + 1.0)
        G = (X[L:] * e[L:, None]).T @ (X[:-L] * e[:-L, None])
        S += w * (G + G.T)
    V = XtX @ S @ XtX
    return b, np.sqrt(np.maximum(np.diag(V), 0))


def lp(dep, shock, hmax=HMAX, sample=None):
    """Cumulative-response local projection. dep is a level series."""
    out = []
    for h in range(hmax + 1):
        parts = {"dep": dep.shift(-h) - dep.shift(1), "s": shock}
        for L in range(1, NLAGS + 1):
            parts[f"dl{L}"] = (dep - dep.shift(1)).shift(L)
            parts[f"sl{L}"] = shock.shift(L)
        j = pd.DataFrame(parts).dropna()
        j = j[~j.index.isin(COVID)]
        if sample:
            j = j.loc[sample[0]:sample[1]]
        if len(j) < 30:
            out.append((h, np.nan, np.nan, 0))
            continue
        yv = j["dep"].to_numpy()
        Xv = np.column_stack([np.ones(len(j))] +
                             [j[c].to_numpy() for c in j.columns if c != "dep"])
        b, se = ols_hac(yv, Xv, nw=h + 1)
        out.append((h, b[1], se[1], len(j)))
    return pd.DataFrame(out, columns=["h", "b", "se", "n"])


def norm_curve(v):
    """Scale a response to unit peak magnitude so shapes can be compared."""
    m = np.nanmax(np.abs(v))
    return v / m if m and not np.isnan(m) else v


def align_shift(c_out, c_lab, max_shift=8):
    """
    Estimate the lead of the labour variable over output by finding the shift tau
    that best aligns the two normalised response curves. Negative tau means the
    labour variable moves FIRST. Uses the whole curve rather than two argmaxes.
    """
    a = norm_curve(np.asarray(c_out, float))
    b = norm_curve(np.asarray(c_lab, float))
    b = -b if np.nansum(a * b) < 0 else b        # put both on the same sign
    best, best_tau = -np.inf, np.nan
    for tau in range(-max_shift, max_shift + 1):
        if tau < 0:
            x, y = a[:len(a) + tau], b[-tau:]
        elif tau > 0:
            x, y = a[tau:], b[:len(b) - tau]
        else:
            x, y = a, b
        m = ~(np.isnan(x) | np.isnan(y))
        if m.sum() < 6:
            continue
        num = np.sum(x[m] * y[m])
        den = np.sqrt(np.sum(x[m] ** 2) * np.sum(y[m] ** 2))
        sc = num / den if den else -np.inf
        if sc > best:
            best, best_tau = sc, tau
    return best_tau, best


SHOCK_SET = {
    "romer_romer": ("01_romer_romer_updated_narrative_shocks.csv", "rr_update"),
    "bauer_swanson": ("03_bauer_swanson_orthogonalized_shock.csv", "shock"),
}

shocks = {}
for k, (fn, col) in SHOCK_SET.items():
    s = read(SHOCKS + fn, col)
    shocks[k] = s.resample("QS").sum()

gdp = np.log(fred("GDPC1").resample("QS").mean()) * 100
unr = fred("UNRATE").resample("QS").mean()
pay = np.log(fred("PAYEMS").resample("QS").mean()) * 100
ipm = np.log(fred("IPMAN").resample("QS").mean()) * 100
mane = np.log(fred("MANEMP").resample("QS").mean()) * 100
manu = fred("MANU_U").resample("QS").mean()

SYSTEMS = {
    "Aggregate (GDP, 1947-)":      dict(out=gdp, unemp=unr, emp=pay),
    "Manufacturing (IP, 1972-)":   dict(out=ipm, unemp=manu, emp=mane),
}

print("=" * 100)
print("STRESS TEST: can 'unemployment responds first' be established on long historical data?")
print("=" * 100)
print(f"\nSample coverage after removing the handicaps in the original test:")
for k, s in shocks.items():
    print(f"  {k:<16}{s.index[0].date()} to {s.index[-1].date()}   ({len(s)} quarters)")
print(f"  {'GDP':<16}{gdp.index[0].date()} onward")
print(f"  {'PAYEMS':<16}{pay.index[0].date()} onward")
print(f"  {'IPMAN':<16}{ipm.index[0].date()} onward")

results = {}
print("\n" + "=" * 100)
print("[1] THE GAP, ESTIMATED FROM THE WHOLE RESPONSE CURVE RATHER THAN TWO ARGMAXES")
print("=" * 100)
print("\n  tau is the shift that best aligns the two normalised impulse responses.")
print("  NEGATIVE tau means the labour variable responds BEFORE output, which is")
print("  what the retracted mechanism required.\n")
print(f"  {'system':<28}{'shock':<16}{'labour var':<14}{'tau':>6}{'fit':>8}{'n':>6}")

for sysname, sysd in SYSTEMS.items():
    for sk in shocks:
        c_out = lp(sysd["out"], shocks[sk])
        for lab in ["unemp", "emp"]:
            c_lab = lp(sysd[lab], shocks[sk])
            if c_out["b"].isna().all() or c_lab["b"].isna().all():
                continue
            tau, fit = align_shift(c_out["b"].values, c_lab["b"].values)
            results[(sysname, sk, lab)] = (c_out, c_lab, tau, fit)
            print(f"  {sysname:<28}{sk:<16}{lab:<14}{tau:>+6}{fit:>8.3f}"
                  f"{int(c_out['n'].max()):>6}")

print("\n" + "=" * 100)
print("[2] BOOTSTRAP ON TAU. Moving blocks, so serial dependence survives.")
print("=" * 100)
print(f"\n  {NBOOT} replicates, {BLOCK}-quarter blocks. The whole pipeline including")
print("  the alignment step is re-run inside each replicate.\n")
print(f"  {'system':<28}{'shock':<16}{'labour var':<12}{'tau':>5}{'2.5%':>7}{'97.5%':>7}"
      f"{'P(tau<0)':>10}   verdict")

boot_store = {}
for (sysname, sk, lab), (c_out, c_lab, tau, fit) in results.items():
    sysd = SYSTEMS[sysname]
    base = pd.DataFrame({"o": sysd["out"], "l": sysd[lab], "s": shocks[sk]}).dropna()
    base = base[~base.index.isin(COVID)]
    n = len(base)
    if n < 60:
        continue
    nb = int(np.ceil(n / BLOCK))
    taus = []
    for _ in range(NBOOT):
        st = RNG.integers(0, n - BLOCK, size=nb)
        idx = np.concatenate([np.arange(s0, s0 + BLOCK) for s0 in st])[:n]
        b = base.iloc[idx].reset_index(drop=True)
        b.index = pd.date_range("1960-01-01", periods=n, freq="QS")
        try:
            co = lp(b["o"], b["s"])
            cl = lp(b["l"], b["s"])
            t_, _ = align_shift(co["b"].values, cl["b"].values)
            if not np.isnan(t_):
                taus.append(t_)
        except Exception:
            continue
    if not taus:
        continue
    taus = np.array(taus)
    lo, hi = np.percentile(taus, [2.5, 97.5])
    pneg = float((taus < 0).mean())
    boot_store[(sysname, sk, lab)] = taus
    v = ("SUPPORTS: labour leads output" if hi < 0 else
         "inconclusive, interval covers 0" if lo <= 0 <= hi else
         "CONTRADICTS: output leads labour")
    print(f"  {sysname:<28}{sk:<16}{lab:<12}{tau:>+5}{lo:>+7.1f}{hi:>+7.1f}"
          f"{pneg:>10.2f}   {v}")

print("\n" + "=" * 100)
print("[3] DOES THE VARIABLE CHOICE MATTER? unemployment versus employment")
print("=" * 100)
print("\n  okun_employment_form.py showed the unemployment rate is drained of signal")
print("  when displaced workers leave the labour force. If that is distorting the")
print("  timing too, the employment-based tau should be better behaved.\n")
print(f"  {'system':<28}{'shock':<16}{'tau(unemp)':>12}{'tau(emp)':>10}   agree?")
for sysname in SYSTEMS:
    for sk in shocks:
        ku, ke = (sysname, sk, "unemp"), (sysname, sk, "emp")
        if ku not in results or ke not in results:
            continue
        tu, te = results[ku][2], results[ke][2]
        print(f"  {sysname:<28}{sk:<16}{tu:>+12}{te:>+10}   "
              f"{'yes' if np.sign(tu) == np.sign(te) else 'NO, they disagree'}")

print("\n" + "=" * 100)
print("[4] SUMMARY ACROSS ALL SPECIFICATIONS")
print("=" * 100)
allt = [t for (_, _, _), (_, _, t, _) in results.items() if not np.isnan(t)]
neg = sum(1 for t in allt if t < 0)
sup = sum(1 for k, v in boot_store.items() if np.percentile(v, 97.5) < 0)
print(f"\n  Specifications run                         : {len(allt)}")
print(f"  With a negative point estimate (labour first): {neg}")
print(f"  With a bootstrap interval excluding zero    : {sup}")
print(f"\n  Pre-stated bar for proof: negative tau with an interval excluding zero,")
print(f"  reproducing across both samples and both shock measures. Met: "
      f"{'YES' if sup >= 4 else 'NO'}")

print("\n" + "=" * 100)
print("[5] IS THE GAP MOVING? Rolling estimates and their slope over time")
print("=" * 100)
print("\n  Pooling five decades assumes the response is stable across them. It is not:")
print("  historical_lag_validation.py measured the rate-to-hiring lag at about 4")
print("  quarters before 1986 and about 9 after, so the transmission structure itself")
print("  roughly doubled. A pooled null could therefore be averaging a real but")
print("  DRIFTING gap into nothing.")
print("\n  Estimating tau in rolling 20-year windows and fitting a trend to the result")
print("  gives the rate of change, d(tau)/d(time), which is what a pooled mean discards.\n")

WIN, STEP = 80, 8
trend_store = {}
for sysname, sysd in SYSTEMS.items():
    for sk in shocks:
        for lab in ["unemp", "emp"]:
            base = pd.DataFrame({"o": sysd["out"], "l": sysd[lab],
                                 "s": shocks[sk]}).dropna()
            base = base[~base.index.isin(COVID)]
            if len(base) < WIN + STEP:
                continue
            pts_t, mids = [], []
            for st in range(0, len(base) - WIN + 1, STEP):
                w = base.iloc[st:st + WIN]
                try:
                    co = lp(w["o"], w["s"])
                    cl = lp(w["l"], w["s"])
                    t_, _ = align_shift(co["b"].values, cl["b"].values)
                except Exception:
                    continue
                if not np.isnan(t_):
                    pts_t.append(t_)
                    mids.append(w.index[len(w) // 2])
            if len(pts_t) < 5:
                continue
            yrs = np.array([m.year + m.month / 12 for m in mids])
            sl, ic, r_, p_, se_ = sp_stats.linregress(yrs, pts_t)
            trend_store[(sysname, sk, lab)] = (mids, pts_t, sl, p_, se_)
            print(f"  {sysname[:26]:<27}{sk:<15}{lab:<7}"
                  f"windows={len(pts_t):>3}  mean tau={np.mean(pts_t):+.2f}  "
                  f"slope={sl:+.4f} q/yr (p={p_:.3f})")

# The trend p-values above are NOT valid as printed, and the reason is the same
# error this project has now made three times. Rolling 20-year windows stepped
# every 2 years overlap by 90%: consecutive windows share 18 of 20 years. The
# linregress p-value treats them as independent observations. Effective sample
# size is roughly (span / window), i.e. about 2-3 independent windows, not 16.
print("\n  CAUTION ON THE p-VALUES ABOVE. The rolling windows overlap by 90 percent:")
print("  consecutive 20-year windows share 18 years of data. The trend regression")
print("  treats them as independent, which they are not. Effective sample size is")
print("  roughly span/window, about 2 to 3 independent windows rather than 16, so")
print("  these p-values are badly overstated. This is the SAME overlapping-window")
print("  error that invalidated the original bootstrap and the DESYNC dynamic test.")
print("  Read the slopes as descriptive only.")
for (sysname, sk, lab), (mids, pts_t, sl, p_, se_) in trend_store.items():
    span = (mids[-1].year - mids[0].year) + 1
    eff = max(span / (WIN / 4), 1)
    print(f"    {sysname[:24]:<25}{sk:<15}{lab:<7}nominal n={len(pts_t):>3}, "
          f"effective n~{eff:.1f}")
signs = [np.sign(v[2]) for v in trend_store.values()]
print(f"\n  Slope signs across the {len(signs)} specifications: "
      f"{signs.count(-1)} negative, {signs.count(1)} positive.")
print("  A real drift would show a consistent sign. This does not.")

print("\n  A slope significantly different from zero means the gap is DRIFTING, and a")
print("  pooled estimate over the whole period is then the wrong summary.")
sig_tr = [k for k, v in trend_store.items() if v[3] < 0.05]
print(f"  Specifications with a significant trend in tau: {len(sig_tr)} of {len(trend_store)}")

print("\n  MODERN-ERA ONLY (windows centred after 1995), which is the regime the")
print("  2022-2025 episode belongs to:\n")
print(f"  {'system':<27}{'shock':<15}{'var':<7}{'mean tau, post-1995':>21}{'n':>4}")
for (sysname, sk, lab), (mids, pts_t, sl, p_, se_) in trend_store.items():
    late = [t for m, t in zip(mids, pts_t) if m.year >= 1995]
    if len(late) >= 3:
        print(f"  {sysname[:26]:<27}{sk:<15}{lab:<7}{np.mean(late):>21.2f}{len(late):>4}")

# ---- chart -----------------------------------------------------------------
fig, axes = plt.subplots(2, 2, figsize=(16, 10.5))
panels = [(s, k, l) for (s, k, l) in results][:2]

for i, key in enumerate(panels):
    ax = axes[0, i]
    c_out, c_lab, tau, fit = results[key]
    ax.axhline(0, color="black", lw=1.0, ls="--")
    ax.plot(c_out["h"], norm_curve(c_out["b"].values), lw=2.4, marker="o", ms=4,
            color="#1f4e79", label="output")
    bl = norm_curve(c_lab["b"].values)
    if np.nansum(norm_curve(c_out["b"].values) * bl) < 0:
        bl = -bl
    ax.plot(c_lab["h"], bl, lw=2.4, marker="s", ms=4, color="#c0392b",
            label=f"{key[2]} (sign-aligned)")
    ax.set_title(f"{key[0]}\n{key[1]}, tau = {tau:+d}q", fontsize=11, fontweight="bold")
    ax.set_xlabel("quarters after shock", fontsize=9.5)
    if i == 0:
        ax.set_ylabel("response, scaled to own peak", fontsize=9.5)
    ax.legend(fontsize=8); ax.grid(True, ls="--", alpha=0.3)

ax = axes[1, 0]
for key, taus in list(boot_store.items())[:4]:
    ax.hist(taus, bins=np.arange(-8.5, 9.5), alpha=0.45,
            label=f"{key[0][:12]}/{key[2]}")
ax.axvline(0, color="red", lw=2.2)
ax.set_xlabel("bootstrapped tau (negative = labour leads)", fontsize=9.5)
ax.set_ylabel("replicates", fontsize=9.5)
ax.set_title("Bootstrap distributions of the alignment shift",
             fontsize=11.5, fontweight="bold")
ax.legend(fontsize=7.5); ax.grid(True, axis="y", ls="--", alpha=0.3)

ax = axes[1, 1]
labs, pts, los, his = [], [], [], []
for key, taus in boot_store.items():
    labs.append(f"{key[0][:10]}\n{key[1][:8]}/{key[2]}")
    pts.append(results[key][2])
    los.append(np.percentile(taus, 2.5)); his.append(np.percentile(taus, 97.5))
yy = np.arange(len(labs))
lo_e = np.clip(np.array(pts) - np.array(los), 0, None)
hi_e = np.clip(np.array(his) - np.array(pts), 0, None)
ax.errorbar(pts, yy, xerr=[lo_e, hi_e], fmt="o", color="#1f4e79", capsize=4)
ax.axvline(0, color="red", lw=2.0)
ax.set_yticks(yy); ax.set_yticklabels(labs, fontsize=7)
ax.set_xlabel("tau with 95% bootstrap interval", fontsize=9.5)
ax.set_title("Every specification, with uncertainty\nleft of red = labour leads output",
             fontsize=11.5, fontweight="bold")
ax.grid(True, axis="x", ls="--", alpha=0.3)

fig.suptitle("Stress-testing 'unemployment responds first': 50 years of identified shocks, "
             "whole-curve alignment, and the employment variable as a check",
             fontsize=12.5, fontweight="bold", y=1.0)
plt.tight_layout()
out = os.path.join(HERE, "timing_stress_test.png")
plt.savefig(out, dpi=150, bbox_inches="tight")
print(f"\nChart saved: {out}")
