"""
FiLoSoFi 2019 — Income, Poverty & Living Standards
Data Storytelling App
"""

import streamlit as st

# --- 1. Page Configuration (Must be first) ---
st.set_page_config(
    layout="wide",
    page_title="France: The Geography of Wealth",
    page_icon="🇫🇷",
    initial_sidebar_state="expanded"
)

import os
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.ops import unary_union
import folium
from folium.features import GeoJsonTooltip
from streamlit_folium import st_folium
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import tempfile

# --- 2. Custom CSS for Premium Feel ---
st.markdown("""
<style>
    /* Main titles */
    h1 {
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        font-weight: 700;
        color: #1E3A8A; /* Dark Blue */
    }
    h2, h3 {
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        color: #334155;
    }
    /* Metrics styling */
    div[data-testid="stMetricValue"] {
        font-size: 2rem;
        color: #0F172A;
    }
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #F8FAFC; /* Light Slate */
    }
    /* Ensure sidebar text is dark and visible */
    section[data-testid="stSidebar"] .stMarkdown, 
    section[data-testid="stSidebar"] h1, 
    section[data-testid="stSidebar"] h2, 
    section[data-testid="stSidebar"] h3, 
    section[data-testid="stSidebar"] p, 
    section[data-testid="stSidebar"] span, 
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] div[data-testid="stRadio"] label {
        color: #1E293B !important; /* Dark Slate */
    }
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: transparent;
        border-radius: 4px 4px 0px 0px;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. Data Loading & Caching Functions ---

def safe_divide(num, den, fill=np.nan):
    """Elementwise safe divide."""
    num = np.array(num, dtype=float)
    den = np.array(den, dtype=float)
    with np.errstate(divide='ignore', invalid='ignore'):
        out = np.where((den == 0) | np.isnan(den) | np.isinf(den), fill, num / den)
    return out

def fix_geometry(geom):
    """Fix invalid geometries."""
    if geom is None or geom.is_empty:
        return None
    try:
        if geom.is_valid:
            return geom
        return geom.buffer(0)
    except:
        return None

@st.cache_data(show_spinner="Loading 1km Tiles Data...")
def load_data(tiles_path, communes_path):
    """Load and prepare the core datasets."""
    if not os.path.exists(tiles_path):
        return None, None
    if not os.path.exists(communes_path):
        return None, None

    # Load Tiles
    tiles = gpd.read_file(tiles_path)
    tiles.columns = tiles.columns.str.strip().str.lower()
    
    # Load Communes
    communes = gpd.read_file(communes_path)
    communes.columns = communes.columns.str.strip().str.lower()
    
    return tiles, communes

@st.cache_data(show_spinner="Processing Indicators...")
def process_tiles(_tiles_gdf):
    """Calculate socioeconomic indicators on tiles."""
    df = _tiles_gdf.copy()
    
    # Convert columns to numeric
    numeric_cols = ['ind', 'men', 'men_pauv', 'men_prop', 'log_soc', 'ind_snv']
    for c in numeric_cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors='coerce')

    # Calculate Ratios
    df['poverty_rate'] = safe_divide(df['men_pauv'], df['men']) * 100
    df['ownership_rate'] = safe_divide(df['men_prop'], df['men']) * 100
    df['social_housing_rate'] = safe_divide(df['log_soc'], df['men']) * 100
    df['avg_income'] = safe_divide(df['ind_snv'], df['ind'])
    
    return df

@st.cache_data(show_spinner="Aggregating to Communes...")
def aggregate_to_communes(_tiles_processed, _communes_gdf):
    """Aggregate tile data to commune level for lighter mapping."""
    # Spatial join or merge based on ID?
    # The dataset description says 'lcog_geo' in tiles matches commune code.
    
    # 1. Identify commune code column in communes_gdf
    commune_key = next((c for c in ['insee', 'insee_com', 'code_insee', 'com', 'code'] if c in _communes_gdf.columns), None)
    if not commune_key:
        st.error("Could not find commune code column.")
        return None

    # 2. Merge
    # Ensure we keep the name column
    name_key = next((c for c in ['nom', 'nom_com', 'nom_comm', 'libelle'] if c in _communes_gdf.columns), None)
    cols_to_keep = [commune_key, 'geometry']
    if name_key:
        cols_to_keep.append(name_key)
        
    merged = _tiles_processed.merge(_communes_gdf[cols_to_keep], left_on='lcog_geo', right_on=commune_key, how='inner')
    
    # 3. Group by Commune
    # We need weighted averages
    # Define aggregation logic
    def weighted_avg(x, val_col, weight_col):
        try:
            return np.average(x[val_col], weights=x[weight_col])
        except ZeroDivisionError:
            return np.nan

    # Grouping
    # We can't use apply easily with complex logic on large data, so we do it manually or optimized
    # Optimization: Pre-calculate weighted sums
    merged['pop_income'] = merged['avg_income'] * merged['ind']
    merged['hh_poverty'] = merged['poverty_rate'] * merged['men']
    merged['hh_ownership'] = merged['ownership_rate'] * merged['men']
    merged['hh_social'] = merged['social_housing_rate'] * merged['men']
    
    grouped = merged.groupby(commune_key).agg({
        'ind': 'sum',
        'men': 'sum',
        'pop_income': 'sum',
        'hh_poverty': 'sum',
        'hh_ownership': 'sum',
        'hh_social': 'sum'
    }).reset_index()
    
    # Calculate final weighted averages
    grouped['avg_income'] = grouped['pop_income'] / grouped['ind']
    grouped['poverty_rate'] = grouped['hh_poverty'] / grouped['men']
    grouped['ownership_rate'] = grouped['hh_ownership'] / grouped['men']
    grouped['social_housing_rate'] = grouped['hh_social'] / grouped['men']
    
    # Rename for clarity
    grouped = grouped.rename(columns={'ind': 'total_pop', 'men': 'total_households'})
    
    # 4. Attach Geometry and Name back
    communes_final = _communes_gdf.merge(grouped, on=commune_key, how='inner')
    
    # Ensure name column is standardized
    if name_key and name_key != 'nom':
        communes_final['nom'] = communes_final[name_key]
    elif not name_key:
        communes_final['nom'] = communes_final[commune_key] # Fallback to ID
    
    # 5. Simplify geometry for web performance
    # Increased simplification to 0.01 (approx 1km) for better performance
    communes_final['geometry'] = communes_final.geometry.simplify(0.01)
    
    return communes_final

# --- 4. Main App Logic ---

def main():
    # Sidebar
    st.sidebar.title("🇫🇷 Wealth & Poverty")
    st.sidebar.markdown("Based on INSEE FiLoSoFi 2019 Data")
    
    nav = st.sidebar.radio("Navigation", ["The Narrative", "Interactive Dashboard", "About the Data"])
    
    # File Paths (Hardcoded for the user's workspace, but editable)
    # Using the files we saw in the directory
    default_tiles = "carreaux_1km_met.gpkg"
    default_communes = "communes2020.gpkg"
    
    # Check if files exist
    if not os.path.exists(default_tiles) or not os.path.exists(default_communes):
        st.error(f"Data files not found. Please ensure `{default_tiles}` and `{default_communes}` are in the directory.")
        return

    # Load Data
    tiles_raw, communes_raw = load_data(default_tiles, default_communes)
    
    if tiles_raw is None:
        st.stop()
        
    tiles = process_tiles(tiles_raw)
    
    # Aggregate (Cached)
    communes_agg = aggregate_to_communes(tiles, communes_raw)

    # --- PAGE: THE NARRATIVE ---
    if nav == "The Narrative":
        st.title("The Geography of Inequality in France")
        st.markdown("### A data-driven story about income, housing, and poverty.")
        
        st.markdown("---")
        
        # ACT 1: The Big Picture
        st.header("1. The Big Picture: Income Distribution")
        st.write("""
        France is often seen as a country with a strong social safety net, but how is wealth actually distributed across the territory?
        Using data from 1km² tiles, we can see the disparity between the wealthiest and the poorest areas.
        """)
        
        col1, col2 = st.columns(2)
        with col1:
            median_inc = tiles['avg_income'].median()
            st.metric("Median Annual Income (per person)", f"{median_inc:,.0f} €")
        with col2:
            poverty_avg = tiles['poverty_rate'].mean()
            st.metric("Average Neighborhood Poverty Rate", f"{poverty_avg:.1f}%")
            
        # Histogram
        fig_hist = px.histogram(
            tiles, 
            x="avg_income", 
            nbins=100, 
            title="Distribution of Average Income (by 1km Tile)",
            labels={"avg_income": "Average Income (€)"},
            color_discrete_sequence=["#3B82F6"]
        )
        fig_hist.add_vline(x=median_inc, line_dash="dash", line_color="red", annotation_text="Median")
        st.plotly_chart(fig_hist, width="stretch")
        
        st.info("**Insight:** The distribution is right-skewed. While most neighborhoods cluster around the median, there is a long tail of very wealthy areas.")

        st.markdown("---")

        # ACT 2: Urban vs Rural
        st.header("2. The Urban Paradox")
        st.write("""
        Cities are engines of wealth, but they also concentrate poverty. 
        High income areas often sit right next to social housing districts.
        """)
        
        if communes_agg is None:
             st.error("Could not aggregate data to communes. Please check the data files.")
             st.stop()

        # Scatter Plot: Income vs Social Housing
        fig_scatter = px.scatter(
            communes_agg.sample(1000), # Sample for performance
            x="avg_income",
            y="social_housing_rate",
            size="total_pop",
            color="poverty_rate",
            hover_name="nom", # Assuming 'nom' exists, need to check columns
            color_continuous_scale="RdYlGn_r",
            title="Income vs. Social Housing (Sample of 1000 Communes)",
            labels={"avg_income": "Avg Income (€)", "social_housing_rate": "Social Housing %", "poverty_rate": "Poverty Rate %"}
        )
        st.plotly_chart(fig_scatter, width="stretch")
        
        st.write("""
        **Observation:** There is a clear negative correlation. Wealthier communes tend to have less social housing. 
        However, some large urban centers (large bubbles) show both high income and significant social housing, indicating internal inequality.
        """)

        st.markdown("---")
        
        # ACT 3: Implications
        st.header("3. Implications for Policy")
        st.success("""
        **Targeted Interventions:**
        - **Rural Areas:** Focus on connectivity and services, as income is lower but poverty is less concentrated than in specific urban pockets.
        - **Urban Centers:** Address the sharp divide between neighborhoods.
        """)

    # --- PAGE: DASHBOARD ---
    elif nav == "Interactive Dashboard":
        st.title("Interactive Explorer")
        st.markdown("Explore the data at the commune level.")
        
        # Filters
        col1, col2 = st.columns(2)
        with col1:
            metric = st.selectbox("Select Metric to Map", 
                                  ["avg_income", "poverty_rate", "ownership_rate", "social_housing_rate"],
                                  format_func=lambda x: x.replace("_", " ").title())
        with col2:
            opacity = st.slider("Map Opacity", 0.1, 1.0, 0.7)

        # Map Logic
        m = folium.Map(location=[46.603354, 1.888334], zoom_start=6, tiles="CartoDB positron", prefer_canvas=True)
        
        # Color scales
        scales = {
            "avg_income": "YlGnBu",
            "poverty_rate": "OrRd",
            "ownership_rate": "Greens",
            "social_housing_rate": "Purples"
        }
        
        # Choropleth with integrated Tooltip
        choropleth = folium.Choropleth(
            geo_data=communes_agg,
            name="Choropleth",
            data=communes_agg,
            columns=[communes_agg.index, metric], # Using index if we can't find a stable ID
            key_on="feature.id", # GeoPandas to_json uses index as ID by default
            fill_color=scales.get(metric, "Blue"),
            fill_opacity=opacity,
            line_opacity=0.1,
            legend_name=metric.replace("_", " ").title(),
            smooth_factor=2.0
        )
        
        # Add tooltip to the choropleth layer directly
        choropleth.geojson.add_child(
            GeoJsonTooltip(
                fields=['nom', 'avg_income', 'poverty_rate', 'total_pop'],
                aliases=['Commune:', 'Income:', 'Poverty %:', 'Pop:'],
                localize=True
            )
        )
        
        choropleth.add_to(m)

        # Render map with limited return objects for performance
        st_folium(m, width="100%", height=600, returned_objects=[])
        
        # Data Table
        st.subheader("Top Communes by Selected Metric")
        st.dataframe(
            communes_agg[['nom', 'total_pop', metric]]
            .sort_values(metric, ascending=False)
            .head(10)
            .style.format({metric: "{:.2f}"})
        )

    # --- PAGE: ABOUT ---
    elif nav == "About the Data":
        st.title("About the Dataset")
        st.markdown("""
        **Source:** [data.gouv.fr - FiLoSoFi 2019](https://www.data.gouv.fr/fr/datasets/revenus-pauvrete-et-niveau-de-vie-en-2019-donnees-carroyees-a-200m-et-1km/)
        
        **Description:**
        The **FiLoSoFi** (Fichier Localisé Social et Fiscal) dataset provides granular data on income, poverty, and living standards in France.
        
        **Methodology:**
        - **Gridding:** Data is aggregated into 1km x 1km squares to preserve anonymity while providing high resolution.
        - **Indicators:** Includes median standard of living, poverty rates, and household characteristics.
        
        **Credits:**
        - App built with Streamlit.
        - Analysis by Harish.
        """)

if __name__ == "__main__":
    main()