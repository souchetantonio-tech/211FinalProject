# 09_Other_Materials — supporting notes

## Reproducibility note
All results, tables, and figures in this repository are produced by the three
numbered scripts in `01_Code/`, in order. The processed datasets in
`03_ProcessedData/` are committed so that `02_analyze_data.py` and
`03_make_figures.py` run without re-downloading the raw GHCN file. Running
`01_clean_data.py` against `02_RawData/4311294.csv` regenerates those processed
datasets.

## Statistics library
Because the environment used to build the project did not have SciPy or
statsmodels available, `01_Code/stats_utils.py` implements the needed
distributions (Student-t, F, χ², normal) from the regularized incomplete
beta/gamma functions, plus Pearson/Spearman correlation, OLS regression,
Welch's t-test, one-way ANOVA, the χ² independence test, the Mann-Kendall trend
test, the Theil-Sen slope, moving-average smoothing, classical seasonal
decomposition, and the autocorrelation function. The module includes a
self-test (`python stats_utils.py`) that reproduces standard 0.05 critical
values.

## Scope decision
The proposal framed the question over ~30 years (1990–2024). The NOAA records
actually returned for the chosen stations begin in May 2009, so the analysis
was honestly re-scoped to the available 2009–2024 record (formal trend tests on
the 14 complete calendar years 2010–2023). This is discussed in the report's
Data and Discussion sections.
