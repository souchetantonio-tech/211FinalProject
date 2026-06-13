"""
03_make_figures.py
------------------------------------------------------------------
Generate all figures for the Midwest extreme-precipitation project.

Input  : 03_ProcessedData/*.csv  (produced by 01_clean_data.py / supplied)
Output : 05_Figures/*.png

Figures
   fig1_regional_trends.png      annual Rx1day & >=1in days with OLS trend
   fig2_period_boxplots.png      station-year >=1in days: early vs late
   fig3_monthly_smoothing.png    monthly series + 12-month moving average
   fig4_seasonal_decomposition.png  observed / trend / seasonal / residual
   fig5_autocorrelation.png      ACF of raw vs deseasonalised series
   fig6_station_map.png          station locations sized by extreme frequency
   fig7_extreme_share.png        % extreme days early vs late (chi-square)
------------------------------------------------------------------
"""

import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import stats_utils as su

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PROC = os.path.join(ROOT, "03_ProcessedData")
FIG = os.path.join(ROOT, "05_Figures")
os.makedirs(FIG, exist_ok=True)

plt.rcParams.update({"figure.dpi": 130, "font.size": 11,
                     "axes.grid": True, "grid.alpha": 0.3,
                     "axes.spines.top": False, "axes.spines.right": False})
BLUE, RED, GREY = "#2c6fbb", "#c0392b", "#7f8c8d"

sy = pd.read_csv(os.path.join(PROC, "station_year_summary.csv"))
meta = pd.read_csv(os.path.join(PROC, "station_metadata.csv"))
region = pd.read_csv(os.path.join(PROC, "region_annual.csv"))
mon = pd.read_csv(os.path.join(PROC, "monthly_region_precip.csv"))
dec = pd.read_csv(os.path.join(PROC, "monthly_decomposition.csv"))

COMPLETE = list(range(2010, 2024))
EARLY, LATE = list(range(2010, 2017)), list(range(2017, 2024))
core = sy[(sy.core == 1) & (sy.year.isin(COMPLETE))].copy()
yr = region["year"].values.astype(float)


def trendline(ax, x, y, color, label):
    lr = su.linregress(x, y)
    xx = np.array([x.min(), x.max()])
    ax.plot(xx, lr["intercept"] + lr["slope"] * xx, "--", color=color, lw=1.6)
    return lr


# ---- fig1 : regional annual trends ----------------------------------
fig, ax = plt.subplots(1, 2, figsize=(11, 4.2))
for a, m, lab, col in [(ax[0], "max_in", "Annual max 1-day precip (in)", BLUE),
                       (ax[1], "d_ge_100", "Days ≥ 1 in (25.4 mm) / yr", RED)]:
    yv = region[m].values
    a.plot(yr, yv, "o-", color=col, lw=1.8, ms=5)
    lr = trendline(a, yr, yv, GREY, None)
    a.set_title(f"{lab}\nOLS {lr['slope']*10:+.2f}/decade, p = {lr['p']:.2f}",
                fontsize=10)
    a.set_xlabel("Year")
ax[0].set_ylabel("inches")
ax[1].set_ylabel("days per year")
fig.suptitle("Regional mean annual extreme-precipitation metrics, 10 Midwest stations (2010–2023)",
             fontsize=11, y=1.02)
fig.tight_layout()
fig.savefig(os.path.join(FIG, "fig1_regional_trends.png"), bbox_inches="tight")
plt.close(fig)

# ---- fig2 : early vs late boxplots -----------------------------------
fig, ax = plt.subplots(1, 2, figsize=(9, 4.2))
for a, m, lab in [(ax[0], "d_ge_100", "Days ≥ 1 in per year"),
                  (ax[1], "total_in", "Annual total precip (in)")]:
    e = core[core.year.isin(EARLY)][m].values
    l = core[core.year.isin(LATE)][m].values
    bp = a.boxplot([e, l], labels=["2010–2016", "2017–2023"],
                   patch_artist=True, widths=0.55, showmeans=True)
    for patch, c in zip(bp["boxes"], [BLUE, RED]):
        patch.set_facecolor(c); patch.set_alpha(0.45)
    tt = su.welch_ttest(l, e)
    a.set_title(f"{lab}\nWelch t-test p = {tt['p']:.3f}", fontsize=10)
    a.set_ylabel(lab)
fig.suptitle("Station-year distributions: early vs late period", y=1.02, fontsize=11)
fig.tight_layout()
fig.savefig(os.path.join(FIG, "fig2_period_boxplots.png"), bbox_inches="tight")
plt.close(fig)

# ---- fig3 : monthly smoothing ----------------------------------------
fig, ax = plt.subplots(figsize=(12, 4))
x = np.arange(len(mon))
ax.plot(x, mon["region_mean_total_in"], color=GREY, lw=0.9, alpha=0.7,
        label="Monthly regional mean")
ax.plot(x, su.moving_average(mon["region_mean_total_in"].values, 12),
        color=RED, lw=2.3, label="12-month moving average")
ticks = x[::12]
ax.set_xticks(ticks)
ax.set_xticklabels(mon["year_month"].values[::12], rotation=45, ha="right")
ax.set_ylabel("Precipitation (in)")
ax.set_title("Monthly regional precipitation with 12-month smoothing (2009–2024)")
ax.legend(frameon=False)
fig.tight_layout()
fig.savefig(os.path.join(FIG, "fig3_monthly_smoothing.png"), bbox_inches="tight")
plt.close(fig)

# ---- fig4 : seasonal decomposition -----------------------------------
fig, ax = plt.subplots(4, 1, figsize=(12, 8), sharex=True)
comps = [("observed", "Observed", GREY), ("trend", "Trend", BLUE),
         ("seasonal", "Seasonal", "#27ae60"), ("residual", "Residual", RED)]
for a, (c, lab, col) in zip(ax, comps):
    a.plot(x, dec[c], color=col, lw=1.4)
    a.set_ylabel(lab)
    a.axhline(0, color="k", lw=0.5, alpha=0.3)
ax[-1].set_xticks(ticks)
ax[-1].set_xticklabels(mon["year_month"].values[::12], rotation=45, ha="right")
fig.suptitle("Classical additive decomposition of monthly regional precipitation", y=0.995)
fig.tight_layout()
fig.savefig(os.path.join(FIG, "fig4_seasonal_decomposition.png"), bbox_inches="tight")
plt.close(fig)

# ---- fig5 : autocorrelation ------------------------------------------
ts = mon["region_mean_total_in"].values
resid = dec["residual"].values
ac_raw = su.acf(ts, 24)
ac_res = su.acf(resid[~np.isnan(resid)], 24)
ci = su.acf_confint(len(ts))
fig, ax = plt.subplots(1, 2, figsize=(11, 4), sharey=True)
for a, ac, lab in [(ax[0], ac_raw, "Raw monthly series"),
                   (ax[1], ac_res, "Deseasonalised residuals")]:
    lags = np.arange(len(ac))
    a.bar(lags, ac, width=0.5, color=BLUE)
    a.axhline(ci, color=RED, ls="--", lw=1)
    a.axhline(-ci, color=RED, ls="--", lw=1)
    a.axhline(0, color="k", lw=0.6)
    a.set_title(lab, fontsize=10)
    a.set_xlabel("Lag (months)")
ax[0].set_ylabel("Autocorrelation")
fig.suptitle("Autocorrelation function (dashed = 95% white-noise band)", y=1.02, fontsize=11)
fig.tight_layout()
fig.savefig(os.path.join(FIG, "fig5_autocorrelation.png"), bbox_inches="tight")
plt.close(fig)

# ---- fig6 : station map ----------------------------------------------
cm = meta[meta.core == 1].merge(
    core.groupby("station")["d_ge_100"].mean().rename("mean_ge1"),
    on="station")
fig, ax = plt.subplots(figsize=(7.5, 6.5))
sc = ax.scatter(cm["lon"], cm["lat"], s=cm["mean_ge1"] * 35,
                c=cm["mean_ge1"], cmap="YlOrRd", edgecolor="k", zorder=3)
for _, r in cm.iterrows():
    short = r["name"].split(",")[0].title()
    ax.annotate(short, (r["lon"], r["lat"]), fontsize=7,
                xytext=(4, 4), textcoords="offset points")
plt.colorbar(sc, label="Mean days ≥ 1 in per year")
ax.set_xlabel("Longitude"); ax.set_ylabel("Latitude")
ax.set_title("Core station network and mean heavy-precipitation frequency")
fig.tight_layout()
fig.savefig(os.path.join(FIG, "fig6_station_map.png"), bbox_inches="tight")
plt.close(fig)

# ---- fig7 : extreme-day share early vs late --------------------------
def share(period):
    sub = core[core.year.isin(period)]
    return 100 * sub["d_ge_100"].sum() / sub["n_obs"].sum()
vals = [share(EARLY), share(LATE)]
fig, ax = plt.subplots(figsize=(5.2, 4.4))
bars = ax.bar(["2010–2016", "2017–2023"], vals, color=[BLUE, RED],
              alpha=0.8, width=0.6)
for b, v in zip(bars, vals):
    ax.text(b.get_x() + b.get_width()/2, v + 0.02, f"{v:.2f}%",
            ha="center", fontsize=11)
ax.set_ylabel("Share of observed days ≥ 1 in")
ax.set_title("Heavy-precipitation day frequency\n(chi-square p = 0.029)")
ax.set_ylim(0, max(vals) * 1.25)
fig.tight_layout()
fig.savefig(os.path.join(FIG, "fig7_extreme_share.png"), bbox_inches="tight")
plt.close(fig)

print("[done] figures written to 05_Figures/:",
      sorted(os.listdir(FIG)))
