#!/usr/bin/env python3
"""
Calculate population for tiles - assumes tiles are already uploaded to GEE.
"""

import ee

def calculate_population_for_tiles(asset_id: str):
    """Calculate population for the specified tile asset."""
    print(f"=== Population Calculation for {asset_id} ===")
    
    # Initialize GEE
    ee.Initialize()
    print("✓ Google Earth Engine initialized successfully")
    
    # Load the tile FeatureCollection
    print("Loading tile FeatureCollection...")
    try:
        tiles = ee.FeatureCollection(asset_id)
        print("✓ Tiles loaded successfully")
    except Exception as e:
        print(f"❌ Error loading tiles: {e}")
        return
    
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
    
    # Export to Drive
    print("Exporting to Google Drive...")
    task = ee.batch.Export.table.toDrive(
        collection=tiles_with_pop,
        description='tiles_population_2020',
        fileFormat='CSV'
    )
    
    task.start()
    print(f"✓ Export task started: {task.id}")
    print("Check Google Drive for the CSV file")
    print("The CSV will contain tile IDs and population totals")

def main():
    """Main function with different asset options."""
    
    # Try the existing asset first
    existing_asset = "projects/gbsc-gcp-lab-emordeca/assets/costa_rica/analysis/tile_activity_lonlat"
    
    print("Trying existing asset...")
    try:
        calculate_population_for_tiles(existing_asset)
    except Exception as e:
        print(f"Existing asset failed: {e}")
        print("\nTrying alternative approaches...")
        
        # Try without the full path
        alt_asset = "tile_activity_lonlat"
        print(f"Trying: {alt_asset}")
        try:
            calculate_population_for_tiles(alt_asset)
        except Exception as e2:
            print(f"Alternative asset failed: {e2}")
            print("\nManual upload required:")
            print("1. Upload your GPKG file to GEE manually")
            print("2. Update the asset_id in this script")
            print("3. Run the script again")

if __name__ == "__main__":
    main()
