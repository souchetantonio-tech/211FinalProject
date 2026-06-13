# 02_RawData

Raw, unmodified data exactly as downloaded from the providers.

## Files used in the final analysis

| File | Source | Description |
|------|--------|-------------|
| `4311294.csv` | NOAA GHCN-Daily via [CDO](https://www.ncdc.noaa.gov/cdo-web/) | Daily precipitation (PRCP, inches) for 13 stations, 2009-05-01 to 2024-05-31. One row per station-day. Columns: STATION, NAME, LATITUDE, LONGITUDE, ELEVATION, DATE, DAPR, MDPR, PRCP. **This is the dataset analysed in the project.** |

## Files collected for an alternative question (not used)

During the proposal stage a second research question on Chicago urban heat was
considered. The files below were downloaded for that idea and are kept for
record, but the final project focuses solely on Midwest precipitation, so they
are **not** part of the analysis pipeline.

| File | Source | Description |
|------|--------|-------------|
| `landsat_ot_c2_l2_6a028d11a8777548.csv` | USGS EarthExplorer | Landsat 8/9 Collection-2 Level-2 scene metadata (acquisition date, path/row, cloud cover). |
| `LC08_L2SP_023031_20230831_..._QA_PIXEL.TIF` | USGS EarthExplorer | Landsat 8 QA-pixel band (GeoTIFF) for a single Chicago scene. |
| `ACS_5_Year_Data_by_Ward_20260511.csv` | U.S. Census Bureau (data.census.gov) | ACS 5-year demographic estimates by Chicago ward. |

## Notes / data quality

* PRCP is reported in **inches** (NOAA "standard" units).
* Blank PRCP cells denote missing daily observations.
* One non-core station, `USW00063888` (Beckley, OH), contains an implausible
  2020 value (24.98 in in one day; 305 in for the year) — a clear data error.
  It is excluded from the core analysis network (see `01_Code/01_clean_data.py`).
