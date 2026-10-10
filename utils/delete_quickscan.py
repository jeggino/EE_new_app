def delete_quickscan(qs_id, supabase):
    import streamlit as st
    import time

    st.error("⚠️ This action is permanent and cannot be undone.")
    st.write(
        "If you continue, **all data related to this Quickscan will be deleted**, including:\n"
        "- 📄 The Quickscan record\n"
        "- 🖼️ All photos linked to this Quickscan\n"
        "- 📍 The geometry file (GeoJSON)\n\n"
        "**This is irreversible.**"
    )

    confirm = st.checkbox("I understand that this is permanent and want to continue.")

    if confirm:
        if st.button("❌ Delete this Quickscan"):
            with st.spinner("Deleting Quickscan…"):

                # 1. Delete Quickscan record
                supabase.table("quickscan").delete().eq("id", qs_id).execute()

                # 2. Delete geometry file
                geometry_path = f"quickscan/geometries/{qs_id}.geojson"
                supabase.storage.from_("new_app").remove([geometry_path])

                # 3. Delete photos linked by Quickscan_id
                photos = supabase.table("quickscan_photos").select("*").eq("Quickscan_id", qs_id).execute()

                if photos.data:
                    for photo in photos.data:
                        photo_path = photo["foto_pad"]
                        supabase.storage.from_("new_app").remove([photo_path])

                    supabase.table("quickscan_photos").delete().eq("Quickscan_id", qs_id).execute()

                time.sleep(1)

            st.success("Quickscan successfully deleted.")
            st.switch_page("Home.py")
