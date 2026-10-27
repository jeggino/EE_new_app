import folium
import geopandas as gpd
from shapely.geometry import Point, Polygon, MultiPolygon
from shapely.ops import transform
import pyproj
import base64
from branca.element import Element
from streamlit_folium import st_folium
from utils.supabase_client import supabase
import streamlit as st
import tempfile
import os

RD = "EPSG:28992"
WGS = "EPSG:4326"

project_to_rd = pyproj.Transformer.from_crs(WGS, RD, always_xy=True).transform
project_to_wgs = pyproj.Transformer.from_crs(RD, WGS, always_xy=True).transform


def flatten_geometry(gdf):
    def flatten(geom):
        if geom is None:
            return None
        if geom.has_z:
            if geom.geom_type == "Polygon":
                exterior = [(x, y) for (x, y, *_) in geom.exterior.coords]
                interiors = [
                    [(x, y) for (x, y, *_) in ring.coords]
                    for ring in geom.interiors
                ]
                return Polygon(exterior, interiors)
            elif geom.geom_type == "MultiPolygon":
                return MultiPolygon([flatten(p) for p in geom.geoms])
        return geom

    gdf["geometry"] = gdf["geometry"].apply(flatten)
    return gdf


# ---------------------------------------------------------
# CACHE NATURA2000 (load only once!)
# ---------------------------------------------------------
def load_n2000_cached():
    key = "cached_n2000_gdf"

    if key in st.session_state:
        return st.session_state[key]

    # Download from Supabase
    file_bytes = supabase.storage.from_("new_app").download(
        "quickscan/data/natura2000.gpkg"
    )

    # MUST write to temp file because GeoPandas cannot read bytes directly
    with tempfile.NamedTemporaryFile(delete=False, suffix=".gpkg") as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name

    gdf = gpd.read_file(tmp_path)
    os.remove(tmp_path)

    gdf = gdf.set_crs(RD, allow_override=True)
    gdf = flatten_geometry(gdf)

    st.session_state[key] = gdf
    return gdf

print("Natura2000 total rows:", len(n2000))
print("Natura2000 CRS:", n2000.crs)
print("Natura2000 geometry type:", n2000.geometry.iloc[0].geom_type)
print("Natura2000 columns:", n2000.columns)

# ---------------------------------------------------------
# STYLE FUNCTION FOR NATURA2000 COLORS
# ---------------------------------------------------------
def n2000_style(feature):
    t = feature["properties"].get("beschermin", "Unknown")

    colors = {
        "HR": "red",
        "VR": "purple",
        "VR+HR": "orange",
        "HR groeve": "darkred"
    }

    return {
        "color": colors.get(t, "gray"),
        "weight": 2,
        "fillColor": colors.get(t, "gray"),
        "fillOpacity": 0.3
    }


# ---------------------------------------------------------
# MAIN FUNCTION
# ---------------------------------------------------------
def voer_gis_analyse_natura2000(qs):

    # Load Quickscan polygon
    geometry_path = f"quickscan/geometries/{qs['id']}.geojson"
    data = supabase.storage.from_("new_app").download(geometry_path)
    qs_gdf = gpd.read_file(data).set_crs(WGS)

    # Centroid
    centroid = qs_gdf.geometry.centroid.iloc[0]
    lat = centroid.y
    lon = centroid.x

    # Convert centroid to RD
    x_rd, y_rd = transform(project_to_rd, Point(lon, lat)).coords[0]

    # Load cached Natura2000
    n2000 = load_n2000_cached()

    # Bounding box (10 km)
    bbox = Point(x_rd, y_rd).buffer(10000)
    n2000_filtered = n2000[n2000.intersects(bbox)]

    print("Aantal Natura2000 polygonen binnen 5 km:", len(n2000_filtered))

    # Convert to WGS
    n2000_wgs = n2000_filtered.to_crs(WGS)

    # Create 3 km buffer
    buffer_n2000 = Point(x_rd, y_rd).buffer(3000)
    buffer_n2000_wgs = transform(project_to_wgs, buffer_n2000)

    # Build map
    m = folium.Map(
        location=[lat, lon],
        zoom_start=11,
        control_scale=True,
        zoom_control=False,
        tiles="https://api.mapbox.com/styles/v1/jeggino/cmhdim6mj005g01s618ln55m2/tiles/256/{z}/{x}/{y}@2x?access_token=pk.eyJ1IjoiamVnZ2lubyIsImEiOiJjbHdscmRkZHAxMTl1MmlyeTJpb3Z2eHdzIn0.N9TRN7xxTikk235dVs1YeQ",
        attr="Mapbox"
    )

    layer_n2000 = folium.FeatureGroup(name="Natura2000", show=True)
    layer_buffers = folium.FeatureGroup(name="Buffers", show=True)

    # Add Natura2000 polygons
    for _, row in n2000_wgs.iterrows():
        folium.GeoJson(
            {
                "type": "Feature",
                "properties": {"beschermin": row.get("beschermin", "Unknown")},
                "geometry": row.geometry.__geo_interface__
            },
            style_function=n2000_style,
            tooltip=str(row.get("beschermin", "Unknown"))
        ).add_to(layer_n2000)

    # Add buffer
    folium.GeoJson(
        buffer_n2000_wgs,
        style_function=lambda x: {
            "color": "red",
            "weight": 2,
            "fillOpacity": 0.1
        },
        tooltip="3 km Natura2000 buffer"
    ).add_to(layer_buffers)

    # Add centroid marker
    folium.Marker(
        [lat, lon],
        popup="Centroid Quickscan",
        icon=folium.Icon(color="blue", icon="home", prefix="fa")
    ).add_to(m)

    layer_n2000.add_to(m)
    layer_buffers.add_to(m)

    # Legend
    legend_html = """
    <div style="
        position: fixed;
        top: 15px;
        left: 15px;
        width: 170px;
        background: rgba(255, 255, 255, 0.85);
        border: 1px solid #444;
        border-radius: 6px;
        padding: 8px;
        z-index: 9999;
        font-size: 12px;
        color: black;
    ">
    
    <b>Natura 2000 gebieden</b><br><br>
    
    <i class="fa fa-home" style="color: blue;"></i> Locatie<br><br>
    
    <span style="
        display:inline-block;
        width:12px;
        height:12px;
        background:red;
        border-radius:50%;
    "></span> HR<br>
    
    <span style="
        display:inline-block;
        width:12px;
        height:12px;
        background:purple;
        border-radius:50%;
    "></span> VR<br>
    
    <span style="
        display:inline-block;
        width:12px;
        height:12px;
        background:orange;
        border-radius:50%;
    "></span> VR+HR<br>
    
    <span style="
        display:inline-block;
        width:12px;
        height:12px;
        background:darkred;
        border-radius:50%;
    "></span> HR groeve<br>
    
    </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))

    # Logo
    logo_path = "utils/pictures/pngwing.com.png"
    with open(logo_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()

    logo_html = f"""
    <div id="map-logo" style="
        position: fixed;
        top: 15px;
        right: 15px;
        z-index: 999999;
        background: rgba(255,255,255,0.7);
        padding: 6px;
        border-radius: 8px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.25);
    ">
        <img src="data:image/jpeg;base64,{encoded}" style="width:55px;">
    </div>
    """
    m.get_root().html.add_child(Element(logo_html))

    # Display in Streamlit
    st_folium(m, width=700, height=500, returned_objects=[])

