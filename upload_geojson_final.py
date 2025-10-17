#!/usr/bin/env python3
"""
Upload GeoJSON with proper asset naming convention.
"""

import ee
import json
import os

def main():
    """Upload GeoJSON with proper asset path."""
    print("=== Upload GeoJSON (Proper Asset Path) ===")
    
    # Initialize GEE
    ee.Initialize()
    print("✓ Google Earth Engine initialized successfully")
    
    # File paths
    geojson_path = "Data/tile_activity_lonlat.geojson"
    # Use proper asset naming: projects/PROJECT/assets/folder/subfolder/name
    asset_id = "projects/gbsc-gcp-lab-emordeca/assets/costa_rica/tiles/tile_activity_geojson"
    
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
        
        # Export to asset with proper path
        print(f"Uploading to asset: {asset_id}")
        task = ee.batch.Export.table.toAsset(
            collection=fc,
            description='Upload GeoJSON tiles for Costa Rica mobility analysis',
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
        
        print(f"\n⏱️  Estimated Upload Time:")
        if file_size < 1:
            print("   - Small file: 1-5 minutes")
        elif file_size < 10:
            print("   - Medium file: 5-15 minutes")
        else:
            print("   - Large file: 15-60 minutes")
        
        print(f"\n📊 To check status:")
        print(f"   1. Go to: https://code.earthengine.google.com")
        print(f"   2. Check the 'Tasks' tab")
        print(f"   3. Look for task ID: {task.id}")
        
        return task.id
        
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        print("\nThe asset path might not exist. Let's try manual upload:")
        print("1. Go to https://code.earthengine.google.com")
        print("2. Assets → New → Table upload")
        print("3. Upload: Data/tile_activity_lonlat.geojson")
        print("4. Set asset ID to: projects/gbsc-gcp-lab-emordeca/assets/costa_rica/tiles/tile_activity_geojson")
        return None

if __name__ == "__main__":
    task_id = main()
    if task_id:
        print(f"\n🎯 Next Steps:")
        print(f"1. Wait for upload to complete (check GEE console)")
        print(f"2. Run: python3 calculate_population_final.py")
        print(f"3. Get your CSV with population data!")
