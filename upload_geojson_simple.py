#!/usr/bin/env python3
"""
Upload GeoJSON using a simple asset path that should work.
"""

import ee
import json
import os

def main():
    """Upload GeoJSON with a simple asset path."""
    print("=== Upload GeoJSON (Simple Asset Path) ===")
    
    # Initialize GEE
    ee.Initialize()
    print("✓ Google Earth Engine initialized successfully")
    
    # File paths
    geojson_path = "Data/tile_activity_lonlat.geojson"
    # Use a simple asset path that should work
    asset_id = "projects/gbsc-gcp-lab-emordeca/assets/costa_rica_tiles"
    
    # Check if file exists
    if not os.path.exists(geojson_path):
        print(f"❌ GeoJSON file not found: {geojson_path}")
        return
    
    print(f"✓ Found GeoJSON file: {geojson_path}")
    file_size = os.path.getsize(geojson_path) / (1024*1024)
    print(f"  File size: {file_size:.1f} MB")
    
    try:
        # Read the GeoJSON file
        with open(geojson_path, 'r') as f:
            geojson_data = json.load(f)
        
        print(f"✓ GeoJSON file read successfully")
        print(f"  Features: {len(geojson_data['features'])}")
        
        # Create FeatureCollection from GeoJSON
        fc = ee.FeatureCollection(geojson_data)
        print("✓ FeatureCollection created from GeoJSON")
        
        # Export to asset with simple path
        print(f"Uploading to asset: {asset_id}")
        task = ee.batch.Export.table.toAsset(
            collection=fc,
            description='Upload Costa Rica tiles - simple path',
            assetId=asset_id
        )
        
        task.start()
        print(f"✓ Upload task started: {task.id}")
        print("⏳ Upload in progress...")
        
        print(f"\n📋 Upload Details:")
        print(f"   Task ID: {task.id}")
        print(f"   Asset ID: {asset_id}")
        print(f"   Features: {len(geojson_data['features'])} tiles")
        print(f"   File size: {file_size:.1f} MB")
        
        print(f"\n⏱️  Estimated Upload Time: 1-5 minutes")
        
        return task.id
        
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        print("\nLet's try with an even simpler path...")
        
        # Try with just the project and a simple name
        simple_asset_id = "projects/gbsc-gcp-lab-emordeca/assets/costa_rica_tiles_simple"
        
        try:
            task = ee.batch.Export.table.toAsset(
                collection=fc,
                description='Upload Costa Rica tiles - ultra simple',
                assetId=simple_asset_id
            )
            
            task.start()
            print(f"✓ Upload task started with simple path: {task.id}")
            print(f"   Asset ID: {simple_asset_id}")
            return task.id
            
        except Exception as e2:
            print(f"❌ Simple path also failed: {e2}")
            print("\nManual upload required:")
            print("1. Go to https://code.earthengine.google.com")
            print("2. Assets → New → Table upload")
            print("3. Upload the GeoJSON file manually")
            print("4. Choose any asset name you want")
            return None

if __name__ == "__main__":
    task_id = main()
    if task_id:
        print(f"\n🎯 Next Steps:")
        print(f"1. Wait for upload to complete (check GEE console)")
        print(f"2. Update the asset ID in calculate_population_simple.py")
        print(f"3. Run the population calculation script")
    else:
        print(f"\n📝 Manual Upload Instructions:")
        print(f"1. Go to https://code.earthengine.google.com")
        print(f"2. Click 'Assets' in the left panel")
        print(f"3. Click 'New' → 'Table upload'")
        print(f"4. Upload: {os.path.abspath('Data/tile_activity_lonlat.geojson')}")
        print(f"5. Choose any asset name (e.g., 'costa_rica_tiles')")
        print(f"6. Wait for upload to complete")
