#!/usr/bin/env python3
"""
Simple script to sum WorldPop population within existing tile FeatureCollection.
This version avoids the export asset access issue.
"""

import ee

def main():
    """Simple population calculation and export."""
    print("=== Simple Population Sum ===")
    
    # Initialize GEE
    ee.Initialize()
    print("✓ Google Earth Engine initialized successfully")
    
    # Load the existing tile FeatureCollection
    print("Loading tile FeatureCollection...")
    tiles = ee.FeatureCollection(
        "projects/gbsc-gcp-lab-emordeca/assets/costa_rica/analysis/tile_activity_lonlat"
    )
    
    # Load WorldPop 2020 data
    print("Loading WorldPop 2020 data...")
    pop2020 = (
        ee.ImageCollection('WorldPop/GP/100m/pop')
        .select('CRI_2020_population')
        .mosaic()
    )
    
    # Calculate population per tile
    print("Calculating population per tile...")
    tiles_with_pop = pop2020.reduceRegions(
        collection=tiles,
        reducer=ee.Reducer.sum(),
        scale=100,
        tileScale=4
    )
    
    # Export directly to Drive
    print("Exporting to Google Drive...")
    task = ee.batch.Export.table.toDrive(
        collection=tiles_with_pop,
        description='cr_tile_population_2020',
        fileFormat='CSV'
    )
    
    task.start()
    print(f"✓ Export task started: {task.id}")
    print("Check GEE console or Google Drive for the CSV file")
    print("The CSV will contain tile IDs and population totals")

if __name__ == "__main__":
    main()
