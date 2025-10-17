#!/usr/bin/env python3
"""
WorldPop Data Extraction for Costa Rica Districts using Google Earth Engine
This script extracts WorldPop population data and sums it per district,
then exports the results as a shapefile.
"""

import ee

def main():
    """
    Main function to extract WorldPop data per Costa Rica district.
    """
    print("=== WorldPop Data Extraction for Costa Rica Districts ===")
    
    # Initialize GEE
    ee.Initialize()
    print("✓ Google Earth Engine initialized successfully")
    
    # ---- District boundaries ----
    print("Loading Costa Rica district boundaries...")
    districts = ee.FeatureCollection(
        "projects/gbsc-gcp-lab-emordeca/assets/costa_rica/boundaries/CR_Districts_Mainland"
    )
    
    # ---- WorldPop 2020 (100 m) ----
    print("Loading WorldPop 2020 data...")
    pop2020 = (
        ee.ImageCollection('WorldPop/GP/100m/pop')
        .select('CRI_2020_population')
        .mosaic()   # flatten into one image
    )
    
    # ---- Sum population per district ----
    print("Calculating population per district...")
    pop_fc = pop2020.reduceRegions(
        collection=districts,
        reducer=ee.Reducer.sum(),
        scale=100,
        tileScale=4
    )
    
    # ---- Export shapefile (geometry + attributes) ----
    print("Starting export to Google Drive as shapefile...")
    task = ee.batch.Export.table.toDrive(
        collection=pop_fc,
        description='cr_district_population_2020_shp',
        fileFormat='SHP'
    )
    
    task.start()
    print("✓ Export task started successfully!")
    print("Task ID:", task.id)
    print("Check the GEE console or Google Drive for the exported shapefile")
    print("The shapefile will contain district geometries with population totals")

if __name__ == "__main__":
    main()
