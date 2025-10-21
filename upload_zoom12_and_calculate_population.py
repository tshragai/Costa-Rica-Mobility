#!/usr/bin/env python3
"""
Upload new tile data (zoom12) to GEE and calculate population for both WorldPop and GHSL.
"""

import ee
import json
import os
import pandas as pd

def upload_zoom12_tiles_to_gee(geojson_path: str, asset_id: str):
    """Upload zoom12 GeoJSON tiles to GEE."""
    print(f"📤 Uploading zoom12 tiles to GEE...")
    
    if not os.path.exists(geojson_path):
        print(f"❌ GeoJSON file not found: {geojson_path}")
        return False
    
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
            description='Upload zoom12 tile activity data',
            assetId=asset_id
        )
        
        task.start()
        print(f"✓ Upload task started: {task.id}")
        print("⏳ Wait for upload to complete in GEE console")
        
        return task.id
        
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        return None

def calculate_population_for_zoom12_tiles(asset_id: str):
    """Calculate population for zoom12 tiles using both WorldPop and GHSL."""
    print(f"\n=== Population Calculation for Zoom12 Tiles ===")
    
    try:
        # Load the uploaded zoom12 tiles
        print("Loading zoom12 tiles...")
        tiles = ee.FeatureCollection(asset_id)
        print("✓ Zoom12 tiles loaded successfully")
        
        # Get tile count
        count = tiles.size().getInfo()
        print(f"✓ Number of tiles: {count}")
        
        # Load WorldPop 2020 data
        print("Loading WorldPop 2020 data...")
        worldpop_data = (
            ee.ImageCollection('WorldPop/GP/100m/pop')
            .filterDate('2020-01-01', '2020-12-31')
            .select('population')
            .mosaic()
            .clip(tiles)
        )
        
        print("✓ WorldPop data loaded successfully")
        
        # Load GHSL population image (2025) with proper handling
        print("Loading GHSL population image (2025)...")
        ghsl_population = (
            ee.Image("JRC/GHSL/P2023A/GHS_POP/2025")
            .select("population_count")
            .clip(tiles)
            .max(0)  # Ensure no negative values
        )
        
        print("✓ GHSL population data loaded and negative values filtered")
        
        # Calculate WorldPop population per tile
        print("Calculating WorldPop population per tile...")
        worldpop_fc = worldpop_data.reduceRegions(
            collection=tiles,
            reducer=ee.Reducer.sum().unweighted(),
            scale=100
        )
        
        print("✓ WorldPop calculation completed!")
        
        # Calculate GHSL population per tile
        print("Calculating GHSL population per tile...")
        ghsl_fc = ghsl_population.reduceRegions(
            collection=tiles,
            reducer=ee.Reducer.sum().unweighted(),
            scale=100
        )
        
        print("✓ GHSL calculation completed!")
        
        # Get the results
        print("Retrieving results...")
        worldpop_results = worldpop_fc.getInfo()
        ghsl_results = ghsl_fc.getInfo()
        
        # Convert to DataFrames
        print("Processing results...")
        
        # WorldPop DataFrame
        worldpop_features = worldpop_results['features']
        worldpop_data = []
        
        for feature in worldpop_features:
            properties = feature['properties']
            properties['geometry'] = json.dumps(feature['geometry'])
            worldpop_data.append(properties)
        
        df_worldpop = pd.DataFrame(worldpop_data)
        df_worldpop = df_worldpop.rename(columns={'sum': 'worldpop_population'})
        
        # GHSL DataFrame
        ghsl_features = ghsl_results['features']
        ghsl_data = []
        
        for feature in ghsl_features:
            properties = feature['properties']
            properties['geometry'] = json.dumps(feature['geometry'])
            ghsl_data.append(properties)
        
        df_ghsl = pd.DataFrame(ghsl_data)
        df_ghsl = df_ghsl.rename(columns={'sum': 'ghsl_population_2025'})
        
        # Ensure no negative values in the final data
        df_ghsl['ghsl_population_2025'] = df_ghsl['ghsl_population_2025'].clip(lower=0)
        
        # Merge the datasets
        print("Merging datasets...")
        df_combined = df_worldpop.merge(
            df_ghsl[['geometry', 'ghsl_population_2025']], 
            on='geometry', 
            how='inner'
        )
        
        # Reorder columns for better readability
        df_combined = df_combined[['activity', 'worldpop_population', 'ghsl_population_2025', 'geometry']]
        
        # Save as GeoJSON (sf-compatible format)
        print("Saving as GeoJSON for sf import...")
        
        # Create GeoJSON structure
        geojson_data = {
            "type": "FeatureCollection",
            "features": []
        }
        
        for _, row in df_combined.iterrows():
            feature = {
                "type": "Feature",
                "properties": {
                    "activity": row['activity'],
                    "worldpop_population": row['worldpop_population'],
                    "ghsl_population_2025": row['ghsl_population_2025']
                },
                "geometry": json.loads(row['geometry'])
            }
            geojson_data["features"].append(feature)
        
        # Save GeoJSON
        output_geojson = "Data/tile_activity_zoom12_dual_population.geojson"
        with open(output_geojson, 'w') as f:
            json.dump(geojson_data, f, indent=2)
        
        print(f"✓ GeoJSON saved to: {output_geojson}")
        
        # Also save as CSV (without geometry for backup)
        output_csv = "Data/tile_activity_zoom12_dual_population.csv"
        df_combined_no_geom = df_combined.drop('geometry', axis=1)
        df_combined_no_geom.to_csv(output_csv, index=False)
        
        print(f"✓ CSV saved to: {output_csv}")
        
        # Show statistics
        print(f"\n📊 Population Statistics:")
        print(f"   WorldPop 2020 - Total: {df_combined['worldpop_population'].sum():,.0f}")
        print(f"   GHSL 2025 - Total: {df_combined['ghsl_population_2025'].sum():,.0f}")
        print(f"   Difference: {df_combined['worldpop_population'].sum() - df_combined['ghsl_population_2025'].sum():,.0f}")
        
        print(f"\n🎉 Success! Zoom12 population data ready for sf import in R!")
        print(f"📁 Files saved in your local Data folder:")
        print(f"   - {output_geojson} (for sf::st_read())")
        print(f"   - {output_csv} (CSV backup)")
        
        print(f"\n📖 To read in R:")
        print(f"   library(sf)")
        print(f"   tiles_pop_zoom12 <- st_read('Data/tile_activity_zoom12_dual_population.geojson')")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Main function to upload zoom12 tiles and calculate population."""
    print("=== Upload Zoom12 Tiles and Calculate Population ===")
    
    # Initialize GEE
    ee.Initialize()
    print("✓ Google Earth Engine initialized successfully")
    
    # File paths and asset configuration
    geojson_path = "Data/tile_activity_lonlat_zoom12.geojson"
    asset_id = "projects/gbsc-gcp-lab-emordeca/assets/costa_rica_tiles_zoom12"
    
    # Check if file exists
    if not os.path.exists(geojson_path):
        print(f"❌ GeoJSON file not found: {geojson_path}")
        print("Please make sure the file exists in your Data folder")
        return
    
    print(f"✓ Found GeoJSON file: {geojson_path}")
    
    # Step 1: Upload zoom12 tiles
    print("\n" + "="*60)
    print("STEP 1: Upload Zoom12 Tiles to GEE")
    print("="*60)
    
    upload_task_id = upload_zoom12_tiles_to_gee(geojson_path, asset_id)
    
    if upload_task_id:
        print(f"\n📋 Upload Task ID: {upload_task_id}")
        print("⏳ Please wait for upload to complete")
        print("Check GEE console for upload status")
        print("\nOnce upload is complete, run this script again to calculate population")
        print("Or uncomment the population calculation section below")
        
        # Uncomment the following lines to run population calculation after upload
        # print("\n" + "="*60)
        # print("STEP 2: Calculate Population")
        # print("="*60)
        # calculate_population_for_zoom12_tiles(asset_id)
        
    else:
        print("❌ Upload failed - please check the error messages above")

if __name__ == "__main__":
    main()
