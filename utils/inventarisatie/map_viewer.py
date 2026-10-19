# utils/inventarisatie/map_viewer.py

import folium
from streamlit_folium import st_folium


def show_geometry_map(geojson, key="map_preview"):
    """Display geometry on a simple Folium map using st_folium."""

    # Default center (Amsterdam)
    center = [52.37, 4.90]
    zoom = 12

    # If geometry exists → compute center
    if geojson:
        try:
            coords = geojson["geometry"]["coordinates"]

            if geojson["geometry"]["type"] == "Polygon":
                flat = coords[0]
            else:  # MultiPolygon
                flat = coords[0][0]

            lats = [p[1] for p in flat]
            lngs = [p[0] for p in flat]
            center = [sum(lats) / len(lats), sum(lngs) / len(lngs)]
            zoom = 14
        except Exception:
            pass

    # Create map
    m = folium.Map(location=center, zoom_start=zoom, zoom_control=True)

    # Add geometry layer
    if geojson:
        folium.GeoJson(
            geojson,
            name="Geometrie",
            style_function=lambda x: {
                "color": "blue",
                "weight": 3,
                "fillColor": "blue",
                "fillOpacity": 0.2,
            },
        ).add_to(m)

    # Render map
    st_folium(m, height=500, use_container_width=True, key=key)
