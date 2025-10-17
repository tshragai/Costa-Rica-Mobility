#!/usr/bin/env python3
"""
Calculate population and save results locally to the Data folder.
"""

import ee
import pandas as pd
import json
import os

def main():
    """Calculate population and save to local Data folder."""
    print("=== Population Calculation (Local Export) ===")
    
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
        print("\nTrying alternative approach...")
        
        # Alternative: Export to a temporary asset first, then download
        try:
            print("Exporting to temporary asset...")
            temp_asset_id = "projects/gbsc-gcp-lab-emordeca/assets/temp_population_results"
            
            export_task = ee.batch.Export.table.toAsset(
                collection=tiles_with_pop,
                description='temp_population_results',
                assetId=temp_asset_id
            )
            
            export_task.start()
            print(f"✓ Temporary export started: {export_task.id}")
            print("⏳ Wait for export to complete, then we can download it")
            
        except Exception as e2:
            print(f"❌ Alternative approach also failed: {e2}")
            print("The calculation worked, but we need to find another way to export the data")

if __name__ == "__main__":
    main()
