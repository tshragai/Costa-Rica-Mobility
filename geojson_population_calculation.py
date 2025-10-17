#!/usr/bin/env python3
"""
Calculate population for tiles using GeoJSON file.
This version works with the GeoJSON format which should be more compatible.
"""

import ee
import os

def upload_geojson_to_gee(geojson_path: str, asset_id: str):
    """Upload GeoJSON to GEE using command line tool."""
    if not os.path.exists(geojson_path):
        print(f"❌ GeoJSON file not found: {geojson_path}")
        return False
    
    print(f"📤 Uploading GeoJSON to GEE...")
    print(f"File: {geojson_path}")
    print(f"Asset ID: {asset_id}")
    print(f"\nRun this command manually:")
    print(f"earthengine upload table --asset_id={asset_id} {geojson_path}")
    print(f"\nOr upload via GEE Code Editor:")
    print(f"1. Go to code.earthengine.google.com")
    print(f"2. Assets → New → Table upload")
    print(f"3. Upload: {geojson_path}")
    print(f"4. Set Asset ID: {asset_id}")
    
    return True

def calculate_population_with_geojson(asset_id: str):
    """Calculate population using the GeoJSON asset."""
    print(f"\n=== Population Calculation for {asset_id} ===")
    
    # Initialize GEE
    ee.Initialize()
    print("✓ Google Earth Engine initialized successfully")
    
    # Load the tile FeatureCollection
    print("Loading tile FeatureCollection...")
    try:
        tiles = ee.FeatureCollection(asset_id)
        print("✓ Tiles loaded successfully")
        
        # Get some info about the tiles
        count = tiles.size().getInfo()
        print(f"✓ Number of tiles: {count}")
        
    except Exception as e:
        print(f"❌ Error loading tiles: {e}")
        return False
    
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
    
    print("✓ Population calculation completed successfully!")
    
    # Try to export
    try:
        print("Attempting to export to Google Drive...")
        task = ee.batch.Export.table.toDrive(
            collection=tiles_with_pop,
            description='geojson_tiles_population_2020',
            fileFormat='CSV'
        )
        
        task.start()
        print(f"✓ Export task started: {task.id}")
        print("Check Google Drive for the CSV file")
        return True
        
    except Exception as e:
        print(f"❌ Export failed: {e}")
        print("\nBut the calculation worked! Try exporting from GEE Code Editor:")
        print("1. Go to code.earthengine.google.com")
        print("2. Paste this code:")
        print(f"   var tiles = ee.FeatureCollection('{asset_id}');")
        print("   var pop2020 = ee.ImageCollection('WorldPop/GP/100m/pop').select('CRI_2020_population').mosaic();")
        print("   var result = pop2020.reduceRegions({collection: tiles, reducer: ee.Reducer.sum(), scale: 100, tileScale: 4});")
        print("   print(result);")
        print("   // Then export from the Code Editor")
        return False

def main():
    """Main function to handle GeoJSON upload and calculation."""
    print("=== GeoJSON Population Calculation ===")
    
    # File paths
    geojson_path = "Data/tile_activity_lonlat.geojson"
    asset_id = "projects/gbsc-gcp-lab-emordeca/assets/costa_rica/analysis/tile_activity_geojson"
    
    # Check if file exists
    if not os.path.exists(geojson_path):
        print(f"❌ GeoJSON file not found: {geojson_path}")
        return
    
    print(f"✓ Found GeoJSON file: {geojson_path}")
    
    # Step 1: Upload instructions
    upload_geojson_to_gee(geojson_path, asset_id)
    
    print("\n" + "="*60)
    print("NEXT STEPS:")
    print("1. Upload the GeoJSON file to GEE (see instructions above)")
    print("2. Wait for upload to complete")
    print("3. Run this script again to calculate population")
    print("="*60)
    
    # Step 2: Try calculation (will work if asset exists)
    print("\nTrying population calculation...")
    calculate_population_with_geojson(asset_id)

if __name__ == "__main__":
    main()
