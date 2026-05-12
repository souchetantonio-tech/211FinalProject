# 211FinalProject

# Part 3

## Question 1
### How does summer land surface temperature vary across Chicago neighborhoods, and is higher heat exposure associated with differences in income, tree cover, or population density?

This project will track patterns of urban heat across Chicago neighborhoods during the summer. The goal is to determine whether lower income neighborhoods (often those with lower tree coverage or higher population density) experience higher surface temperatures. Urban heat exposure is an important environmental and public health issue because extreme heat can increase heat-related illness, worsen air quality, and affect vulnerable communities. Understanding spatial differences in heat exposure can help identify environmental inequalities and support urban planning strategies like increasing tree coverage or green infrastructure. This topic is scientifically meaningful because it combines geospatial analysis, remote sensing, environmental statistics, and urban environmental science.

### Response Variable
- Summer land surface temperature (LST)

### Explanatory Variables
- Median household income
- Tree canopy coverage or NDVI vegetation index
- Population density
- Distance from downtown or lakefront

### Data Sources
- Landsat 8 or Landsat 9 satellite imagery for land surface temperature
- MODIS land surface temperature products
- U.S. Census American Community Survey (ACS) demographic data
- Chicago Data Portal neighborhood boundary shapefiles
- Chicago tree canopy or vegetation datasets
- NOAA climate datasets (optional for comparison)

### Types of Analysis
- Geospatial analysis using GIS or Python geospatial libraries
- Correlation analysis
- Multiple linear regression
- Heat maps and choropleth maps
- Scatterplots comparing LST with income, tree cover, and population density

---

## Question 2
### Have extreme precipitation events increased in the Midwest over the past 30 years?

This project will investigate whether the frequency or intensity of extreme precipitation events have changed across the Midwest region of the United States between 1990 and 2024. The analysis will focus on identifying long-term trends in heavy rainfall events and determining whether these have become more common over time.

Extreme precipitation can cause flooding, infrastructure damage, agricultural impacts, and public safety risks. Climate studies suggest that warming temperatures may increase atmospheric moisture and contribute to heavier rainfall events. Investigating precipitation trends in the Midwest is scientifically meaningful because the region is highly sensitive to flooding and agricultural disruption. This project also connects to broader climate change research.

### Response Variables
- Daily precipitation totals
- Annual maximum precipitation
- Number of heavy precipitation days per year
- Frequency of rainfall above some threshold

### Explanatory Variables
- Year or time
- Geographic region or station location

# Part 4

### Data Sources
- NOAA Global Historical Climatology Network (GHCN)
- NOAA National Centers for Environmental Information (NCEI)
- PRISM climate datasets
- NOAA weather station observations
- Midwest regional climate datasets

### Types of Analysis
- Time-series analysis
- Linear regression
- Statistical summaries of annual extremes
- Geographic visualization of precipitation trends
- Histograms or boxplots comparing precipitation distributions over time

### Data Sources in 02_RawData
Landsat Collection 2 Level-2 scene metadata (Landsat 8/9) from the USGS EarthExplorer website: https://earthexplorer.usgs.gov/. The spatial coverage includes Landsat scenes overlapping Chicago and the broader Midwest region, and the temporal coverage spans summer 2023 (June–August). The main variables include acquisition date, satellite (Landsat 8 or 9), path/row, cloud cover percentage, and scene identifiers. The file format is CSV (.csv).

Landsat Collection 2 Level-2 QA Pixel band (Landsat 8) from the U.S. Geological Survey EarthExplorer website: https://earthexplorer.usgs.gov/
. The spatial coverage includes a Landsat scene overlapping Chicago and the surrounding Midwest region, and the temporal coverage corresponds to a single acquisition date on August 31, 2023. The main variables include pixel-level quality assessment values indicating cloud cover, cloud shadows, snow, water, and other surface conditions used for masking and preprocessing satellite imagery. The file format is GeoTIFF (.tif).


