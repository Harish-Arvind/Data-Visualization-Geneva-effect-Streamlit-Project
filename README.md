# 🇫🇷 The Hidden Geography of Wealth
> An interactive Streamlit dashboard exploring socioeconomic inequalities in France (2015-2019) using granular INSEE Filosofi data.

## 📋 Project Overview
This tool allows researchers and policymakers to visualize:
- **Income & Poverty** distribution at the commune level.
- **Housing dynamics** (social housing, ownership).
- **Demographic shifts** (rejuvenation vs. aging).
- **The "Geneva Effect":** How the Swiss border reshapes local wealth.

## 🛠️ Setup & Installation
**(Requirement: Python 3.9+)**

1.  **Clone the repository:**
    ```bash
    git clone <repo-url>
    cd <repo-name>
    ```

2.  **Create a virtual environment:**
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # Mac/Linux
    # .venv\Scripts\activate   # Windows
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## 🚀 How to Run
Execute the following command in your terminal:
```bash
streamlit run app.py
```
The app will open in your browser at `http://localhost:8501`.

## 📂 Data Sources
All data is sourced from **INSEE (Institut national de la statistique et des études économiques)** via data.gouv.fr.

*   **Dataset:** [Revenus, pauvreté et niveau de vie en 2015-2019 (Dispositif Fichier localisé social et fiscal - Filosofi)](https://www.data.gouv.fr/fr/datasets/revenus-pauvrete-et-niveau-de-vie-donnees-carroyees/)
*   **Format:** The app expects GeoPackage (`.gpkg`) files in the `data/` directory.

**Required Files Structure:**
```
data/
├── Filosofi2015_carreaux_1000m_metropole.gpkg
├── Filosofi2017_carreaux_1km_met.gpkg
├── carreaux_1km_met.gpkg  (2019 data)
└── communes2020.gpkg      (Geometries)
```

## 🧪 Methodology & Quality
*   **Aggregation:** 1km grid tiles are spatially joined to commune centroids.
*   **Privacy:** Aggregated metrics protect individual anonymity.
*   **Imputation:** Sparse demographic counts are filled with 0.

## 📜 License
Code is MIT Licensed. Data is Open License (Etalab/INSEE).
