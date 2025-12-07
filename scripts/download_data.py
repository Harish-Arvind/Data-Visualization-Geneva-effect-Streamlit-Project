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
            # Find the file matching the pattern
            candidates = [f for f in z.namelist() if pattern in f and f.endswith('.gpkg')]
            if not candidates:
                 # Try exact match
                if pattern in z.namelist():
                    candidates = [pattern]
                # Try sloppy match (sometimes the zip has folders)
                else: 
                     candidates = [f for f in z.namelist() if target_filename in f]

                if not candidates:
                    print(f"❌ Could not find file matching '{pattern}' in zip.")
                    print(f"   Contents: {z.namelist()[:5]}...")
                    return
            
            # Pick the first one
            source_file = candidates[0]
            with z.open(source_file) as source, open(target_path, "wb") as target:
                target.write(source.read())
            
            print(f"✅ Saved to {target_path}")

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

def download_all():
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

if __name__ == "__main__":
    download_all()
