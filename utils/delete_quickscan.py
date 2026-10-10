import streamlit as st
import time



def verwijder_quickscan(qs_id, supabase):
    with st.expander(":red[**Quickscan verwijder**]"):
        st.error("⚠️ Deze actie is permanent en kan niet ongedaan worden gemaakt.")
        st.write(
            "Als je doorgaat, worden **alle gegevens van deze Quickscan verwijderd**, waaronder:\n"
            "- 📄 Het Quickscan‑record\n"
            "- 🖼️ Alle foto’s die gekoppeld zijn aan deze Quickscan\n"
            "- 📍 Het geometriebestand (GeoJSON)\n"
            "- 📝 Alle conclusies met dezelfde projectnaam\n\n"
            "**Dit is onomkeerbaar.**"
        )
    
        bevestiging = st.checkbox("Ik begrijp dat dit permanent is en wil doorgaan.")
    
        if bevestiging:
            if st.button("❌ Verwijder deze Quickscan"):
                with st.spinner("Quickscan wordt verwijderd…"):
    
                    # 1. Verwijder Quickscan record
                    supabase.table("new_app_quickscan").delete().eq("id", qs_id).execute()
    
                    # 2. Verwijder geometrie (zelfde naam als ID)
                    geo_path = f"quickscan/geometries/{qs_id}.geojson"
                    supabase.storage.from_("new_app").remove([geo_path])
    
                    # 3. Verwijder foto’s gekoppeld via Quickscan_id
                    fotos = supabase.table("new_app_quickscan_fotos").select("*").eq("quickscan_id", qs_id).execute()
    
                    if fotos.data:
                        for foto in fotos.data:
                            foto_pad = foto["foto_pad"]  # dit is de volledige opslag‑URL
                            supabase.storage.from_("new_app").remove([foto_pad])
    
                        # Verwijder fotoregels uit de database
                        supabase.table("new_app_quickscan_fotos").delete().eq("quickscan_id", qs_id).execute()
    
                    # 4. Verwijder conclusies uit new_app_quickscan_conclusions
                    supabase.table("new_app_quickscan_conclusions").delete().eq("project_naam", qs_id).execute()
    
                    
    
                st.success("Quickscan succesvol verwijderd.")
                time.sleep(1)
                st.rerun()

