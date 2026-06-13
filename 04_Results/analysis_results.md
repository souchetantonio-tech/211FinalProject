# Midwest Extreme Precipitation -- Analysis Results

Core stations: 10  |  Complete years analysed: 2010-2023 (14 years)
Core station-year records: 140

## 1-3. Trend and correlation on regional annual metrics

Each metric is the average across the 10 core stations for each year, 2010-2023 (n = 14 years). 'per decade' = OLS slope x 10.

### Annual total precip (in)
- mean = 37.17,  range = 26.23 to 47.04
- OLS slope = +0.0712/yr (+0.712/decade), R^2 = 0.003, t = 0.20, p = 0.843
- Theil-Sen slope = -0.1134/yr (-1.134/decade)
- Mann-Kendall: tau = -0.077, S = -7, z = -0.33, p = 0.743
- Pearson r = +0.058 (p = 0.843); Spearman rho = -0.147 (p = 0.615)
- Result: NOT significant linear trend at alpha = 0.05

### Annual max 1-day precip / Rx1day (in)
- mean = 2.75,  range = 2.01 to 3.76
- OLS slope = -0.0148/yr (-0.148/decade), R^2 = 0.017, t = -0.46, p = 0.656
- Theil-Sen slope = -0.0147/yr (-0.147/decade)
- Mann-Kendall: tau = -0.121, S = -11, z = -0.55, p = 0.584
- Pearson r = -0.131 (p = 0.656); Spearman rho = -0.213 (p = 0.464)
- Result: NOT significant linear trend at alpha = 0.05

### Days >= 1 in (25.4 mm) per year
- mean = 8.25,  range = 4.40 to 11.80
- OLS slope = +0.0495/yr (+0.495/decade), R^2 = 0.014, t = 0.41, p = 0.686
- Theil-Sen slope = +0.0000/yr (+0.000/decade)
- Mann-Kendall: tau = +0.011, S = 1, z = 0.00, p = 1.000
- Pearson r = +0.119 (p = 0.686); Spearman rho = -0.110 (p = 0.708)
- Result: NOT significant linear trend at alpha = 0.05

### Days >= 2 in (50.8 mm) per year
- mean = 1.42,  range = 0.50 to 2.20
- OLS slope = -0.0279/yr (-0.279/decade), R^2 = 0.049, t = -0.79, p = 0.447
- Theil-Sen slope = -0.0333/yr (-0.333/decade)
- Mann-Kendall: tau = -0.132, S = -12, z = -0.61, p = 0.544
- Pearson r = -0.221 (p = 0.447); Spearman rho = -0.237 (p = 0.415)
- Result: NOT significant linear trend at alpha = 0.05

### Days >= 0.5 in (12.7 mm) per year
- mean = 24.01,  range = 15.20 to 31.10
- OLS slope = +0.0688/yr (+0.688/decade), R^2 = 0.005, t = 0.25, p = 0.803
- Theil-Sen slope = -0.0250/yr (-0.250/decade)
- Mann-Kendall: tau = -0.055, S = -5, z = -0.22, p = 0.826
- Pearson r = +0.073 (p = 0.803); Spearman rho = -0.148 (p = 0.615)
- Result: NOT significant linear trend at alpha = 0.05

Correlation between annual total and number of >=1 in days (regional, n=14): Pearson r = +0.918, p = 0.000.

## 4. Two-sample t-test: early (2010-2016) vs late (2017-2023)

Unit of analysis = station-year values pooled across the 10 core stations (7 years x 10 stations = 70 per period). Welch's t-test (unequal variances). H0: equal means; H1: means differ.

- Days >= 1 in (25.4 mm) per year: early mean = 7.73, late mean = 8.77, diff = +1.04, t = 1.94, df = 135.5, p = 0.055
- Days >= 2 in (50.8 mm) per year: early mean = 1.43, late mean = 1.41, diff = -0.01, t = -0.07, df = 137.1, p = 0.943
- Annual max 1-day precip / Rx1day (in): early mean = 2.71, late mean = 2.79, diff = +0.08, t = 0.44, df = 134.0, p = 0.664
- Annual total precip (in): early mean = 35.93, late mean = 38.40, diff = +2.47, t = 2.01, df = 137.4, p = 0.046

## 5. Chi-square test of independence (period x day-type)

Contingency table built from observed daily records of the 10 core stations. Columns: extreme days (>=1 in) vs all other observed days. Rows: early (2010-2016) vs late (2017-2023). H0: probability of an extreme day is independent of period.

- Early: 541 extreme days / 25519 observed days = 2.120%
- Late:  614 extreme days / 25493 observed days = 2.409%
- chi-square = 4.797, df = 1, p = 0.029
- Result: significant difference in extreme-day frequency between periods.

## 6. Monthly time-series: smoothing and seasonal decomposition

Seasonal component (deviation from mean monthly precip, inches):
  Jan -1.46, Feb -1.21, Mar -0.54, Apr +0.61, May +1.62, Jun +1.12, Jul +1.09, Aug +0.47, Sep -0.03, Oct +0.43, Nov -1.14, Dec -0.97
  Wettest month (climatology): May; driest: Jan.

Trend of the 12-month decomposition trend component vs time: slope = +0.0034 in/yr, p = 0.653 (not significant).
Variance shares -- seasonal: 1.007, trend: 0.161, residual: 1.562 (seasonal cycle dominates monthly variability).

## 7. Autocorrelation analysis

95% white-noise band (monthly series, n=181): +/- 0.146
- Raw monthly ACF at lag 6  = -0.249 (half-year, expect negative)
- Raw monthly ACF at lag 12 = +0.307 (annual, expect positive)
- Deseasonalised-residual ACF at lag 1  = -0.107
- Deseasonalised-residual ACF at lag 12 = -0.030
  Interpretation: the raw series shows a strong 12-month cycle; after removing the seasonal component the residuals show little persistence, i.e. month-to-month precipitation is close to serially independent.

- ACF(lag1) of annual Rx1day regression residuals = -0.339 (inside the +/-0.52 white-noise band for n=14 -> OLS independence assumption reasonable).

## Supplementary. One-way ANOVA: spatial variation in extreme-day frequency

H0: mean annual number of >=1 in days is equal across the 10 core stations.
- F = 5.86, df = (9, 130), p = 0.0000 (significant).
Mean >=1 in days/yr by state:
  IL: 7.82 (n stations = 8)
  MO: 12.57 (n stations = 1)
  OH: 7.36 (n stations = 1)

