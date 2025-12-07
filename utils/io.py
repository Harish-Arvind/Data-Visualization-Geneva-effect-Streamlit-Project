import streamlit as st
import geopandas as gpd
import os
import pandas as pd
from utils.constants import DATA_DIR, FILES, COMMUNES_FILE

@st.cache_data(show_spinner="Loading Data...")
def load_data(data_dir=DATA_DIR):
    """
    Load all available datasets defined in constants.
    Returns:
        dict: {year: gdf}, communes_gdf
    """
    tiles_data = {}
    
    for year, filename in FILES.items():
        path = os.path.join(data_dir, filename)
        if os.path.exists(path):
            try:
                gdf = gpd.read_file(path)
                gdf.columns = gdf.columns.str.strip().str.lower()
                tiles_data[year] = gdf
            except Exception as e:
                st.warning(f"Could not load {year} data: {e}")
        else:
            # Silent fail or debug log, app shouldn't crash if one year missing
            # st.warning(f"File not found for {year}: {path}") 
            pass

    # Load Communes
    communes_path = os.path.join(data_dir, COMMUNES_FILE)
    if os.path.exists(communes_path):
        communes = gpd.read_file(communes_path)
        communes.columns = communes.columns.str.strip().str.lower()
    else:
        st.error(f"Communes file not found at {communes_path}")
        communes = None
            
    return tiles_data, communes
