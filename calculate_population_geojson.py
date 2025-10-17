#!/usr/bin/env python3
"""
Calculate population for the uploaded GeoJSON tiles.
Run this after the upload is complete.
"""

import ee

def main():
    """Calculate population for uploaded GeoJSON tiles."""
    print("=== Population Calculation for GeoJSON Tiles ===")
    
    # Initialize GEE
    ee.Initialize()
    print("✓ Google Earth Engine initialized successfully")
    
    # Asset ID of the uploaded GeoJSON tiles
    asset_id = "projects/gbsc-gcp-lab-emordeca/assets/costa_rica/analysis/tile_activity_geojson"
    
    try:
        # Load the uploaded tiles
        print("Loading uploaded tiles...")
        tiles = ee.FeatureCollection(asset_id)
        print("✓ Tiles loaded successfully")
        
        # Get tile count
        count = tiles.size().getInfo()
        print(f"✓ Number of tiles: {count}")
        
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
        
        print("✓ Population calculation completed!")
        
        # Export results to Google Drive
        print("Exporting results to Google Drive...")
        export_task = ee.batch.Export.table.toDrive(
            collection=tiles_with_pop,
            description='geojson_tiles_population_2020',
            fileFormat='CSV'
        )
        
        export_task.start()
        print(f"✓ Export task started: {export_task.id}")
        print("📁 Check Google Drive for the CSV file")
        print("📊 The CSV will contain tile IDs and population totals")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nThis might mean the upload is still in progress.")
        print("Check GEE console for upload status.")
        print("Upload Task ID was: GRB5AJ56IJYYOB4LUUC2Y7UY")

if __name__ == "__main__":
    main()
