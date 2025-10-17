#!/usr/bin/env python3
"""
Upload GeoJSON with a simpler asset path that should work.
"""

import ee
import json
import os

def main():
    """Upload GeoJSON with corrected asset path."""
    print("=== Upload GeoJSON (Fixed Asset Path) ===")
    
    # Initialize GEE
    ee.Initialize()
    print("✓ Google Earth Engine initialized successfully")
    
    # File paths
    geojson_path = "Data/tile_activity_lonlat.geojson"
    # Use a simpler asset path that should exist
    asset_id = "tile_activity_geojson"
    
    # Check if file exists
    if not os.path.exists(geojson_path):
        print(f"❌ GeoJSON file not found: {geojson_path}")
        return
    
    print(f"✓ Found GeoJSON file: {geojson_path}")
    
    try:
        # Read the GeoJSON file
        with open(geojson_path, 'r') as f:
            geojson_data = json.load(f)
        
        print(f"✓ GeoJSON file read successfully")
        print(f"  Features: {len(geojson_data['features'])}")
        
        # Create FeatureCollection from GeoJSON
        fc = ee.FeatureCollection(geojson_data)
        print("✓ FeatureCollection created from GeoJSON")
        
        # Export to asset with simpler path
        print(f"Uploading to asset: {asset_id}")
        task = ee.batch.Export.table.toAsset(
            collection=fc,
            description='Upload GeoJSON tiles - fixed path',
            assetId=asset_id
        )
        
        task.start()
        print(f"✓ Upload task started: {task.id}")
        print("⏳ Wait for upload to complete in GEE console")
        print(f"📋 Task ID: {task.id}")
        
        return task.id
        
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        print("\nTrying with even simpler asset path...")
        
        # Try with just the filename
        simple_asset_id = "tile_activity"
        
        try:
            task = ee.batch.Export.table.toAsset(
                collection=fc,
                description='Upload GeoJSON tiles - simple path',
                assetId=simple_asset_id
            )
            
            task.start()
            print(f"✓ Upload task started with simple path: {task.id}")
            return task.id
            
        except Exception as e2:
            print(f"❌ Simple path also failed: {e2}")
            print("\nManual upload required:")
            print("1. Go to https://code.earthengine.google.com")
            print("2. Assets → New → Table upload")
            print("3. Upload the GeoJSON file manually")
            return None

if __name__ == "__main__":
    task_id = main()
    if task_id:
        print(f"\n📋 Upload Task ID: {task_id}")
        print("⏳ Upload time depends on file size and GEE server load")
        print("📊 Typical upload times:")
        print("   - Small files (< 1MB): 1-5 minutes")
        print("   - Medium files (1-10MB): 5-15 minutes") 
        print("   - Large files (> 10MB): 15-60 minutes")
        print(f"   - Your file: {os.path.getsize('Data/tile_activity_lonlat.geojson') / (1024*1024):.1f} MB")
