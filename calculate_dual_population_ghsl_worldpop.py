#!/usr/bin/env python3
"""
Calculate both WorldPop and GHSL population for predefined tiles and combine into one file.
"""

import ee
import pandas as pd
import json
import os

def main():
    """Calculate both WorldPop and GHSL population for predefined tiles."""
    print("=== Dual Population Calculation (WorldPop + GHSL) for Predefined Tiles ===")
    
    # Initialize GEE
    ee.Initialize()
    print("✓ Google Earth Engine initialized successfully")
    
    # Load your predefined tiles
    tiles = ee.FeatureCollection(
        "projects/gbsc-gcp-lab-emordeca/assets/costa_rica_tiles"
    )
    
    print("✓ Predefined tiles loaded successfully")
    
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
    
    # Load GHSL population image (2025)
    print("Loading GHSL population image (2025)...")
    ghsl_population = (
        ee.Image("JRC/GHSL/P2023A/GHS_POP/2025")
        .select("population_count")
        .clip(tiles)
    )
    
    print("✓ GHSL population data loaded successfully")
    
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
    print("Retrieving WorldPop results...")
    worldpop_results = worldpop_fc.getInfo()
    
    print("Retrieving GHSL results...")
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
    
    # Merge the datasets
    print("Merging datasets...")
    df_combined = df_worldpop.merge(
        df_ghsl[['geometry', 'ghsl_population_2025']], 
        on='geometry', 
        how='inner'
    )
    
    # Reorder columns for better readability
    df_combined = df_combined[['activity', 'worldpop_population', 'ghsl_population_2025', 'geometry']]
    
    # Save to local Data folder
    output_file = "Data/tile_activity_dual_population_worldpop_ghsl.csv"
    df_combined.to_csv(output_file, index=False)
    
    print(f"✓ Results saved to: {output_file}")
    print(f"✓ File contains {len(df_combined)} rows and {len(df_combined.columns)} columns")
    print(f"✓ Columns: {list(df_combined.columns)}")
    
    # Show some statistics
    print(f"\n📊 Population Statistics:")
    print(f"   WorldPop 2020 - Total: {df_combined['worldpop_population'].sum():,.0f}")
    print(f"   GHSL 2025 - Total: {df_combined['ghsl_population_2025'].sum():,.0f}")
    print(f"   Difference: {df_combined['worldpop_population'].sum() - df_combined['ghsl_population_2025'].sum():,.0f}")
    
    # Also save as JSON for backup
    output_json = "Data/tile_activity_dual_population_worldpop_ghsl.json"
    df_combined.to_json(output_json, orient='records', indent=2)
    print(f"✓ Backup saved as JSON: {output_json}")
    
    print(f"\n🎉 Success! Your Costa Rica mobility analysis with dual population data is ready!")
    print(f"📁 Files saved in your local Data folder:")
    print(f"   - {output_file}")
    print(f"   - {output_json}")

if __name__ == "__main__":
    main()
