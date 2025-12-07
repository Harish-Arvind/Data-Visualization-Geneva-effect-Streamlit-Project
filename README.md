# 🇫🇷 The Geneva Effect: A Socioeconomic Visualizer
> **"Does the rising tide lift all boats, or does gravity pull everything to the border?"**

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://data-visualization-geneva-effect-app-project-lq9abawy2pgrghcj2.streamlit.app)
[![GitHub](https://img.shields.io/badge/GitHub-Repo-181717?logo=github)](https://github.com/Harish-Arvind/Data-Visualization-Geneva-effect-Streamlit-Project)

## 🎯 Project Overview
This interactive dashboard analyzes the **socioeconomic fabric of the French-Swiss border** (2015-2019). Using granular INSEE Filosofi data, it tests the hypothesis of the **"Geneva Gravity"**—the idea that the massive salaries of Geneva create a "Wealth Cliff" that distorts local housing markets and segregates populations by age and income.

### 🔍 Key Findings (The 3 Laws)
Our data analysis reveals three structural forces shaping the territory:
1.  **Law #1: Distance Decay (The Wealth Cliff)**
    *   *Observation:* Income levels collapse by **50%** once you move >15km from the border.
    *   *Result:* A distinct "Frontalier Elite" belt vs. a rural periphery.
2.  **Law #2: Poverty Displacement (The Iron Curtain)**
    *   *Observation:* A strong **-0.65 correlation** between Wealth and Poverty.
    *   *Result:* High housing prices in the border zone effectively "filter out" low-income residents.
3.  **Law #3: The Demographic Lever (Housing = Youth)**
    *   *Observation:* A **+0.40 correlation** between New Housing and Youth population.
    *   *Result:* The only way to attract young families is to build; existing housing stock is aging rapidly.

---

## 💻 Dashboard Features
*   **🌍 Interactive 3D Map:** Explore the "topography of wealth" with a tiltable, extrudable map of all communes.
*   **� Pinpoint Analysis:** Filter the map to highlight specific communes (e.g., Sauverny, Archamps) and see their specific metrics.
*   **📈 Time-Series Trends:** Track the evolution of income, poverty, and housing from 2015 to 2019.
*   **� Dist-to-Geneva Calculator:** Automatic calculation of every commune's distance to the Swiss economic center.
*   **📊 Correlation Matrix:** A real-time "Truth Table" showing how variables (Social Housing, Income, Age) interact.

---

## 🛠️ Technical Stack
*   **Core:** Python 3.9+, Streamlit
*   **Data Processing:** Pandas, GeoPandas, Shapely
*   **Visualization:** Plotly Express, PyDeck (3D Maps), Folium
*   **Data Source:** [INSEE Filosofi (2015-2019)](https://www.data.gouv.fr/fr/datasets/revenus-pauvrete-et-niveau-de-vie-donnees-carroyees/)

## 🚀 Local Installation
1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Harish-Arvind/Data-Visualization-Geneva-effect-Streamlit-Project.git
    cd Data-Visualization-Geneva-effect-Streamlit-Project
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the App:**
    ```bash
    streamlit run app.py
    ```
    
---
**Author:** Harish EFREI | **Institution:** EFREI Paris Panthéon-Assas
