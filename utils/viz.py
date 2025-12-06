import plotly.express as px
import plotly.graph_objects as go
import folium
from folium.features import GeoJsonTooltip
from streamlit_folium import st_folium
import streamlit as st
import pandas as pd

# --- Design System & Constants ---
THEME_COLORS = {
    "primary": "#3B82F6",    # Blue
    "secondary": "#10B981",  # Emerald
    "accent": "#8B5CF6",     # Violet
    "background": "#F8FAFC", # Slate-50
    "text": "#1E293B",       # Slate-800
    "grid": "#E2E8F0"        # Slate-200
}

COLOR_SCALES = {
    "avg_income": "Blues",
    "poverty_rate": "Reds",
    "ownership_rate": "Greens",
    "social_housing_rate": "Purples",
    "youth_pct": "YlOrRd",      # Sunset -> YlOrRd
    "senior_pct": "YlOrBr",     # OrYl -> YlOrBr
    "old_housing_pct": "Oranges", # Copper -> Oranges
    "new_housing_pct": "PuBuGn"   # Teal -> PuBuGn
}

def _apply_layout(fig, title, x_title, y_title):
    """Apply consistent styling to Plotly figures."""
    fig.update_layout(
        title=title,
        xaxis_title=x_title,
        yaxis_title=y_title,
        margin=dict(l=0, r=0, t=50, b=0),
        hovermode="x unified"
    )
    return fig

def format_metric_label(metric):
    """Helper to format metric names."""
    return metric.replace("_", " ").title()

def line_chart(data, metric, title=None):
    """Plot trends over time with area fill."""
    if data.empty:
        st.warning("No data available for trends.")
        return

    label = format_metric_label(metric)
    formatted_title = title or f"Evolution of {label} (2015-2019)"
    
    # Check if we have multiple groups (e.g. Regions) or just one aggregate
    if 'nom' in data.columns and data['nom'].nunique() > 1:
        fig = px.line(
            data, 
            x="year", 
            y=metric, 
            color='nom',
            markers=True,
            color_discrete_sequence=px.colors.qualitative.Prism
        )
    else:
        fig = px.area(
            data, 
            x="year", 
            y=metric, 
            markers=True,
            color_discrete_sequence=[THEME_COLORS["primary"]]
        )

    fig = _apply_layout(fig, formatted_title, "Year", label)
    fig.update_layout(xaxis=dict(tickmode='linear', tick0=2015, dtick=2))
    st.plotly_chart(fig, use_container_width=True)

def bar_chart(data, metric, top_n=10, orientation='v', year=None):
    """Plot comparison of entities."""
    if data.empty:
        st.warning("No data available for comparison.")
        return

    label = format_metric_label(metric)
    
    # Sort
    data = data.sort_values(metric, ascending=True if orientation=='h' else False).head(top_n)
    
    title = f"Top {top_n} Communes by {label}"
    if year:
        title += f" ({year})"
    
    if orientation == 'h':
        x_col, y_col = metric, "nom"
        x_title, y_title = label, "Commune"
    else:
        x_col, y_col = "nom", metric
        x_title, y_title = "Commune", label

    fig = px.bar(
        data,
        x=x_col,
        y=y_col,
        orientation=orientation,
        text_auto='.2s',
        color=metric,
        color_continuous_scale=COLOR_SCALES.get(metric, "Viridis")
    )
    
    fig = _apply_layout(fig, title, x_title, y_title)
    fig.update_coloraxes(showscale=False)
    st.plotly_chart(fig, use_container_width=True)

def distribution_chart(data, metric, year=None, ref_value=None, ref_label="Avg"):
    """Plot distribution histogram with optional reference line."""
    label = format_metric_label(metric)
    title = f"Distribution of {label}"
    if year:
        title += f" ({year})"
        
    fig = px.histogram(
        data, 
        x=metric,
        nbins=30,
        color_discrete_sequence=[THEME_COLORS["accent"]],
        marginal="box",
        title=title
    )
    
    if ref_value is not None:
        fig.add_vline(
            x=ref_value, 
            line_dash="dash", 
            line_color="white", 
            annotation_text=f" {ref_label}: {ref_value:,.0f}", 
            annotation_position="top right"
        )
        
    fig = _apply_layout(fig, title, label, "Count")
    st.plotly_chart(fig, use_container_width=True)

def correlation_matrix(data, metrics, year=None):
    """Plot correlation heatmap."""
    if len(metrics) < 2:
        st.warning("Need at least 2 metrics for correlation.")
        return

    corr = data[metrics].corr()
    
    title = "Correlation Matrix"
    if year:
        title += f" ({year})"
    
    fig = px.imshow(
        corr,
        text_auto=".2f",
        aspect="auto",
        color_continuous_scale="RdBu_r",
        title=title
    )
    fig = _apply_layout(fig, title, "", "")
    st.plotly_chart(fig, use_container_width=True)

def scatter_plot(data, x, y, size=None, hover_name="nom", year=None):
    """Plot interaction between two metrics."""
    title = f"{format_metric_label(x)} vs {format_metric_label(y)}"
    if year:
        title += f" ({year})"
        
    fig = px.scatter(
        data,
        x=x,
        y=y,
        size=size,
        hover_name=hover_name,
        color=y,
        color_continuous_scale="Viridis",
        title=title
    )
    fig = _apply_layout(fig, title, format_metric_label(x), format_metric_label(y))
    st.plotly_chart(fig, use_container_width=True)

def population_pyramid(data, year=None):
    """Plot age structure."""
    if data.empty: return
    
    # We expect aggregated sums of these columns
    age_cols = ['ind_0_3', 'ind_4_5', 'ind_6_10', 'ind_11_17', 'ind_18_24',
                'ind_25_39', 'ind_40_54', 'ind_55_64', 'ind_65_79', 'ind_80p']
    
    # Check existence
    existing = [c for c in age_cols if c in data.columns]
    if not existing: 
        st.warning("Demographic data missing.")
        return
        
    # Sum up for the selection (usually single commune or national sum)
    # If data has multiple rows, we sum them
    totals = data[existing].sum().reset_index()
    totals.columns = ['Age Group', 'Population']
    
    # Clean up labels
    totals['Age Group'] = totals['Age Group'].str.replace('ind_', '').str.replace('_', '-')
    
    title = "Demographic Profile"
    if year:
        title += f" ({year})"
    
    fig = px.bar(
        totals,
        x='Age Group', 
        y='Population',
        color='Population',
        color_continuous_scale='Burg'
    )
    fig = _apply_layout(fig, title, "Age Group", "Population")
    st.plotly_chart(fig, use_container_width=True)

def housing_mix_chart(data, year=None):
    """Plot housing construction eras."""
    eras = ['log_av45', 'log_45_70', 'log_70_90', 'log_ap90', 'log_inc']
    existing = [c for c in eras if c in data.columns]
    
    if not existing: return
    
    totals = data[existing].sum().reset_index()
    totals.columns = ['Construction Era', 'Count']
    
    # Better labels
    labels = {
        'log_av45': 'Pre-1945',
        'log_45_70': '1945-1970',
        'log_70_90': '1970-1990',
        'log_ap90': 'Post-1990',
        'log_inc': 'Unknown'
    }
    totals['Construction Era'] = totals['Construction Era'].map(labels)
    
    title = "Housing Age Mix"
    if year:
        title += f" ({year})"
    
    fig = px.pie(
        totals,
        names='Construction Era',
        values='Count',
        hole=0.4,
        color_discrete_sequence=px.colors.sequential.Teal
    )
    fig.update_layout(title=title)
    st.plotly_chart(fig, use_container_width=True)

import pydeck as pdk

# ... (previous functions)

@st.cache_data(show_spinner=True)
def _prepare_3d_data(geo_data, metric):
    """
    Preprocess geo_data for 3D mapping. 
    Handles expensive CRS reprojection, color calculation, and serialization once per metric.
    """
    # 1. Coordinate Magnitude Check
    bounds = geo_data.total_bounds
    is_projected_coords = (bounds[0] > 360 or bounds[1] > 360) 

    try:
        if is_projected_coords:
            geo_data_fixed = geo_data.copy()
            geo_data_fixed.set_crs(epsg=2154, allow_override=True, inplace=True)
            geo_data_proj = geo_data_fixed.to_crs(epsg=4326)
        elif geo_data.crs and geo_data.crs.to_string() != "EPSG:4326":
            geo_data_proj = geo_data.to_crs(epsg=4326)
        else:
            geo_data_proj = geo_data.copy()
    except Exception as e:
        st.error(f"CRS Visualization Error: {e}")
        return None, None, None, None

    # Calculate Center
    bounds_proj = geo_data_proj.total_bounds
    center_lat = (bounds_proj[1] + bounds_proj[3]) / 2
    center_lon = (bounds_proj[0] + bounds_proj[2]) / 2

    # Normalize metric for coloring
    min_val = geo_data_proj[metric].min()
    max_val = geo_data_proj[metric].max()

    # Optimized color calculation
    def get_color(val):
        norm = (val - min_val) / (max_val - min_val) if max_val > min_val else 0
        r = 220 - int(norm * (220 - 8))
        g = 240 - int(norm * (240 - 48))
        b = 255 - int(norm * (255 - 107))
        return [r, g, b, 160] # Alpha 160
    
    geo_data_proj['fill_color'] = geo_data_proj[metric].apply(get_color)

    # Pre-calculate formatted values
    if "income" in metric:
        geo_data_proj["formatted_val"] = geo_data_proj[metric].apply(lambda x: f"{x:,.0f} €")
    elif "rate" in metric or "pct" in metric:
        geo_data_proj["formatted_val"] = geo_data_proj[metric].apply(lambda x: f"{x:.1f}%")
    else:
        geo_data_proj["formatted_val"] = geo_data_proj[metric].astype(str)

    # Return geo structure via __geo_interface__ for maximum speed (cached)
    return geo_data_proj.__geo_interface__, center_lat, center_lon, max_val

def map_chart_3d(geo_data, metric="avg_income", opacity=0.8, height=500):
    """Render a 3D Tilted Map using PyDeck."""
    if geo_data is None or geo_data.empty:
        st.warning("No geographic data available.")
        return

    # Use cached data preparation
    geo_data_dict, center_lat, center_lon, max_val = _prepare_3d_data(geo_data, metric)
    
    if geo_data_dict is None:
        return

    label = format_metric_label(metric)
    
    # Define Layer using GeoJSON Interface
    geojson_layer = pdk.Layer(
        "GeoJsonLayer",
        data=geo_data_dict, 
        opacity=opacity,
        stroked=True,
        filled=True,
        extruded=True,
        wireframe=True,
        get_elevation=f"properties.{metric}",
        elevation_scale=10 if max_val < 1000 else 0.1,
        get_fill_color="properties.fill_color",
        get_line_color=[255, 255, 255],
        get_line_width=10,
        pickable=True,
        auto_highlight=True,
    )

    # Set View
    view_state = pdk.ViewState(
        latitude=center_lat,
        longitude=center_lon,
        zoom=9,
        pitch=45,
        bearing=0
    )

    # Render
    r = pdk.Deck(
        layers=[geojson_layer],
        initial_view_state=view_state,
        tooltip={"text": "{nom}\n" + label + ": {formatted_val}"},
        map_style="light",
    )
    
    st.pydeck_chart(r, use_container_width=True, height=height)

