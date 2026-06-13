"""
01_clean_data.py
------------------------------------------------------------------
Clean the raw NOAA GHCN-Daily download and build the processed datasets
used by every downstream script.

Input  : 02_RawData/4311294.csv      (raw GHCN-Daily, one row per station-day)
Output : 03_ProcessedData/station_metadata.csv
         03_ProcessedData/station_year_summary.csv
         03_ProcessedData/monthly_region_precip.csv

Raw schema (NOAA CDO "standard" units):
   STATION, NAME, LATITUDE, LONGITUDE, ELEVATION, DATE,
   DAPR  (number of days in a multi-day precip total),
   MDPR  (multi-day precip total, inches),
   PRCP  (daily precipitation, inches)

Cleaning / processing decisions (documented in the final report):
  * PRCP is in INCHES (NOAA standard units). Heavy-precipitation thresholds
    are defined as 1 in (25.4 mm) and 2 in (50.8 mm); 0.5 in (12.7 mm) is
    kept as a moderate-rain reference.
  * Rows with a blank PRCP are treated as missing and ignored in sums/counts.
  * The "core" analysis network keeps the 10 stations that (a) lie in the
    Midwest (Illinois, Ohio, Missouri) and (b) have a complete daily record
    spanning the full 2009-05 to 2024-05 download window. Excluded:
      - USW00054740 (Springfield, VERMONT) -- outside the Midwest;
      - USW00063888 (Beckley, OH) -- record only begins 2017 and contains an
        implausible 2020 value (24.98 in in a single day / 305 in for the
        year), a clear data-quality error;
      - USC00116703 (Peoria, IL) -- only 296 days of data (2009-2010).
    All 13 stations are retained in the station-year file (core flag = 0/1)
    for transparency; only core==1 stations enter the trend analysis.
  * Annual metrics are computed for every calendar year, but only COMPLETE
    calendar years (2010-2023) are used downstream, because 2009 is missing
    Jan-Apr and 2024 is missing Jun-Dec in this download.

This script reproduces, byte-for-byte, the processed CSVs shipped in
03_ProcessedData (verified via character checksums).
------------------------------------------------------------------
"""

import os
import re
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
RAW = os.path.join(ROOT, "02_RawData", "4311294.csv")
PROC = os.path.join(ROOT, "03_ProcessedData")
os.makedirs(PROC, exist_ok=True)

# The 10 Midwest stations with a complete 2009-2024 record.
CORE = {
    "USW00094846",  # Chicago O'Hare, IL
    "USW00014880",  # Chicago Waukegan, IL
    "USW00094830",  # Toledo Express, OH
    "USW00004838",  # Chicago Palwaukee, IL
    "USW00013995",  # Springfield WSO, MO
    "USW00004808",  # Chicago Aurora, IL
    "USW00094822",  # Rockford, IL
    "USW00093822",  # Springfield Abraham Lincoln, IL
    "USW00014819",  # Chicago Midway, IL
    "USW00094892",  # Chicago West Chicago DuPage, IL
}


def state_of(name):
    m = re.search(r",\s*([A-Z]{2})\s*US", str(name))
    return m.group(1) if m else "?"


def main():
    df = pd.read_csv(RAW, dtype={"STATION": str})
    df["state"] = df["NAME"].map(state_of)
    df["DATE"] = pd.to_datetime(df["DATE"])
    df["year"] = df["DATE"].dt.year
    df["ym"] = df["DATE"].dt.strftime("%Y-%m")
    df["core"] = df["STATION"].isin(CORE).astype(int)

    # --- station metadata ------------------------------------------------
    meta = (df.groupby("STATION")
              .agg(name=("NAME", "first"), state=("state", "first"),
                   lat=("LATITUDE", "first"), lon=("LONGITUDE", "first"),
                   elev_m=("ELEVATION", "first"), n_days=("DATE", "size"),
                   min_date=("DATE", "min"), max_date=("DATE", "max"),
                   core=("core", "first"))
              .reset_index().rename(columns={"STATION": "station"}))
    meta["min_date"] = meta["min_date"].dt.strftime("%Y-%m-%d")
    meta["max_date"] = meta["max_date"].dt.strftime("%Y-%m-%d")
    meta.to_csv(os.path.join(PROC, "station_metadata.csv"), index=False)

    # --- station-year summary -------------------------------------------
    valid = df[df["PRCP"].notna()].copy()
    g = valid.groupby(["STATION", "state", "core", "year"])
    sy = g.agg(
        n_obs=("PRCP", "size"),
        total_in=("PRCP", "sum"),
        max_in=("PRCP", "max"),
        d_ge_050=("PRCP", lambda s: int((s >= 0.5).sum())),
        d_ge_100=("PRCP", lambda s: int((s >= 1.0).sum())),
        d_ge_200=("PRCP", lambda s: int((s >= 2.0).sum())),
        wet_days=("PRCP", lambda s: int((s >= 0.01).sum())),
    ).reset_index().rename(columns={"STATION": "station"})
    sy["total_in"] = sy["total_in"].round(2)
    sy["max_in"] = sy["max_in"].round(2)
    sy = sy.sort_values(["station", "year"])
    sy.to_csv(os.path.join(PROC, "station_year_summary.csv"), index=False)

    # --- monthly regional series (core stations only) -------------------
    core_valid = valid[valid["core"] == 1]
    station_month = (core_valid.groupby(["ym", "STATION"])["PRCP"]
                     .sum().reset_index())
    mon = (station_month.groupby("ym")
           .agg(n_stations=("STATION", "nunique"),
                region_mean_total_in=("PRCP", "mean"),
                region_sum_total_in=("PRCP", "sum"))
           .reset_index().rename(columns={"ym": "year_month"}))
    mon["region_mean_total_in"] = mon["region_mean_total_in"].round(3)
    mon["region_sum_total_in"] = mon["region_sum_total_in"].round(3)
    mon.to_csv(os.path.join(PROC, "monthly_region_precip.csv"), index=False)

    print(f"[done] {len(meta)} stations, {len(sy)} station-years, "
          f"{len(mon)} months written to 03_ProcessedData/")


if __name__ == "__main__":
    main()
