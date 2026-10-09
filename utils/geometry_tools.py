import streamlit as st
from streamlit_folium import st_folium
import folium
from folium.plugins import Draw, Fullscreen, Geocoder

def draw_geometry(key="map"):

    if "last_drawings" not in st.session_state:
        st.session_state.last_drawings = None

    if "confirm_multipolygon" not in st.session_state:
        st.session_state.confirm_multipolygon = False

    m = folium.Map(location=[52.37, 4.90], zoom_start=12,zoom_control=False)

    Draw(
        draw_options={
            "polyline": False,
            "polygon": True,
            "circle": False,
            "rectangle": False,
            "marker": False,
            "circlemarker": False
        },
        edit_options={"edit": False, "remove": True},
    ).add_to(m)


    Fullscreen().add_to(m)
    Geocoder(add_marker=True).add_to(m)

    map_data = st_folium(m, height=500, use_container_width=True, key=key)

    if map_data and "all_drawings" in map_data:
        st.session_state.last_drawings = map_data["all_drawings"]

    if not st.session_state.last_drawings:
        return None

    polygons = []
    for d in st.session_state.last_drawings:
        geom = d.get("geometry", {})
        if geom.get("type") == "Polygon":
            polygons.append(geom["coordinates"])
        elif geom.get("type") == "MultiPolygon":
            polygons.extend(geom["coordinates"])

    if len(polygons) > 1:
        if not st.session_state.confirm_multipolygon:
            st.warning("Je hebt meerdere polygonen getekend. Dit wordt opgeslagen als een MultiPolygon.")

            if st.button("Opslaan als MultiPolygon"):
                st.session_state.confirm_multipolygon = True
                st.rerun()
            else:
                st.stop()

        return {
            "type": "Feature",
            "geometry": {"type": "MultiPolygon", "coordinates": polygons}
        }

    return {
        "type": "Feature",
        "geometry": {"type": "Polygon", "coordinates": polygons[0]}
    }
