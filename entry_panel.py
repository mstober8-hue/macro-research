"""
entry_panel.py
One construction of the occupation-by-year entry-level panel, shared by every
script that estimates on it.

WHY THIS EXISTS
The denominator used to be rebuilt by hand in each script from a list of age
bands. One of those lists left a hole at exactly age 25, so every 25-year-old
was dropped from total employment and the 22-25 share became a ratio whose
numerator was not inside it. That survived several rounds of review because
nothing forced the bands to tile. Here the tiling is asserted, once, and callers
cannot express the bug.

PROVIDES
  load()            the estimation panel: shares, exposure measures, controls
  fe(...)           two-way FE with occupation-clustered SEs
  z(...)            z-score
  BANDS, MEAS       the standard band and exposure-measure labels

The panel is 2016-2026 from cps_panel_bands.csv (build_cps_panel_bands.py, 6.0M
IPUMS CPS person records). Exposure is Eloundou et al. GPT-4 beta, either raw or
discounted by an O*NET complementarity index. Controls are O*NET Job Zone
(education and preparation) and the OEWS May 2022 log median wage.
"""
import os, re, numpy as np, pandas as pd
from scipy import stats as sp
from fastfe import _demean

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "FRED-Data") + os.sep
OEWS = DATA + "oews_national_industry_files/"
COMP_VARS = ["Physical Proximity",
             "Face-to-Face Discussions with Individuals and Within Teams",
             "Deal With External Customers or the Public in General",
             "Health and Safety of Other Workers", "Consequence of Error"]

# The non-overlapping bands MUST tile 16-64. a25 is a singleton and is not
# decorative: without it the set leaves a hole at exactly age 25.
NONOVERLAP = ["u20", "a20_24", "a25", "a26_30", "a31_34", "a35p"]

BASE_YEAR, POST = 2022, 2023
BANDS = [("share_2225", "22-25 (primary)"), ("share_2024", "20-24 (robustness)")]
MEAS  = [("rep_good", "composite"), ("en_raw", "raw GPT-4 beta")]


def _soc6(c):
    m = re.match(r"(\d{2}-\d{4})", str(c)); return m.group(1) if m else None


def _exposure():
    el = pd.read_csv(DATA + "eloundou_gpt_occupational_exposure_scores.csv")
    el.columns = [c.strip() for c in el.columns]
    el["soc"] = el["O*NET-SOC Code"].map(_soc6)
    el["en_raw"] = el[["human_rating_beta", "dv_rating_beta"]].mean(axis=1)
    EL = el.dropna(subset=["soc"]).groupby("soc", as_index=False)["en_raw"].mean()

    wc = pd.read_csv(DATA + "onet_work_context_ratings.csv")
    wc.columns = [c.strip() for c in wc.columns]
    wc["cv"] = pd.to_numeric(wc["Data Value"], errors="coerce")
    wc["soc"] = wc["O*NET-SOC Code"].map(_soc6)
    g = wc[(wc["Scale ID"] == "CX") & (wc["Element Name"].isin(COMP_VARS))]
    piv = g.pivot_table(index="soc", columns="Element Name", values="cv")
    piv = (piv - piv.min()) / (piv.max() - piv.min())
    R = EL.merge(pd.DataFrame({"comp": piv.mean(axis=1)}).reset_index(), on="soc", how="left")
    R["comp"] = R.comp.fillna(R.comp.median())
    R["en_mm"] = (R.en_raw - R.en_raw.min()) / (R.en_raw.max() - R.en_raw.min())
    R["rep_good"] = R.en_mm * (1 - R.comp)

    jz = pd.read_csv(DATA + "onet_job_zones.txt", sep="\t"); jz.columns = [c.strip() for c in jz.columns]
    jz["soc"] = jz["O*NET-SOC Code"].map(_soc6)
    JZ = (jz.dropna(subset=["soc"]).groupby("soc", as_index=False)["Job Zone"].mean()
            .rename(columns={"Job Zone": "jobzone"}))
    ow = pd.read_excel(OEWS + "oews_may2022_national_occupations.xlsx")
    ow.columns = [c.strip().upper() for c in ow.columns]
    gg = "O_GROUP" if "O_GROUP" in ow.columns else "OCC_GROUP"
    ow = ow[ow[gg].astype(str).str.strip() == "detailed"].copy()
    ow["soc"] = ow["OCC_CODE"].astype(str).map(_soc6)
    ow["wage"] = pd.to_numeric(ow["A_MEDIAN"], errors="coerce")
    WG = ow.dropna(subset=["soc", "wage"]).groupby("soc", as_index=False)["wage"].mean()
    CTL = JZ.merge(WG, on="soc", how="outer"); CTL["lwage"] = np.log(CTL.wage)
    return R.merge(CTL[["soc", "jobzone", "lwage"]], on="soc", how="left")


def load(require_controls=False):
    """The estimation panel. require_controls drops occupations missing Job Zone
    or an OEWS wage, which is the sample Section 4 needs."""
    R = _exposure()
    XW = pd.read_csv(DATA + "occ2010_soc_crosswalk.csv")
    cols = ["rep_good", "en_raw", "jobzone", "lwage"]

    def lookup(soc):
        h = R[R.soc == soc]
        if len(h): return [h[c].iloc[0] for c in cols]
        for n in (5, 2):
            h = R[R.soc.astype(str).str.startswith(str(soc)[:n])]
            if len(h): return [h[c].mean() for c in cols]
        return [np.nan] * len(cols)

    got = np.array([lookup(s) for s in XW.soc])
    for i, c in enumerate(cols): XW[c] = got[:, i]
    OCC = XW[["occ"] + cols].dropna(subset=["rep_good"]).drop_duplicates("occ")

    P = pd.read_csv(os.path.join(HERE, "cps_panel_bands.csv"))
    W = (P.pivot_table(index=["occ", "year"], columns="band", values="emp", aggfunc="sum")
           .fillna(0.0).reset_index().merge(OCC, on="occ", how="inner"))

    missing = [c for c in NONOVERLAP if c not in W.columns]
    assert not missing, (f"cps_panel_bands.csv is missing {missing}. The "
                         f"non-overlapping bands must tile 16-64; rerun "
                         f"build_cps_panel_bands.py.")
    W["tot"] = W[NONOVERLAP].sum(axis=1)      # a22_25 excluded: it overlaps a20_24

    D = W[(W.year >= 2016) & (W.tot > 0) & (W.a20_24 > 0) & (W.a22_25 > 0)].copy()
    D["share_2024"] = 100 * D.a20_24 / D.tot
    D["share_2225"] = 100 * D.a22_25 / D.tot
    if require_controls:
        D = D.dropna(subset=["jobzone", "lwage"])
    return D


def z(v):
    v = np.asarray(v, dtype=float)
    return (v - v.mean()) / v.std()


def fe(d, ycol, xmat, wcol="tot"):
    """Two-way (occupation, year) FE with occupation-clustered SEs.
    Returns b, se, t, p, n_clusters, n_obs."""
    y = d[ycol].values.astype(float)
    w = (d[wcol].values.astype(float) if wcol else np.ones(len(d))); w = w / w.mean()
    oc, ou = pd.factorize(d.occ.values); yc, yu = pd.factorize(d.year.values)
    M = _demean(np.hstack([xmat, y.reshape(-1, 1)]), oc, yc, w, len(ou), len(yu))
    Xt, yt = M[:, :-1], M[:, -1]
    inv = np.linalg.pinv(Xt.T @ (w[:, None] * Xt)); b = inv @ (Xt.T @ (w * yt))
    r = yt - Xt @ b; meat = np.zeros((Xt.shape[1],) * 2)
    for gi in range(len(ou)):
        m = oc == gi
        if m.any():
            s = Xt[m].T @ (w[m] * r[m]); meat += np.outer(s, s)
    G = len(ou); V = inv @ (meat * (G / max(G - 1, 1))) @ inv
    se = np.sqrt(np.maximum(np.diag(V), 0)); t = b / se
    return b, se, t, 2 * (1 - sp.norm.cdf(np.abs(t))), G, len(d)


def post_x(d, xcols, post_from=POST):
    """z(x) x post for each column, the standard regressor block."""
    post = (d.year.values >= post_from).astype(float)
    return np.column_stack([z(d[c].values) * post for c in xcols])


def stars(p):
    return "***" if p < .01 else ("**" if p < .05 else ("*" if p < .10 else ""))

def aei():
    """Anthropic Economic Index, revealed Claude usage by SOC occupation.

    This is a REVEALED measure and a single 2026 cross-section, so it is dated
    after the treatment period it would be used to assign. Section 6 treats that
    as the substantive issue rather than a footnote.

    Returns one row per OCC2010 with:
      use       share of Claude conversations mapped to the occupation, percent
      auto_sh   share of that usage in automation-type collaboration
      aug_sh    share in augmentation-type collaboration
      autonomy  mean AI autonomy
      auto_use  use x automation share, usage weighted toward substitution
    """
    from datapaths import dp
    src = dp("aei_claude_ai_2026-06-26.csv")
    ren = {"pct": "use", "collaboration_bucket_automation_pct": "auto_sh",
           "collaboration_bucket_augmentation_pct": "aug_sh", "ai_autonomy_mean": "autonomy"}
    head = pd.read_csv(src, nrows=0).columns
    if "geo_level" in head:                     # long layout
        A = pd.read_csv(src)
        A = A[(A.geo_level == "global") & (A.category_name == "soc_occupation")]
        A["soc"] = A.node_external_id.astype(str).str.extract(r"(\d{2}-\d{4})")[0]
        Wv = A.pivot_table(index="soc", columns="metric_id", values="value", aggfunc="mean")
        S = Wv[list(ren)].rename(columns=ren).reset_index()
    else:                                       # already pivoted by SOC
        S = pd.read_csv(src)
        S["soc"] = S.soc.astype(str).str.extract(r"(\d{2}-\d{4})")[0]
        S = S.rename(columns=ren)[["soc"] + list(ren.values())]
    S = S.dropna(subset=["use"])
    S["auto_use"] = S.use * S.auto_sh / 100.0

    XW = pd.read_csv(DATA + "occ2010_soc_crosswalk.csv")
    cols = ["use", "auto_sh", "aug_sh", "autonomy", "auto_use"]

    def lk(soc):
        h = S[S.soc == soc]
        if len(h): return [h[c].iloc[0] for c in cols]
        for n in (5, 2):
            h = S[S.soc.astype(str).str.startswith(str(soc)[:n])]
            if len(h): return [h[c].mean() for c in cols]
        return [np.nan] * len(cols)

    got = np.array([lk(s) for s in XW.soc])
    for i, c in enumerate(cols): XW[c] = got[:, i]
    return XW[["occ"] + cols].dropna(subset=["use"]).drop_duplicates("occ")
