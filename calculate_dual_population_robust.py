#!/usr/bin/env python3
"""
Calculate population for both WorldPop and GHSL datasets with robust error handling.
"""

import ee
import pandas as pd
import json
import os

def main():
    """Calculate population for both WorldPop and GHSL datasets."""
    print("=== Dual Population Calculation (WorldPop + GHSL) ===")
    
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
        pop2020_worldpop = (
            ee.ImageCollection('WorldPop/GP/100m/pop')
            .filterDate('2020-01-01', '2020-12-31')
            .select('population')
            .mosaic()
        )
        
        print("✓ WorldPop data loaded successfully")
        
        # Calculate WorldPop population per tile
        print("Calculating WorldPop population per tile...")
        tiles_with_worldpop = pop2020_worldpop.reduceRegions(
            collection=tiles,
            reducer=ee.Reducer.sum(),
            scale=100,
            tileScale=4
        )
        
        print("✓ WorldPop calculation completed!")
        
        # Get WorldPop results first
        print("Retrieving WorldPop results...")
        worldpop_results = tiles_with_worldpop.getInfo()
        
        # Process WorldPop DataFrame
        worldpop_features = worldpop_results['features']
        worldpop_data = []
        
        for feature in worldpop_features:
            properties = feature['properties']
            properties['geometry'] = json.dumps(feature['geometry'])
            worldpop_data.append(properties)
        
        df_worldpop = pd.DataFrame(worldpop_data)
        df_worldpop = df_worldpop.rename(columns={'sum': 'worldpop_population'})
        
        print(f"✓ WorldPop data processed: {len(df_worldpop)} tiles")
        
        # Now try GHSL with different approaches
        print("\nTrying GHSL data...")
        
        # Try different GHSL collection names
        ghsl_collections = [
            'JRC/GHSL/P2023A/POP_MT',
            'JRC/GHSL/P2023A/POP_GP', 
            'JRC/GHSL/P2023A/POP_SM',
            'JRC/GHSL/P2023A/POP'
        ]
        
        ghsl_success = False
        df_ghsl = None
        
        for collection in ghsl_collections:
            try:
                print(f"Trying GHSL collection: {collection}")
                
                # Load GHSL data
                pop2020_ghsl = (
                    ee.ImageCollection(collection)
                    .filterDate('2020-01-01', '2020-12-31')
                    .select('population')
                    .mosaic()
                )
                
                print(f"✓ GHSL data loaded from: {collection}")
                
                # Calculate GHSL population per tile
                print("Calculating GHSL population per tile...")
                tiles_with_ghsl = pop2020_ghsl.reduceRegions(
                    collection=tiles,
                    reducer=ee.Reducer.sum(),
                    scale=100,
                    tileScale=4
                )
                
                print("✓ GHSL calculation completed!")
                
                # Get GHSL results
                print("Retrieving GHSL results...")
                ghsl_results = tiles_with_ghsl.getInfo()
                
                # Process GHSL DataFrame
                ghsl_features = ghsl_results['features']
                ghsl_data = []
                
                for feature in ghsl_features:
                    properties = feature['properties']
                    properties['geometry'] = json.dumps(feature['geometry'])
                    ghsl_data.append(properties)
                
                df_ghsl = pd.DataFrame(ghsl_data)
                df_ghsl = df_ghsl.rename(columns={'sum': 'ghsl_population'})
                
                print(f"✓ GHSL data processed: {len(df_ghsl)} tiles")
                ghsl_success = True
                break
                
            except Exception as e:
                print(f"❌ Failed: {collection} - {e}")
                continue
        
        if ghsl_success and df_ghsl is not None:
            # Merge the datasets
            print("\nMerging datasets...")
            df_combined = df_worldpop.merge(
                df_ghsl[['geometry', 'ghsl_population']], 
                on='geometry', 
                how='inner'
            )
            
            # Reorder columns for better readability
            df_combined = df_combined[['activity', 'worldpop_population', 'ghsl_population', 'geometry']]
            
            # Save to local Data folder
            output_file = "Data/tile_activity_dual_population.csv"
            df_combined.to_csv(output_file, index=False)
            
            print(f"✓ Results saved to: {output_file}")
            print(f"✓ File contains {len(df_combined)} rows and {len(df_combined.columns)} columns")
            print(f"✓ Columns: {list(df_combined.columns)}")
            
            # Show some statistics
            print(f"\n📊 Population Statistics:")
            print(f"   WorldPop 2020 - Total: {df_combined['worldpop_population'].sum():,.0f}")
            print(f"   GHSL 2020 - Total: {df_combined['ghsl_population'].sum():,.0f}")
            print(f"   Difference: {df_combined['worldpop_population'].sum() - df_combined['ghsl_population'].sum():,.0f}")
            
            # Also save as JSON for backup
            output_json = "Data/tile_activity_dual_population.json"
            df_combined.to_json(output_json, orient='records', indent=2)
            print(f"✓ Backup saved as JSON: {output_json}")
            
            print(f"\n🎉 Success! Your Costa Rica mobility analysis with dual population data is ready!")
            
        else:
            print("\n❌ GHSL data could not be processed. Saving WorldPop data only...")
            
            # Save WorldPop data only
            output_file = "Data/tile_activity_worldpop_only.csv"
            df_worldpop.to_csv(output_file, index=False)
            
            print(f"✓ WorldPop results saved to: {output_file}")
            print(f"✓ File contains {len(df_worldpop)} rows and {len(df_worldpop.columns)} columns")
            print(f"✓ Columns: {list(df_worldpop.columns)}")
            
            print(f"\n📊 WorldPop Statistics:")
            print(f"   WorldPop 2020 - Total: {df_worldpop['worldpop_population'].sum():,.0f}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Please check your GEE authentication and try again.")

if __name__ == "__main__":
    main()
