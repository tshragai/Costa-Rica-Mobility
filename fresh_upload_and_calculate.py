#!/usr/bin/env python3
"""
Upload GPKG file fresh and calculate population.
This avoids issues with the existing asset.
"""

import ee
import os

def main():
    """Upload GPKG fresh and calculate population."""
    print("=== Fresh Upload and Population Calculation ===")
    
    # Initialize GEE
    ee.Initialize()
    print("✓ Google Earth Engine initialized successfully")
    
    # Upload the GPKG file fresh
    gpkg_path = "Data/tile_activity_lonlat.gpkg"
    new_asset_id = "projects/gbsc-gcp-lab-emordeca/assets/costa_rica/analysis/tile_activity_fresh"
    
    if not os.path.exists(gpkg_path):
        print(f"❌ GPKG file not found: {gpkg_path}")
        return
    
    print(f"Uploading {gpkg_path} to {new_asset_id}...")
    print("Note: This requires the earthengine command line tool")
    print(f"Run this command manually:")
    print(f"earthengine upload table --asset_id={new_asset_id} {gpkg_path}")
    print("\nOr use the GEE Code Editor to upload the file manually")
    print("Then run the population calculation part of this script")
    
    print("\n" + "="*60)
    print("NEXT STEPS:")
    print("1. Wait for upload to complete in GEE console")
    print("2. Run: python3 calculate_population_fresh.py")
    print("="*60)

def calculate_population():
    """Calculate population using the fresh upload."""
    print("=== Population Calculation with Fresh Upload ===")
    
    ee.Initialize()
    
    # Use the fresh asset
    tiles = ee.FeatureCollection(
        "projects/gbsc-gcp-lab-emordeca/assets/costa_rica/analysis/tile_activity_fresh"
    )
    
    # Load WorldPop data
    pop2020 = (
        ee.ImageCollection('WorldPop/GP/100m/pop')
        .select('CRI_2020_population')
        .mosaic()
    )
    
    # Calculate population
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
        description='tiles_population_fresh',
        fileFormat='CSV'
    )
    
    task.start()
    print(f"✓ Export task started: {task.id}")
    print("Check Google Drive for the CSV file")

if __name__ == "__main__":
    main()
