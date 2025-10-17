#!/usr/bin/env python3
"""
Upload tile activity data to GEE and sum WorldPop population within each tile.
This script uploads the GPKG file as a FeatureCollection and calculates 
population totals for each tile.
"""

import ee
import os

def initialize_gee():
    """Initialize Google Earth Engine."""
    try:
        ee.Initialize()
        print("✓ Google Earth Engine initialized successfully")
    except Exception as e:
        print(f"Initialization failed: {e}")
        print("Please authenticate using: earthengine authenticate")
        raise

def upload_gpkg_to_gee(gpkg_path: str, asset_id: str) -> str:
    """
    Upload a GPKG file to GEE as a FeatureCollection.
    
    Args:
        gpkg_path: Path to the GPKG file
        asset_id: GEE asset ID where the FeatureCollection will be stored
    
    Returns:
        str: The asset ID of the uploaded FeatureCollection
    """
    
    if not os.path.exists(gpkg_path):
        raise FileNotFoundError(f"GPKG file not found: {gpkg_path}")
    
    print(f"Uploading {gpkg_path} to GEE as {asset_id}...")
    
    # Upload the GPKG file to GEE
    upload_task = ee.batch.Upload.table.toAsset(
        source=gpkg_path,
        assetId=asset_id,
        description=f"Upload tile activity data from {os.path.basename(gpkg_path)}"
    )
    
    upload_task.start()
    print(f"✓ Upload task started: {upload_task.id}")
    print("Check GEE console for upload status")
    print("Note: This may take several minutes depending on file size")
    
    return asset_id

def sum_population_by_tiles(tile_asset_id: str, 
                          population_year: str = "2020",
                          scale: int = 100,
                          tile_scale: int = 4) -> ee.FeatureCollection:
    """
    Sum WorldPop population within each tile.
    
    Args:
        tile_asset_id: GEE asset ID of the tile FeatureCollection
        population_year: Year of population data to use
        scale: Scale for reduceRegions operation
        tile_scale: Tile scale for reduceRegions operation
    
    Returns:
        ee.FeatureCollection: Tiles with population sums added
    """
    
    print(f"Loading tile FeatureCollection from {tile_asset_id}...")
    tiles = ee.FeatureCollection(tile_asset_id)
    
    print(f"Loading WorldPop {population_year} data...")
    pop_data = (
        ee.ImageCollection('WorldPop/GP/100m/pop')
        .select(f'CRI_{population_year}_population')
        .mosaic()
    )
    
    print("Calculating population per tile...")
    tiles_with_pop = pop_data.reduceRegions(
        collection=tiles,
        reducer=ee.Reducer.sum(),
        scale=scale,
        tileScale=tile_scale
    )
    
    print("✓ Population calculation completed")
    return tiles_with_pop

def export_results_to_drive(feature_collection: ee.FeatureCollection,
                           filename: str = "tile_population_summary",
                           folder: str = "Costa_Rica_Mobility",
                           file_format: str = "GPKG") -> None:
    """
    Export results to Google Drive.
    
    Args:
        feature_collection: FeatureCollection with population data
        filename: Name of the exported file
        folder: Google Drive folder name
        file_format: Export format ('GPKG', 'SHP', 'CSV', etc.)
    """
    
    print(f"Exporting results to Google Drive as {file_format}...")
    
    export_task = ee.batch.Export.table.toDrive(
        collection=feature_collection,
        description=f'tile_population_{file_format.lower()}',
        fileNamePrefix=filename,
        folder=folder,
        fileFormat=file_format
    )
    
    export_task.start()
    print(f"✓ Export task started: {export_task.id}")
    print("Check GEE console or Google Drive for the exported file")

def main():
    """
    Main function to upload tiles and calculate population sums.
    """
    print("=== Upload Tiles and Sum Population ===")
    
    # Initialize GEE
    initialize_gee()
    
    # File paths and asset configuration
    gpkg_path = "Data/tile_activity_lonlat.gpkg"
    asset_id = "projects/gbsc-gcp-lab-emordeca/assets/costa_rica/analysis/tile_activity_lonlat"
    
    # Check if asset already exists
    try:
        existing_fc = ee.FeatureCollection(asset_id)
        print(f"✓ FeatureCollection already exists at {asset_id}")
        print("Skipping upload, using existing asset...")
    except Exception:
        print(f"FeatureCollection not found at {asset_id}")
        print("Uploading GPKG file to GEE...")
        upload_gpkg_to_gee(gpkg_path, asset_id)
        
        print("\n" + "="*50)
        print("IMPORTANT: Wait for the upload to complete before proceeding!")
        print("Check the GEE console for upload status.")
        print("You can run the population calculation part separately once upload is done.")
        print("="*50)
        return
    
    # Calculate population per tile
    tiles_with_pop = sum_population_by_tiles(
        tile_asset_id=asset_id,
        population_year="2020",
        scale=100,
        tile_scale=4
    )
    
    # Export results
    export_results_to_drive(
        feature_collection=tiles_with_pop,
        filename="tile_activity_with_population",
        folder="Costa_Rica_Mobility",
        file_format="CSV"
    )
    
    print("\n✓ Script completed successfully!")
    print("The exported GPKG file will contain your tiles with population totals")

def run_population_calculation_only():
    """
    Run only the population calculation part (use this after upload is complete).
    """
    print("=== Population Calculation Only ===")
    
    # Initialize GEE
    initialize_gee()
    
    # Asset ID of the uploaded tiles
    asset_id = "projects/gbsc-gcp-lab-emordeca/assets/costa_rica/analysis/tile_activity_lonlat"
    
    # Calculate population per tile
    tiles_with_pop = sum_population_by_tiles(
        tile_asset_id=asset_id,
        population_year="2020",
        scale=100,
        tile_scale=4
    )
    
    # Export results
    export_results_to_drive(
        feature_collection=tiles_with_pop,
        filename="tile_activity_with_population",
        folder="Costa_Rica_Mobility",
        file_format="CSV"
    )
    
    print("\n✓ Population calculation completed!")

if __name__ == "__main__":
    # Run the full workflow (upload + calculation)
    main()
    
    # Uncomment the line below to run only the population calculation
    # (use this after the upload is complete)
    # run_population_calculation_only()
