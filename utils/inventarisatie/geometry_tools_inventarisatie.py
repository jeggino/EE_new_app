from utils.geometry_tools import (
    draw_geometry,
    draw_geometry_with_existing
)

# Wrapper names for clarity in Inventarisatie page

def draw_inventarisatie_geometry(key="inv_map"):
    return draw_geometry(key=key)


def draw_inventarisatie_geometry_with_existing(existing_geojson=None, key="inv_edit_map"):
    return draw_geometry_with_existing(existing_geojson=existing_geojson, key=key)
