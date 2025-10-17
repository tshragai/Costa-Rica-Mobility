#!/usr/bin/env python3
"""
Export population results to GEE asset first, then export to Drive.
This avoids the direct export permission issue.
"""

import ee

def main():
    """Calculate population and save to asset, then export."""
    print("=== Population Sum with Asset Export ===")
    
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
    
    # Save to asset first
    asset_id = "projects/gbsc-gcp-lab-emordeca/assets/costa_rica/analysis/tiles_with_population"
    print(f"Saving results to asset: {asset_id}")
    
    asset_task = ee.batch.Export.table.toAsset(
        collection=tiles_with_pop,
        description='tiles_with_population_asset',
        assetId=asset_id
    )
    
    asset_task.start()
    print(f"✓ Asset export task started: {asset_task.id}")
    print("Wait for this task to complete, then you can export from the asset")
    print("Check GEE console for task status")

if __name__ == "__main__":
    main()
