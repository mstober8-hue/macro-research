"""
section4_remote_work.py
Is the entry-level result really about remote work?

WHY THIS IS THE MOST SERIOUS REMAINING CONFOUNDER
AI-exposed occupations are overwhelmingly office occupations, and office
occupations are the ones that went remote. Remote work plausibly reduces junior
hiring on its own: training, mentoring and supervising new entrants is harder at a
distance, so firms with remote-capable roles may have hired fewer young workers
after 2022 for reasons that have nothing to do with AI. If so, the Section 3
estimate would be measuring telework, and it would be a confound that changes the
result rather than its framing. Brynjolfsson et al. control for it; Fairlie and Wu
(2026) report "some evidence of a positive relationship with remote work
availability" in young-graduate unemployment.

THE MEASURE
Dingel and Neiman (2020), "How Many Jobs Can Be Done at Home?", the classification
Brynjolfsson et al. use. It is rebuilt here from O*NET following their published
rules: an occupation cannot be done entirely at home if ANY of the following hold.

  Work Context (average respondent unless noted)
    uses e-mail less than once a month
    deals with violent or physically aggressive people at least weekly
    MAJORITY of respondents work outdoors every day (either outdoor element)
    exposed to disease or infection at least weekly
    exposed to minor burns, cuts, bites or stings at least weekly
    spends the majority of time walking or running
    spends the majority of time wearing common or specialised protective equipment
  Work Activities, importance above 4.0 on the 1-5 scale
    general physical activities; handling and moving objects; controlling
    machines and processes; operating vehicles or mechanised equipment; performing
    for or working directly with the public; repairing mechanical equipment;
    repairing electronic equipment; inspecting equipment, structures or materials

Detailed O*NET occupations are scored 0/1 and averaged to six-digit SOC, so the
measure is the share of an occupation's sub-occupations that are teleworkable.

VALIDATION GATE
Dingel and Neiman's headline is that 37 percent of US jobs can be done entirely at
home. If the employment-weighted share here is not close to that, the construction
is wrong and nothing downstream should be believed.

Writes section4_remote_work.png.
"""
import re, numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from entry_panel import load, fe, z, post_x, stars, NONOVERLAP, DATA, BANDS

def soc6(c):
    m = re.match(r"(\d{2}-\d{4})", str(c)); return m.group(1) if m else None

wc = pd.read_csv(DATA + "onet_work_context_ratings.csv"); wc.columns = [c.strip() for c in wc.columns]
wa = pd.read_csv(DATA + "onet_work_activities_importance_ratings.csv"); wa.columns = [c.strip() for c in wa.columns]
for d in (wc, wa):
    d["Data Value"] = pd.to_numeric(d["Data Value"], errors="coerce")
code = "O*NET-SOC Code"

cx = wc[wc["Scale ID"] == "CX"].pivot_table(index=code, columns="Element Name", values="Data Value")
cxp = wc[(wc["Scale ID"] == "CXP") & (wc["Category"] == 5)].pivot_table(
    index=code, columns="Element Name", values="Data Value")          # % answering "every day"
im = wa[wa["Scale ID"] == "IM"].pivot_table(index=code, columns="Element Name", values="Data Value")

CTX_GE4 = ["Dealing with Violent or Physically Aggressive People",
           "Exposed to Disease or Infections",
           "Exposed to Minor Burns, Cuts, Bites, or Stings",
           "Spend Time Walking or Running",
           [c for c in cx.columns if c.startswith("Wear Common Protective")][0],
           [c for c in cx.columns if c.startswith("Wear Specialized Protective")][0]]
OUTDOOR = ["Outdoors, Exposed to All Weather Conditions", "Outdoors, Under Cover"]
ACTS = ["Performing General Physical Activities", "Handling and Moving Objects",
        "Controlling Machines and Processes",
        "Operating Vehicles, Mechanized Devices, or Equipment",
        "Performing for or Working Directly with the Public",
        "Repairing and Maintaining Mechanical Equipment",
        "Repairing and Maintaining Electronic Equipment",
        "Inspecting Equipment, Structures, or Materials"]

idx = cx.index.intersection(im.index)
fail = pd.Series(False, index=idx)
fail |= cx.loc[idx, "E-Mail"] < 3                                   # less than monthly
for c in CTX_GE4:
    fail |= cx.loc[idx, c].fillna(0) >= 4                          # weekly+ / majority of time
for c in OUTDOOR:
    fail |= cxp.reindex(idx)[c].fillna(0) > 50                      # majority every day
for c in ACTS:
    fail |= im.loc[idx, c].fillna(0) > 4.0
tele8 = (~fail).astype(float).rename("tele").reset_index()
tele8["soc"] = tele8[code].map(soc6)
TELE = tele8.dropna(subset=["soc"]).groupby("soc", as_index=False)["tele"].mean()

XW = pd.read_csv(DATA + "occ2010_soc_crosswalk.csv")
EXACT = set(TELE.soc)
def lk(s):
    h = TELE[TELE.soc == s]
    if len(h): return h.tele.iloc[0]
    for n in (5, 2):
        h = TELE[TELE.soc.astype(str).str.startswith(str(s)[:n])]
        if len(h): return h.tele.mean()
    return np.nan
XW["tele"] = [lk(s) for s in XW.soc]
XW["tele_exact"] = XW.soc.isin(EXACT)
TO = XW[["occ", "tele", "tele_exact"]].dropna(subset=["tele"]).drop_duplicates("occ")

D = load(require_controls=True).merge(TO, on="occ", how="inner")
for b in NONOVERLAP: D[f"sh_{b}"] = 100 * D[b] / D.tot
D["sh_a22_25"] = 100 * D.a22_25 / D.tot
o22 = D[D.year == 2022].drop_duplicates("occ")
t = pd.read_csv(DATA + "occ2010_soc_crosswalk.csv").drop_duplicates("occ").set_index("occ")["title"]

print("=" * 96)
print("1. VALIDATION: does the rebuilt measure reproduce Dingel and Neiman?")
print("=" * 96)
share = 100 * np.average(o22.tele, weights=o22.tot)
ok = 30 <= share <= 45
print(f"\n  employment-weighted teleworkable share, CPS 2022: {share:.1f}%   "
      f"(Dingel and Neiman: 37%)   {'PASS' if ok else 'FAIL'}")
assert ok, "teleworkability measure does not reproduce the published benchmark"
for kw in ["Software developers", "Accountants", "Cashiers", "Construction laborers",
           "Registered nurses", "Lawyers", "Customer service", "Janitors"]:
    h = o22[o22.occ.map(t).astype(str).str.contains(kw, case=False, na=False)]
    if len(h):
        print(f"    {str(t.get(h.occ.iloc[0]))[:46]:<48}{h.tele.iloc[0]:.2f}")
print(f"\n  exact SOC match rate for this measure: {100*TO.tele_exact.mean():.1f}%")

print("\n" + "=" * 96)
print("2. HOW CLOSELY DOES TELEWORK TRACK AI EXPOSURE?")
print("=" * 96)
r = np.corrcoef(o22.rep_good, o22.tele)[0, 1]; r2 = np.corrcoef(o22.en_raw, o22.tele)[0, 1]
print(f"\n  corr(AI composite, teleworkable)  = {r:+.3f}")
print(f"  corr(raw GPT-4 beta, teleworkable) = {r2:+.3f}")
print(f"  shared variance with the composite: {100*r*r:.0f}%  -> this is a real threat")

print("\n" + "=" * 96)
print("3. THE HORSE RACE, 22-25 share")
print("=" * 96)
print(f"\n  {'specification':<50}{'AI exposure':>18}{'teleworkable':>18}")
R = {}
for xs, lab in [(["rep_good"], "AI exposure alone"),
                (["tele"], "teleworkable alone"),
                (["rep_good", "tele"], "both"),
                (["rep_good", "tele", "jobzone", "lwage"], "both + education + pay")]:
    b, se, tt, p, G, n = fe(D, "sh_a22_25", post_x(D, xs))
    ai = f"{b[xs.index('rep_good')]:+.4f} ({p[xs.index('rep_good')]:.3f})" if "rep_good" in xs else ""
    te = f"{b[xs.index('tele')]:+.4f} ({p[xs.index('tele')]:.3f})" if "tele" in xs else ""
    R[lab] = (b, se, p, xs)
    print(f"  {lab:<50}{ai:>18}{te:>18}")

print("\n  Same, raw GPT-4 beta in place of the composite:")
for xs, lab in [(["en_raw"], "AI exposure alone"), (["en_raw", "tele"], "both")]:
    b, se, tt, p, G, n = fe(D, "sh_a22_25", post_x(D, xs))
    te = f"{b[1]:+.4f} ({p[1]:.3f})" if len(xs) > 1 else ""
    print(f"  {lab:<50}{b[0]:>+11.4f} ({p[0]:.3f}){te:>18}")

ex = D[D.tele_exact]
b, se, tt, p, G, n = fe(ex, "sh_a22_25", post_x(ex, ["rep_good", "tele"]))
print(f"\n  both, teleworkability exactly matched only ({ex.occ.nunique()} occ):"
      f"  AI {b[0]:+.4f} ({p[0]:.3f})   tele {b[1]:+.4f} ({p[1]:.3f})")

print("\n" + "=" * 96)
print("4. DOES THE AGE PATTERN SURVIVE THE TELEWORK CONTROL?")
print("=" * 96)
print(f"\n  {'band':<14}{'AI alone':>20}{'AI | telework':>22}{'telework coef':>20}")
LAD = [("sh_u20", "under 20"), ("sh_a20_24", "20-24"), ("sh_a25", "25"),
       ("sh_a26_30", "26-30"), ("sh_a31_34", "31-34"), ("sh_a35p", "35+")]
AG = {}
for col, lab in LAD:
    b1, s1, _, p1, _, _ = fe(D, col, post_x(D, ["rep_good"]))
    b2, s2, _, p2, _, _ = fe(D, col, post_x(D, ["rep_good", "tele"]))
    AG[lab] = (b1[0], s1[0], b2[0], s2[0])
    print(f"  {lab:<14}{b1[0]:>+11.4f} ({p1[0]:.3f}){b2[0]:>+13.4f} ({p2[0]:.3f})"
          f"{b2[1]:>+12.4f} ({p2[1]:.3f})")

# ---- chart ---------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10, 5.4))
labs = [l for _, l in LAD]; x = np.arange(len(labs)); w = 0.38
ax.bar(x - w/2, [AG[l][0] for l in labs], w, yerr=[1.96*AG[l][1] for l in labs],
       color="#c0392b", error_kw=dict(lw=1.2, capsize=3), label="AI exposure alone")
ax.bar(x + w/2, [AG[l][2] for l in labs], w, yerr=[1.96*AG[l][3] for l in labs],
       color="#1f4e79", error_kw=dict(lw=1.2, capsize=3), label="AI exposure, controlling for teleworkability")
ax.axhline(0, color="black", lw=1.2)
ax.set_xticks(x); ax.set_xticklabels(labs, fontsize=9)
ax.set_ylabel("pp change in band's employment share per sd of AI exposure", fontsize=9.5)
ax.set_title("The age pattern with and without the remote-work control", fontsize=12.5, fontweight="bold")
ax.legend(fontsize=9); ax.grid(True, axis="y", ls="--", alpha=.35)
plt.tight_layout(); plt.savefig("section4_remote_work.png", dpi=150, bbox_inches="tight")
print("\nChart saved: section4_remote_work.png")
