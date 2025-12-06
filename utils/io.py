import streamlit as st
import geopandas as gpd
import os
import pandas as pd

@st.cache_data(show_spinner="Loading Data (2015-2019)...")
def load_data(data_dir="data"):
    """
    Load all available datasets (2015, 2017, 2019) and communes.
    Returns:
        dict: {year: gdf}, communes_gdf
    """
    files = {
        2015: "Filosofi2015_carreaux_1000m_metropole.gpkg",
        2017: "Filosofi2017_carreaux_1km_met.gpkg",
        2019: "carreaux_1km_met.gpkg"
    }
    
    tiles_data = {}
    
    for year, filename in files.items():
        path = os.path.join(data_dir, filename)
        if os.path.exists(path):
            try:
                gdf = gpd.read_file(path)
                gdf.columns = gdf.columns.str.strip().str.lower()
                tiles_data[year] = gdf
            except Exception as e:
                st.warning(f"Could not load {year} data: {e}")
        else:
            st.warning(f"File not found for {year}: {path}")

    # Load Communes
    communes_path = os.path.join(data_dir, "communes2020.gpkg")
    if os.path.exists(communes_path):
        communes = gpd.read_file(communes_path)
        communes.columns = communes.columns.str.strip().str.lower()
    else:
        st.error(f"Communes file not found at {communes_path}")
        communes = None
            
    return tiles_data, communes
