#!/usr/bin/env python3
"""
Calculate population for both WorldPop and accessible alternative population datasets.
"""

import ee
import pandas as pd
import json
import os

def main():
    """Calculate population for both WorldPop and accessible alternative datasets."""
    print("=== Dual Population Calculation (WorldPop + Accessible Alternative) ===")
    
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
        
        # Try accessible alternative population datasets
        print("\nTrying accessible alternative population datasets...")
        
        # Try different accessible population collections
        alternative_collections = [
            'CIESIN/GPWv4/population-density',
            'CIESIN/GPWv4/population-count', 
            'CIESIN/GPWv4/population-density-adjusted',
            'CIESIN/GPWv4/population-count-adjusted',
            'CIESIN/GPWv4/population-density-adjusted-to-2015-unwpp-country-totals',
            'CIESIN/GPWv4/population-count-adjusted-to-2015-unwpp-country-totals'
        ]
        
        ghsl_success = False
        df_alternative = None
        
        for collection in alternative_collections:
            try:
                print(f"Trying alternative collection: {collection}")
                
                # Load alternative population data
                pop_alt = ee.ImageCollection(collection)
                
                # Get the most recent image (usually the last one)
                pop_alt_image = pop_alt.sort('system:time_start', False).first()
                
                print(f"✓ Alternative data loaded from: {collection}")
                
                # Calculate alternative population per tile
                print("Calculating alternative population per tile...")
                tiles_with_alt = pop_alt_image.reduceRegions(
                    collection=tiles,
                    reducer=ee.Reducer.sum(),
                    scale=100,
                    tileScale=4
                )
                
                print("✓ Alternative calculation completed!")
                
                # Get alternative results
                print("Retrieving alternative results...")
                alt_results = tiles_with_alt.getInfo()
                
                # Process alternative DataFrame
                alt_features = alt_results['features']
                alt_data = []
                
                for feature in alt_features:
                    properties = feature['properties']
                    properties['geometry'] = json.dumps(feature['geometry'])
                    alt_data.append(properties)
                
                df_alternative = pd.DataFrame(alt_data)
                df_alternative = df_alternative.rename(columns={'sum': 'alternative_population'})
                
                print(f"✓ Alternative data processed: {len(df_alternative)} tiles")
                ghsl_success = True
                break
                
            except Exception as e:
                print(f"❌ Failed: {collection} - {e}")
                continue
        
        if ghsl_success and df_alternative is not None:
            # Merge the datasets
            print("\nMerging datasets...")
            df_combined = df_worldpop.merge(
                df_alternative[['geometry', 'alternative_population']], 
                on='geometry', 
                how='inner'
            )
            
            # Reorder columns for better readability
            df_combined = df_combined[['activity', 'worldpop_population', 'alternative_population', 'geometry']]
            
            # Save to local Data folder
            output_file = "Data/tile_activity_dual_population.csv"
            df_combined.to_csv(output_file, index=False)
            
            print(f"✓ Results saved to: {output_file}")
            print(f"✓ File contains {len(df_combined)} rows and {len(df_combined.columns)} columns")
            print(f"✓ Columns: {list(df_combined.columns)}")
            
            # Show some statistics
            print(f"\n📊 Population Statistics:")
            print(f"   WorldPop 2020 - Total: {df_combined['worldpop_population'].sum():,.0f}")
            print(f"   Alternative - Total: {df_combined['alternative_population'].sum():,.0f}")
            print(f"   Difference: {df_combined['worldpop_population'].sum() - df_combined['alternative_population'].sum():,.0f}")
            
            # Also save as JSON for backup
            output_json = "Data/tile_activity_dual_population.json"
            df_combined.to_json(output_json, orient='records', indent=2)
            print(f"✓ Backup saved as JSON: {output_json}")
            
            print(f"\n🎉 Success! Your Costa Rica mobility analysis with dual population data is ready!")
            
        else:
            print("\n❌ Alternative population data could not be processed. Saving WorldPop data only...")
            
            # Save WorldPop data only
            output_file = "Data/tile_activity_worldpop_only.csv"
            df_worldpop.to_csv(output_file, index=False)
            
            print(f"✓ WorldPop results saved to: {output_file}")
            print(f"✓ File contains {len(df_worldpop)} rows and {len(df_worldpop.columns)} columns")
            print(f"✓ Columns: {list(df_worldpop.columns)}")
            
            print(f"\n📊 WorldPop Statistics:")
            print(f"   WorldPop 2020 - Total: {df_worldpop['worldpop_population'].sum():,.0f}")
            
            print(f"\n💡 Suggestion:")
            print(f"   You can manually search for population datasets in GEE Code Editor")
            print(f"   or use the WorldPop data you have for now")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Please check your GEE authentication and try again.")

if __name__ == "__main__":
    main()
