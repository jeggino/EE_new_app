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

    tiles = 'https://api.mapbox.com/styles/v1/jeggino/cmn7ms1u3001f01pl691k0eyu/tiles/256/{z}/{x}/{y}@2x?access_token=pk.eyJ1IjoiamVnZ2lubyIsImEiOiJjbHdscmRkZHAxMTl1MmlyeTJpb3Z2eHdzIn0.N9TRN7xxTikk235dVs1YeQ'
    folium.TileLayer(tiles=tiles,
                     attr='XXX Mapbox Attribution',
                         max_zoom=24,
        max_native_zoom=22,
        overlay=False,
        control=False,name="OpenStreetMap").add_to(m)
    
    
    # Satellite
    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attr="Esri",
        name="Satellite",
        max_native_zoom=21,
        max_zoom=21,
        overlay=False,
        control=False
    ).add_to(m)

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


def draw_geometry_with_existing(existing_geojson=None, key="map"):

    if "last_drawings" not in st.session_state:
        st.session_state.last_drawings = None

    if "confirm_multipolygon" not in st.session_state:
        st.session_state.confirm_multipolygon = False

    # Default map center
    center = [52.37, 4.90]
    zoom = 12

    # If old geometry exists, compute a better center
    if existing_geojson:
        try:
            coords = existing_geojson["geometry"]["coordinates"]

            # Handle Polygon vs MultiPolygon
            if existing_geojson["geometry"]["type"] == "Polygon":
                flat = coords[0]
            else:
                flat = coords[0][0]

            # Compute center
            lats = [p[1] for p in flat]
            lngs = [p[0] for p in flat]
            center = [sum(lats)/len(lats), sum(lngs)/len(lngs)]
            zoom = 14
        except:
            pass

    m = folium.Map(location=center, zoom_start=zoom, zoom_control=False)

    tiles = 'https://api.mapbox.com/styles/v1/jeggino/cmn7ms1u3001f01pl691k0eyu/tiles/256/{z}/{x}/{y}@2x?access_token=pk.eyJ1IjoiamVnZ2lubyIsImEiOiJjbHdscmRkZHAxMTl1MmlyeTJpb3Z2eHdzIn0.N9TRN7xxTikk235dVs1YeQ'
    folium.TileLayer(tiles=tiles,
                     attr='XXX Mapbox Attribution',
                         max_zoom=24,
        max_native_zoom=22,
        overlay=False,
        control=False,name="OpenStreetMap").add_to(m)
    
    
    # Satellite
    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attr="Esri",
        name="Satellite",
        max_native_zoom=21,
        max_zoom=21,
        overlay=False,
        control=False
    ).add_to(m)

    # Draw old geometry in red
    if existing_geojson:
        folium.GeoJson(
            existing_geojson,
            name="Old Geometry",
            style_function=lambda x: {
                "color": "red",
                "weight": 3,
                "fillColor": "red",
                "fillOpacity": 0.2,
            },
        ).add_to(m)

    # Drawing tools for new geometry
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

