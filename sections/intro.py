import streamlit as st

def render():
    st.markdown("<h1 style='text-align: center; '>🇫🇷 The Geneva Effect: Mapping Wealth on the French Border</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; '>Analyzing the Socioeconomic Impact of Cross-Border Wealth (2015-2019)</h3>", unsafe_allow_html=True)
    st.markdown("---")

    col1, col2 = st.columns([1.5, 1])
    
    with col1:
        st.markdown("""
        <div style='font-size: 1.1rem; line-height: 1.6;'>
        
        

        <strong>The Core Question:</strong><br>
        <em>As the French economy improves nationwide, does the "Geneva Effect" still dominate local prosperity?</em><br><br>
        
        <strong>The Narrative Arc:</strong>
        This project explores the tension between <strong>National Growth</strong> and <strong>Border Dominance</strong>. While wealth is rising generally, the gravitational pull of Geneva creates a unique distortion:
        <ul style="margin-top: 5px;">
            <li>💰 <strong>Wealth Shift:</strong> How "Frontalier" communes are capturing the lion's share of regional growth.</li>
            <li>🏘️ <strong>The Fortress:</strong> How extreme housing pressure locks out the middle class despite rising incomes.</li>
            <li>👶 <strong>Rejuvenation:</strong> The surprising demographic crossover where young families return to the border.</li>
        </ul>
        <div style=' padding: 15px; border-radius: 8px; border: 1px solid #E2E8F0; margin-bottom: 20px;'>
            <strong>🇨🇭 What is the "Geneva Effect"?</strong><br>
            <span style='font-size: 0.95rem;'>
            It is the economic phenomenon where <strong>high Swiss salaries</strong> drive up the cost of living and real estate prices in neighboring French border towns ("Frontalier" communes). This creates islands of extreme wealth that contrast sharply with the rural periphery.
            </span>
        </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.info("ℹ️ **Data Source:** [INSEE - Filosofi 2015, 2017, 2019 (Open License)](https://www.data.gouv.fr/datasets/revenus-pauvrete-et-niveau-de-vie-donnees-carroyees/)")
        
        with st.expander("🛠️ Data Quality & Methodology"):
            st.markdown("""
            *   **Sourcing:** Data is sourced from the official **INSEE Filosofi** datasets at the 1km grid level, aggregated to communes.
            *   **Variable Engineering:** 
                *   *Distance to Geneva:* Calculated as the geodesic distance from each commune's centroid to Geneva City Hall (Lat: 46.2044, Lon: 6.1432).
                *   *Ratios:* Derived metrics (e.g., Youth %) are calculated dynamically to ensure comparability across years.
            *   **Cleaning & Imputation:** 
                *   Missing numeric values (e.g., specific age brackets in small villages) were imputed with 0 to allow for regional aggregation.
                *   **Privacy:** To protect anonymity, INSEE suppresses data for grid squares with <11 households. Our analysis respects this by using only the available non-suppressed data.
            *   **Limitations:** The analysis focuses on valid residential tax households. Collective housing (dorms, institutions) is excluded, and the dataset is limited to the available administrative boundaries of the region.
            """)
        
    with col2:
        st.markdown("""
        <div style=' padding: 20px; border-radius: 10px; border: 1px solid #E2E8F0;'>
            <h4 style='margin-top:0;'>🚀 Analysis Patterns</h4>
            <ol style='font-size: 1rem;'>
                <li><strong>Rankings & Distribution</strong>: Identifying the "Winners" of the wealth shift.</li>
                <li><strong>Change Over Time</strong>: Tracking the 2015-2019 evolution.</li>
                <li><strong>Compare Groups</strong>: Frontalier vs. Interior dynamics.</li>
            </ol>
            <hr style="border-top: 1px solid #E2E8F0;">
            <h4 style='margin-top:0;'>🎛️ Sidebar Controls</h4>
            <ul style='font-size: 1.1rem;'>
                <li><strong>🗓️ Year Filter</strong>: Toggle between <strong>2015, 2017, and 2019</strong> to see how data evolves over time.</li>
                <li><strong>📊 Primary Metric</strong>: Select the main variable (e.g., <em>Poverty Rate</em>) to update all maps and charts.</li>
                <li><strong>📍 Commune Filter</strong>: Search for specific cities (e.g., <em>"Paris"</em>) to compare them in the Deep Dives section.</li>
                <li><strong>ℹ️Reset Cache</strong>: Option to reset the cache and by clearing the saved cache data and you can start new.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    
    st.subheader("Variable Dictionary")
    st.markdown("Below are the key metrics used in this analysis:")
    
    variables = {
        "Wealth & Poverty": {
            "Average Income (`avg_income`)": "Average disposable income per consumption unit in the commune.",
            "Poverty Rate (`poverty_rate`)": "Percentage of households falling below the poverty line (60% of median income)."
        },
        "Housing": {
            "Home Ownership (`ownership_rate`)": "Percentage of households owning their primary residence.",
            "Social Housing (`social_housing_rate`)": "Percentage of social housing units in the housing stock.",
            "Old Housing (`old_housing_pct`)": "Share of dwellings constructed before 1945.",
            "New Housing (`new_housing_pct`)": "Share of dwellings constructed after 1990."
        },
        "Demographics": {
            "Youth Share (`youth_pct`)": "Percentage of population under 18 years old.",
            "Senior Share (`senior_pct`)": "Percentage of population over 65 years old.",
            "Single Parents (`single_parent_pct`)": "Percentage of families headed by a single parent."
        }
    }
    
    for category, vars in variables.items():
        with st.expander(category, expanded=True):
            for name, desc in vars.items():
                st.markdown(f"- **{name}**: {desc}")
