"""
tech_capital_vs_labor.py
The capital-side discriminator: is tech capital fleeing, or flooding in, while tech sheds jobs?

WHY THIS EXISTS
`is_the_slowdown_distinctive.py` establishes that Information's 2024-2026 hiring
slowdown is a genuine anomaly against its own cyclical history, and that the only
other episode where it ranked worst of nine sectors was the 2001 dot-com bust.
It then finds that the obvious discriminator fails: output kept growing while
employment fell in BOTH episodes, and the productivity surge was larger in 2001.
On that evidence an overhang-correction story reproduces the current episode
with an exact precedent and no AI in it.

But "the same shape on the labor side" is not the same thing as "the same event."
The dot-com bust had a specific cause that is directly measurable and that has
nothing to do with the labor market: a collapse in the valuation of and capital
flowing into technology. Equity prices fell about two thirds, funding vanished,
and firms cut staff because the money stopped. If the current episode is the same
kind of event, tech capital should be in retreat now too.

It is not. It is doing the opposite, and by a wide margin. That is the test.

WHY THE CAPITAL SIDE SEPARATES THE TWO STORIES
  A bubble or overhang unwind: capital flees. Valuations fall, investment in the
  technology falls, and employment falls with them. All three move together
  because all three are responding to the same withdrawal of funding.

  Capital-labor substitution: capital does the opposite of labor. Firms spend MORE
  on the technology precisely while employing fewer people, because the spending
  is what displaces the employment. Rising capex alongside falling headcount is
  the signature, and it is not something a funding collapse can produce.

The two stories make opposite predictions about the same period, which is what
makes this worth running.

SERIES NOTE, AND A CORRECTION MADE WHILE BUILDING THIS
Tech investment is BEA's "private fixed investment in information processing
equipment and software" (A679), which ALREADY INCLUDES software. A first cut of
this analysis used Y033 (all nonresidential equipment) and added software to it
separately, which both mismeasured the numerator and double-counted; it produced
a tech share of business investment around 60 percent, which should have been an
immediate signal that something was wrong. The corrected share is around 28 to 33
percent. Real terms come from A679's own chain price index (1947-2013) spliced to
BEA's published real series (2007-2026); the two overlap for 21 quarters and their
year-over-year growth rates correlate +0.995.

Reads FRED-Data/. Writes tech_capital_vs_labor.png.
"""

import os
import glob
import warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

warnings.filterwarnings("ignore")

DATA = "FRED-Data/"
EPISODES = [("2001 dot-com bust", "2000-04-01", "2003-01-01"),
            ("2024-2026 current", "2022-10-01", "2026-04-01")]


def load(f):
    p = DATA + f if os.path.exists(DATA + f) else (glob.glob(DATA + "*" + f) +
                                                   glob.glob(DATA + "*" + f + "*"))[0]
    d = pd.read_csv(p)
    d.columns = [c.strip() for c in d.columns]
    d[d.columns[0]] = pd.to_datetime(d[d.columns[0]])
    d = d.set_index(d.columns[0])
    return pd.to_numeric(d.iloc[:, 0], errors="coerce").dropna()


nasdaq = load("nasdaq_composite_NASDAQCOM.csv").resample("QS").mean()
tin = load("info_processing_equipment_software_investment_A679RC1Q027SBEA.csv")
tpx = load("info_processing_equipment_software_price_index_A679RG3Q086SBEA.csv")
trx = load("info_processing_equipment_software_investment_real_A679RX1Q020SBEA.csv")
pnfi = load("private_nonresidential_fixed_investment_PNFI.csv")
emp = load("information_sector_employment_USINFO.csv").resample("QS").mean()

# splice the discontinued price-index-deflated series onto BEA's published real series
old = (tin / tpx * 100).dropna()
ov = pd.DataFrame({"o": old.pct_change(4) * 100, "n": trx.pct_change(4) * 100}).dropna()
scale = trx.loc["2007-01-01"] / old.loc["2007-01-01"]
real_ti = pd.concat([old.loc[:"2006-10-01"] * scale, trx])
real_ti = real_ti[~real_ti.index.duplicated()].sort_index()
share = (tin / pnfi.reindex(tin.index) * 100).dropna()

print("=" * 100)
print("CAPITAL-SIDE DISCRIMINATOR: tech capital versus tech labor, 2001 against now")
print("=" * 100)
print(f"\nSplice check: over {len(ov)} overlapping quarters "
      f"({ov.index[0].date()} to {ov.index[-1].date()}) the two real")
print(f"series' year-over-year growth rates correlate {ov['o'].corr(ov['n']):+.3f}.\n")


def ch(s, a, b):
    x = s.loc[a:b]
    return (x.iloc[-1] / x.iloc[0] - 1) * 100


print(f"{'episode':<22}{'NASDAQ':>10}{'its trough':>12}{'real tech capex':>17}"
      f"{'tech % of capex':>19}{'INFO jobs':>11}")
for lab, a, b in EPISODES:
    n0 = nasdaq.loc[a:b].iloc[0]
    print(f"{lab:<22}{ch(nasdaq, a, b):>+9.1f}%{(nasdaq.loc[a:b].min()/n0-1)*100:>+11.1f}%"
          f"{ch(real_ti, a, b):>+16.1f}%"
          f"{share.loc[a:b].iloc[0]:>9.1f} to {share.loc[a:b].iloc[-1]:<6.1f}{ch(emp, a, b):>+10.1f}%")

print("\n  The two episodes cost Information almost exactly the same share of its jobs.")
print("  Every capital variable moves in the OPPOSITE direction between them. In 2001 the")
print("  NASDAQ lost two thirds of its value and tech's share of business investment fell.")
print("  Now the NASDAQ has more than doubled with no drawdown below its starting level,")
print("  real tech capex is up over 40 percent, and tech's share of all business fixed")
print("  investment is at its highest in the series.\n")

g = real_ti.pct_change(4) * 100
nn = nasdaq.pct_change(4) * 100
print(f"{'window':<24}{'real tech capex':>17}{'NASDAQ':>12}{'tech % of capex':>18}")
for lab, a, b in [("1997-2000 boom", "1997-01-01", "2000-12-31"),
                  ("2001-2003 bust", "2001-01-01", "2003-12-31"),
                  ("2013-2019 pre-AI", "2013-01-01", "2019-12-31"),
                  ("2020-2022", "2020-01-01", "2022-12-31"),
                  ("2023-2026 current", "2023-01-01", "2026-12-31")]:
    print(f"{lab:<24}{g.loc[a:b].mean():>+16.2f}%{nn.loc[a:b].mean():>+11.1f}%"
          f"{share.loc[a:b].mean():>17.1f}%")

print("\nTech share of all business fixed investment, selected years:")
print("  " + "   ".join(f"{y}: {share.loc[str(y)].mean():.1f}%"
                        for y in [1997, 2000, 2003, 2013, 2019, 2022, 2025]))
print(f"\n  The 2000 bubble peak was {share.loc['2000'].mean():.1f}%. It is "
      f"{share.iloc[-4:].mean():.1f}% now, higher than the")
print("  dot-com peak. Firms are putting a larger share of their capital budget into")
print("  information technology than at any point in the series while cutting technology")
print("  headcount. A funding collapse cannot produce that; capital-labor substitution can.")

print("\nWHAT THIS DOES AND DOES NOT SETTLE")
print("  Settles: the 2001 analogy does not carry. The mechanism that drove 2001, capital")
print("  withdrawal, is not merely absent now, it is running hard in reverse. An overhang")
print("  story can still be told about the pandemic hiring boom, but it cannot borrow")
print("  2001's precedent, because 2001's cause is not present.")
print("  Does not settle: rising tech capex is consistent with AI substitution and also")
print("  with an ordinary capital-deepening boom that happens to coincide with a hiring")
print("  correction. This is a strong disconfirmation of one rival story, not a direct")
print("  measurement of substitution. That still needs task-level evidence.")

# ---- chart -------------------------------------------------------------------
fig, axes = plt.subplots(1, 3, figsize=(19, 6.2))

for ax, (lab, a, b), col in zip(axes[:2], EPISODES, ["#c0392b", "#1f4e79"]):
    idx = lambda s: s.loc[a:b] / s.loc[a:b].iloc[0] * 100
    ax.axhline(100, color="black", lw=1.0, ls="--")
    ax.plot(idx(nasdaq).index, idx(nasdaq).values, lw=2.4, color="#8e44ad", label="NASDAQ")
    ax.plot(idx(real_ti).index, idx(real_ti).values, lw=2.4, color="#16a085",
            label="real tech capex")
    ax.plot(idx(emp).index, idx(emp).values, lw=2.6, color=col, label="Information jobs")
    ax.set_title(f"{lab}\nindexed to 100 at the start", fontsize=11.5, fontweight="bold")
    ax.legend(fontsize=8.5); ax.grid(True, ls="--", alpha=0.35)
    ax.set_ylabel("index", fontsize=10)

ax = axes[2]
s = share.loc["1990-01-01":]
ax.plot(s.index, s.values, lw=2.2, color="#1f4e79")
ax.axvspan(pd.Timestamp("2000-04-01"), pd.Timestamp("2003-01-01"), color="#c0392b",
           alpha=0.16, label="dot-com bust")
ax.axvspan(pd.Timestamp("2022-10-01"), s.index[-1], color="gold", alpha=0.22,
           label="current episode")
ax.set_ylabel("tech share of business fixed investment (%)", fontsize=10)
ax.set_title("Tech's share of business capital spending\nis above its dot-com peak",
             fontsize=11.5, fontweight="bold")
ax.legend(fontsize=8.5); ax.grid(True, ls="--", alpha=0.35)

fig.suptitle("Same job losses, opposite capital conditions: why the 2001 analogy does not carry",
             fontsize=13, fontweight="bold", y=1.02)
plt.tight_layout()
plt.savefig("tech_capital_vs_labor.png", dpi=150, bbox_inches="tight")
print("\nChart saved: tech_capital_vs_labor.png")
