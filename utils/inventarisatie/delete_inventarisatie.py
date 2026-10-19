def delete_inventarisatie(project_id: str):
    """Delete project + geometry file."""

    # 1. Delete geometry file
    try:
        path = f"inventarisatie/geometries/{project_id}.json"
        supabase.storage.from_("new_app").remove([path])
    except Exception as e:
        print("Geometry delete error:", e)

    # 2. Delete database row
    try:
        supabase.table("new_app_inventarisatie") \
            .delete() \
            .eq("id", project_id) \
            .execute()
    except Exception as e:
        return False, str(e)

    return True, None




