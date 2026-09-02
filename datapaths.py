"""
datapaths.py
Resolve a data filename to wherever it actually lives under FRED-Data/.

WHY THIS EXISTS
Several scripts in this project were written when their inputs sat in the repository
root or in ad-hoc folders (bls/, aei/), and the data has since been consolidated
under FRED-Data/ in subject subfolders. That left scripts referring to paths like
"bls/aa2011.htm" or "old_Sector.xlsx" that no longer resolve, so the project did not
run from a clean checkout. Rather than hardcode the new locations in eight files, or
paper over it with symlinks, call sites ask for a bare filename and this resolves it.

It also carries an alias map for files that were renamed rather than moved, notably
the pre-2025-revision BTOS vintages and the current Anthropic Economic Index release.
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "FRED-Data")

_SEARCH = [
    HERE,
    DATA,
    os.path.join(DATA, "bls_occ_age"),
    os.path.join(DATA, "btos_full"),
    os.path.join(DATA, "aei_2026"),
    os.path.join(DATA, "oews_national_industry_files"),
]

# files that were renamed, not just moved
_ALIAS = {
    "old_Sector.xlsx": "pre2025revision_Sector.xlsx",
    "old_State.xlsx": "pre2025revision_State.xlsx",
    "old_National.xlsx": "pre2025revision_National.xlsx",
    "aei_claude_ai_2026-06-26.csv": "aei_soc_occupation_global_2026_06_26.csv",
}


def dp(name):
    """Return a usable path for `name`, searching the known data folders."""
    base = os.path.basename(str(name))
    for cand in (base, _ALIAS.get(base)):
        if not cand:
            continue
        for d in _SEARCH:
            p = os.path.join(d, cand)
            if os.path.exists(p):
                return p
    return os.path.join(HERE, base)      # let the caller raise a clear error
