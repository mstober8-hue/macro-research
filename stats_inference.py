"""
stats_inference.py
One correct place to compute a p-value in this project.

WHY THIS EXISTS
This project has now made the same class of inference error five separate times,
each caught only after it had been written into a README as a finding:

  1. Rolling-correlation break p-values assumed normality and independence across
     12-quarter windows that share 11 quarters. Corrected by permutation_test.py.
  2. The differential-lag bootstrap resampled individual quarters i.i.d., which
     destroys the serial dependence that makes a lag measurable at all, and
     reported a 95% interval of [-5, -1] for a gap that is actually unidentified.
  3. The DESYNC dynamic re-test reported corr = -0.251 at p < 0.0001 on two
     12-quarter rolling series whose effective sample is about 21, not 258.
  4. Rolling-window trend estimates treated 16 windows overlapping by 90% as
     independent, giving an effective n of 1.6 and a nominal p of 0.005.
  5. A circular-shift bootstrap compared an 8-quarter statistic against a null
     built from full-length series, returning p = 1.0 for a strongly negative
     correlation because the null's spread was far too small.

Every one is a variant of the same mistake: treating overlapping or persistent
observations as independent draws. The fix is always one of three things, and
they are implemented here so no script has to reinvent them.

WHEN EACH TOOL APPLIES

  CROSS-SECTIONAL data (one observation per sector, industry, or occupation, at a
  single point in time). Ordinary Pearson or Spearman p-values are VALID here,
  because the units really are separate. The danger is not bias but POWER, so
  cross_section() returns the minimum detectable correlation and a confidence
  interval alongside the p-value, since a null is uninformative if the test could
  only ever have detected an enormous effect.

  TIME-SERIES correlation between two persistent series, including anything built
  from 4-quarter overlapping differences. Use timeseries_corr(), which reports a
  Newey-West HAC p-value AND a circular-shift bootstrap p-value. The circular
  shift preserves each series' own autocorrelation exactly while destroying the
  relationship between them, which is the right null.

  A STATISTIC COMPUTED ON A SHORT WINDOW that you want to test against history.
  Use window_stat_p(), which draws the null at the SAME window length. This is
  error 5 above: a null built from a longer window has smaller spread and will
  return absurd p-values.

  REGRESSION on time-series data. Use ols_hac(), which returns Newey-West
  standard errors. For a local projection at horizon h, pass nw_lags = h + 1,
  because such a regression has MA(h) errors by construction.

A NOTE ON WHAT THIS CANNOT FIX
None of this rescues a small sample. If a correlation across nine sectors is
insignificant, correcting the standard errors will not change that, and the
honest report is the minimum detectable effect, not the p-value. effective_n()
exists to make that visible: it converts a nominal sample size into the number of
genuinely independent observations given a window length.
"""

import numpy as np
import pandas as pd
from scipy import stats as sp_stats

__all__ = ["ols_hac", "timeseries_corr", "cross_section", "window_stat_p",
           "effective_n", "mde_correlation", "fisher_ci"]


def ols_hac(y, X, nw_lags=8):
    """OLS with Newey-West (Bartlett) standard errors. Returns (beta, se)."""
    y = np.asarray(y, float)
    X = np.asarray(X, float)
    XtX = np.linalg.pinv(X.T @ X)
    b = XtX @ X.T @ y
    e = y - X @ b
    S = (X * e[:, None]).T @ (X * e[:, None])
    for L in range(1, max(int(nw_lags), 1) + 1):
        w = 1.0 - L / (nw_lags + 1.0)
        G = (X[L:] * e[L:, None]).T @ (X[:-L] * e[:-L, None])
        S += w * (G + G.T)
    V = XtX @ S @ XtX
    return b, np.sqrt(np.maximum(np.diag(V), 0))


def effective_n(n, window):
    """
    Independent observations implied by n overlapping windows of the given length.
    Two 12-quarter windows one quarter apart share 11 quarters, so n/window is the
    honest count. Use this before quoting any n from a rolling statistic.
    """
    return max(float(n) / max(float(window), 1.0), 1.0)


def fisher_ci(r, n, alpha=0.05):
    """Confidence interval for a correlation via the Fisher z transform."""
    if n <= 3 or not np.isfinite(r):
        return (np.nan, np.nan)
    se = 1.0 / np.sqrt(n - 3)
    z = np.arctanh(np.clip(r, -0.999999, 0.999999))
    c = sp_stats.norm.ppf(1 - alpha / 2)
    return (float(np.tanh(z - c * se)), float(np.tanh(z + c * se)))


def mde_correlation(n, alpha=0.05, power=0.80):
    """Smallest |r| detectable at the given n. Report this whenever a null is claimed."""
    if n <= 4:
        return np.nan
    se = 1.0 / np.sqrt(n - 3)
    z = (sp_stats.norm.ppf(1 - alpha / 2) + sp_stats.norm.ppf(power)) * se
    return float(np.tanh(z))


def cross_section(x, y, alpha=0.05, power=0.80):
    """
    Correlation across independent units (sectors, industries, occupations).
    Ordinary p-values are valid; power is the binding constraint, so the minimum
    detectable effect and the confidence interval are returned with them.
    """
    x = pd.Series(x).astype(float)
    y = pd.Series(y).astype(float)
    d = pd.concat([x.rename("x"), y.rename("y")], axis=1).dropna()
    n = len(d)
    if n < 4:
        return dict(n=n, r=np.nan, p=np.nan, rho=np.nan, p_rho=np.nan,
                    ci=(np.nan, np.nan), mde=np.nan, informative=False)
    r, p = sp_stats.pearsonr(d.x, d.y)
    rho, p_rho = sp_stats.spearmanr(d.x, d.y)
    mde = mde_correlation(n, alpha, power)
    return dict(n=n, r=float(r), p=float(p), rho=float(rho), p_rho=float(p_rho),
                ci=fisher_ci(r, n, alpha), mde=mde,
                informative=bool(np.isfinite(mde) and mde <= 0.5))


def timeseries_corr(a, b, nboot=4000, seed=0, drop=None):
    """
    Correlation between two persistent time series.

    Returns the naive p-value for comparison, a Newey-West HAC p-value from
    regressing b on a, and a circular-shift bootstrap p-value. The circular shift
    keeps each series' own autocorrelation intact while breaking the link between
    them, which is the appropriate null. Quote the bootstrap.
    """
    rng = np.random.default_rng(seed)
    d = pd.concat([pd.Series(a).rename("a"), pd.Series(b).rename("b")],
                  axis=1).dropna()
    if drop is not None:
        d = d[~d.index.isin(drop)]
    n = len(d)
    if n < 20:
        return dict(n=n, r=np.nan, p_naive=np.nan, p_hac=np.nan, p_boot=np.nan)
    x, y = d.a.to_numpy(float), d.b.to_numpy(float)
    r, p_naive = sp_stats.pearsonr(x, y)

    X = np.column_stack([np.ones(n), x])
    nw = max(int(round(n ** 0.25)) * 2, 8)
    beta, se = ols_hac(y, X, nw_lags=nw)
    t = beta[1] / se[1] if se[1] > 0 else np.nan
    p_hac = float(2 * (1 - sp_stats.norm.cdf(abs(t)))) if np.isfinite(t) else np.nan

    null = np.empty(nboot)
    for i in range(nboot):
        null[i] = np.corrcoef(x, np.roll(y, rng.integers(1, n - 1)))[0, 1]
    p_boot = float((np.abs(null) >= abs(r)).mean())
    return dict(n=n, r=float(r), p_naive=float(p_naive), p_hac=p_hac,
                p_boot=p_boot, nw_lags=nw)


def window_stat_p(a, b, obs, n_window, tail="two", nboot=4000, seed=0, drop=None):
    """
    Test a statistic computed on a SHORT window against a matched-length null.

    The null draws windows of exactly n_window observations from circularly
    shifted data, so its spread matches the statistic's. Comparing a short-window
    statistic against a full-sample null understates the spread enormously and
    produces meaningless p-values.
    """
    rng = np.random.default_rng(seed)
    d = pd.concat([pd.Series(a).rename("a"), pd.Series(b).rename("b")],
                  axis=1).dropna()
    if drop is not None:
        d = d[~d.index.isin(drop)]
    x, y = d.a.to_numpy(float), d.b.to_numpy(float)
    if len(x) < n_window + 5 or not np.isfinite(obs):
        return np.nan
    vals = []
    for _ in range(nboot):
        ys = np.roll(y, rng.integers(1, len(y) - 1))
        st = rng.integers(0, len(x) - n_window)
        s1, s2 = x[st:st + n_window], ys[st:st + n_window]
        if np.std(s1) > 1e-9 and np.std(s2) > 1e-9:
            vals.append(np.corrcoef(s1, s2)[0, 1])
    v = np.asarray(vals)
    if v.size == 0:
        return np.nan
    if tail == "low":
        return float((v <= obs).mean())
    if tail == "high":
        return float((v >= obs).mean())
    return float((np.abs(v) >= abs(obs)).mean())
