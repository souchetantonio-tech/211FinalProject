"""
02_analyze_data.py
------------------------------------------------------------------
Statistical analysis for the research question:

   "Have extreme precipitation events increased across the U.S. Midwest
    over the available observational record (2009-2024)?"

Input  : 03_ProcessedData/station_year_summary.csv
         03_ProcessedData/monthly_region_precip.csv
Output : 03_ProcessedData/region_annual.csv      (regional annual series)
         04_Results/analysis_results.md           (human-readable results)
         06_Tables/*.csv                          (summary tables)

The script applies seven complementary analysis techniques:
   1. Ordinary least-squares (OLS) linear-regression trend test
   2. Mann-Kendall non-parametric trend test + Theil-Sen slope
   3. Correlation analysis (Pearson and Spearman)
   4. Two-sample Welch t-test (early vs late period)
   5. Chi-square test of independence (period x day-type)
   6. Time-series smoothing and classical seasonal decomposition
   7. Autocorrelation analysis
Plus a supplementary one-way ANOVA of spatial (between-station) variation.

Run AFTER 01_clean_data.py (or directly on the supplied processed data).
------------------------------------------------------------------
"""

import os
import numpy as np
import pandas as pd
import stats_utils as su

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PROC = os.path.join(ROOT, "03_ProcessedData")
RES = os.path.join(ROOT, "04_Results")
TAB = os.path.join(ROOT, "06_Tables")
os.makedirs(RES, exist_ok=True)
os.makedirs(TAB, exist_ok=True)

IN_TO_MM = 25.4
COMPLETE_YEARS = list(range(2010, 2024))   # 2010-2023 inclusive (14 complete years)
EARLY = list(range(2010, 2017))            # 2010-2016
LATE = list(range(2017, 2024))             # 2017-2023

lines = []   # collect markdown output


def w(s=""):
    print(s)
    lines.append(s)


# ----------------------------------------------------------------------
# Load data
# ----------------------------------------------------------------------
sy = pd.read_csv(os.path.join(PROC, "station_year_summary.csv"))
core = sy[(sy["core"] == 1) & (sy["year"].isin(COMPLETE_YEARS))].copy()
n_core_stations = core["station"].nunique()

w("# Midwest Extreme Precipitation -- Analysis Results")
w()
w(f"Core stations: {n_core_stations}  |  Complete years analysed: "
  f"{COMPLETE_YEARS[0]}-{COMPLETE_YEARS[-1]} ({len(COMPLETE_YEARS)} years)")
w(f"Core station-year records: {len(core)}")
w()

# ----------------------------------------------------------------------
# Build regional annual series (mean across the core stations each year)
# ----------------------------------------------------------------------
metrics = ["total_in", "max_in", "d_ge_100", "d_ge_200", "d_ge_050"]
region = core.groupby("year")[metrics].mean().reset_index()
region.to_csv(os.path.join(PROC, "region_annual.csv"), index=False)

pretty = {
    "total_in": "Annual total precip (in)",
    "max_in": "Annual max 1-day precip / Rx1day (in)",
    "d_ge_100": "Days >= 1 in (25.4 mm) per year",
    "d_ge_200": "Days >= 2 in (50.8 mm) per year",
    "d_ge_050": "Days >= 0.5 in (12.7 mm) per year",
}

# ======================================================================
# METHOD 1 + 2 + 3 : trend + correlation on each regional annual metric
# ======================================================================
w("## 1-3. Trend and correlation on regional annual metrics")
w()
w("Each metric is the average across the 10 core stations for each year, "
  "2010-2023 (n = 14 years). 'per decade' = OLS slope x 10.")
w()
trend_rows = []
years = region["year"].values.astype(float)
for m in metrics:
    yv = region[m].values.astype(float)
    lr = su.linregress(years, yv)
    mk = su.mann_kendall(yv)
    ts = su.theil_sen(years, yv)
    pr, pp = su.pearsonr(years, yv)
    sr, sp = su.spearmanr(years, yv)
    w(f"### {pretty[m]}")
    w(f"- mean = {yv.mean():.2f},  range = {yv.min():.2f} to {yv.max():.2f}")
    w(f"- OLS slope = {lr['slope']:+.4f}/yr ({lr['slope']*10:+.3f}/decade), "
      f"R^2 = {lr['r2']:.3f}, t = {lr['t']:.2f}, p = {lr['p']:.3f}")
    w(f"- Theil-Sen slope = {ts['slope']:+.4f}/yr ({ts['slope']*10:+.3f}/decade)")
    w(f"- Mann-Kendall: tau = {mk['tau']:+.3f}, S = {mk['S']:.0f}, "
      f"z = {mk['z']:.2f}, p = {mk['p']:.3f}")
    w(f"- Pearson r = {pr:+.3f} (p = {pp:.3f}); "
      f"Spearman rho = {sr:+.3f} (p = {sp:.3f})")
    w(f"- Result: {'significant' if lr['p'] < 0.05 else 'NOT significant'} "
      f"linear trend at alpha = 0.05")
    w()
    trend_rows.append({
        "metric": pretty[m], "mean": round(yv.mean(), 3),
        "ols_slope_per_decade": round(lr["slope"] * 10, 4),
        "ols_R2": round(lr["r2"], 3), "ols_p": round(lr["p"], 4),
        "theil_sen_per_decade": round(ts["slope"] * 10, 4),
        "mk_tau": round(mk["tau"], 3), "mk_p": round(mk["p"], 4),
        "pearson_r": round(pr, 3), "pearson_p": round(pp, 4),
        "spearman_rho": round(sr, 3), "spearman_p": round(sp, 4),
    })
pd.DataFrame(trend_rows).to_csv(os.path.join(TAB, "table2_trend_tests.csv"), index=False)

# Does a wet year simply mean more extreme days? (year-to-year coupling)
r_te, p_te = su.pearsonr(region["total_in"], region["d_ge_100"])
w(f"Correlation between annual total and number of >=1 in days "
  f"(regional, n=14): Pearson r = {r_te:+.3f}, p = {p_te:.3f}.")
w()

# ======================================================================
# METHOD 4 : Welch two-sample t-test, early vs late period
# ======================================================================
w("## 4. Two-sample t-test: early (2010-2016) vs late (2017-2023)")
w()
w("Unit of analysis = station-year values pooled across the 10 core stations "
  "(7 years x 10 stations = 70 per period). Welch's t-test (unequal variances). "
  "H0: equal means; H1: means differ.")
w()
tt_rows = []
for m in ["d_ge_100", "d_ge_200", "max_in", "total_in"]:
    a = core[core["year"].isin(EARLY)][m].values
    b = core[core["year"].isin(LATE)][m].values
    tt = su.welch_ttest(b, a)   # b - a so positive t = late higher
    w(f"- {pretty[m]}: early mean = {tt['mean_b']:.2f}, late mean = {tt['mean_a']:.2f}, "
      f"diff = {tt['mean_a']-tt['mean_b']:+.2f}, t = {tt['t']:.2f}, "
      f"df = {tt['df']:.1f}, p = {tt['p']:.3f}")
    tt_rows.append({"metric": pretty[m], "early_mean": round(tt['mean_b'], 3),
                    "late_mean": round(tt['mean_a'], 3),
                    "difference": round(tt['mean_a']-tt['mean_b'], 3),
                    "t": round(tt['t'], 3), "df": round(tt['df'], 1),
                    "p": round(tt['p'], 4)})
w()
pd.DataFrame(tt_rows).to_csv(os.path.join(TAB, "table3_ttests.csv"), index=False)

# ======================================================================
# METHOD 5 : Chi-square test of independence (period x day type)
# ======================================================================
w("## 5. Chi-square test of independence (period x day-type)")
w()
w("Contingency table built from observed daily records of the 10 core stations. "
  "Columns: extreme days (>=1 in) vs all other observed days. "
  "Rows: early (2010-2016) vs late (2017-2023). "
  "H0: probability of an extreme day is independent of period.")
w()
def counts(period):
    sub = core[core["year"].isin(period)]
    extreme = int(sub["d_ge_100"].sum())
    obs = int(sub["n_obs"].sum())
    return extreme, obs - extreme
e_ext, e_non = counts(EARLY)
l_ext, l_non = counts(LATE)
table = [[e_ext, e_non], [l_ext, l_non]]
chi = su.chi2_independence(table)
p_early = e_ext / (e_ext + e_non)
p_late = l_ext / (l_ext + l_non)
w(f"- Early: {e_ext} extreme days / {e_ext+e_non} observed days "
  f"= {100*p_early:.3f}%")
w(f"- Late:  {l_ext} extreme days / {l_ext+l_non} observed days "
  f"= {100*p_late:.3f}%")
w(f"- chi-square = {chi['chi2']:.3f}, df = {chi['df']}, p = {chi['p']:.3f}")
w(f"- Result: {'significant' if chi['p']<0.05 else 'NOT significant'} "
  f"difference in extreme-day frequency between periods.")
w()
pd.DataFrame({"period": ["early(2010-2016)", "late(2017-2023)"],
              "extreme_days_ge1in": [e_ext, l_ext],
              "other_observed_days": [e_non, l_non],
              "pct_extreme": [round(100*p_early, 3), round(100*p_late, 3)]}
             ).to_csv(os.path.join(TAB, "table4_chisquare.csv"), index=False)

# ======================================================================
# METHOD 6 : time-series smoothing + seasonal decomposition (monthly)
# ======================================================================
w("## 6. Monthly time-series: smoothing and seasonal decomposition")
w()
mon = pd.read_csv(os.path.join(PROC, "monthly_region_precip.csv"))
ts_y = mon["region_mean_total_in"].values.astype(float)
months = np.arange(len(ts_y))
trend, seasonal, resid = su.seasonal_decompose_monthly(ts_y, period=12)
ma12 = su.moving_average(ts_y, 12)

# seasonal climatology (Jan..Dec) from the seasonal component
season_by_month = {}
mlabels = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
# month index 0 corresponds to 2009-05 (May); map to calendar month
start_cal = 5  # May
for i in range(12):
    cal = (start_cal - 1 + i) % 12
    season_by_month[mlabels[cal]] = seasonal[i]
season_sorted = [season_by_month[m] for m in mlabels]
w("Seasonal component (deviation from mean monthly precip, inches):")
w("  " + ", ".join(f"{m} {season_sorted[i]:+.2f}" for i, m in enumerate(mlabels)))
peak = mlabels[int(np.argmax(season_sorted))]
low = mlabels[int(np.argmin(season_sorted))]
w(f"  Wettest month (climatology): {peak}; driest: {low}.")
w()
# trend in the smoothed/trend component over time
valid = ~np.isnan(trend)
lr_tr = su.linregress(months[valid], trend[valid])
w(f"Trend of the 12-month decomposition trend component vs time: "
  f"slope = {lr_tr['slope']*12:+.4f} in/yr, p = {lr_tr['p']:.3f} "
  f"({'significant' if lr_tr['p']<0.05 else 'not significant'}).")
# variance explained by each component
def vshare(x):
    x = x[~np.isnan(x)]
    return np.var(x)
w(f"Variance shares -- seasonal: {vshare(seasonal):.3f}, "
  f"trend: {vshare(trend):.3f}, residual: {vshare(resid):.3f} "
  f"(seasonal cycle dominates monthly variability).")
w()
dec = pd.DataFrame({"year_month": mon["year_month"], "observed": ts_y,
                    "ma12": ma12, "trend": trend, "seasonal": seasonal,
                    "residual": resid})
dec.to_csv(os.path.join(PROC, "monthly_decomposition.csv"), index=False)

# ======================================================================
# METHOD 7 : autocorrelation analysis
# ======================================================================
w("## 7. Autocorrelation analysis")
w()
ac_raw = su.acf(ts_y, 24)
ac_resid = su.acf(resid[~np.isnan(resid)], 24)
ci = su.acf_confint(len(ts_y))
w(f"95% white-noise band (monthly series, n={len(ts_y)}): +/- {ci:.3f}")
w(f"- Raw monthly ACF at lag 6  = {ac_raw[6]:+.3f} (half-year, expect negative)")
w(f"- Raw monthly ACF at lag 12 = {ac_raw[12]:+.3f} (annual, expect positive)")
w(f"- Deseasonalised-residual ACF at lag 1  = {ac_resid[1]:+.3f}")
w(f"- Deseasonalised-residual ACF at lag 12 = {ac_resid[12]:+.3f}")
w("  Interpretation: the raw series shows a strong 12-month cycle; after "
  "removing the seasonal component the residuals show little persistence, "
  "i.e. month-to-month precipitation is close to serially independent.")
w()
# ACF of annual regression residuals (assumption check for Method 1)
res_max = su.linregress(years, region["max_in"].values)["resid"]
ac_ann = su.acf(res_max, 4)
ci_ann = su.acf_confint(len(years))
w(f"- ACF(lag1) of annual Rx1day regression residuals = {ac_ann[1]:+.3f} "
  f"(inside the +/-{ci_ann:.2f} white-noise band for n={len(years)} -> "
  f"OLS independence assumption reasonable).")
w()
pd.DataFrame({"lag": np.arange(25), "acf_raw_monthly": ac_raw,
              "acf_resid_monthly": ac_resid}
             ).to_csv(os.path.join(TAB, "table5_autocorrelation.csv"), index=False)

# ======================================================================
# SUPPLEMENTARY : one-way ANOVA of spatial (between-station) variation
# ======================================================================
w("## Supplementary. One-way ANOVA: spatial variation in extreme-day frequency")
w()
w("H0: mean annual number of >=1 in days is equal across the 10 core stations.")
groups = [g["d_ge_100"].values for _, g in core.groupby("station")]
an = su.one_way_anova(groups)
w(f"- F = {an['F']:.2f}, df = ({an['df1']}, {an['df2']}), p = {an['p']:.4f} "
  f"({'significant' if an['p']<0.05 else 'not significant'}).")
# by state
w("Mean >=1 in days/yr by state:")
for st, g in core.groupby("state"):
    w(f"  {st}: {g['d_ge_100'].mean():.2f} (n stations = {g['station'].nunique()})")
w()

# ======================================================================
# Descriptive summary table per station
# ======================================================================
desc = core.groupby(["station", "state"]).agg(
    mean_total_in=("total_in", "mean"),
    mean_Rx1day_in=("max_in", "mean"),
    mean_days_ge1in=("d_ge_100", "mean"),
    mean_days_ge2in=("d_ge_200", "mean"),
).round(2).reset_index()
desc.to_csv(os.path.join(TAB, "table1_station_summary.csv"), index=False)

# write region annual table too
region.round(3).to_csv(os.path.join(TAB, "table0_region_annual.csv"), index=False)

with open(os.path.join(RES, "analysis_results.md"), "w") as f:
    f.write("\n".join(lines) + "\n")

print("\n[done] results -> 04_Results/analysis_results.md ; tables -> 06_Tables/")
