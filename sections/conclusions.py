import streamlit as st

def render():
    st.header("🏁 Strategic Conclusions: A Territory in Transformation")
    
    st.markdown("""
    Our multidimensional analysis of the 2015-2019 period allows us to answer our core question: 
    *How does the gravitational pull of Geneva reshape the local socioeconomic fabric?*
    """)

    # --- Pillar 1: The Wealth Engine ---
    st.markdown("### 1. The Geneva Hyper-Gradient 💸")
    st.info("""
    **Conclusion:** The territory is defined not by a smooth economic transition, but by a sharp **"Wealth Cliff"**.
    
    *   **The Findings:** Communes within the immediate "Frontalier" belt (Archamps, Sauverny) have decoupled from the national trend, achieving income levels (>50k€) that rival Parisian hubs.
    *   **The Mechanism:** This is a direct importation of purchasing power. The "Geneva Effect" is an external economic shock that local wealth creation cannot replicate.
    *   **The Risk:** A "two-speed" territory where the gap between the border elite and the rural interior (the "valleys" in our 3D map) widens, potentially creating social friction.
    """)
    
    # --- Pillar 2: The Zoning Paradox ---
    st.markdown("### 2. The Zoning Paradox 🏡")
    st.warning("""
    **Conclusion:** The housing market is a **"Golden Cage"**—wealthy, stable, but rigid.
    
    *   **The Findings:** With **90%+ individual houses** and **invariant Social Housing rates (~3.7%)**, the territory has effectively "zoned out" lower-income diversity.
    *   **The Mechanism:** High correlations between `Avg Income` and `Home Ownership` prove that wealth here is essentially a function of real estate access.
    *   **The Risk:** This rigidity creates a "Fortress Effect," preventing middle-class service workers (teachers, nurses) from living where they work, exacerbating traffic and labor shortages.
    """)

    # --- Pillar 3: The Demographic Pivot ---
    st.markdown("### 3. The Future: A Rejuvenation Pivot? 👶")
    st.success("""
    **Conclusion:** Against the odds, the territory is **getting younger**, driven by construction.
    
    *   **The Findings:** Our scatter plots reveal a robust link: **New Housing = New Families**. The positive deviation in youth projection for 2025 suggests the area is successfully attracting a new generation.
    *   **The Mechanism:** Development projects are working. They are the only effective lever to counter the natural aging of historic populations.
    *   **The Opportunity:** To sustain this, the "Fortress" must open its gates slightly—building varied housing types to accommodate these young families who may not yet afford the "Villa Standard."
    """)

    st.markdown("---")
    
    st.subheader("🚀 Final Recommendation")
    st.markdown("""
    > **For Policymakers:**
    > *The "Geneva Effect" brings wealth, but urban planning distributes it. To avoid becoming a dormitory for the ultra-wealthy, the territory must prioritize **diversified housing stock**. The data proves that where we build, the youth follow. The path to a balanced future lies in breaking the "Single-Family Zoning" lock.*
    """)

    st.markdown("---")
    st.caption("Data Quality Note: Analysis based on INSEE Filosofi 2015-2019. See 'Introduction' for full methodology.")
