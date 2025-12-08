import os
import sys
import zipfile
import requests
from io import BytesIO
import geopandas as gpd

# Add project root to sys.path to import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.constants import DATA_DIR, FILES, DATA_URLS, COMMUNES_FILE

# Map of Target Filename -> {URL, SourcePattern}
DATASETS = {
    FILES[2015]: {
        "url": DATA_URLS["Filosofi2015"],
        "pattern": FILES[2015]
    },
    FILES[2017]: {
        "url": DATA_URLS["Filosofi2017"],
        "pattern": FILES[2017]
    },
    FILES[2019]: {
        "url": DATA_URLS["Filosofi2019"],
        "pattern": FILES[2019]
    }
}

def download_and_extract(url, target_filename, pattern):
    target_path = os.path.join(DATA_DIR, target_filename)
    if os.path.exists(target_path):
        print(f"✅ {target_filename} already exists.")
        return

    print(f"⬇️  Downloading {target_filename}...")
    try:
        response = requests.get(url, stream=True)
        if response.status_code != 200:
            print(f"❌ Failed to download from {url} (Status: {response.status_code})")
            return

        print("📦 Extracting...")
        with zipfile.ZipFile(BytesIO(response.content)) as z:
            # 1. Look for .7z file inside the ZIP
            seven_z_files = [f for f in z.namelist() if f.endswith('.7z')]
            
            if not seven_z_files:
                print(f"❌ No .7z file found in ZIP. Contents: {z.namelist()[:5]}")
                return

            seven_z_filename = seven_z_files[0]
            
            # 2. Extract .7z content from ZIP to memory
            with z.open(seven_z_filename) as f:
                seven_z_content = BytesIO(f.read())
                
            # 3. Extract .gpkg from .7z
            try:
                import py7zr
                with py7zr.SevenZipFile(seven_z_content, mode='r') as archive:
                    all_files = archive.getnames()
                    # Find the gpkg matching pattern
                    candidates = [f for f in all_files if pattern in f and f.endswith('.gpkg')]
                    
                    if not candidates:
                         # Fallback searches
                        if pattern in all_files:
                            candidates = [pattern]
                        else: 
                             candidates = [f for f in all_files if target_filename.replace('.gpkg', '') in f and f.endswith('.gpkg')]

                    if not candidates:
                        print(f"❌ Could not find .gpkg matching '{pattern}' in .7z archive.")
                        print(f"   Contents: {all_files[:5]}...")
                        return

                    source_file = candidates[0]
                    
                    # Extract specifically this file to DATA_DIR
                    # py7zr.extract(path=...) extracts all or targets.
                    archive.extract(path=DATA_DIR, targets=[source_file])
                    
                    # Rename if necessary (if extracted name != target_filename)
                    extracted_path = os.path.join(DATA_DIR, source_file)
                    if os.path.abspath(extracted_path) != os.path.abspath(target_path):
                        os.rename(extracted_path, target_path)

                    print(f"✅ Saved to {target_path}")

            except ImportError:
                print("❌ 'py7zr' module missing. Please install it: pip install py7zr")
                return

    except Exception as e:
        print(f"❌ Error: {e}")

def download_communes():
    """Download and process Communes explicitly."""
    target_path = os.path.join(DATA_DIR, COMMUNES_FILE)
    if os.path.exists(target_path):
         print(f"✅ {COMMUNES_FILE} already exists.")
         return

    print(f"⬇️  Downloading Communes (GeoJSON)...")
    url = DATA_URLS["Communes"]
    try:
        # Download GeoJSON using requests (handles SSL better on some systems)
        response = requests.get(url) 
        if response.status_code != 200:
            print(f"❌ Failed to download communes: {response.status_code}")
            return
            
        gdf = gpd.read_file(BytesIO(response.content))
        
        # Standardize Columns
        # Our app expects 'insee' or 'insee_com'. 
        # GregoireDavid/france-geojson uses 'code' and 'nom'.
        if 'code' in gdf.columns:
            gdf = gdf.rename(columns={'code': 'insee'})
            
        print(f"⚙️  Converting to GeoPackage...")
        gdf.to_file(target_path, driver="GPKG")
        
        print(f"✅ Saved to {target_path}")
        
    except Exception as e:
        # Keep old file if failure?
        print(f"❌ Error downloading/processing communes: {e}")

if __name__ == "__main__":
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        
    print("--- Data Download Script ---")
    print("Source: INSEE & Github (France-GeoJSON)")
    
    # 1. Download INSEE Data
    for filename, config in DATASETS.items():
        download_and_extract(config["url"], filename, config["pattern"])

    # 2. Download Communes
    download_communes()
    
    print("\nDone.")
