# utils/inventarisatie/delete_inventarisatie.py

from utils.supabase_client import supabase


def delete_inventarisatie(project_id: str):
    """Delete project + geometry file."""

    # Delete geometry file
    try:
        path = f"inventarisatie/geometries/{project_id}.json"
        supabase.storage.from_("new_app").remove(path)
    except Exception:
        pass  # geometry may not exist

    # Delete row
    resp = supabase.table("new_app_inventarisatie") \
        .delete() \
        .eq("id", project_id) \
        .execute()

    if resp.error:
        return False, resp.error.message

    return True, None
