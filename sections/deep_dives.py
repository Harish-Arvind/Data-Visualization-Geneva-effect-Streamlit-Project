import streamlit as st
import pandas as pd
from utils.viz import (
    bar_chart, distribution_chart, line_chart, 
    correlation_matrix, population_pyramid, 
    housing_mix_chart, scatter_plot
)
from utils.prep import get_commune_comparison

def render(tables, metric="avg_income", regions=None, selected_years=None):
    st.header("Deep Analysis Laboratory")
    
    df_regions = tables["by_region"]
    
    # Filter by selected years if provided
    if selected_years:
        df_regions = df_regions[df_regions["year"].isin(selected_years)]
        if df_regions.empty:
            st.error("No data available for the selected years.")
            return

    latest_year = df_regions["year"].max()
    latest_data = df_regions[df_regions["year"] == latest_year]
    
    # Tabs for different analysis modes
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🌍 Regional Comparison", 
        "🔗 Correlations", 
        "👥 Demographics", 
        "🏠 Housing", 
        "🔎 Scatter Explorer"
    ])
    
    # --- Tab 1: Regional Comparison ---
    # --- Tab 1: Regional Comparison ---
    with tab1:
        st.subheader("Compare Communes")
        
        if not regions:
            st.info("💡 Select communes in the sidebar for a custom comparison. Showing Top 20 by default.")
            top_data = latest_data.sort_values(metric, ascending=False).head(20)
            bar_chart(top_data, metric, top_n=20, orientation='h', year=latest_year)
        else:
            # Custom Comparison
            comp_data_full = get_commune_comparison(
                df_regions, regions, 
                [metric, 'poverty_rate', 'total_pop', 'ownership_rate', 'youth_pct', 'social_housing_rate']
            )
            
            if not comp_data_full.empty:
                st.subheader(f"Analyzing: {', '.join(regions[:3])}...")
                
                # Latest year snapshot
                comp_view = comp_data_full[comp_data_full["year"] == latest_year]
                
                c1, c2 = st.columns(2)
                with c1:
                    bar_chart(comp_view, metric, orientation='h', year=latest_year)
                with c2:
                    sec_metric = "poverty_rate" if metric != "poverty_rate" else "avg_income"
                    bar_chart(comp_view, sec_metric, orientation='h', year=latest_year)
                
                st.markdown("### Evolution")
                line_chart(comp_data_full, metric, title=f"History of {metric.replace('_', ' ')}")

        st.markdown("---")
        st.subheader(f"Distribution of {metric.replace('_', ' ').title()}")
        
        # Calculate Reference (Median)
        ref_val = latest_data[metric].median()
        distribution_chart(latest_data, metric, year=latest_year, ref_value=ref_val, ref_label="Median")
        
        with st.expander("ℹ️ Methodology Note"):
            st.markdown(f"""
            **What does this show?**
            The histogram displays how {metric.replace('_', ' ')} is distributed across all communes.
            
            *   **Median Line ({ref_val:,.0f}):** Half of the communes are below this line, half are above.
            *   **Shape:** A right-skewed distribution (tail to the right) usually indicates inequality (a few very wealthy outliers).
            """)
        
        st.markdown("""
        ### 🏙️ Analysis: The "Border Effect" & The Shift in Wealth Centers
        
        Comparing the data from **2015 to 2019** reveals a fascinating geographical shift in wealth distribution:

        1.  **The Geneva Magnet:** The proximity to Switzerland is a decisive factor in communal wealth.
            *   **2015:** Border towns like **Archamps** were already among the wealthiest.
            *   **2017-2019:** We see the definitive rise and dominance of the "Frontalier" zone. Communes like **Sauverny**, **Archamps**, and **Beaumont** (all near the Swiss border) consistently surge to the top spots. **Sauverny** specifically marks a significant increase by 2019, approaching an average income of **50k €**.
        2.  **Structural Stability:** Despite these shifts at the top, the **Distribution Histogram** remains remarkably stable. The "bell curve" of income remains centered around **21k-23k €**, proving that while the "ultra-wealthy" enclaves get richer (shifting the top bars right), the general population's economic reality has changed little over this 5-year period.

        *This confirms our hypothesis: Geography (specifically proximity to economic powerhouses like Geneva) is a primary determinant of communal wealth in this territory.*
        """)

    # --- Tab 2: Correlations ---
    with tab2:
        st.subheader("Variable Correlations")
        st.markdown("Explore how different socioeconomic factors relate to each other.")
        
        avail_metrics = [
            "avg_income", "poverty_rate", "ownership_rate", "social_housing_rate",
            "youth_pct", "senior_pct", "old_housing_pct", "new_housing_pct",
            "single_parent_pct"
        ]
        
        selected_corr_metrics = st.multiselect(
            "Select variables to correlate:", 
            avail_metrics,
            default=["avg_income", "poverty_rate", "ownership_rate", "social_housing_rate", "youth_pct"]
        )
        
        correlation_matrix(latest_data, selected_corr_metrics, year=latest_year)
        
        st.markdown("""
        ### Principal Statement: The "Triangle of Inequality"
        
        Our analysis reveals three structural divides shaping French territories:
        
        1.  **The Ownership Gap:** Wealth (`avg_income`) is strongly positively correlated with **Home Ownership**, creating a clear distinction between "owner-occupied" wealthy zones and "tenant-heavy" modest areas.
        2.  **The Social Housing Trap:** There is a mechanical link between **Social Housing Rate** and **Poverty**, highlighting how vulnerable populations are concentrated in specific administrative planning zones.
        3.  **Generational Segregation:** A striking negative correlation between **Youth** and **Seniors** suggests territories specialize by age. disproportionately, younger families are found in areas with higher poverty and social housing, while wealthier municipalities tend to aim towards an older demographic profile.
        
        *This structural rigidity suggests that economic mobility is heavily constrained by the local housing market and urban planning history.*
        """)

    # --- Tab 3: Demographics ---
    with tab3:
        st.subheader("Population Structure")
        
        target_data = latest_data # Default to national view (all rows)
        
        if regions:
            st.info(f"Showing demographic profile for: {', '.join(regions)}")
            target_data = latest_data[latest_data['nom'].isin(regions)]
        else:
            st.info("Showing National Demographic Profile (Aggregated)")
            
        c1, c2 = st.columns([2, 1])
        with c1:
            population_pyramid(target_data, year=latest_year)
        with c2:
            st.markdown("### Key Demographic Stats")
            avg_youth = target_data['youth_pct'].mean()
            avg_senior = target_data['senior_pct'].mean()
            st.metric("Youth Share (<18)", f"{avg_youth:.1f}%")
            st.metric("Senior Share (>65)", f"{avg_senior:.1f}%")
            
        st.markdown("""
        ### 🔮 Demographic Outlook: A Reversal of Trends?
        
        Recent data points towards a potential **rejuvenation** of the territory, challenging the historical aging trend:
        
        *   **2019 (Baseline):** The population structure is dominated by seniors (**23.5%**) compared to youth (**19.9%**), typical of an aging municipality.
        *   **2025 Projection:** A striking shift is observed, with the **Youth share rising to 21.1%** and Seniors dropping to **20.9%**, marking a demographic crossover where the young outnumber the old.
        *   **2027 Outlook:** While stabilizing (Youth **20.4%**, Senior **22.4%**), the gap remains significantly narrower than in 2019.
        
        *This trajectory suggests a successful policy of attracting young families, likely driven by new housing developments or urban renewal projects.*
        """)

    # --- Tab 4: Housing ---
    with tab4:
        st.subheader("Housing Stock Analysis")
        
        target_housing = latest_data
        if regions:
            target_housing = latest_data[latest_data['nom'].isin(regions)]
            
        c1, c2 = st.columns([1, 1])
        with c1:
            housing_mix_chart(target_housing, year=latest_year)
        with c2:
            st.markdown("### Housing Indicators")
            if 'houses_pct' in target_housing.columns:
                 st.metric("Individual Houses", f"{target_housing['houses_pct'].mean():.1f}%")
            if 'social_housing_rate' in target_housing.columns:
                 st.metric("Social Housing Rate", f"{target_housing['social_housing_rate'].mean():.1f}%")

        st.markdown("""
        ### 🏘️ The Fortress of Stability: A Rigid Market
        
        The housing figures reveal a market that has remained virtually **frozen in time** between 2015 and 2019:
        
        *   **Dominance of Individual Houses:** Consistently hovering around **90%**, the territory is overwhelmingly composed of detached homes, characteristic of a suburban or rural "owner-occupier" model.
        *   **Static Social Housing:** The rate has flatlined at **3.7%** for four years. This is significantly below national targets (often 20-25%), indicating a **structural resistance to social mixing**.
        
        *This lack of evolution in the housing stock—neither densifying (more apartments) nor diversifying (more social housing)—suggests strict zoning policies that prioritize maintaining the status quo over welcoming new, diverse populations.*
        """)

    # --- Tab 5: Scatter Explorer ---
    with tab5:
        st.subheader("Multi-Dimensional Exploration")
        st.info("""
        **💡 Recommended Analysis Pairs (What to talk about):**
        1.  **📉 The Inequality Curve:** `Avg Income` (X) vs `Poverty Rate` (Y). *Show how wealth eradicates poverty (or doesn't).*
        2.  **🏗️ The "New Blood" Effect:** `New Housing Pct` (X) vs `Youth Pct` (Y). *Do new buildings attract young families?*
        3.  **🏢 The Social Safety Net:** `Social Housing Rate` (X) vs `Single Parent Pct` (Y). *Where do vulnerable families find support?*
        4.  **👴 The "Old Walls":** `Old Housing Pct` (X) vs `Senior Pct` (Y). *Are historic centers aging?*
        """)
        st.markdown("Plot any two variables against each other.")
        
        c1, c2, c3 = st.columns(3)
        x_axis = c1.selectbox("X Axis", avail_metrics, index=0)
        y_axis = c2.selectbox("Y Axis", avail_metrics, index=1)
        size_var = c3.selectbox("Bubble Size", ["total_pop", "total_households"], index=0)
        
        scatter_plot(latest_data, x_axis, y_axis, size=size_var, hover_name="nom", year=latest_year)
        
        st.markdown("""
        ### 🧬 Correlational Findings: The Structural Laws of the Territory
        
        Analyzing the key interactions reveals the mechanics behind the "Geneva Effect":

        1.  **The Poverty Floor (Income vs. Poverty):** The data clearly forms an "L-shape". Poverty doesn't linearly decrease; it collapses. Once a commune's Average Income exceeds **€25k**, poverty rates drop to near-zero. This identifies the "cost of entry" to live in this wealthy border zone.
        2.  **The Rejuvenation Engine (New Housing vs. Youth):** A positive correlation exists between construction and youth. Communes with high **New Housing (>20%)** consistently exhibit **Younger Populations (>25%)**. This confirms that **urban development** is the primary lever to fight demographic aging.
        3.  **The Historic Trap (Old Housing vs. Seniors):** Conversely, "historic" communes dominated by pre-1945 housing show a higher concentration of seniors. Without new housing stock, these areas struggle to attract the working-age families that drive the local economy.
        """)
