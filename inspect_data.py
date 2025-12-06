import geopandas as gpd
import os

data_dir = "data"
files = {
    2015: "Filosofi2015_carreaux_1000m_metropole.gpkg",
    # 2017: "Filosofi2017_carreaux_1km_met.gpkg",
    # 2019: "carreaux_1km_met.gpkg"
}

for year, filename in files.items():
    path = os.path.join(data_dir, filename)
    if os.path.exists(path):
        try:
            gdf = gpd.read_file(path, rows=1)
            print(f"--- {year} Columns ---")
            print(gdf.columns.tolist())
        except Exception as e:
            print(f"Error reading {year}: {e}")
    else:
        print(f"File not found: {year}")
