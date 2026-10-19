# utils/inventarisatie/delete_inventarisatie.py

from utils.supabase_client import supabase


def delete_inventarisatie(project_id: str):
    """Delete project + geometry file."""

    # 1. Delete geometry file (list of paths!)
    try:
        path = f"inventarisatie/geometries/{project_id}.json"
        result = supabase.storage.from_("new_app").remove([path])
        print("Geometry delete result:", result)
    except Exception as e:
        print("Geometry delete error:", e)

    # 2. Delete database row
    try:
        result = supabase.table("new_app_inventarisatie") \
            .delete() \
            .eq("id", project_id) \
            .execute()
        print("Row delete result:", result.data)
    except Exception as e:
        return False, str(e)

    return True, None



