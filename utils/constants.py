
import os

# --- Data Configuration ---
DATA_DIR = "data"

# File names
FILES = {
    2015: "Filosofi2015_carreaux_1000m_metropole.gpkg",
    2017: "Filosofi2017_carreaux_1km_met.gpkg",
    2019: "carreaux_1km_met.gpkg"
}
COMMUNES_FILE = "communes2020.gpkg"
CACHE_FILE = os.path.join(DATA_DIR, "processed_metrics_cache.pkl")

# Data URLs (for download script)
DATA_URLS = {
    "Filosofi2015": "https://www.insee.fr/fr/statistiques/fichier/4176293/Filosofi2015_carreaux_1000m_gpkg.zip",
    "Filosofi2017": "https://www.insee.fr/fr/statistiques/fichier/6215140/Filosofi2017_carreaux_1km_gpkg.zip",
    "Filosofi2019": "https://www.insee.fr/fr/statistiques/fichier/7655464/Filosofi2019_carreaux_1km_gpkg.zip",
    "Communes": "https://raw.githubusercontent.com/gregoiredavid/france-geojson/master/communes.geojson"
}

# --- App Configuration ---
PAGE_TITLE = "France Wealth Geography"
PAGE_ICON = "🇫🇷"

# --- Analysis Constants ---
AVAILABLE_YEARS = [2015, 2017, 2019]
DEFAULT_YEAR = 2019

# Metrics
METRICS = [
    "avg_income", "poverty_rate", "ownership_rate", "social_housing_rate",
    "youth_pct", "senior_pct", "single_parent_pct", 
    "old_housing_pct", "new_housing_pct", "houses_pct", "apartments_pct"
]

# Formatting
METRIC_LABELS = {m: m.replace("_", " ").title() for m in METRICS}
