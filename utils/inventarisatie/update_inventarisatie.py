# utils/inventarisatie/update_inventarisatie.py

import json
from utils.supabase_client import supabase


def update_inventarisatie(project_id: str, update_data: dict, new_geometry: dict | None):
    """Update metadata + optionally replace geometry file."""

    # Let Postgres update the timestamp
    update_data["bijgewerkt_op"] = "now()"

    # -----------------------------
    # 1. Update metadata
    # -----------------------------
    try:
        supabase.table("new_app_inventarisatie") \
            .update(update_data) \
            .eq("id", project_id) \
            .execute()
    except Exception as e:
        return False, str(e)

    # -----------------------------
    # 2. Replace geometry if provided
    # -----------------------------
    if new_geometry:
        try:
            geo_json = json.dumps(new_geometry).encode("utf-8")
            path = f"inventarisatie/geometries/{project_id}.json"

            supabase.storage.from_("new_app").upload(
                path,
                geo_json,
                file_options={"content-type": "application/geo+json", "x-upsert": "true"}
            )
        except Exception as e:
            return False, f"Geometry update failed: {e}"

    return True, None

