import numpy as np, pandas as pd
from scipy import stats as sp

def _demean(M, occ_codes, yr_codes, w, n_occ, n_yr, iters=60, tol=1e-11):
    """Weighted alternating projections onto occ and year FE (plus intercept)."""
    M = M.astype(float).copy()
    for _ in range(iters):
        prev = M.copy()
        so = np.bincount(occ_codes, weights=w, minlength=n_occ)
        for j in range(M.shape[1]):
            num = np.bincount(occ_codes, weights=w*M[:,j], minlength=n_occ)
            M[:,j] -= (num/so)[occ_codes]
        sy = np.bincount(yr_codes, weights=w, minlength=n_yr)
        for j in range(M.shape[1]):
            num = np.bincount(yr_codes, weights=w*M[:,j], minlength=n_yr)
            M[:,j] -= (num/sy)[yr_codes]
        if np.max(np.abs(M-prev)) < tol: break
    return M

def fe_did(d, ycol, xvals, wcol="tot", post_from=2023):
    """Two-way FE DiD via within transformation. xvals = raw exposure per row."""
    post = (d["year"].values >= post_from).astype(float)
    z = (xvals - xvals.mean())/xvals.std()
    X = (z*post).reshape(-1,1); y = d[ycol].values.reshape(-1,1)
    w = np.ones(len(d)) if wcol is None else d[wcol].values.astype(float)
    w = w/w.mean()
    oc, occ_u = pd.factorize(d["occ"].values); yc, yr_u = pd.factorize(d["year"].values)
    M = _demean(np.hstack([X,y]), oc, yc, w, len(occ_u), len(yr_u))
    xt, yt = M[:,0], M[:,1]
    sxx = (w*xt*xt).sum()
    b = (w*xt*yt).sum()/sxx
    r = yt - b*xt
    s = np.bincount(oc, weights=w*xt*r, minlength=len(occ_u))
    G = len(occ_u)
    V = (s**2).sum()/sxx**2 * (G/max(G-1,1))
    se = float(np.sqrt(max(V,0))); t = b/se
    return b, se, t, 2*(1-sp.norm.cdf(abs(t))), G, len(d)
