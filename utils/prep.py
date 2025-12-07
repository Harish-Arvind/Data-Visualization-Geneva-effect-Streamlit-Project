import numpy as np
import pandas as pd
import geopandas as gpd
import streamlit as st

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

def process_tiles(df):
    """Pre-process tile data (convert strings to numeric)."""
    df = df.copy()
    
    # Extensive list of potential columns from 2015-2019 datasets
    cols_to_numeric = [
        'ind', 'men', 'men_pauv', 'men_prop', 'log_soc', 'ind_snv',
        # Demographics
        'ind_0_3', 'ind_4_5', 'ind_6_10', 'ind_11_17', 'ind_18_24', 
        'ind_25_39', 'ind_40_54', 'ind_55_64', 'ind_65_79', 'ind_80p',
        # Housing
        'log_av45', 'log_45_70', 'log_70_90', 'log_ap90', 'log_inc',
        'men_mais', 'men_coll',
        # Family
        'men_1ind', 'men_5ind', 'men_fmp'
    ]
    
    for c in cols_to_numeric:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)
            
    return df

@st.cache_data(show_spinner="Aggregating Granular Data...")
def make_tables(_tiles_data, _communes_gdf):
    """
    Process all years, aggregate to commune level, and calculate derived metrics.
    Args:
        _tiles_data (dict): {year: gdf}
        _communes_gdf (gdf): Communes geometries
    Returns:
        dict: {'timeseries': df, 'by_region': df, 'geo': gdf}
    """
    processed_frames = []
    
    # Identify commune code column in communes_gdf upfront
    commune_key = next((c for c in ['insee', 'insee_com', 'code_insee', 'com', 'code'] if c in _communes_gdf.columns), None)
    if not commune_key:
        st.error("Could not find commune code column.")
        return {}
    
    # Columns to preserve during aggregation (Must sum these up)
    sum_cols = [
        'ind', 'men', 'men_pauv', 'men_prop', 'log_soc', 'pop_income',
        'ind_0_3', 'ind_4_5', 'ind_6_10', 'ind_11_17', 'ind_18_24', 
        'ind_25_39', 'ind_40_54', 'ind_55_64', 'ind_65_79', 'ind_80p',
        'log_av45', 'log_45_70', 'log_70_90', 'log_ap90', 'log_inc',
        'men_mais', 'men_coll', 'men_1ind', 'men_5ind', 'men_fmp'
    ]

    for year, gdf in _tiles_data.items():
        processed = process_tiles(gdf)
        processed['year'] = year
        
        # --- Handle missing 'lcog_geo' (2015 case) ---
        if 'lcog_geo' not in processed.columns:
            with st.spinner(f"Mapping {year} data to communes (Spatial Join)..."):
                # Use centroids to assign grid to commune
                # Ensure correct CRS
                if processed.crs != _communes_gdf.crs:
                    processed = processed.to_crs(_communes_gdf.crs)
                
                # Warning: Sjoin can be slow. Use centroids.
                centroids = processed.copy()
                centroids['geometry'] = centroids.geometry.centroid
                
                # Sjoin with commune boundaries
                # Keep only necessary cols from communes to speed up?
                communes_simple = _communes_gdf[[commune_key, 'geometry']]
                
                joined = gpd.sjoin(centroids, communes_simple, how='left', predicate='within')
                processed['lcog_geo'] = joined[commune_key]
                
                # Drop rows that didn't match a commune
                processed = processed.dropna(subset=['lcog_geo'])

        # Calculate weighted income for later aggregation
        if 'avg_income' not in processed.columns and 'ind_snv' in processed.columns:
             processed['pop_income'] = processed['ind_snv'] 
        elif 'avg_income' in processed.columns:
             processed['pop_income'] = processed['avg_income'] * processed['ind']
        else:
             processed['pop_income'] = 0

        # Filter cols that exist
        current_sum_cols = [c for c in sum_cols if c in processed.columns]
        
        # Keep only necessary columns + location + year
        cols = ['year', 'lcog_geo'] + current_sum_cols
        processed_frames.append(processed[cols])
        
    if not processed_frames:
        return {}
        
    full_df = pd.concat(processed_frames, ignore_index=True)

    # Aggregation Dictionary
    agg_dict = {c: 'sum' for c in full_df.columns if c not in ['year', 'lcog_geo']}
    
    # Group by Year and Commune
    grouped = full_df.groupby(['year', 'lcog_geo']).agg(agg_dict).reset_index()
    
    # --- Feature Engineering: The Geneva Gravity ---
    # Geneva Coordinates (approx center)
    GENEVA_LAT = 46.2044
    GENEVA_LON = 6.1432
    
    # We need the geometry of the commune to calculate distance
    # Merge geometries back first (using centroids for speed)
    if 'geometry' not in grouped.columns:
        # Get centroids from original communes_gdf
        commune_centroids = _communes_gdf[[commune_key, 'geometry']].copy()
        # Ensure we are in a metric CRS for distance (Lambert-93 is standard for France: EPSG:2154)
        if commune_centroids.crs and commune_centroids.crs.to_string() != "EPSG:2154":
             try:
                 commune_centroids = commune_centroids.to_crs(epsg=2154)
             except:
                 pass # Fallback
        
        commune_centroids['centroid'] = commune_centroids.geometry.centroid
        
        # Geneva Point in EPSG:2154
        from shapely.geometry import Point
        geneva_pt = gpd.GeoSeries([Point(GENEVA_LON, GENEVA_LAT)], crs="EPSG:4326").to_crs(commune_centroids.crs).iloc[0]
        
        # Calculate Distance (in km)
        commune_centroids['dist_geneva_km'] = commune_centroids['centroid'].distance(geneva_pt) / 1000.0
        
        # Merge distance into grouped
        grouped = grouped.merge(commune_centroids[[commune_key, 'dist_geneva_km']], left_on='lcog_geo', right_on=commune_key, how='left')
    
    # --- Feature Engineering (Derived Metrics) ---
    
    # 1. Standard Metrics
    grouped['total_pop'] = grouped['ind']
    grouped['total_households'] = grouped['men']
    grouped['avg_income'] = safe_divide(grouped['pop_income'], grouped['ind'])
    grouped['poverty_rate'] = safe_divide(grouped['men_pauv'], grouped['men']) * 100
    grouped['ownership_rate'] = safe_divide(grouped['men_prop'], grouped['men']) * 100
    
    # 2. Demographics
    df = grouped # Alias for brevity
    
    # Sum age bands if available
    youth_cols = ['ind_0_3', 'ind_4_5', 'ind_6_10', 'ind_11_17']
    senior_cols = ['ind_65_79', 'ind_80p']
    working_cols = ['ind_18_24', 'ind_25_39', 'ind_40_54', 'ind_55_64']
    
    df['pop_youth'] = df[[c for c in youth_cols if c in df.columns]].sum(axis=1)
    df['pop_senior'] = df[[c for c in senior_cols if c in df.columns]].sum(axis=1)
    df['pop_working'] = df[[c for c in working_cols if c in df.columns]].sum(axis=1)
    
    df['youth_pct'] = safe_divide(df['pop_youth'], df['ind']) * 100
    df['senior_pct'] = safe_divide(df['pop_senior'], df['ind']) * 100
    
    # 3. Family Structure
    if 'men_fmp' in df.columns:
        df['single_parent_pct'] = safe_divide(df['men_fmp'], df['men']) * 100
    if 'men_1ind' in df.columns:
        df['single_person_pct'] = safe_divide(df['men_1ind'], df['men']) * 100
        
    # 4. Housing Stock
    housing_eras = ['log_av45', 'log_45_70', 'log_70_90', 'log_ap90', 'log_inc']
    existing_eras = [c for c in housing_eras if c in df.columns]
    
    # Total estimated housings (sum of eras) - might defer from 'men' slightly
    df['total_housing_est'] = df[existing_eras].sum(axis=1)
    
    # Use total_housing_est as denominator for housing eras
    if 'log_av45' in df.columns:
        df['old_housing_pct'] = safe_divide(df['log_av45'], df['total_housing_est']) * 100
    if 'log_ap90' in df.columns:
        df['new_housing_pct'] = safe_divide(df['log_ap90'], df['total_housing_est']) * 100
        
    # Social housing density
    if 'log_soc' in df.columns:
        # Use total housing estimate if valid, else 'men'
        denom = np.where(df['total_housing_est'] > 0, df['total_housing_est'], df['men'])
        df['social_housing_rate'] = safe_divide(df['log_soc'], denom) * 100

    # 5. Housing Type (Maison vs Coll)
    if 'men_mais' in df.columns and 'men_coll' in df.columns:
        # Denom is sum of these two usually ~ men
        denom_type = df['men_mais'] + df['men_coll']
        df['houses_pct'] = safe_divide(df['men_mais'], denom_type) * 100
        df['apartments_pct'] = safe_divide(df['men_coll'], denom_type) * 100

    # Clean up infinities/NaNs in rates
    rate_cols = [c for c in df.columns if 'rate' in c or 'pct' in c]
    df[rate_cols] = df[rate_cols].fillna(0).clip(0, 100)

    # --- Output Tables ---
    
    # Timeseries (National) - Aggregating using sum of sums, then recalc ratios
    # We can just sum the raw columns again for national level then recalc
    national_sum_cols = [c for c in agg_dict.keys() if c in df.columns]
    timeseries = df.groupby('year')[national_sum_cols].sum().reset_index()
    
    # Re-apply Ratio logic for National Level (Copy-paste logic essentially)
    # 1. Standard
    timeseries['total_pop'] = timeseries['ind']
    timeseries['avg_income'] = safe_divide(timeseries['pop_income'], timeseries['ind'])
    timeseries['poverty_rate'] = safe_divide(timeseries['men_pauv'], timeseries['men']) * 100
    timeseries['ownership_rate'] = safe_divide(timeseries['men_prop'], timeseries['men']) * 100
    
    # 2. Demographics
    timeseries['pop_youth'] = timeseries[[c for c in youth_cols if c in timeseries.columns]].sum(axis=1)
    timeseries['pop_senior'] = timeseries[[c for c in senior_cols if c in timeseries.columns]].sum(axis=1)
    timeseries['youth_pct'] = safe_divide(timeseries['pop_youth'], timeseries['ind']) * 100
    timeseries['senior_pct'] = safe_divide(timeseries['pop_senior'], timeseries['ind']) * 100
    
    # 3. Family
    if 'men_fmp' in timeseries.columns:
        timeseries['single_parent_pct'] = safe_divide(timeseries['men_fmp'], timeseries['men']) * 100
    
    # Missing from previous aggregation
    if 'log_soc' in timeseries.columns:
        # National approximate
        timeseries['social_housing_rate'] = safe_divide(timeseries['log_soc'], timeseries['men']) * 100
        
    # 4. Housing Stock (National)
    eras = ['log_av45', 'log_ap90']
    timeseries['total_housing_est'] = timeseries[[c for c in housing_eras if c in timeseries.columns]].sum(axis=1)
    
    if 'log_av45' in timeseries.columns:
        timeseries['old_housing_pct'] = safe_divide(timeseries['log_av45'], timeseries['total_housing_est']) * 100
    if 'log_ap90' in timeseries.columns:
        timeseries['new_housing_pct'] = safe_divide(timeseries['log_ap90'], timeseries['total_housing_est']) * 100
        
    if 'men_mais' in timeseries.columns and 'men_coll' in timeseries.columns:
        denom = timeseries['men_mais'] + timeseries['men_coll']
        timeseries['houses_pct'] = safe_divide(timeseries['men_mais'], denom) * 100
        timeseries['apartments_pct'] = safe_divide(timeseries['men_coll'], denom) * 100
        
    # By Region (Commune Level)
    name_key = next((c for c in ['nom', 'nom_com', 'nom_comm', 'libelle'] if c in _communes_gdf.columns), None)
    cols_to_keep = [commune_key]
    if name_key:
        cols_to_keep.append(name_key)
        
    by_region = df.merge(_communes_gdf[cols_to_keep], left_on='lcog_geo', right_on=commune_key, how='inner')
    by_region['nom'] = by_region[name_key] if name_key else by_region[commune_key]
        
    # Geo (Latest Year)
    latest_year = max(_tiles_data.keys())
    latest_data = df[df['year'] == latest_year]
    geo = _communes_gdf.merge(latest_data, left_on=commune_key, right_on='lcog_geo', how='inner')
    # Optimize geometry for web rendering
    # If CRS is metric (e.g. Lambert-93), 100-500m tolerance is good.
    # If CRS is broad (WGS84), 0.001-0.01 is good.
    # We'll use a dynamic simplistic approach or just a stronger value.
    try:
        geo['geometry'] = geo.geometry.simplify(tolerance=200 if geo.crs and "meter" in geo.crs.axis_info[0].unit_name else 0.005)
    except:
        # Fallback if CRS check fails
        geo['geometry'] = geo.geometry.simplify(0.01)
    
    return {
        "timeseries": timeseries,
        "by_region": by_region,
        "geo": geo,
        "raw_grouped": df
    }

def get_commune_comparison(df, commune_names, metrics):
    """Get comparison data for specific communes."""
    if not commune_names:
        return pd.DataFrame()
    # Ensure metrics exist in df columns
    valid_metrics = [m for m in metrics if m in df.columns]
    return df[df['nom'].isin(commune_names)][['nom', 'year'] + valid_metrics]
