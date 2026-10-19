# utils/inventarisatie/load_inventarisatie.py

import json
from utils.supabase_client import supabase


def load_inventarisatie(project_id: str):
    """Load metadata + geometry for an Inventarisatie project."""

    # Load metadata
    try:
        resp = supabase.table("new_app_inventarisatie") \
            .select("*") \
            .eq("id", project_id) \
            .single() \
            .execute()
    except Exception as e:
        return None, f"Database error: {e}"

    data = resp.data
    if not data:
        return None, "Project niet gevonden."

    # Load geometry file
    try:
        path = f"inventarisatie/geometries/{project_id}.json"
        geo_bytes = supabase.storage.from_("new_app").download(path)
        geometry = json.loads(geo_bytes.decode("utf-8"))
    except Exception:
        geometry = None  # geometry may not exist

    return {"metadata": data, "geometry": geometry}, None

