import json
import streamlit as st
from utils.supabase_client import supabase, BUCKET

def save_quickscan(name, description, geojson):

    if not geojson:
        st.error("Teken eerst een geometrie.")
        st.stop()

    safe_name = name.replace(" ", "_")
    filename = f"quickscan/geometries/{safe_name}.geojson"

    supabase.storage.from_(BUCKET).upload(
        filename,
        json.dumps(geojson).encode("utf-8"),
        file_options={"content-type": "application/geo+json", "x-upsert": "true"}
    )

    supabase.table("new_app_quickscan").insert({
        "name": safe_name,
        "description": description,
        "geometry_path": filename
    }).execute()
