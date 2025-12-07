import streamlit as st

def render():
    st.header("🏁 Final Verdict: The Triumph of Gravity")
    
    st.markdown("""
    At the start of this project, we asked a simple question: **Is the region's growth benefiting everyone equally?**
    
    After analyzing thousands of data points for every commune, the answer is clear: **No. The "Geneva Effect" is the single most powerful force shaping our territory.** It creates a landscape where your distance from the border dictates your destiny.
    """)

    st.markdown("---")

    # --- Section 1: The Three Main Lessons ---
    st.markdown("### 🔍 The Three Key Lessons from the Data")
    
    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.info("**1. The \"Wealth Cliff\"**")
        st.markdown("""
        **What we saw:** 
        As soon as you move just **15km** away from Geneva, the average income drops dramatically.
        
        **What it means:** 
        This is not a "regional" economy. It is a **dormitory economy**. The wealth here is not being created by local businesses; it is being "imported" by workers commuting to Switzerland. If you are close to the border, you are wealthy. If you are far, you are not.
        """)
        
    with c2:
        st.error("**2. The \"Iron Curtain\" of Prices**")
        st.markdown("""
        **What we saw:** 
        There is a massive **-0.65 correlation** between Wealth and Poverty.
        
        **What it means:** 
        Usually, rich and poor areas can coexist. Here, they do not. The Swiss salaries drive up real estate prices so high that they create an invisible wall. Low-income families are literally **priced out** of the border zone and forced to move further inland.
        """)
        
    with c3:
        st.success("**3. Construction is Youth**")
        st.markdown("""
        **What we saw:** 
        The only places with a growing population of children are the places building **New Housing**.
        
        **What it means:** 
        Young families cannot afford the old, expensive villas near the border. They only move to where new, affordable apartments are being built. **No construction = No young families.**
        """)

    # --- Section 2: The Big Picture ---
    st.markdown("---")
    st.markdown("### 🏰 The Big Picture: The \"Golden Ghetto\" Trap")
    
    st.markdown("""
    When we put all these pieces together, we see a dangerous trend. The territory is becoming a **"Golden Ghetto"**:
    
    *   ✅ It is extremely **Wealthy** (thanks to Geneva).
    *   ✅ It is extremely **Safe** and well-maintained.
    *   ⚠️ **BUT:** It is freezing out the middle class (teachers, nurses, service workers) who simply cannot afford to live here anymore.
    
    The territory is slowly turning into a luxury retirement home and a sleeping zone for wealthy commuters, losing its social diversity.
    """)

    # --- Section 3: Recommendation ---
    st.markdown("---")
    st.subheader("🚀 What Must Be Done?")
    
    st.warning("""
    **To fix this, we need a new strategy:**
    
    We cannot change geography (Geneva will always be there). But we **can** change how we build.
    
    The data proves that **building diverse housing (apartments, social housing, townhouses)** is the ONLY way to bring young families and essential workers back into the wealthy zones. 
    
    *   **If we do nothing:** The "Gravity" will continue to segregate the region.
    *   **If we build smart:** We can use the wealth from Geneva to build a balanced, vibrant community for everyone.
    """)
