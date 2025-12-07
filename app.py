import streamlit as st
from utils.io import load_data
from utils.prep import make_tables
from sections import intro, overview, deep_dives, conclusions
from utils.constants import (
    PAGE_TITLE, PAGE_ICON, CACHE_FILE, AVAILABLE_YEARS, 
    DEFAULT_YEAR, METRICS, METRIC_LABELS
)

# --- Page Configuration ---
st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon=PAGE_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS for Premium Feel ---
import os
import pandas as pd
from streamlit_option_menu import option_menu

# --- Custom Styling (Cards & Modern UI) ---
st.markdown("""
<style>
    /* Card Styling for Metrics & Charts - Layout Only */
    div[data-testid="stMetric"], div[data-testid="stPlotlyChart"], .stDataFrame {
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        border: 1px solid #E2E8F0; /* Keep border for definition */
    }
    
    /* Option Menu Customization - Minimal */
    .nav-link-selected {
        background-color: #ff4b4b !important; /* Streamlit Red/Primary Default-ish */
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data(show_spinner=False)
def get_app_data():
    # CACHE_FILE is imported from constants
    
    # 1. Try Loading from Disk
    if os.path.exists(CACHE_FILE):
        try:
            return pd.read_pickle(CACHE_FILE)
        except Exception as e:
            st.warning(f"Cache corrupted, rebuilding... ({e})")
            
    # 2. Build Data Engine (Slow Path)
    with st.spinner("Building data engine (One-time setup)..."):
        tiles_data, communes_gdf = load_data()
        if not tiles_data or communes_gdf is None:
            return None
        
        tables = make_tables(_tiles_data=tiles_data, _communes_gdf=communes_gdf)
        
        # 3. Save to Disk
        if tables:
            try:
                pd.to_pickle(tables, CACHE_FILE)
            except Exception as e:
                st.warning(f"Could not save cache: {e}")
                
        return tables

def main():
    # --- Sidebar Navigation ---
    with st.sidebar:
        # Logo
        if os.path.exists("assets/efrei_logo.png"):
             st.image("assets/efrei_logo.png", use_container_width=True)
        
        st.title("🇫🇷 The Geneva Effect")
        st.caption("v2.1 | EFREI Data Story")
        
        # Navigation with Icons
        page = option_menu(
            menu_title=None,
            options=["Introduction", "Overview", "Deep Dives", "Conclusions"],
            icons=["book", "bar-chart-fill", "search", "flag"],
            menu_icon="cast",
            default_index=1,
            styles={
                "container": {"padding": "0!important", "background-color": "transparent"},
                "icon": {"color": "#64748B", "font-size": "16px"}, 
                "nav-link": {"font-size": "14px", "text-align": "left", "margin": "5px", "--hover-color": "#E2E8F0"},
                "nav-link-selected": {"background-color": "#3B82F6", "color": "white", "font-weight": "600"},
            }
        )
        
        st.markdown("---")
        st.subheader("Global Filters")
        
        # Load Data
        with st.spinner("Loading data engine..."):
            tables = get_app_data()
        
        if not tables:
            st.error("Failed to load data.")
            st.stop()
            
        # Common Filters
        # 2. Year Selection - Improved Interaction
        avail_years = AVAILABLE_YEARS
        # Use a slider for a clearer "timeline" feel
        focus_year = st.select_slider("Select Data Year", options=avail_years, value=DEFAULT_YEAR)
        
        # Logic: We keep all years up to the focus year for trends
        selected_years = [y for y in avail_years if y <= focus_year]
        
        metric_options = METRICS
        metric = st.selectbox("Primary Metric", metric_options, format_func=lambda x: METRIC_LABELS.get(x, x))
        
        # Region Filter for Deep Dives & Overview (Map Pin-pointing)
        selected_regions = []
        if page in ["Overview", "Deep Dives"]:
            # 3. Region Filter
            all_communes = sorted(tables['by_region']['nom'].unique().tolist())
            # Default empty for Overview to show full map initially
            default_regions = [] 
            if page == "Deep Dives":
                 # Pre-select for deep dives demo if desired, or keep empty
                 default_regions = all_communes[:4] if len(all_communes) > 4 else all_communes
                 # Reset default for Deep Dives to empty if user prefers, but existing logic had defaults. 
                 # Let's keep existing default logic for Deep Dives but empty for Overview.
                 pass

            label = "Select Communes to Compare" if page == "Deep Dives" else "🔎 Pinpoint Commune on Map"
            selected_regions = st.multiselect(label, all_communes, default=default_regions if page == "Deep Dives" else [])

        if st.button("🔄 Reset Cache"):
            if os.path.exists(CACHE_FILE):
                os.remove(CACHE_FILE)
                st.cache_data.clear()
                st.rerun()

    # --- Router ---
    if page == "Introduction":
        intro.render()
        
    elif page == "Overview":
        overview.render(
            tables, 
            metric=metric if 'metric' in locals() else "avg_income", 
            selected_years=selected_years,
            regions=selected_regions
        )
        
    elif page == "Deep Dives":
        deep_dives.render(tables, metric=metric if 'metric' in locals() else "avg_income", regions=selected_regions, selected_years=selected_years)
        
    elif page == "Conclusions":
        conclusions.render()

if __name__ == "__main__":
    main()
