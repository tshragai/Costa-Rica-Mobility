#!/usr/bin/env python3
"""
Calculate population for zoom12 tiles (run this after upload is complete).
"""

import ee
import pandas as pd
import json
import os

def main():
    """Calculate population for zoom12 tiles."""
    print("=== Population Calculation for Zoom12 Tiles ===")
    
    # Initialize GEE
    ee.Initialize()
    print("✓ Google Earth Engine initialized successfully")
    
    # Asset ID of the uploaded zoom12 tiles
    asset_id = "projects/gbsc-gcp-lab-emordeca/assets/costa_rica_tiles_zoom12"
    
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
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("This might mean the upload is still in progress.")
        print("Check GEE console for upload status and try again.")

if __name__ == "__main__":
    main()
