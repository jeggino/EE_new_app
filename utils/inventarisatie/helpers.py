# utils/inventarisatie/helpers.py

from utils.supabase_client import supabase
import json


def get_full_name(email: str) -> str:
    """Return full name for a given employee email."""
    resp = supabase.table("new_app_employees") \
        .select("volledige_naam") \
        .eq("email", email) \
        .single() \
        .execute()

    return resp.data["volledige_naam"] if resp.data else email


def load_geometry(project_id: str):
    """Load geometry JSON from Supabase storage."""
    try:
        path = f"inventarisatie/geometries/{project_id}.json"
        geo_bytes = supabase.storage.from_("new_app").download(path)
        return json.loads(geo_bytes.decode("utf-8"))
    except Exception:
        return None
