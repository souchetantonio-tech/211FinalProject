# Have extreme precipitation events increased across the U.S. Midwest?

**A data-analysis project using NOAA GHCN-Daily station records (2009–2024).**

## Research question

Has the frequency or intensity of **extreme precipitation events** changed
across the U.S. Midwest over the available observational record? The project
was originally framed around a 30-year window (1990–2024); however, the daily
station records obtained from NOAA for the selected stations only begin in
**May 2009**, so the analysis is honestly scoped to the **2009–2024** download
(with formal trend tests run on the 14 complete calendar years, 2010–2023).

## Short summary

Daily precipitation from **10 core Midwest weather stations** (Illinois, Ohio,
Missouri) is aggregated into annual extreme-precipitation indices (annual
maximum 1-day rainfall, and counts of days ≥ 0.5 / 1 / 2 inches) and a monthly
regional series. Seven complementary techniques are applied. At the
regional-annual scale **no statistically significant monotonic trend** is
found in any extreme index — the 14-year record is simply too short to resolve
one. However, higher-powered tests that pool the station-level data detect a
**modest but statistically significant increase** in the frequency of
heavy-rain days (≥ 1 in) in the later half of the record (2.12 % → 2.41 % of
days; χ² p = 0.029), while the most intense metrics (annual maximum, days ≥ 2
in) show no change. The evidence is therefore *suggestive of*, but far from
*conclusive proof of*, an increase in Midwest extreme precipitation.

## Data sources

* **NOAA GHCN-Daily** daily precipitation (`02_RawData/4311294.csv`), obtained
  from NOAA Climate Data Online, https://www.ncdc.noaa.gov/cdo-web/ .
* Spatial coverage: 13 stations in IL, OH, MO (+ 1 VT station used only for
  screening). Temporal coverage: 2009-05-01 to 2024-05-31. Main variable:
  daily precipitation `PRCP` (inches).

Full citations are in `07_References/references.md`.

## Repository structure

```
README.md                  – this overview
01_Code/                   – analysis pipeline (numbered, run in order)
  ├─ 01_clean_data.py       raw GHCN CSV → processed datasets
  ├─ 02_analyze_data.py     all statistical tests → 04_Results + 06_Tables
  ├─ 03_make_figures.py     all figures → 05_Figures
  └─ stats_utils.py         self-contained statistics library (no SciPy needed)
02_RawData/                – raw NOAA download (unmodified) + data notes
03_ProcessedData/          – cleaned station-year, monthly, and metadata CSVs
04_Results/                – analysis_results.md (human-readable findings)
05_Figures/                – publication figures (PNG)
06_Tables/                 – summary tables (CSV)
07_References/             – data, literature, software, and method citations
08_Final_Report/           – Final_Report.md (the full report)
09_Other_Materials/        – supporting notes
```

## Analysis workflow

1. **Clean** (`01_clean_data.py`) — parse the raw GHCN file, label states,
   flag the 10-station Midwest "core" network, drop a data-quality error,
   and write three processed CSVs.
2. **Analyze** (`02_analyze_data.py`) — build the regional annual and monthly
   series and run: (1) OLS linear-regression trend, (2) Mann-Kendall +
   Theil-Sen, (3) Pearson/Spearman correlation, (4) Welch two-sample t-test,
   (5) χ² test of independence, (6) seasonal decomposition + smoothing,
   (7) autocorrelation analysis, plus a one-way ANOVA of spatial variation.
3. **Visualize** (`03_make_figures.py`) — produce the seven figures.

### Reproducing

```bash
cd 01_Code
python 01_clean_data.py     # requires 02_RawData/4311294.csv
python 02_analyze_data.py
python 03_make_figures.py
```

Only NumPy, pandas, and Matplotlib are required; all statistical tests are
implemented in `stats_utils.py`. The processed CSVs are also committed, so
steps 2–3 run without re-downloading the raw data.

## Generative AI

Generative AI assisted with brainstorming, data-source discovery, code
scaffolding, and editing; every meaningful use is documented in the
**Generative AI Acknowledgment** section of `08_Final_Report/Final_Report.md`.
All numbers were produced by the committed code and independently checked.
