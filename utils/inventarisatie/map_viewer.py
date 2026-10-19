# utils/inventarisatie/map_viewer.py

import leafmap.foliumap as leafmap


def show_geometry_map(geojson, key="map_preview"):
    """Display geometry on a simple map."""
    m = leafmap.Map(draw_export=False)

    if geojson:
        m.add_geojson(geojson, layer_name="Geometrie")

    return m.to_streamlit(height=500, key=key)
