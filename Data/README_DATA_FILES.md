# Data Files Documentation

This folder contains all data files used in the Costa Rica Mobility analysis pipeline.

## Input Data Files (Source Data)

### `malaria_cr_2023.csv`
- **Description**: Raw 2023 malaria case data from Google Sheets
- **Created by**: Process CR malaria data.Rmd (downloaded from Google Drive)
- **Used in**: Process CR malaria data.Rmd
- **Content**: Individual malaria cases with location, date, and case information

### `Costa_Rica_districts.gpkg`
- **Description**: Full district polygon boundaries for Costa Rica
- **Source**: External shapefile data (CR_district_population_GHSL_2025)
- **Used in**: Data prep for shiny app.Rmd, Process CR malaria data.Rmd
- **Content**: District polygons with province and district names

### `costa_rica_activity_tiles.gpkg`
- **Description**: Base tile polygons created from mobility data visit locations
- **Created by**: Process CR Mobility Data.Rmd
- **Used in**: calculate_population_new_tiles.py
- **Content**: Tile polygon geometries (no attributes)

## Processed Data Files

### `malaria_cases_2023_geocoded.rds`
- **Description**: Geocoded malaria cases from 2023 with final coordinates
- **Created by**: Process CR malaria data.Rmd
- **Used in**: Data prep for shiny app.Rmd
- **Content**: Malaria cases with geocoded lat/lon coordinates, district assignments

### `malaria_cases_2023_points.rds`
- **Description**: Spatial points for malaria cases (2023)
- **Created by**: Data prep for shiny app.Rmd
- **Used in**: Data prep for shiny app.Rmd, Create static malaria mobility figures.Rmd
- **Content**: Spatial points (sf object) with case_id and coordinates

### `districts_polygons_minimal.rds`
- **Description**: Minimal district polygons (province, district, geometry only)
- **Created by**: Data prep for shiny app.Rmd
- **Used in**: Data prep for shiny app.Rmd, Create static malaria mobility figures.Rmd, Shiny app
- **Content**: Simplified district polygons for base map visualization

### `costa_rica_activity_tiles_population.geojson`
- **Description**: Tile polygons with population estimates from GHSL (2025) and WorldPop (2020)
- **Created by**: calculate_population_new_tiles.py
- **Used in**: Data prep for shiny app.Rmd, Create static malaria mobility figures.Rmd
- **Content**: Tile polygons with worldpop_population and ghsl_population_2025 columns

### `costa_rica_activity_tiles_population.csv`
- **Description**: Same as .geojson but without geometry (CSV backup)
- **Created by**: calculate_population_new_tiles.py
- **Content**: Tile_id, population columns only

### `activity_by_pop_tiles_overall_wgs84.geojson`
- **Description**: Activity tiles with population and activity metrics (aggregated across all dates)
- **Created by**: Process CR Mobility Data.Rmd
- **Used in**: Data prep for shiny app.Rmd, Create static malaria mobility figures.Rmd
- **Content**: Tiles with activity metrics and population data (used for elevation extraction)

### `mobility_flows_with_elevation.rds`
- **Description**: Mobility flow lines with elevation data
- **Created by**: Data prep for shiny app.Rmd
- **Used in**: Data prep for shiny app.Rmd, Create static malaria mobility figures.Rmd
- **Content**: Spatial flow lines (sf object) connecting tiles with malaria cases, includes elevation

### `shiny_mobility_data.rds`
- **Description**: Compiled data package for Shiny app
- **Created by**: Data prep for shiny app.Rmd
- **Used in**: Shiny app (Visualize_CR_mobility_data/)
- **Content**: List containing districts_base, cases_all, tiles_base, travel_df_week

## Supporting Data Files

### `osm_localities_by_district.rds`
- **Description**: OSM locality points cached by district
- **Created by**: Process CR malaria data.Rmd
- **Used in**: Process CR malaria data.Rmd
- **Content**: Cached geocoding results for faster processing

### `osm_locality_polygons_by_district.rds`
- **Description**: OSM locality polygons cached by district
- **Created by**: Process CR malaria data.Rmd
- **Used in**: Process CR malaria data.Rmd
- **Content**: Cached polygon data for geocoding

## Data Flow Summary

1. **Raw Data** → Process CR malaria data.Rmd → `malaria_cases_2023_geocoded.rds`
2. **Raw Data** → Process CR Mobility Data.Rmd → `activity_by_pop_tiles_overall_wgs84.geojson`, `ca_aug.csv`
3. **Base Tiles** → calculate_population_new_tiles.py → `costa_rica_activity_tiles_population.geojson`
4. **All Above** → Data prep for shiny app.Rmd → `malaria_cases_2023_points.rds`, `districts_polygons_minimal.rds`, `mobility_flows_with_elevation.rds`, `shiny_mobility_data.rds`

