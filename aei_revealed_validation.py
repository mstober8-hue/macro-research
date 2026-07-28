"""
aei_revealed_validation.py
Validate the AI-replaceability score against REVEALED AI usage.

The project's replaceability score is built from theory: Eloundou et al.'s
GPT-exposure ratings times one minus an O*NET-derived complementarity index.
Its weakest point is circularity. Both inputs describe how automatable a job
looks on paper, so "automatable sectors show labor-saving productivity growth"
is uncomfortably close to restating the measure's own construction.

This script tests the finding against a completely independent source: the
Anthropic Economic Index, which reports what people actually do with Claude.
Nothing in it is a rating of how automatable a job seems; it is observed
behavior. Two AEI series are used, both at SOC-occupation level:

  observed_exposure                      how much AI use that occupation shows
                                         (labor_market_impacts/job_exposure.csv)
  collaboration_bucket_automation_pct    of that use, the share that looks like
                                         automation (Claude does the task)
                                         rather than augmentation (Claude helps
                                         a human doing it)

The direct analog of the project's own construction is then

    AEI replaceability = observed_exposure x automation_share

aggregated to the nine industries with BLS OEWS employment weights, exactly as
the theoretical score is.

FINDINGS
  1. Convergent validity: AEI replaceability correlates ~+0.96 with the
     theoretical O*NET score across the nine industries. Two independent
     constructions, one from task ratings and one from observed usage, rank the
     industries almost identically.
  2. The productivity result survives: AEI replaceability predicts real
     productivity growth (r ~ +0.76, p ~ 0.017), so the finding does not depend
     on the theoretical measure and the circularity objection is substantially
     answered.
  3. It does NOT rescue the recency test. Acceleration remains insignificant
     (r ~ +0.41, p ~ 0.28), matching the theoretical measures. The timing
     failure is therefore a property of the data, not of one exposure measure.
  4. A genuine surprise: automation share ALONE runs the wrong way
     (Spearman ~ -0.78). Physical sectors show HIGHER automation shares than
     knowledge sectors, but far lower usage. When a construction or transport
     worker does reach for AI they hand the task over outright, they just do it
     rarely. Usage intensity, not the automation/augmentation split, is what
     carries the industry signal.

DATA. Both AEI inputs are pulled from the public HuggingFace dataset and cached
in FRED-Data/. The Claude usage file is ~219 MB, so FETCH=True streams it and
keeps only global SOC-occupation rows; after the first run the cache is reused.
"""

import os, glob, warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats as sp
warnings.filterwarnings("ignore")

DATA  = "FRED-Data/"
CACHE = DATA + "aei_soc_automation.csv"
EXPO  = DATA + "aei_job_exposure.csv"
HF    = "https://huggingface.co/datasets/Anthropic/EconomicIndex/resolve/main/"

SECTORS = {
    "Financial Activities":       (["52", "53"], 1.538, 0.267),
    "Information":                (["51"], 1.268, 0.325),
    "Education & Health":         (["61", "62"], 0.775, 0.152),
    "Professional & Business":    (["54", "55", "56"], 0.654, 0.233),
    "Wholesale Trade":            (["42"], 0.264, 0.207),
    "Leisure & Hospitality":      (["71", "72"], -0.315, 0.088),
    "Transportation & Utilities": (["48-49", "22"], -0.342, 0.120),
    "Manufacturing":              (["31-33"], -0.484, 0.138),
    "Construction":               (["23"], -0.997, 0.091),
}

# real productivity growth 2013-25, from real_productivity_ai_crosssection.py
PROD = {"Financial Activities": 2.83, "Information": 7.17, "Education & Health": 1.14,
        "Professional & Business": 2.84, "Wholesale Trade": 0.34, "Leisure & Hospitality": 0.13,
        "Transportation & Utilities": -0.30, "Manufacturing": 1.02, "Construction": -0.85}

KEEP = ["collaboration_bucket_automation_pct", "collaboration_bucket_augmentation_pct", "pct"]


def fetch_aei():
    """Stream the AEI usage file and cache the global SOC-occupation rows."""
    import ssl, urllib.request, socket
    socket.setdefaulttimeout(300)
    ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
    if not os.path.exists(EXPO):
        u = HF + "labor_market_impacts/job_exposure.csv"
        raw = urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"}), context=ctx).read().decode()
        open(EXPO, "w").write(raw)
    u = HF + "release_2026_06_26/data/aei_claude_ai_2026-06-26.csv"
    r = urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"}), context=ctx)
    out = open(CACHE, "w"); header = None; buf = b""
    while True:
        chunk = r.read(1 << 20)
        if not chunk:
            break
        buf += chunk
        *lines, buf = buf.split(b"\n")
        for lb in lines:
            line = lb.decode("utf-8", "ignore")
            if header is None:
                header = line; out.write(line + "\n"); continue
            if "soc_occupation" not in line or "global" not in line:
                continue
            p = line.split(",")
            if len(p) < 8 or p[3] != "global" or p[4] != "soc_occupation" or p[6] not in KEEP:
                continue
            out.write(line + "\n")
    out.close()


if not (os.path.exists(CACHE) and os.path.exists(EXPO)):
    print("Fetching Anthropic Economic Index from HuggingFace (one time, ~219 MB stream)...")
    fetch_aei()

# ---- occupation-level revealed measures ----
d = pd.read_csv(CACHE)
d = d[d.hierarchy_level == 0].copy()
d["soc"] = d["node_external_id"].astype(str).str[:7]
piv = d.pivot_table(index="soc", columns="metric_id", values="value", aggfunc="mean")

occ = pd.DataFrame({"auto": piv["collaboration_bucket_automation_pct"] / 100.0})
ex = pd.read_csv(EXPO); ex["soc"] = ex["occ_code"].astype(str).str[:7]
occ["expo"] = ex.groupby("soc")["observed_exposure"].mean()
occ = occ.dropna(subset=["auto", "expo"])
occ["aei_repl"] = occ["expo"] * occ["auto"]
print(f"Occupations with revealed automation share and exposure: {len(occ)}")

# ---- aggregate to industry with OEWS employment weights ----
oe = pd.read_excel(glob.glob(DATA + "**/*national_sector_wages*", recursive=True)[0])
oe = oe[oe["O_GROUP"] == "detailed"].copy()
oe["TOT_EMP"] = pd.to_numeric(oe["TOT_EMP"], errors="coerce"); oe["soc"] = oe["OCC_CODE"]
oe = oe.dropna(subset=["TOT_EMP"])

rows = []
for sec, (codes, aiie, my_repl) in SECTORS.items():
    s = oe[oe["NAICS"].astype(str).isin(codes)]
    m = s.merge(occ.reset_index(), on="soc", how="inner").dropna(subset=["aei_repl"])
    w = m["TOT_EMP"].values
    rows.append(dict(sector=sec, aiie=aiie, my_repl=my_repl,
                     aei_auto=np.average(m["auto"], weights=w),
                     aei_expo=np.average(m["expo"], weights=w),
                     aei_repl=np.average(m["aei_repl"], weights=w),
                     coverage=m["TOT_EMP"].sum() / s["TOT_EMP"].sum() * 100,
                     prod=PROD[sec]))
R = pd.DataFrame(rows)

print("\n" + R.sort_values("aei_repl", ascending=False).round(3).to_string(index=False))
print(f"\nEmployment coverage of the AEI merge: {R.coverage.min():.0f}% to {R.coverage.max():.0f}% per industry")

print("\n=== Predicting real productivity growth 2013-25 ===")
for c, lab in [("aiie", "AIIE (2021, theoretical)"),
               ("my_repl", "Replaceability (O*NET + Eloundou)"),
               ("aei_repl", "AEI replaceability (REVEALED)"),
               ("aei_expo", "AEI exposure alone (revealed)"),
               ("aei_auto", "AEI automation share alone")]:
    r, p = sp.pearsonr(R[c], R["prod"]); rs, ps = sp.spearmanr(R[c], R["prod"])
    print(f"  {lab:<36} r={r:+.3f} p={p:.3f}   spearman={rs:+.3f} p={ps:.3f}")

print("\n=== Convergent validity: do independent measures agree? ===")
for a, b in [("aei_repl", "my_repl"), ("aei_repl", "aiie"), ("aei_expo", "aiie")]:
    print(f"  corr({a}, {b}) = {sp.pearsonr(R[a], R[b])[0]:+.2f}")

# ---- chart ----
fig, axes = plt.subplots(1, 3, figsize=(18, 5.8))


def scat(ax, x, y, xl, yl, title, color):
    sl, ic, r, p, se = sp.linregress(R[x], R[y])
    ax.scatter(R[x], R[y], s=90, color=color, zorder=3)
    for _, rw in R.iterrows():
        ax.annotate(rw["sector"].replace(" & ", "&\n"), (rw[x], rw[y]),
                    xytext=(4, 3), textcoords="offset points", fontsize=7)
    xs = np.linspace(R[x].min(), R[x].max(), 40)
    ax.plot(xs, ic + sl * xs, "--", color="black", lw=1.5)
    ax.text(0.04, 0.96, f"r={r:+.2f}  p={p:.3f}", transform=ax.transAxes, va="top",
            fontsize=11, bbox=dict(boxstyle="round", fc="white", alpha=0.88))
    ax.set_xlabel(xl, fontsize=10); ax.set_ylabel(yl, fontsize=10)
    ax.set_title(title, fontsize=11, fontweight="bold"); ax.grid(True, ls="--", alpha=0.3)


scat(axes[0], "my_repl", "aei_repl", "Theoretical replaceability (O*NET)",
     "AEI replaceability (revealed usage)",
     "Convergent validity\ntheory vs observed behavior", "#6a3d9a")
scat(axes[1], "aei_repl", "prod", "AEI replaceability (revealed usage)",
     "Real productivity growth 2013-25 (%/yr)",
     "The result survives on revealed data\n(circularity objection answered)", "steelblue")
scat(axes[2], "aei_auto", "prod", "AEI automation share alone",
     "Real productivity growth 2013-25 (%/yr)",
     "The surprise: automation share alone\nruns the WRONG way", "firebrick")

fig.suptitle("Validating the replaceability score against what people actually do with AI\n"
             "Anthropic Economic Index, observed Claude usage by occupation, aggregated to industry",
             fontsize=13, fontweight="bold")
plt.tight_layout(rect=[0, 0, 1, 0.89])
plt.savefig("aei_revealed_validation.png", dpi=150, bbox_inches="tight")
print("\nChart saved: aei_revealed_validation.png")
