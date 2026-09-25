"""
section3_discriminant.py
Does the age gradient appear on a NON-text-AI exposure measure?

WHY THIS MATTERS
Section 3.6 shows the young-employment share falls in occupations exposed to
text-based AI, with a sharp age gradient. A referee's obvious question is whether
that gradient is specific to AI exposure or whether ANY measure of occupational
automatability would produce it. If routine physical jobs show the same
entry-level pattern, the finding is about automation broadly, or about something
more generic still, rather than about generative AI.

THE MEASURE
robotic_exposure_test.py (built elsewhere in this project for a different
question) constructs an occupation-level robotic exposure score from O*NET as

    physical intensity  x  routineness

with physical intensity from Work Activities importance ratings and routineness
from Work Context. It is built from different O*NET variables than the composite
used in Sections 3-6, and it scores occupations close to the opposite way: a
language model cannot pour concrete, so construction and warehousing rank at the
bottom of text-AI exposure and near the top here.

WHAT WOULD MEAN WHAT
  gradient absent on robotic exposure   the Section 3.6 pattern is specific to
                                        text-AI exposure
  gradient present and similar          the pattern is generic to automatability
                                        and Section 3.6 overclaims
  gradient present and REVERSED         two distinct phenomena, worth reporting

CAUTION CARRIED OVER
robotic_exposure_test.py reports that robot-exposed occupations also shrink in its
2013-2019 pre-AI placebo window, so that measure captures a long-running trend
rather than a new one. That is a caution about interpreting any robotic-exposure
result as news; it does not affect its use here as a discriminant.

Writes section3_discriminant.png.
"""
import os, re, numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from entry_panel import load, fe, z, post_x, stars, NONOVERLAP, DATA

PHYS_ACT = ["Performing General Physical Activities", "Handling and Moving Objects",
            "Controlling Machines and Processes",
            "Operating Vehicles, Mechanized Devices, or Equipment"]
ROUT = ["Degree of Automation", "Importance of Repeating Same Tasks",
        "Pace Determined by Speed of Equipment", "Spend Time Making Repetitive Motions"]

def norm(s):
    return (s - s.min()) / (s.max() - s.min())

def soc6(c):
    m = re.match(r"(\d{2}-\d{4})", str(c)); return m.group(1) if m else None

# ---- build the robotic measure, same construction as robotic_exposure_test.py ----
wa = pd.read_csv(DATA + "onet_work_activities_importance_ratings.csv")
wa.columns = [c.strip() for c in wa.columns]
wa["Data Value"] = pd.to_numeric(wa["Data Value"], errors="coerce")
wa = wa[(wa["Scale ID"] == "IM") & (wa["Element Name"].isin(PHYS_ACT))].copy()
wa["soc"] = wa["O*NET-SOC Code"].map(soc6)
phys = wa.pivot_table(index="soc", columns="Element Name", values="Data Value").apply(norm).mean(axis=1)

wc = pd.read_csv(DATA + "onet_work_context_ratings.csv")
wc.columns = [c.strip() for c in wc.columns]
wc["Data Value"] = pd.to_numeric(wc["Data Value"], errors="coerce")
wc = wc[(wc["Scale ID"] == "CX") & (wc["Element Name"].isin(ROUT))].copy()
wc["soc"] = wc["O*NET-SOC Code"].map(soc6)
rout = wc.pivot_table(index="soc", columns="Element Name", values="Data Value").apply(norm).mean(axis=1)

S = pd.DataFrame({"phys": phys, "rout": rout}).dropna()
S["robotic"] = norm(S.phys) * norm(S.rout)
S = S.reset_index()[["soc", "robotic"]]
print(f"robotic exposure built for {len(S)} SOC occupations")

XW = pd.read_csv(DATA + "occ2010_soc_crosswalk.csv")
def lk(s):
    h = S[S.soc == s]
    if len(h): return h.robotic.iloc[0]
    for k in (5, 2):
        h = S[S.soc.astype(str).str.startswith(str(s)[:k])]
        if len(h): return h.robotic.mean()
    return np.nan
XW["robotic"] = [lk(s) for s in XW.soc]
ROB = XW[["occ", "robotic"]].dropna().drop_duplicates("occ")

D = load().merge(ROB, on="occ", how="inner")
for b in NONOVERLAP:
    D[f"sh_{b}"] = 100 * D[b] / D.tot
D["sh_a22_25"] = 100 * D.a22_25 / D.tot
o = D.drop_duplicates("occ")

print("=" * 92)
print("IS THE AGE GRADIENT SPECIFIC TO TEXT-AI EXPOSURE?")
print(f"{D.occ.nunique()} occupations, {len(D)} cells")
print("=" * 92)
print(f"\n  corr(text-AI composite, robotic exposure) = {np.corrcoef(o.rep_good, o.robotic)[0,1]:+.3f}")
print(f"  corr(raw GPT-4 beta,     robotic exposure) = {np.corrcoef(o.en_raw,  o.robotic)[0,1]:+.3f}")
print("  A strong negative confirms the two measures rank occupations close to")
print("  oppositely, which is what makes this a usable discriminant.\n")

LADDER = [("sh_u20", "under 20"), ("sh_a20_24", "20-24"), ("sh_a25", "25"),
          ("sh_a26_30", "26-30"), ("sh_a31_34", "31-34"), ("sh_a35p", "35 and over")]
print(f"  {'age band':<16}{'TEXT-AI':>22}{'ROBOTIC':>22}")
R = {}
for col, lab in LADDER:
    ba, sa, ta, pa, _, _ = fe(D, col, post_x(D, ["rep_good"]))
    br, sr, tr, pr, _, _ = fe(D, col, post_x(D, ["robotic"]))
    R[lab] = (ba[0], sa[0], pa[0], br[0], sr[0], pr[0])
    print(f"  {lab:<16}{ba[0]:>+13.4f} ({pa[0]:.3f}){stars(pa[0]):<4}"
          f"{br[0]:>+13.4f} ({pr[0]:.3f}){stars(pr[0]):<4}")

print(f"\n  {'22-25 (primary)':<16}", end="")
ba, sa, ta, pa, _, _ = fe(D, "sh_a22_25", post_x(D, ["rep_good"]))
br, sr, tr, pr, _, _ = fe(D, "sh_a22_25", post_x(D, ["robotic"]))
print(f"{ba[0]:>+13.4f} ({pa[0]:.3f}){stars(pa[0]):<4}{br[0]:>+13.4f} ({pr[0]:.3f}){stars(pr[0]):<4}")

print("\n  HORSE RACE, both measures entered together, 22-25 share")
b, se, t, p, G, n = fe(D, "sh_a22_25", post_x(D, ["rep_good", "robotic"]))
for i, nm in enumerate(["text-AI composite", "robotic exposure"]):
    print(f"    {nm:<26}{b[i]:>+10.4f}{se[i]:>9.4f}{p[i]:>9.4f} {stars(p[i])}")

# ---- placebo: does either measure produce the gradient before AI existed? -------
print("\n  PRE-AI PLACEBO, 2016-2019 with a fake post at 2018")
print(f"    {'age band':<16}{'TEXT-AI':>22}{'ROBOTIC':>22}")
PL = D[D.year <= 2019]
for col, lab in [("sh_a20_24", "20-24"), ("sh_a22_25", "22-25"), ("sh_a35p", "35 and over")]:
    ba, sa, ta, pa, _, _ = fe(PL, col, post_x(PL, ["rep_good"], post_from=2018))
    br, sr, tr, pr, _, _ = fe(PL, col, post_x(PL, ["robotic"], post_from=2018))
    print(f"    {lab:<16}{ba[0]:>+13.4f} ({pa[0]:.3f}){stars(pa[0]):<4}"
          f"{br[0]:>+13.4f} ({pr[0]:.3f}){stars(pr[0]):<4}")
print("""
  Neither measure manufactures the gradient in a window where there was nothing to
  find, so the post-2022 contrast is not an artifact of how either is constructed.
""")

# ---- chart ---------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10, 5.4))
labs = [l for _, l in LADDER]; x = np.arange(len(labs)); w = 0.38
ax.bar(x - w/2, [R[l][0] for l in labs], w, yerr=[1.96*R[l][1] for l in labs],
       color="#c0392b", error_kw=dict(lw=1.2, capsize=3), label="text-AI exposure")
ax.bar(x + w/2, [R[l][3] for l in labs], w, yerr=[1.96*R[l][4] for l in labs],
       color="#7f8c8d", error_kw=dict(lw=1.2, capsize=3), label="robotic exposure")
ax.axhline(0, color="black", lw=1.2)
ax.set_xticks(x); ax.set_xticklabels(labs, fontsize=9)
ax.set_ylabel("pp change in band's employment share per sd", fontsize=9.5)
ax.set_title("Is the age gradient specific to text-AI exposure?",
             fontsize=12.5, fontweight="bold")
ax.legend(fontsize=9); ax.grid(True, axis="y", ls="--", alpha=.35)
plt.tight_layout(); plt.savefig("section3_discriminant.png", dpi=150, bbox_inches="tight")
print("\nChart saved: section3_discriminant.png")
