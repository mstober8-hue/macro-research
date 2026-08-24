"""
window_robustness.py
The test that decides whether the employment-form break is real.

WHY THIS IS THE DECIDING TEST
why_in_sync.py killed the original goods-sector "Okun inversion" with one
observation: measured on the UNEMPLOYMENT form, it reverses at 20-quarter
windows. Three of four sectors go negative again, meaning the law holds. A
structural break should not care whether you look through a 12-quarter or a
20-quarter window; a short-window artifact does. That is why this folder's
headline conclusion became "the hiring slowdown is real, the inversion is not."

okun_decomposed.py then found the inversion is LARGER when measured on
employment instead of unemployment, and employment is a headcount that
labour-force exit cannot distort. If that employment-form break also dissolves at
20 quarters, both forms are short-window artifacts and nothing changes. If it
survives where the unemployment form did not, the folder's headline conclusion is
wrong and the break is real.

A CONFOUND THE ORIGINAL TEST DID NOT CONTROL FOR
A 20-quarter window ending in 2025 reaches back to 2020. COVID was the single
most Okun-consistent episode in the entire sample: output collapsed and jobs
vanished together, driving rolling correlations to between -0.68 and -0.97. So
lengthening the window does two things at once, it adds more of the recent period
AND it drags COVID in, and COVID alone would push the correlation back toward
normal regardless of what happened in 2024-2025.

That makes the original 20-quarter reversal ambiguous. This script separates the
two by running every window length twice, once with COVID quarters left in and
once with them removed before the windows are formed, so a "20-quarter window"
means 20 non-COVID quarters.

INFERENCE
Rolling windows overlap heavily, so ordinary p-values are invalid, as this project
has now learned three separate times. Significance here is a circular-shift
bootstrap, which preserves each series' own autocorrelation exactly while
destroying the relationship between them.

Reads FRED CSVs from ../FRED-Data/. Writes window_robustness.png.
"""

import os
import glob
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE  = os.path.dirname(os.path.abspath(__file__))
DATA  = os.path.join(HERE, "..", "FRED-Data") + os.sep
COVID = pd.date_range("2020-04-01", "2021-10-01", freq="QS")
WINDOWS = [8, 12, 16, 20, 24]
NBOOT = 4000
RNG = np.random.default_rng(90210)

SEC = {
    "Construction": ("construction_value_added_RVAC.csv",
                     "construction_unemployment_rate_LNU04032231.csv",
                     ["construction_employment_USCONS.csv"], "#1f3b73"),
    "Manufacturing": ("manufacturing_value_added_RVAMA.csv",
                      "manufacturing_unemployment_rate_LNU04032232.csv",
                      ["manufacturing_employment_MANEMP.csv"], "#3f7cac"),
    "Transportation": ("transportation_warehousing_value_added_RVAT.csv",
                       "transportation_utilities_unemployment_rate_LNU04032236.csv",
                       ["transportation_warehousing_employment_CES4300000001.csv",
                        "utilities_employment_CES4422000001.csv"], "#6fb0d6"),
    "Wholesale": ("wholesale_trade_value_added_RVAW.csv",
                  "wholesale_retail_trade_unemployment_rate_LNU04032235.csv",
                  ["wholesale_trade_employment_USWTRADE.csv"], "#9dc6e0"),
}


def rd(n):
    p = DATA + n if os.path.exists(DATA + n) else glob.glob(DATA + "*" + n)[0]
    d = pd.read_csv(p)
    d.columns = [c.strip() for c in d.columns]
    d[d.columns[0]] = pd.to_datetime(d[d.columns[0]])
    d = d.set_index(d.columns[0])
    return pd.to_numeric(d.iloc[:, 0], errors="coerce").dropna()


def roll_corr(a, b, w, drop_covid):
    d = pd.DataFrame({"a": a, "b": b}).dropna()
    if drop_covid:
        d = d[~d.index.isin(COVID)]
    idx = d.index.tolist()
    o = {}
    for i in range(w, len(idx) + 1):
        seg = d.iloc[i - w:i]
        if seg.a.std() > 1e-9 and seg.b.std() > 1e-9:
            o[idx[i - 1]] = np.corrcoef(seg.a, seg.b)[0, 1]
    return pd.Series(o)


def matched_null_p(a, b, obs, n_obs, tail):
    """
    Circular-shift null drawn at the SAME window length as the observed statistic.
    An earlier version compared an 8-quarter statistic against a null built from
    full-length series, whose spread is far smaller, which returned p = 1.0 for a
    strongly negative correlation. Window length must match.
    """
    d = pd.DataFrame({"a": a, "b": b}).dropna()
    d = d[~d.index.isin(COVID)]
    x, y = d.a.to_numpy(), d.b.to_numpy()
    if len(x) < n_obs + 5 or np.isnan(obs):
        return np.nan
    vals = []
    for _ in range(NBOOT):
        ys = np.roll(y, RNG.integers(1, len(y) - 1))
        st = RNG.integers(0, len(x) - n_obs)
        s1, s2 = x[st:st + n_obs], ys[st:st + n_obs]
        if np.std(s1) > 1e-9 and np.std(s2) > 1e-9:
            vals.append(np.corrcoef(s1, s2)[0, 1])
    v = np.array(vals)
    return float((v <= obs).mean()) if tail == "low" else float((v >= obs).mean())


data = {}
for nm, (of, uf, efs, _) in SEC.items():
    y = (rd(of).pct_change(4) * 100).dropna()
    u = rd(uf).resample("QS").mean().diff(4).dropna()
    e = None
    for f in efs:
        x = rd(f).resample("QS").mean()
        e = x if e is None else e.add(x, fill_value=np.nan)
    data[nm] = (y, u, (e.pct_change(4) * 100).dropna())

print("=" * 100)
print("WINDOW-LENGTH ROBUSTNESS: does the employment-form break survive where the")
print("unemployment-form one dissolved?")
print("=" * 100)
print("\n  Unemployment form: normal NEGATIVE. Break means POSITIVE. Reported as the MAX")
print("  over 2024-2026, matching why_in_sync.py.")
print("  Employment form:   normal POSITIVE. Break means NEGATIVE. Reported as the MIN.\n")

for drop in [False, True]:
    tag = "COVID REMOVED before windowing" if drop else "COVID INCLUDED (as in why_in_sync.py)"
    print(f"\n  --- {tag} ---\n")
    print(f"  {'sector':<16}{'form':<7}" + "".join(f"{w:>8}q" for w in WINDOWS))
    for nm in SEC:
        y, u, eg = data[nm]
        ru, re_ = [], []
        for w in WINDOWS:
            a = roll_corr(y, u, w, drop)
            b = roll_corr(y, eg, w, drop)
            a2 = a.loc["2024":"2026"]
            b2 = b.loc["2024":"2026"]
            ru.append(a2.max() if len(a2) else np.nan)
            re_.append(b2.min() if len(b2) else np.nan)
        print(f"  {nm:<16}{'unemp':<7}" + "".join(f"{v:>+9.2f}" for v in ru))
        print(f"  {'':<16}{'emp':<7}" + "".join(f"{v:>+9.2f}" for v in re_))

print("\n" + "=" * 100)
print("THE DECIDING COMPARISON: sign at the 20-quarter window")
print("=" * 100)
print("\n  why_in_sync.py's finding was that at 20 quarters the unemployment-form")
print("  inversion reverses. Does the employment-form break do the same?\n")
print(f"  {'sector':<16}{'COVID in: unemp':>17}{'emp':>8}   {'COVID out: unemp':>18}{'emp':>8}")
survive_in, survive_out = 0, 0
for nm in SEC:
    y, u, eg = data[nm]
    row = []
    for drop in [False, True]:
        a = roll_corr(y, u, 20, drop).loc["2024":"2026"]
        b = roll_corr(y, eg, 20, drop).loc["2024":"2026"]
        au = a.max() if len(a) else np.nan
        be = b.min() if len(b) else np.nan
        row += [au, be]
        if not drop and be < 0:
            survive_in += 1
        if drop and be < 0:
            survive_out += 1
    print(f"  {nm:<16}{row[0]:>+17.2f}{row[1]:>+8.2f}   {row[2]:>+18.2f}{row[3]:>+8.2f}")
print(f"\n  Employment-form break still negative at 20q, COVID included : "
      f"{survive_in} of {len(SEC)}")
print(f"  Employment-form break still negative at 20q, COVID removed  : "
      f"{survive_out} of {len(SEC)}")

print("\n" + "=" * 100)
print("IS THE EMPLOYMENT-FORM BREAK SIGNIFICANT? Matched-length circular-shift bootstrap")
print("=" * 100)
print("\n  Tested on the POOLED 2024-2026 correlation rather than a rolling mean, because")
print("  a rolling value indexed at t is built from t-11 to t and therefore describes")
print("  an earlier period than its label suggests.\n")
print(f"  {'sector':<16}{'2013-19':>10}{'2024-26':>10}{'n':>4}{'boot p':>9}   verdict")
for nm in SEC:
    y, u, eg = data[nm]
    d1 = pd.DataFrame({"a": y, "b": eg}).dropna().loc["2013":"2019"]
    d1 = d1[~d1.index.isin(COVID)]
    d2 = pd.DataFrame({"a": y, "b": eg}).dropna().loc["2024":"2026"]
    d2 = d2[~d2.index.isin(COVID)]
    pre = np.corrcoef(d1.a, d1.b)[0, 1] if len(d1) > 3 else np.nan
    cur = np.corrcoef(d2.a, d2.b)[0, 1] if len(d2) > 3 else np.nan
    p = matched_null_p(y, eg, cur, len(d2), "low")
    v = "significant break" if (not np.isnan(p) and p < 0.05) else "no significant break"
    print(f"  {nm:<16}{pre:>+10.3f}{cur:>+10.3f}{len(d2):>4}{p:>9.3f}   {v}")

fig, axes = plt.subplots(1, 2, figsize=(16, 6.2))
for ax, drop in zip(axes, [False, True]):
    for nm, (_, _, _, c) in SEC.items():
        y, u, eg = data[nm]
        vals = []
        for w in WINDOWS:
            b = roll_corr(y, eg, w, drop).loc["2024":"2026"]
            vals.append(b.min() if len(b) else np.nan)
        ax.plot(WINDOWS, vals, marker="o", lw=2.4, color=c, label=f"{nm} (employment)")
        vu = []
        for w in WINDOWS:
            a = roll_corr(y, u, w, drop).loc["2024":"2026"]
            vu.append(a.max() if len(a) else np.nan)
        ax.plot(WINDOWS, vu, marker="s", lw=1.6, ls="--", color=c, alpha=0.55)
    ax.axhline(0, color="black", lw=1.3)
    ax.set_xlabel("rolling window length (quarters)", fontsize=10)
    ax.set_ylabel("extreme 2024-26 correlation", fontsize=10)
    ax.set_title(("COVID removed before windowing" if drop
                  else "COVID included (original test)"), fontsize=12, fontweight="bold")
    ax.grid(True, ls="--", alpha=0.3)
axes[0].legend(fontsize=8, loc="upper left")
axes[0].text(0.02, 0.03, "solid = employment form (break is negative)\n"
                          "dashed = unemployment form (break is positive)",
             transform=axes[0].transAxes, fontsize=8)
fig.suptitle("Does the break survive longer windows? Employment form vs unemployment form, "
             "with and without COVID in the window", fontsize=13, fontweight="bold", y=1.0)
plt.tight_layout()
out = os.path.join(HERE, "window_robustness.png")
plt.savefig(out, dpi=150, bbox_inches="tight")
print(f"\nChart saved: {out}")
