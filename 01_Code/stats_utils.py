"""
stats_utils.py
------------------------------------------------------------------
Self-contained statistical functions for the Midwest extreme-precipitation
project. This module re-implements the handful of probability distributions
and hypothesis tests we need (Student-t, F, chi-square, normal, Pearson /
Spearman correlation, OLS regression, Welch t-test, Mann-Kendall trend test,
Theil-Sen slope, autocorrelation) using only the Python standard library +
NumPy.

Why re-implement instead of importing SciPy / statsmodels?
The analysis environment used to build this project did not have SciPy or
statsmodels installed and had no internet access to install them. Rather than
drop the rigorous tests, the required special functions (regularized
incomplete beta and gamma) are implemented from standard numerical recipes so
that p-values are exact (not normal approximations). All functions were
cross-checked against textbook values and against an independent in-browser
re-computation of the underlying data.

Author: project author, with assistance from a generative-AI coding assistant
(see the Generative AI Acknowledgment in the final report).
------------------------------------------------------------------
"""

import math
import numpy as np

# ----------------------------------------------------------------------
# Special functions: regularized incomplete gamma and beta
# (Numerical Recipes style implementations)
# ----------------------------------------------------------------------

def _gammln(x):
    """Natural log of the gamma function (Lanczos approximation)."""
    cof = [76.18009172947146, -86.50532032941677, 24.01409824083091,
           -1.231739572450155, 0.1208650973866179e-2, -0.5395239384953e-5]
    y = x
    tmp = x + 5.5
    tmp -= (x + 0.5) * math.log(tmp)
    ser = 1.000000000190015
    for c in cof:
        y += 1.0
        ser += c / y
    return -tmp + math.log(2.5066282746310005 * ser / x)


def _gser(a, x):
    """Series representation of the lower regularized incomplete gamma P(a,x)."""
    gln = _gammln(a)
    if x <= 0.0:
        return 0.0
    ap = a
    summ = 1.0 / a
    delta = summ
    for _ in range(1000):
        ap += 1.0
        delta *= x / ap
        summ += delta
        if abs(delta) < abs(summ) * 1e-15:
            break
    return summ * math.exp(-x + a * math.log(x) - gln)


def _gcf(a, x):
    """Continued-fraction representation of the upper regularized gamma Q(a,x)."""
    gln = _gammln(a)
    FPMIN = 1e-300
    b = x + 1.0 - a
    c = 1.0 / FPMIN
    d = 1.0 / b
    h = d
    for i in range(1, 1000):
        an = -i * (i - a)
        b += 2.0
        d = an * d + b
        if abs(d) < FPMIN:
            d = FPMIN
        c = b + an / c
        if abs(c) < FPMIN:
            c = FPMIN
        d = 1.0 / d
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < 1e-15:
            break
    return math.exp(-x + a * math.log(x) - gln) * h


def gammp(a, x):
    """Lower regularized incomplete gamma function P(a, x)."""
    if x < 0.0 or a <= 0.0:
        raise ValueError("invalid arguments to gammp")
    if x < a + 1.0:
        return _gser(a, x)
    return 1.0 - _gcf(a, x)


def _betacf(a, b, x):
    """Continued fraction for the incomplete beta function."""
    FPMIN = 1e-300
    qab = a + b
    qap = a + 1.0
    qam = a - 1.0
    c = 1.0
    d = 1.0 - qab * x / qap
    if abs(d) < FPMIN:
        d = FPMIN
    d = 1.0 / d
    h = d
    for m in range(1, 1000):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        if abs(d) < FPMIN:
            d = FPMIN
        c = 1.0 + aa / c
        if abs(c) < FPMIN:
            c = FPMIN
        d = 1.0 / d
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        if abs(d) < FPMIN:
            d = FPMIN
        c = 1.0 + aa / c
        if abs(c) < FPMIN:
            c = FPMIN
        d = 1.0 / d
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < 1e-15:
            break
    return h


def betai(a, b, x):
    """Regularized incomplete beta function I_x(a, b)."""
    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0
    bt = math.exp(_gammln(a + b) - _gammln(a) - _gammln(b)
                  + a * math.log(x) + b * math.log(1.0 - x))
    if x < (a + 1.0) / (a + b + 2.0):
        return bt * _betacf(a, b, x) / a
    return 1.0 - bt * _betacf(b, a, 1.0 - x) / b


# ----------------------------------------------------------------------
# Distribution tail probabilities (survival functions / cdfs)
# ----------------------------------------------------------------------

def norm_cdf(z):
    """Standard-normal cumulative distribution function."""
    return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))


def norm_sf(z):
    """Standard-normal two-sided survival (P(|Z| > |z|))."""
    return 2.0 * (1.0 - norm_cdf(abs(z)))


def t_sf_two_sided(t, df):
    """Two-sided p-value for a Student-t statistic with df degrees of freedom."""
    if df <= 0:
        return float("nan")
    x = df / (df + t * t)
    return betai(0.5 * df, 0.5, x)


def f_sf(f, df1, df2):
    """Upper-tail p-value for an F statistic."""
    if f <= 0:
        return 1.0
    x = df2 / (df2 + df1 * f)
    return betai(0.5 * df2, 0.5 * df1, x)


def chi2_sf(x, df):
    """Upper-tail p-value for a chi-square statistic."""
    if x <= 0:
        return 1.0
    return 1.0 - gammp(0.5 * df, 0.5 * x)


# ----------------------------------------------------------------------
# Correlation
# ----------------------------------------------------------------------

def pearsonr(x, y):
    """Pearson correlation coefficient and two-sided p-value."""
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    n = len(x)
    r = np.corrcoef(x, y)[0, 1]
    if abs(r) >= 1.0:
        return r, 0.0
    df = n - 2
    t = r * math.sqrt(df / (1.0 - r * r))
    p = t_sf_two_sided(t, df)
    return r, p


def _rankdata(a):
    """Average ranks, handling ties (like scipy.stats.rankdata)."""
    a = np.asarray(a, dtype=float)
    order = np.argsort(a, kind="mergesort")
    ranks = np.empty(len(a), dtype=float)
    sa = a[order]
    i = 0
    n = len(a)
    while i < n:
        j = i
        while j + 1 < n and sa[j + 1] == sa[i]:
            j += 1
        avg = (i + j) / 2.0 + 1.0  # ranks are 1-based
        ranks[order[i:j + 1]] = avg
        i = j + 1
    return ranks


def spearmanr(x, y):
    """Spearman rank correlation coefficient and two-sided p-value."""
    rx = _rankdata(x)
    ry = _rankdata(y)
    return pearsonr(rx, ry)


# ----------------------------------------------------------------------
# Ordinary least-squares linear regression (single predictor)
# ----------------------------------------------------------------------

def linregress(x, y):
    """
    Simple linear regression y = intercept + slope * x.
    Returns a dict with slope, intercept, r, r2, p-value for the slope,
    standard error of the slope, and the t-statistic.
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    n = len(x)
    xm = x.mean()
    ym = y.mean()
    sxx = np.sum((x - xm) ** 2)
    sxy = np.sum((x - xm) * (y - ym))
    slope = sxy / sxx
    intercept = ym - slope * xm
    yhat = intercept + slope * x
    resid = y - yhat
    ss_res = np.sum(resid ** 2)
    ss_tot = np.sum((y - ym) ** 2)
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else float("nan")
    r = math.copysign(math.sqrt(max(r2, 0.0)), slope)
    df = n - 2
    s_err = math.sqrt(ss_res / df) if df > 0 else float("nan")
    se_slope = s_err / math.sqrt(sxx)
    t = slope / se_slope if se_slope > 0 else float("nan")
    p = t_sf_two_sided(t, df)
    return {"slope": slope, "intercept": intercept, "r": r, "r2": r2,
            "p": p, "se_slope": se_slope, "t": t, "n": n, "df": df,
            "resid": resid, "yhat": yhat}


# ----------------------------------------------------------------------
# Two-sample Welch t-test (unequal variances)
# ----------------------------------------------------------------------

def welch_ttest(a, b):
    """Welch's two-sample t-test. Returns t, df, two-sided p, means."""
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    na, nb = len(a), len(b)
    ma, mb = a.mean(), b.mean()
    va, vb = a.var(ddof=1), b.var(ddof=1)
    se = math.sqrt(va / na + vb / nb)
    t = (ma - mb) / se
    df = (va / na + vb / nb) ** 2 / (
        (va / na) ** 2 / (na - 1) + (vb / nb) ** 2 / (nb - 1))
    p = t_sf_two_sided(t, df)
    return {"t": t, "df": df, "p": p, "mean_a": ma, "mean_b": mb,
            "n_a": na, "n_b": nb}


# ----------------------------------------------------------------------
# One-way ANOVA
# ----------------------------------------------------------------------

def one_way_anova(groups):
    """One-way ANOVA across a list of 1-D arrays. Returns F, df1, df2, p."""
    groups = [np.asarray(g, dtype=float) for g in groups]
    grand = np.concatenate(groups)
    gm = grand.mean()
    k = len(groups)
    n = len(grand)
    ss_between = sum(len(g) * (g.mean() - gm) ** 2 for g in groups)
    ss_within = sum(np.sum((g - g.mean()) ** 2) for g in groups)
    df1 = k - 1
    df2 = n - k
    ms_between = ss_between / df1
    ms_within = ss_within / df2
    F = ms_between / ms_within
    p = f_sf(F, df1, df2)
    return {"F": F, "df1": df1, "df2": df2, "p": p}


# ----------------------------------------------------------------------
# Chi-square test of independence (contingency table)
# ----------------------------------------------------------------------

def chi2_independence(table):
    """Chi-square test of independence on a 2-D contingency table."""
    obs = np.asarray(table, dtype=float)
    row = obs.sum(axis=1, keepdims=True)
    col = obs.sum(axis=0, keepdims=True)
    total = obs.sum()
    exp = row @ col / total
    chi2 = np.sum((obs - exp) ** 2 / exp)
    df = (obs.shape[0] - 1) * (obs.shape[1] - 1)
    p = chi2_sf(chi2, df)
    return {"chi2": chi2, "df": df, "p": p, "expected": exp}


# ----------------------------------------------------------------------
# Mann-Kendall trend test (with tie correction) + Theil-Sen slope
# ----------------------------------------------------------------------

def mann_kendall(y):
    """
    Mann-Kendall non-parametric trend test.
    Returns S, Kendall's tau, the normal z statistic and two-sided p-value.
    """
    y = np.asarray(y, dtype=float)
    n = len(y)
    s = 0
    for i in range(n - 1):
        s += np.sum(np.sign(y[i + 1:] - y[i]))
    # variance with tie correction
    unique, counts = np.unique(y, return_counts=True)
    tie_term = np.sum(counts * (counts - 1) * (2 * counts + 5))
    var_s = (n * (n - 1) * (2 * n + 5) - tie_term) / 18.0
    if s > 0:
        z = (s - 1) / math.sqrt(var_s)
    elif s < 0:
        z = (s + 1) / math.sqrt(var_s)
    else:
        z = 0.0
    p = 2.0 * (1.0 - norm_cdf(abs(z)))
    tau = s / (0.5 * n * (n - 1))
    return {"S": s, "tau": tau, "z": z, "p": p, "var_s": var_s}


def theil_sen(x, y):
    """Theil-Sen median slope and intercept (robust trend estimate)."""
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    n = len(x)
    slopes = []
    for i in range(n - 1):
        for j in range(i + 1, n):
            if x[j] != x[i]:
                slopes.append((y[j] - y[i]) / (x[j] - x[i]))
    slope = float(np.median(slopes))
    intercept = float(np.median(y - slope * x))
    return {"slope": slope, "intercept": intercept}


# ----------------------------------------------------------------------
# Time-series helpers
# ----------------------------------------------------------------------

def moving_average(y, window):
    """Centered simple moving average; returns array with NaN at the edges."""
    y = np.asarray(y, dtype=float)
    n = len(y)
    out = np.full(n, np.nan)
    half = window // 2
    for i in range(n):
        lo = i - half
        hi = i + half + (window % 2)
        if lo >= 0 and hi <= n:
            out[i] = y[lo:hi].mean()
    return out


def seasonal_decompose_monthly(y, period=12):
    """
    Simple additive classical decomposition for a monthly series.
    trend  = centered moving average of length `period`
    seasonal = average detrended value for each calendar position
    residual = y - trend - seasonal
    Returns (trend, seasonal, residual).
    """
    y = np.asarray(y, dtype=float)
    n = len(y)
    # centered moving average (even period -> 2x smoothing)
    trend = np.full(n, np.nan)
    half = period // 2
    for i in range(n):
        if i - half >= 0 and i + half < n:
            window = y[i - half:i + half + 1].copy()
            # weight the endpoints by 0.5 for an even period
            weights = np.ones(len(window))
            weights[0] = 0.5
            weights[-1] = 0.5
            trend[i] = np.sum(window * weights) / np.sum(weights)
    detr = y - trend
    seasonal = np.full(n, np.nan)
    season_means = np.zeros(period)
    for m in range(period):
        vals = detr[m::period]
        vals = vals[~np.isnan(vals)]
        season_means[m] = vals.mean() if len(vals) else 0.0
    season_means -= season_means.mean()  # center so seasonal sums to ~0
    for i in range(n):
        seasonal[i] = season_means[i % period]
    residual = y - trend - seasonal
    return trend, seasonal, residual


def acf(y, nlags):
    """Sample autocorrelation function for lags 0..nlags (NaNs ignored as 0-mean)."""
    y = np.asarray(y, dtype=float)
    y = y[~np.isnan(y)]
    n = len(y)
    ym = y.mean()
    denom = np.sum((y - ym) ** 2)
    out = []
    for k in range(nlags + 1):
        num = np.sum((y[:n - k] - ym) * (y[k:] - ym))
        out.append(num / denom)
    return np.array(out)


def acf_confint(n, alpha=0.05):
    """Approximate +/- confidence bound for white-noise ACF (Bartlett)."""
    z = 1.959963984540054  # 97.5th percentile of N(0,1)
    return z / math.sqrt(n)


if __name__ == "__main__":
    # quick self-test against known values
    # t-dist: P(|T|>2.131) with df=15 ~ 0.0500 (t_0.025,15 = 2.131)
    print("t_sf(2.131,15)=", round(t_sf_two_sided(2.131, 15), 4), "(expect ~0.0500)")
    # chi2: P(X>3.841 | df=1) ~ 0.05
    print("chi2_sf(3.841,1)=", round(chi2_sf(3.841, 1), 4), "(expect ~0.0500)")
    # F: P(F>4.54 | 1,15) ~ 0.05  (F_0.05,1,15=4.54)
    print("f_sf(4.54,1,15)=", round(f_sf(4.54, 1, 15), 4), "(expect ~0.0500)")
    # normal: P(|Z|>1.96) ~ 0.05
    print("norm_sf(1.96)=", round(norm_sf(1.96), 4), "(expect ~0.0500)")
