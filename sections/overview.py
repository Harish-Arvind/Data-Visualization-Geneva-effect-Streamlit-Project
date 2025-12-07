import streamlit as st
from utils.viz import line_chart, bar_chart, map_chart_3d
from utils.prep import safe_divide

def render(tables, metric="avg_income", selected_years=None):
    st.header("National Overview: Is the Rising Tide Tilted Towards Geneva?")
    
    st.markdown("""
    > **💡 Headline Insight:**  
    > *While the French economy shows broad improvement over time, the **'Geneva Effect'** creates an extreme gravitational pull, concentrating wealth disproportionately along the border.*
    """)
    
    
    ts_data = tables["timeseries"]
    geo_data = tables["geo"]
    # For superlatives, we need the region data
    reg_data = tables["by_region"]
    
    if selected_years:
        ts_data = ts_data[ts_data["year"].isin(selected_years)]

    # --- KPIs ---
    if not ts_data.empty:
        latest_yr = ts_data["year"].max()
        current_data = ts_data[ts_data["year"] == latest_yr]
        
        if not current_data.empty:
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Avg Income", f"{current_data['avg_income'].values[0]:,.0f} €")
            c2.metric("Poverty Rate", f"{current_data['poverty_rate'].values[0]:.1f}%")
            # Geneva Gravity KPI
            if 'dist_geneva_km' in current_data.columns:
                # Top 10% Wealthiest
                threshold = current_data['avg_income'].quantile(0.9)
                rich_zone = current_data[current_data['avg_income'] >= threshold]
                avg_dist_rich = rich_zone['dist_geneva_km'].mean()
                
                c3.metric("Wealth Center", f"{avg_dist_rich:.0f} km", delta="from Geneva", delta_color="inverse")
            else:
                youth_val = current_data['youth_pct'].values[0] if 'youth_pct' in current_data.columns else 0
                c3.metric("Youth Pop (<18)", f"{youth_val:.1f}%")
            
            social_val = current_data['social_housing_rate'].values[0] if 'social_housing_rate' in current_data.columns else 0
            c4.metric("Social Housing", f"{social_val:.1f}%")
    
    # --- Highlights (Superlatives) ---
    st.subheader("Commune Highlights (Latest Year)")
    if not reg_data.empty:
        latest_reg = reg_data[reg_data['year'] == reg_data['year'].max()]
        
        h1, h2, h3 = st.columns(3)
        
        # Wealthiest
        wealthiest = latest_reg.sort_values('avg_income', ascending=False).iloc[0]
        h1.metric("Wealthiest Commune", wealthiest['nom'], f"{wealthiest['avg_income']:,.0f} €")
        
        # Youngest
        if 'youth_pct' in latest_reg.columns:
            youngest = latest_reg.sort_values('youth_pct', ascending=False).iloc[0]
            h2.metric("Youngest Commune", youngest['nom'], f"{youngest['youth_pct']:.1f}% (0-17yo)")
            
        # Most Social Housing
        if 'social_housing_rate' in latest_reg.columns:
            social = latest_reg.sort_values('social_housing_rate', ascending=False).iloc[0]
            h3.metric("Most Social Housing", social['nom'], f"{social['social_housing_rate']:.1f}%")

    st.markdown("---")
    
    # --- Visualizations ---
    # --- Visualizations ---
    # 1. Trends Section (Full Width)
    st.subheader("National Growth Dynamics (The Rising Tide)")
    
    if not ts_data.empty:
        # Calculate total growth for the subtitle
        start_val = ts_data[ts_data['year'] == ts_data['year'].min()][metric].values[0]
        end_val = ts_data[ts_data['year'] == ts_data['year'].max()][metric].values[0]
        growth_pct = ((end_val - start_val) / start_val) * 100
        
        st.caption(f"📈 **Trend Analysis:** The national average for {metric.replace('_', ' ')} has grown by **+{growth_pct:.1f}%** between 2015 and 2019, confirming the 'Improving Economy' hypothesis.")
        
        line_chart(ts_data, metric, title=f"Rising Tide: Evolution of {metric.replace('_', ' ').title()}")
    else:
        st.warning("Insufficient data to show trends.")
    
    st.markdown("---")

    # 2. Map Section (Full Width, Large)
    st.subheader("The Gravity of Geneva: Geographic Wealth Concentration")
    st.caption("Interactive 3D Map • Tilt: 45° • Height: Scale based on value")
    
    map_chart_3d(geo_data, metric, height=700)
    
    st.markdown("""
    ### 🏔️ Spatial Analysis: The Topography of Wealth
    
    The 3D visualization above essentially recreates the **Geographic contours of the "Geneva Effect"**.
    
    1.  **The Gradient:** Notice the sharp "cliff" of income. The tallest pillars (wealthiest communes) are strictly clustered along the border, while the "valleys" (poorer areas) begin almost immediately as you move inland.
    2.  **The Urban Sprawl:** The height of the bars correlates with the price of land. This map doubles as a "pressure map" for the housing market—where the income is high, the housing market is locked.
    """)
