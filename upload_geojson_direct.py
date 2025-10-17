#!/usr/bin/env python3
"""
Direct GeoJSON upload and population calculation using Python API.
"""

import ee
import json
import os

def upload_geojson_via_api(geojson_path: str, asset_id: str):
    """Upload GeoJSON using the Python API."""
    print(f"📤 Uploading GeoJSON via Python API...")
    
    try:
        # Read the GeoJSON file
        with open(geojson_path, 'r') as f:
            geojson_data = json.load(f)
        
        print(f"✓ GeoJSON file read successfully")
        print(f"  Features: {len(geojson_data['features'])}")
        
        # Create FeatureCollection from GeoJSON
        fc = ee.FeatureCollection(geojson_data)
        print("✓ FeatureCollection created from GeoJSON")
        
        # Export to asset
        task = ee.batch.Export.table.toAsset(
            collection=fc,
            description='Upload GeoJSON tiles',
            assetId=asset_id
        )
        
        task.start()
        print(f"✓ Upload task started: {task.id}")
        print("⏳ Wait for upload to complete in GEE console")
        return task.id
        
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        return None

def calculate_population(asset_id: str):
    """Calculate population for the uploaded tiles."""
    print(f"\n=== Population Calculation ===")
    
    try:
        # Load the uploaded tiles
        tiles = ee.FeatureCollection(asset_id)
        print("✓ Tiles loaded successfully")
        
        # Get tile count
        count = tiles.size().getInfo()
        print(f"✓ Number of tiles: {count}")
        
        # Load WorldPop data
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
        
        # Export results
        print("Exporting results...")
        export_task = ee.batch.Export.table.toDrive(
            collection=tiles_with_pop,
            description='geojson_tiles_population',
            fileFormat='CSV'
        )
        
        export_task.start()
        print(f"✓ Export task started: {export_task.id}")
        print("Check Google Drive for the CSV file")
        
        return True
        
    except Exception as e:
        print(f"❌ Calculation failed: {e}")
        return False

def main():
    """Main function."""
    print("=== Direct GeoJSON Upload and Population Calculation ===")
    
    # Initialize GEE
    ee.Initialize()
    print("✓ Google Earth Engine initialized successfully")
    
    # File paths
    geojson_path = "Data/tile_activity_lonlat.geojson"
    asset_id = "projects/gbsc-gcp-lab-emordeca/assets/costa_rica/analysis/tile_activity_geojson"
    
    # Check if file exists
    if not os.path.exists(geojson_path):
        print(f"❌ GeoJSON file not found: {geojson_path}")
        return
    
    print(f"✓ Found GeoJSON file: {geojson_path}")
    
    # Step 1: Upload GeoJSON
    upload_task_id = upload_geojson_via_api(geojson_path, asset_id)
    
    if upload_task_id:
        print(f"\n📋 Upload Task ID: {upload_task_id}")
        print("⏳ Please wait for upload to complete")
        print("Check GEE console for upload status")
        print("\nOnce upload is complete, run this script again to calculate population")
    else:
        print("❌ Upload failed - trying alternative approach...")
        print("You may need to upload manually via GEE Code Editor")

if __name__ == "__main__":
    main()
