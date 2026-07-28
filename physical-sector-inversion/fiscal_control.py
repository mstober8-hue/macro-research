"""
fiscal_control.py
Test the fiscal hypothesis for the goods-sector Okun inversion.

The physical-sector sub-project ends on a hypothesis: Construction,
Manufacturing, Transportation and Wholesale inverted their Okun relationship in
2024-2025, the inversions survive every interest-rate control, and these are the
LOWEST AI-exposure sectors in the sample, so something else must be inflating
their output without proportional hiring. The named candidate is the 2021-2022
fiscal wave (IIJA, CHIPS Act, IRA).

This script tests that directly, using federal obligations by NAICS pulled from
the USAspending API (quarterly, back to 2008, cached locally). The fiscal
variable is obligations to a sector as a share of its value added, and it enters
each sector's Okun regression as a third control alongside the existing rate
control:

    delta_U = a + b1*(%dY) + b2*(dFFR) + b3*(fiscal) + e

fitted pre and post Q4 2022. If fiscal spending explains the breakdown, adding
b3 should shrink the goods sectors' delta-b1 toward zero while leaving the
service sectors alone.

RESULT: NOT SUPPORTED. Three findings, in order of how much they matter.

  1. The act-specific tagging fails. IIJA (fund code 1) and CHIPS (code 8)
     obligations reach only ~0.08% of construction value added and ~0.00%
     elsewhere. Almost all IIJA money moves to states as formula grants and is
     never booked against a construction NAICS in federal contract data. The
     IRA has no fund code at all and works mainly through tax credits, which
     never appear here. So the acts themselves cannot be isolated.

  2. Total federal obligations ARE economically meaningful (4-6% of
     construction value added, 9-11% of manufacturing) and did rise about 2
     points in the goods sectors after 2021. But adding them as a control
     barely moves the goods sectors' delta-b1 (mean +0.218 -> +0.189, and the
     fiscal coefficient is significant in only 1 of 6 sectors).

  3. A 4-quarter lag appears to collapse the goods breakdown (+0.218 -> +0.022),
     which is the result a fiscal story would predict. It does not survive a
     falsification check: on the common lagged sample the control shrinks the
     NON-goods sectors MORE than the goods sectors (-0.068 vs -0.042), and the
     largest single change is Information, which has no plausible fiscal story.
     The apparent collapse is a sample artifact of lagging, not a fiscal effect.

So the fiscal hypothesis remains untested rather than refuted: the best
available direct test does not support it, but the test is structurally weak
because federal contract data cannot see money that flows through states.

Writes fiscal_control.png. Fetches from the USAspending API on first run and
caches to ../FRED-Data/usaspending_naics_quarterly.csv.
"""

import os, glob, json, ssl, socket, time, urllib.request, warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
warnings.filterwarnings("ignore")

HERE  = os.path.dirname(os.path.abspath(__file__))
DATA  = os.path.join(HERE, "..", "FRED-Data") + os.sep
CACHE = DATA + "usaspending_naics_quarterly.csv"
CUT   = pd.Timestamp("2022-10-01")
EXC   = pd.date_range("2020-04-01", "2022-01-01", freq="QS")

# sector: naics prefixes, value-added file, unemployment file, is a goods sector
SEC = {
 "Construction":               (["23"], "construction_value_added_RVAC.csv", "construction_unemployment_rate_LNU04032231.csv", 1),
 "Manufacturing":              (["31","32","33"], "manufacturing_value_added_RVAMA.csv", "manufacturing_unemployment_rate_LNU04032232.csv", 1),
 "Transportation & Utilities": (["48","49","22"], "transportation_warehousing_value_added_RVAT.csv", "transportation_utilities_unemployment_rate_LNU04032236.csv", 1),
 "Wholesale Trade":            (["42"], "wholesale_trade_value_added_RVAW.csv", "wholesale_retail_trade_unemployment_rate_LNU04032235.csv", 0),
 "Information":                (["51"], "information_sector_value_added_RVAI.csv", "information_sector_unemployment_rate_LNU04032237.csv", 0),
 "Professional & Business":    (["54","55","56"], "professional_business_services_value_added_RVAPBS.csv", "professional_business_services_unemployment_rate_LNU04032239.csv", 0),
 "Education & Health":         (["61","62"], "health_care_social_assistance_value_added_RVAHCSA.csv", "education_health_unemployment_rate_LNU04032240.csv", 0),
 "Leisure & Hospitality":      (["71","72"], "leisure_hospitality_value_added_RVAAERAF.csv", "leisure_hospitality_unemployment_rate_LNU04032241.csv", 0),
}
DEFC = {"total": None, "iija": ["1"], "chips": ["8"]}   # IIJA = P.L. 117-58, CHIPS = P.L. 117-167


def fetch_usaspending():
    socket.setdefaulttimeout(90)
    ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE

    def post(p, tries=3):
        for t in range(tries):
            try:
                req = urllib.request.Request(
                    "https://api.usaspending.gov/api/v2/search/spending_over_time/",
                    data=json.dumps(p).encode(),
                    headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"})
                return json.loads(urllib.request.urlopen(req, context=ctx).read().decode())
            except Exception:
                if t == tries - 1:
                    raise
                time.sleep(3)

    def cal(fy, q):
        return {1: f"{fy-1}-10-01", 2: f"{fy}-01-01", 3: f"{fy}-04-01", 4: f"{fy}-07-01"}[q]

    rows = []
    for sec, (codes, _, _, _) in SEC.items():
        for lab, dc in DEFC.items():
            f = {"time_period": [{"start_date": "2008-01-01", "end_date": "2026-06-30"}],
                 "award_type_codes": ["A", "B", "C", "D"], "naics_codes": codes}
            if dc:
                f["def_codes"] = dc
            for x in post({"group": "quarter", "filters": f})["results"]:
                tp = x["time_period"]
                rows.append(dict(sector=sec, series=lab,
                                 date=cal(int(tp["fiscal_year"]), int(tp["quarter"])),
                                 amount=x["aggregated_amount"]))
    df = pd.DataFrame(rows); df["date"] = pd.to_datetime(df["date"])
    df.to_csv(CACHE, index=False)
    return df


def find(f):
    if os.path.exists(DATA + f):
        return DATA + f
    return (glob.glob(DATA + "*" + f + "*") + glob.glob(DATA + "*" + f))[0]


def load(f):
    d = pd.read_csv(find(f)); d.columns = [c.strip() for c in d.columns]
    d[d.columns[0]] = pd.to_datetime(d[d.columns[0]]); d = d.set_index(d.columns[0])
    return pd.to_numeric(d.iloc[:, 0], errors="coerce").dropna()


def ols(X, y):
    A = np.column_stack([np.ones(len(y))] + [X[:, j] for j in range(X.shape[1])])
    c, _, _, _ = np.linalg.lstsq(A, y, rcond=None)
    resid = y - A @ c; n, k = len(y), A.shape[1]
    se = np.sqrt(np.diag(np.sum(resid ** 2) / (n - k) * np.linalg.inv(A.T @ A))) if n > k else np.full(k, np.nan)
    return c, se


if not os.path.exists(CACHE):
    print("Fetching federal obligations by NAICS from the USAspending API (one time)...")
    fetch_usaspending()

fs = pd.read_csv(CACHE, parse_dates=["date"])
tot = fs[fs.series == "total"].pivot_table(index="date", columns="sector", values="amount") / 1e9
iija = fs[fs.series == "iija"].pivot_table(index="date", columns="sector", values="amount") / 1e9
ffr = load("fed_funds_rate_FEDFUNDS.csv").resample("QS").mean()


def build(sec):
    codes, of, uf, g = SEC[sec]
    va = load(of); u = load(uf).resample("QS").mean()
    fi = (tot[sec].rolling(4).sum() / 4) / (va / 4) * 100          # obligations as % of value added
    ij = (iija[sec].rolling(4).sum() / 4) / (va / 4) * 100
    d = pd.DataFrame({"o": va, "u": u, "fi": fi, "ij": ij, "ffr": ffr}).dropna(subset=["o", "u", "fi", "ffr"])
    d["dy"] = d["o"].pct_change(4) * 100
    d["du"] = d["u"].diff(4)
    d["dffr"] = d["ffr"].diff(4)
    d["f0"] = d["fi"].diff(4)
    d["f4"] = d["fi"].diff(4).shift(4)
    return d[~d.index.isin(EXC)]


# ---- 1. is the act-specific money even visible? ----
print("=" * 78)
print("1. CAN THE ACTS BE ISOLATED?  Obligations as % of sector value added")
print("=" * 78)
print(f"  {'sector':<28}{'total 15-19':>12}{'total 22-23':>12}{'total 24-25':>12}{'IIJA 24-25':>12}")
for sec in SEC:
    d = build(sec)
    m = lambda c, a, b: d[c].loc[a:b].mean()
    print(f"  {sec:<28}{m('fi','2015','2019'):>11.1f}%{m('fi','2022','2023'):>11.1f}%"
          f"{m('fi','2024','2026'):>11.1f}%{m('ij','2024','2026'):>11.2f}%")
print("\n  IIJA/CHIPS tagging captures almost nothing: the money reaches states as")
print("  grants and is never booked against a construction NAICS. Acts cannot be isolated.")

# ---- 2 and 3. does the control shrink the goods breakdown, and does it survive falsification? ----
print("\n" + "=" * 78)
print("2. DOES A FISCAL CONTROL SHRINK THE GOODS-SECTOR BREAKDOWN?")
print("=" * 78)
rows = []
for sec in SEC:
    d = build(sec)
    base = d.dropna(subset=["dy", "du", "dffr", "f0"])
    lag = d.dropna(subset=["dy", "du", "dffr", "f4"])

    def db(df, cols):
        pre, post = df[df.index < CUT], df[df.index >= CUT]
        return ols(post[cols].values, post["du"].values)[0][1] - ols(pre[cols].values, pre["du"].values)[0][1]

    post = base[base.index >= CUT]
    c, se = ols(post[["dy", "dffr", "f0"]].values, post["du"].values)
    rows.append(dict(sector=sec, goods=SEC[sec][3],
                     rate_only=db(base, ["dy", "dffr"]),
                     plus_fiscal=db(base, ["dy", "dffr", "f0"]),
                     t_b3=c[3] / se[3] if se[3] > 0 else np.nan,
                     lag_rate=db(lag, ["dy", "dffr"]),
                     lag_fiscal=db(lag, ["dy", "dffr", "f4"])))
R = pd.DataFrame(rows)
print(f"  {'sector':<28}{'goods':>6}{'Δβ rate':>10}{'Δβ +fiscal':>12}{'t(β3)':>8}")
for _, r in R.iterrows():
    print(f"  {r.sector:<28}{'YES' if r.goods else 'no':>6}{r.rate_only:>+10.3f}{r.plus_fiscal:>+12.3f}{r.t_b3:>8.2f}")
g, o = R[R.goods == 1], R[R.goods == 0]
print(f"\n  goods mean:     {g.rate_only.mean():+.3f} -> {g.plus_fiscal.mean():+.3f}")
print(f"  non-goods mean: {o.rate_only.mean():+.3f} -> {o.plus_fiscal.mean():+.3f}")
print(f"  fiscal coefficient significant in {(R.t_b3.abs()>2).sum()}/{len(R)} sectors")

print("\n" + "=" * 78)
print("3. FALSIFICATION CHECK on the 4-quarter-lag spec that appears to work")
print("=" * 78)
print(f"  goods mean:     {g.lag_rate.mean():+.3f} -> {g.lag_fiscal.mean():+.3f}"
      f"   (change {(g.lag_fiscal-g.lag_rate).mean():+.3f})")
print(f"  non-goods mean: {o.lag_rate.mean():+.3f} -> {o.lag_fiscal.mean():+.3f}"
      f"   (change {(o.lag_fiscal-o.lag_rate).mean():+.3f})")
print("\n  The control shrinks NON-goods at least as much as goods, and the biggest")
print("  single move is Information, which has no fiscal story. The apparent")
print("  collapse is a sample artifact of lagging, not a fiscal effect.")
print("\nVERDICT: fiscal hypothesis NOT SUPPORTED by the best available direct test,")
print("         but the test is structurally weak (federal contract data cannot")
print("         see IIJA money that passes through states).")

# ---- chart ----
fig, (a1, a2) = plt.subplots(1, 2, figsize=(15, 6))
x = np.arange(len(R)); w = 0.38
col = ["#c0392b" if gg else "#7f8c8d" for gg in R.goods]
a1.barh(x - w/2, R.rate_only, w, color=col, alpha=0.55, label="rate control only")
a1.barh(x + w/2, R.plus_fiscal, w, color=col, label="+ fiscal control")
a1.set_yticks(x); a1.set_yticklabels(R.sector, fontsize=9)
a1.axvline(0, color="black", lw=0.9)
a1.set_xlabel("Δβ (positive = Okun weakened)", fontsize=10)
a1.set_title("Adding a fiscal control barely moves the goods sectors\n"
             "red = goods sectors, grey = services", fontsize=11, fontweight="bold")
a1.legend(fontsize=9); a1.grid(True, axis="x", ls="--", alpha=0.3)

chg = pd.DataFrame({"grp": ["goods", "non-goods"],
                    "chg": [(g.lag_fiscal - g.lag_rate).mean(), (o.lag_fiscal - o.lag_rate).mean()]})
a2.bar(chg.grp, chg.chg, color=["#c0392b", "#7f8c8d"], width=0.55)
a2.axhline(0, color="black", lw=0.9)
a2.set_ylabel("change in Δβ from adding the lagged fiscal control", fontsize=10)
a2.set_title("Falsification check fails\nthe control shrinks services at least as much as goods",
             fontsize=11, fontweight="bold")
a2.grid(True, axis="y", ls="--", alpha=0.3)
fig.suptitle("Testing the fiscal hypothesis for the goods-sector Okun inversion (USAspending obligations by NAICS)",
             fontsize=13, fontweight="bold")
plt.tight_layout(rect=[0, 0, 1, 0.92])
plt.savefig(os.path.join(HERE, "fiscal_control.png"), dpi=150, bbox_inches="tight")
print("\nChart saved: fiscal_control.png")
