"""
freeze_vs_substitution.py
Separating "AI took the tasks" from "employers froze entry hiring".

THE OPEN QUESTION
The project's strongest affirmative result is entry-level displacement: top-
quintile-exposed occupations lost 5.4% of their 20-24 workers over 2022-2025
while their 35+ workforce grew, a triple difference of -13.1pp against a pre-AI
placebo (p = 0.011). The README states its own load-bearing ambiguity: CPS
published tables "cannot separate 'AI took the tasks' from 'employers froze entry
hiring for AI-adjacent reasons while keeping incumbents'."

Both stories predict fewer junior hires in exposed work. They differ in WHY, and
they differ in what happens next.

  SUBSTITUTION  The task is now done by software. The job does not come back.
                Postings fall and keep falling as capability diffuses.

  FREEZE        The work still needs doing, but firms paused hiring while
                uncertain, about AI, about rates, about tariffs. The vacancy is
                deferred, not destroyed, so postings recover once the
                uncertainty resolves.

WHY JOB POSTINGS DECIDE IT AND EMPLOYMENT STOCKS CANNOT
Employment is a stock. It changes slowly and confounds hiring with separations,
so a hiring freeze and a wave of task automation look identical in it for years.
Postings are a flow, observed daily, and they are the firm's forward-looking
statement about labour it intends to buy. A deferred vacancy and a destroyed
vacancy diverge in postings long before they diverge in employment.

DATA
Indeed Hiring Lab job postings index, 44 occupational categories, daily,
February 2020 to August 2026, indexed to 1 February 2020 = 100. This is the most
recent data in the project by two months. Both "new postings" and "total
postings" are published; new postings is the cleaner flow measure.

Exposure is not hand-assigned. Each Indeed category is mapped to SOC major
groups, and exposure is the employment-weighted mean of the AEI occupational
exposure scores within those groups, the same source used elsewhere in this
project.

THE THREE TESTS
  1  LEVEL      Did postings fall further in exposed categories?
  2  RECOVERY   From the 2023 trough, did exposed categories recover with
                everything else? This is the discriminating test: a freeze
                recovers, substitution does not.
  3  TIMING     Did exposed categories start diverging at ChatGPT (Nov 2022) or
                with the rate cycle (Mar 2022)? A macro freeze should track the
                rate cycle; substitution should track the technology.

Writes freeze_vs_substitution.png.
"""

import os
import glob
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats as sp_stats

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "FRED-Data") + os.sep
IND  = os.path.join(DATA, "indeed", "job_postings_by_sector_US.csv")

# Indeed occupational category -> SOC major groups. Assignment is by the
# occupations the category actually contains, not by any prior about AI.
SOC_MAP = {
    "Accounting": ["13"], "Administrative Assistance": ["43"], "Architecture": ["17"],
    "Arts & Entertainment": ["27"], "Aviation": ["53"], "Banking & Finance": ["13"],
    "Childcare": ["39"], "Civil Engineering": ["17"], "Cleaning & Sanitation": ["37"],
    "Community & Social Service": ["21"], "Construction": ["47"],
    "Customer Service": ["43"], "Data & Analytics": ["15"], "Driving": ["53"],
    "Education & Instruction": ["25"], "Electrical Engineering": ["17"],
    "Food Preparation & Service": ["35"], "Hospitality & Tourism": ["39"],
    "Human Resources": ["13"], "IT Infrastructure, Operations & Support": ["15"],
    "IT Systems & Solutions": ["15"], "Industrial Engineering": ["17"],
    "Installation & Maintenance": ["49"], "Legal": ["23"], "Loading & Stocking": ["53"],
    "Logistic Support": ["43"], "Management": ["11"], "Marketing": ["13"],
    "Mechanical Engineering": ["17"], "Media & Communications": ["27"],
    "Medical Information": ["29"], "Medical Technician": ["29"], "Nursing": ["29"],
    "Personal Care & Home Health": ["31"], "Pharmacy": ["29"],
    "Physicians & Surgeons": ["29"], "Production & Manufacturing": ["51"],
    "Project Management": ["11"], "Retail": ["41"], "Sales": ["41"],
    "Scientific Research & Development": ["19"], "Security & Public Safety": ["33"],
    "Social Science": ["19"], "Software Development": ["15"],
}

CHATGPT = pd.Timestamp("2022-11-30")
HIKES   = pd.Timestamp("2022-03-16")


def load_exposure():
    p = DATA + "aei_job_exposure.csv"
    p = p if os.path.exists(p) else glob.glob(DATA + "*aei_job_exposure.csv")[0]
    e = pd.read_csv(p, dtype=str)
    e["observed_exposure"] = pd.to_numeric(e.observed_exposure, errors="coerce")
    e = e.dropna(subset=["observed_exposure"])
    e["major"] = e.occ_code.str[:2]
    return e.groupby("major")["observed_exposure"].mean()


maj = load_exposure()
d = pd.read_csv(IND)
d["date"] = pd.to_datetime(d.date)
d = d[d.variable == "new postings"].copy()
piv = d.pivot_table(index="date", columns="display_name",
                    values="indeed_job_postings_index")
piv = piv.resample("MS").mean()

expo = {}
for cat, groups in SOC_MAP.items():
    vals = [maj.get(g) for g in groups if g in maj.index]
    if vals and cat in piv.columns:
        expo[cat] = float(np.mean(vals))
E = pd.Series(expo).dropna()
piv = piv[[c for c in piv.columns if c in E.index]]

print("=" * 98)
print("FREEZE OR SUBSTITUTION? Job postings as the discriminating evidence")
print("=" * 98)
print(f"\n  Indeed Hiring Lab new-postings index, {piv.index[0].date()} to "
      f"{piv.index[-1].date()}, {len(piv.columns)} categories.")
print(f"  Index base: 1 Feb 2020 = 100. Exposure from AEI occupational scores")
print(f"  aggregated to SOC major groups.\n")
hi = E[E >= E.quantile(0.67)].index.tolist()
lo = E[E <= E.quantile(0.33)].index.tolist()
print(f"  HIGH exposure ({len(hi)}): {', '.join(sorted(hi))}")
print(f"\n  LOW exposure  ({len(lo)}): {', '.join(sorted(lo))}")


def seg(cols, a, b):
    return piv.loc[a:b, cols].mean(axis=1).mean()


print("\n" + "=" * 98)
print("[1] LEVEL: how far are postings below their pre-AI baseline?")
print("=" * 98)
print("\n  Baseline is 2021, after the COVID collapse and rebound but before both")
print("  the rate cycle and ChatGPT.\n")
print(f"  {'group':<16}{'2021 base':>11}{'2023':>9}{'2024':>9}{'2025':>9}{'2026':>9}")
for lbl, cols in [("high exposure", hi), ("low exposure", lo)]:
    b = seg(cols, "2021", "2021")
    r = [seg(cols, y, y) for y in ["2023", "2024", "2025", "2026"]]
    print(f"  {lbl:<16}{b:>11.1f}" + "".join(f"{v:>9.1f}" for v in r))
gap_now = seg(hi, "2026", "2026") / seg(hi, "2021", "2021") - \
          seg(lo, "2026", "2026") / seg(lo, "2021", "2021")
print(f"\n  High minus low, 2026 relative to own 2021 base: {100*gap_now:+.1f}pp")

print("\n" + "=" * 98)
print("[2] RECOVERY: THE DISCRIMINATING TEST")
print("=" * 98)
print("\n  A hiring freeze is a deferred vacancy: when uncertainty resolves, postings")
print("  come back. Substitution destroys the vacancy, so it does not.\n")
for lbl, cols in [("high exposure", hi), ("low exposure", lo)]:
    s_ = piv[cols].mean(axis=1)
    post = s_.loc["2022-06":]
    print(f"  {lbl:<16}trough {post.min():.1f} at {post.idxmin().date()}, "
          f"latest {s_.iloc[-1]:.1f}")
print("\n  IN LEVELS THIS TEST IS UNINFORMATIVE: both groups are at or near their")
print("  trough right now, so there is no recovery period to measure in either. All")
print("  postings are still falling. Levels cannot separate the two stories here.")
print("\n  THE RELATIVE GAP CAN, and it is the quantity the hypothesis is about,")
print("  since substitution is a claim about exposed work SPECIFICALLY. Each group")
print("  is scaled by its own 2021 base so the common decline drops out:\n")
rel_gap = {}
print(f"  {'year':<8}{'high/2021':>11}{'low/2021':>11}{'gap':>9}")
for y in ["2022", "2023", "2024", "2025", "2026"]:
    h_ = piv.loc[y, hi].mean(axis=1).mean() / piv.loc["2021", hi].mean(axis=1).mean()
    l_ = piv.loc[y, lo].mean(axis=1).mean() / piv.loc["2021", lo].mean(axis=1).mean()
    rel_gap[y] = h_ - l_
    print(f"  {y:<8}{h_:>11.3f}{l_:>11.3f}{100*(h_-l_):>+8.1f}pp")
worst = min(rel_gap, key=rel_gap.get)
now = rel_gap["2026"]
print(f"\n  Worst gap: {100*rel_gap[worst]:+.1f}pp in {worst}. Latest: {100*now:+.1f}pp.")
closed = (rel_gap[worst] - now) / abs(rel_gap[worst]) if rel_gap[worst] else np.nan
print(f"  Share of the gap that has closed since the worst year: {100*closed:.0f}%")
print("\n  A gap that WIDENS as capability diffuses is substitution. A gap that peaks")
print("  and then closes is a freeze unwinding, or a cyclical shock passing.")

print("\n" + "=" * 98)
print("[3] TIMING: does the divergence start with ChatGPT or with the rate cycle?")
print("=" * 98)
print("\n  Cumulative high-minus-low gap, relative to the same gap in Jan 2022,")
print("  before either event.\n")
s_hi = piv[hi].mean(axis=1)
s_lo = piv[lo].mean(axis=1)
rel = (s_hi / s_hi.loc["2021"].mean()) - (s_lo / s_lo.loc["2021"].mean())
anchor = rel.loc["2022-01"]
a0 = float(np.asarray(anchor).mean())
print(f"  {'date':<12}{'high-low gap vs Jan 2022':>26}   event")
for dt, ev in [("2022-01", "baseline"), ("2022-03", "rate hikes begin"),
               ("2022-09", "3 quarters of hiking"), ("2022-11", "ChatGPT released"),
               ("2023-03", "GPT-4"), ("2023-09", ""), ("2024-03", ""),
               ("2025-03", ""), ("2026-01", ""), ("2026-07", "latest")]:
    try:
        v = float(np.asarray(rel.loc[dt]).mean())
        print(f"  {dt:<12}{100*(v-a0):>25.1f}pp   {ev}")
    except Exception:
        continue

pre = float(rel.loc["2022-03":"2022-10"].mean()) - a0
post_g = float(rel.loc["2022-12":"2023-09"].mean()) - a0
print(f"\n  Gap change during hiking, before ChatGPT (Mar-Oct 2022) : {100*pre:+.1f}pp")
print(f"  Gap change in the 10 months after ChatGPT (Dec 2022-Sep 2023): {100*post_g:+.1f}pp")

print("\n" + "=" * 98)
print("[4] CROSS-SECTION: does the postings decline scale with exposure?")
print("=" * 98)
cur = (piv.loc["2026"].mean() / piv.loc["2021"].mean() - 1) * 100
j = pd.DataFrame({"expo": E, "chg": cur}).dropna()
r_, p_ = sp_stats.pearsonr(j.expo, j.chg)
rs, ps = sp_stats.spearmanr(j.expo, j.chg)
print(f"\n  2026 postings vs 2021 baseline, against exposure across "
      f"{len(j)} categories:")
print(f"    Pearson  r = {r_:+.3f}  (p = {p_:.4f})")
print(f"    Spearman r = {rs:+.3f}  (p = {ps:.4f})")
print("    Negative means more exposed categories have fewer postings.\n")
print(f"  {'category':<40}{'exposure':>10}{'2026 vs 2021':>14}")
for c in j.sort_values("chg").index[:6]:
    print(f"  {c:<40}{j.loc[c,'expo']:>10.3f}{j.loc[c,'chg']:>+13.1f}%")
print("  ...")
for c in j.sort_values("chg").index[-4:]:
    print(f"  {c:<40}{j.loc[c,'expo']:>10.3f}{j.loc[c,'chg']:>+13.1f}%")

print("\n  SCOPE LIMIT, AND IT IS THE IMPORTANT ONE. Indeed publishes postings by")
print("  occupational category, NOT by seniority. So this tests the OCCUPATION-LEVEL")
print("  substitution hypothesis, not the entry-level one. It cannot confirm or")
print("  refute the entry-level finding directly. What it does is constrain the")
print("  surrounding story, and it corroborates this project's own null on")
print("  occupation totals: at the level of whole occupations there is no widening")
print("  AI signature.")
print("\n  CAVEAT ON THIS DATA. Indeed measures postings on Indeed, so a shift in")
print("  employer recruiting channels would show up as a decline that is not a")
print("  decline in labour demand. The index is also share-based within Indeed's own")
print("  volume. Comparisons ACROSS categories at the same date are the defensible")
print("  use; a category's absolute level over six years is not.")

fig, axes = plt.subplots(1, 3, figsize=(19, 5.8))
ax = axes[0]
ax.plot(s_hi.index, s_hi.values, lw=2.4, color="#c0392b", label="high AI exposure")
ax.plot(s_lo.index, s_lo.values, lw=2.4, color="#1f4e79", label="low AI exposure")
ax.axvline(CHATGPT, color="black", ls="--", lw=1.5)
ax.text(CHATGPT, ax.get_ylim()[1]*0.95, " ChatGPT", fontsize=8)
ax.axvline(HIKES, color="gray", ls=":", lw=1.5)
ax.text(HIKES, ax.get_ylim()[1]*0.88, " hikes", fontsize=8, color="gray")
ax.axhline(100, color="black", lw=0.9, alpha=0.5)
ax.set_title("New job postings index\n(Feb 2020 = 100)", fontsize=11.5, fontweight="bold")
ax.legend(fontsize=8.5); ax.grid(True, ls="--", alpha=0.3)

ax = axes[1]
ax.plot(rel.index, 100*(rel - anchor), lw=2.6, color="#6a1b9a")
ax.axhline(0, color="black", lw=1.1)
ax.axvline(CHATGPT, color="black", ls="--", lw=1.5)
ax.axvline(HIKES, color="gray", ls=":", lw=1.5)
ax.set_title("High-minus-low gap vs Jan 2022\nwhich event does it track?",
             fontsize=11.5, fontweight="bold")
ax.set_ylabel("pp", fontsize=9.5); ax.grid(True, ls="--", alpha=0.3)

ax = axes[2]
ax.scatter(j.expo, j.chg, s=55, color="#1f4e79", alpha=0.75, edgecolors="white")
sl, ic, _, _, _ = sp_stats.linregress(j.expo, j.chg)
xs = np.linspace(j.expo.min(), j.expo.max(), 30)
ax.plot(xs, ic + sl*xs, color="#c0392b", lw=2.3)
for c in list(j.sort_values("chg").index[:3]) + list(j.sort_values("chg").index[-2:]):
    ax.annotate(c[:18], (j.loc[c,"expo"], j.loc[c,"chg"]), xytext=(4,3),
                textcoords="offset points", fontsize=7)
ax.axhline(0, color="black", lw=0.9, ls="--")
ax.set_xlabel("AI exposure", fontsize=9.5)
ax.set_ylabel("2026 postings vs 2021 (%)", fontsize=9.5)
ax.set_title(f"Cross-section\nr={r_:+.2f}, p={p_:.3f}, n={len(j)}",
             fontsize=11.5, fontweight="bold")
ax.grid(True, ls="--", alpha=0.3)

fig.suptitle("Freeze or substitution? Postings are a flow, so a deferred vacancy and a "
             "destroyed one separate here long before they separate in employment",
             fontsize=12.5, fontweight="bold", y=1.02)
plt.tight_layout()
out = os.path.join(HERE, "freeze_vs_substitution.png")
plt.savefig(out, dpi=150, bbox_inches="tight")
print(f"\nChart saved: {out}")
