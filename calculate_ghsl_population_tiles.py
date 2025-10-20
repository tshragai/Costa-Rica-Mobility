#!/usr/bin/env python3
"""
Calculate GHSL population for predefined tiles using the exact approach from the user's script.
"""

import ee
import pandas as pd
import json
import os

def main():
    """Calculate GHSL population for predefined tiles."""
    print("=== GHSL Population Calculation for Predefined Tiles ===")
    
    # Initialize GEE
    ee.Initialize()
    print("✓ Google Earth Engine initialized successfully")
    
    # Load your predefined tiles (instead of districts)
    tiles = ee.FeatureCollection(
        "projects/gbsc-gcp-lab-emordeca/assets/costa_rica_tiles"
    )
    
    print("✓ Predefined tiles loaded successfully")
    
    # Get tile count
    count = tiles.size().getInfo()
    print(f"✓ Number of tiles: {count}")
    
    # Load GHSL population image (2025)
    print("Loading GHSL population image (2025)...")
    ghsl_population = (
        ee.Image("JRC/GHSL/P2023A/GHS_POP/2025")
        .select("population_count")
        .clip(tiles)  # Clip to your tiles instead of districts
    )
    
    print("✓ GHSL population data loaded successfully")
    
    # Sum population per tile (raw pixel sum)
    print("Calculating population per tile...")
    pop_fc = ghsl_population.reduceRegions(
        collection=tiles,
        reducer=ee.Reducer.sum().unweighted(),
        scale=100
    )
    
    print("✓ Population calculation completed!")
    
    # Get the results
    print("Retrieving results...")
    results = pop_fc.getInfo()
    
    # Convert to DataFrame
    features = results['features']
    data = []
    
    for feature in features:
        properties = feature['properties']
        # Add geometry info if needed
        properties['geometry'] = json.dumps(feature['geometry'])
        data.append(properties)
    
    df = pd.DataFrame(data)
    
    # Rename the population column for clarity
    if 'sum' in df.columns:
        df = df.rename(columns={'sum': 'ghsl_population_2025'})
    
    # Save to local Data folder
    output_file = "Data/tile_activity_ghsl_population_2025.csv"
    df.to_csv(output_file, index=False)
    
    print(f"✓ Results saved to: {output_file}")
    print(f"✓ File contains {len(df)} rows and {len(df.columns)} columns")
    print(f"✓ Columns: {list(df.columns)}")
    
    # Show some statistics
    if 'ghsl_population_2025' in df.columns:
        print(f"\n📊 GHSL Population Statistics (2025):")
        print(f"   Total Population: {df['ghsl_population_2025'].sum():,.0f}")
        print(f"   Mean per tile: {df['ghsl_population_2025'].mean():,.0f}")
        print(f"   Max per tile: {df['ghsl_population_2025'].max():,.0f}")
        print(f"   Min per tile: {df['ghsl_population_2025'].min():,.0f}")
    
    # Also save as JSON for backup
    output_json = "Data/tile_activity_ghsl_population_2025.json"
    df.to_json(output_json, orient='records', indent=2)
    print(f"✓ Backup saved as JSON: {output_json}")
    
    print(f"\n🎉 Success! Your Costa Rica mobility analysis with GHSL population data is ready!")
    print(f"📁 Files saved in your local Data folder:")
    print(f"   - {output_file}")
    print(f"   - {output_json}")

if __name__ == "__main__":
    main()
