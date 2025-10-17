#!/usr/bin/env python3
"""
Calculate population with correct band names and save locally.
"""

import ee
import pandas as pd
import json
import os

def main():
    """Calculate population with correct WorldPop bands."""
    print("=== Population Calculation (Fixed Bands) ===")
    
    # Initialize GEE
    ee.Initialize()
    print("✓ Google Earth Engine initialized successfully")
    
    # Asset ID of the uploaded GeoJSON tiles
    asset_id = "projects/gbsc-gcp-lab-emordeca/assets/costa_rica_tiles"
    
    try:
        # Load the uploaded tiles
        print("Loading uploaded tiles...")
        tiles = ee.FeatureCollection(asset_id)
        print("✓ Tiles loaded successfully")
        
        # Get tile count
        count = tiles.size().getInfo()
        print(f"✓ Number of tiles: {count}")
        
        # Load WorldPop 2020 data with correct band selection
        print("Loading WorldPop 2020 data...")
        pop2020 = (
            ee.ImageCollection('WorldPop/GP/100m/pop')
            .filterDate('2020-01-01', '2020-12-31')  # Filter for 2020
            .select('population')  # Use 'population' band instead of 'CRI_2020_population'
            .mosaic()
        )
        
        print("✓ WorldPop data loaded with correct band")
        
        # Calculate population per tile
        print("Calculating population per tile...")
        tiles_with_pop = pop2020.reduceRegions(
            collection=tiles,
            reducer=ee.Reducer.sum(),
            scale=100,
            tileScale=4
        )
        
        print("✓ Population calculation completed!")
        
        # Get the results as a list of dictionaries
        print("Retrieving results...")
        results = tiles_with_pop.getInfo()
        
        # Convert to DataFrame
        features = results['features']
        data = []
        
        for feature in features:
            properties = feature['properties']
            # Add geometry info if needed
            properties['geometry'] = json.dumps(feature['geometry'])
            data.append(properties)
        
        df = pd.DataFrame(data)
        
        # Save to local Data folder
        output_file = "Data/tile_activity_with_population.csv"
        df.to_csv(output_file, index=False)
        
        print(f"✓ Results saved to: {output_file}")
        print(f"✓ File contains {len(df)} rows and {len(df.columns)} columns")
        print(f"✓ Columns: {list(df.columns)}")
        
        # Also save as JSON for backup
        output_json = "Data/tile_activity_with_population.json"
        df.to_json(output_json, orient='records', indent=2)
        print(f"✓ Backup saved as JSON: {output_json}")
        
        print(f"\n🎉 Success! Your Costa Rica mobility analysis with population data is ready!")
        print(f"📁 Files saved in your local Data folder:")
        print(f"   - {output_file}")
        print(f"   - {output_json}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nTrying with different WorldPop approach...")
        
        # Try alternative WorldPop collection
        try:
            print("Trying alternative WorldPop collection...")
            
            # Try the global WorldPop collection
            pop2020_alt = (
                ee.ImageCollection('WorldPop/POP')
                .filterDate('2020-01-01', '2020-12-31')
                .select('population')
                .mosaic()
            )
            
            tiles_with_pop_alt = pop2020_alt.reduceRegions(
                collection=tiles,
                reducer=ee.Reducer.sum(),
                scale=100,
                tileScale=4
            )
            
            print("✓ Alternative calculation completed!")
            
            # Get and save results
            results = tiles_with_pop_alt.getInfo()
            features = results['features']
            data = []
            
            for feature in features:
                properties = feature['properties']
                properties['geometry'] = json.dumps(feature['geometry'])
                data.append(properties)
            
            df = pd.DataFrame(data)
            
            # Save to local Data folder
            output_file = "Data/tile_activity_with_population_alt.csv"
            df.to_csv(output_file, index=False)
            
            print(f"✓ Results saved to: {output_file}")
            print(f"✓ File contains {len(df)} rows and {len(df.columns)} columns")
            
        except Exception as e2:
            print(f"❌ Alternative approach also failed: {e2}")
            print("Let's check what WorldPop collections are available...")

if __name__ == "__main__":
    main()
