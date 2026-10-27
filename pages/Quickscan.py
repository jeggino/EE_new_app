import json
import streamlit as st
from datetime import datetime
from zoneinfo import ZoneInfo

import pandas as pd
import geopandas as gpd
import ast

import requests
import folium
from streamlit_folium import st_folium


from utils.auth import check_password
from utils.geometry_tools import draw_geometry, draw_geometry_with_existing
from utils.quickscan_tools import save_quickscan
from utils.supabase_client import supabase
from utils.species_groups import SPECIES_GROUPS
from utils.media_tools import save_photos
from utils.gis_natura2000 import voer_gis_analyse_natura2000
from utils.gis_nnn import voer_gis_analyse_nnn
from utils.buttons import image_button
from utils.delete_quickscan import verwijder_quickscan




# Hide sidebar
st.markdown("""
    <style>
        [data-testid="stSidebar"] {display: none;}
        [data-testid="stSidebarNav"] {display: none;}
    </style>
""", unsafe_allow_html=True)



if check_password():
    col1, col2 = st.columns([2, 1])
    # col1.title("Quickscan",text_alignment="center",)
    if col2.button("⬅️ Terug naar menu"):
        st.switch_page("Home.py")

    menu = st.pills(
        "Kies een onderdeel",
        default="Nieuwe Quickscan",
        selection_mode="single",
        options={
            "Nieuwe Quickscan": ":material/add_circle:",
            "Quickscan bewerken": ":material/edit:",
            "Quickscan bekijken": ":material/visibility:"
        }
    )
    
    if menu == "Nieuwe Quickscan":
        # st.subheader("Nieuwe Quickscan",text_alignment="center",)

        geojson = draw_geometry(key="new_qs_map")

        naam = st.text_input("Projectnaam")
        opmerking = st.text_area("Beschrijving")

        st.subheader("Veldgegevens")
        
        datum = st.date_input("Datum")
        veldwerker = st.text_input("Veldwerker")
        now_local = datetime.now(ZoneInfo("Europe/Amsterdam")).time()
        starttijd = st.time_input("Starttijd",value=now_local)
        eindtijd = st.time_input("Eindtijd",value=now_local)
        
        temperatuur = st.number_input("Temperatuur (°C)", step=0.1)
        windsnelheid = st.selectbox(
            "Windsnelheid",
            ["0 - Stil", "1 - Zwak", "2 - Matig", "3 - Vrij krachtig", "4 - Sterk", "5 - Storm"]
        )
        regen = st.selectbox(
            "Regen",
            ["Geen", "Licht", "Matig", "Hevig"]
        )

        # st.subheader("Soortgeschiktheid")
        
        # soorten_results = {}
        
        # for group, species_list in SPECIES_GROUPS.items():
        #     suitable = st.toggle(f"Is het gebied geschikt voor {group}?")
        
        #     if suitable:
        #         if species_list:
        #             selected = st.multiselect(
        #                 f"Welke soorten binnen {group}?",
        #                 species_list,
        #                 key=f"species_{group}"
        #             )
        #             soorten_results[group] = selected
        #         else:
        #             soorten_results[group] = True
        #     else:
        #         soorten_results[group] = False

        st.subheader("Soortgeschiktheid")
        
        soorten_results = {}
        
        for group, species_data in SPECIES_GROUPS.items():
        
            suitable = st.toggle(f"Is het gebied geschikt voor {group}?")
            
            if not suitable:
                soorten_results[group] = False
                continue
        
            # --- CASE 1: species_data is a simple list ---
            if isinstance(species_data, list):
                if species_data:
                    selected = st.multiselect(
                        f"Welke soorten binnen {group}?",
                        species_data,
                        key=f"species_{group}"
                    )
                    soorten_results[group] = selected
                else:
                    soorten_results[group] = True
        
            # --- CASE 2: species_data is a dict (e.g. vogels) ---
            elif isinstance(species_data, dict):
        
                group_results = {}
        
                # Create indentation using columns
                main_col, sub_col = st.columns([1, 5])
        
                with sub_col:
                    st.markdown("### Subcategorieën")
        
                    for subcat, species_list in species_data.items():
        
                        sub_suitable = st.toggle(
                            f"{subcat}",
                            key=f"toggle_{group}_{subcat}"
                        )
        
                        if sub_suitable:
                            selected = st.multiselect(
                                f"Welke soorten binnen {subcat}?",
                                species_list,
                                key=f"species_{group}_{subcat}"
                            )
                            group_results[subcat] = selected
                        else:
                            group_results[subcat] = False
        
                soorten_results[group] = group_results
        
            else:
                soorten_results[group] = True



        st.subheader("Foto's")

        beschikbare_soortgroepen = []
        
        for group, value in soorten_results.items():
        
            # --- CASE 1: group has no subcategories and is simply True ---
            if value is True:
                beschikbare_soortgroepen.append(group)
        
            # --- CASE 2: group is a list of selected species ---
            elif isinstance(value, list):
                for species in value:
                    beschikbare_soortgroepen.append(species)
        
            # --- CASE 3: group has subcategories (e.g. vogels) ---
            elif isinstance(value, dict):
                for subcat, subvalue in value.items():
        
                    # subcategory marked suitable but no species selected
                    if subvalue is True:
                        beschikbare_soortgroepen.append(f"{group} – {subcat}")
        
                    # species selected inside this subcategory
                    elif isinstance(subvalue, list) and len(subvalue) > 0:
                        for species in subvalue:
                            beschikbare_soortgroepen.append(species)
        
                    # if subvalue is False → nothing added


                
                
        photos_to_upload = []
        
        add_photo = st.toggle("Wil je een foto toevoegen?", key="add_photo_first")
        
        while add_photo:
            index = len(photos_to_upload)
        
            photo = st.file_uploader(
                "Upload een foto",
                type=["jpg", "jpeg", "png"],
                key=f"photo_{index}"
            )
        
            if photo:
                beschrijving = st.text_area(
                    "Schrijf een beschrijving voor deze foto",
                    key=f"beschrijving_{index}"
                )
        
                soortgroepen_foto = st.multiselect(
                    "Voor welke soortgroepen is dit habitat potentieel geschikt?",
                    beschikbare_soortgroepen,
                    key=f"soortgroepen_{index}"
                )
        
                photos_to_upload.append({
                    "file": photo,
                    "beschrijving": beschrijving,
                    "soortgroepen": soortgroepen_foto
                })
        
                st.success("Foto toegevoegd.")
        
            # IMPORTANT: give this toggle a UNIQUE key
            add_photo = st.toggle(
                "Nog een foto toevoegen?",
                key=f"add_photo_{index}"
            )




        if st.button("Project opslaan"):
        
            if not geojson:
                st.error("Teken eerst een geometrie.")
                st.stop()
        
            if not naam:
                st.error("Voer een projectnaam in.")
                st.stop()
        
            # Check if project name already exists
            existing = supabase.table("new_app_quickscan").select("naam").eq("naam", naam.replace(" ", "_")).execute()
            if existing.data:
                st.error("Projectnaam bestaat al. Kies een andere naam.")
                st.stop()
        
            with st.spinner("Quickscan wordt opgeslagen…"):
            
                qs_id = save_quickscan(
                    naam,
                    opmerking,
                    geojson,
                    datum,
                    veldwerker,
                    starttijd,
                    eindtijd,
                    temperatuur,
                    windsnelheid,
                    regen,
                    soorten_results
                )
            
                if photos_to_upload:
                    save_photos(qs_id, photos_to_upload)
            
            st.success("Quickscan succesvol opgeslagen!")


    # with tab_edit:
    elif menu == "Quickscan bewerken":
        # st.subheader("Quickscan bewerken", text_alignment="center")
        
        # 1. Haal alle quickscans op
        resp = supabase.table("new_app_quickscan").select("id, naam, datum").execute()
        quickscans = resp.data
        
        if not quickscans:
            st.info("Geen quickscans gevonden.")
            st.stop()
        
        # 2. Dropdown
        keuze = st.selectbox(
            "Kies een Quickscan:",
            options=quickscans,
            format_func=lambda x: f"{x['naam']} ({x['datum']})"
        )

        qs_id = keuze["id"]

        qs_resp = supabase.table("new_app_quickscan") \
            .select("*") \
            .eq("id", qs_id) \
            .single() \
            .execute()
    
        qs = qs_resp.data
    
        if not qs:
            st.error("Quickscan niet gevonden.")
            st.stop()
        


        
        # -----------------------------
        # 1. Geometrie laden
        # -----------------------------
        # Huidige geometrie ophalen
        geometry_path = f"quickscan/geometries/{qs['id']}.geojson"
        geometry_data = supabase.storage.from_("new_app").download(geometry_path)
        
        import json
        
        # Decode bytes → JSON dict
        current_geojson = json.loads(geometry_data.decode("utf-8"))
        
        st.write("Nieuwe geometrie tekenen (optioneel):")
        
        nieuwe_geojson = draw_geometry_with_existing(current_geojson, key="edit_map")

        
        # -----------------------------
        # 2. Basisgegevens
        # -----------------------------
        naam = st.text_input("Projectnaam", value=qs["naam"],key=f"naam_edit_{qs['id']}")
        opmerking = st.text_area("Beschrijving", value=qs["opmerking"],key=f"beschrijving_edit_{qs['id']}")
        
        # -----------------------------
        # 3. Veldgegevens
        # -----------------------------
        st.subheader("Veldgegevens")
        
        datum = st.date_input("Datum", value=qs["datum"],key=f"datum_edit_{qs['id']}")
        veldwerker = st.text_input("Veldwerker", value=qs["veldwerker"],key=f"veldwerker_edit_{qs['id']}")
        
        starttijd = st.time_input("Starttijd", value=qs.get("starttijd"),key=f"starttijd_edit_{qs['id']}")
        eindtijd = st.time_input("Eindtijd", value=qs.get("eindtijd"),key=f"eindtijd_edit_{qs['id']}")
        
        temperatuur = st.number_input("Temperatuur (°C)", step=0.1, value=qs["temperatuur"],key=f"temperatuur_edit_{qs['id']}")
        
        windsnelheid = st.selectbox(
            "Windsnelheid",
            ["0 - Stil", "1 - Zwak", "2 - Matig", "3 - Vrij krachtig", "4 - Sterk", "5 - Storm"],
            index=["0 - Stil", "1 - Zwak", "2 - Matig", "3 - Vrij krachtig", "4 - Sterk", "5 - Storm"].index(qs["windsnelheid"]),
            key=f"windsnelheid_edit_{qs['id']}"
        )
        
        regen = st.selectbox(
            "Regen",
            ["Geen", "Licht", "Matig", "Hevig"],
            index=["Geen", "Licht", "Matig", "Hevig"].index(qs["regen"]),
            key=f"regen_{qs['id']}"
        )


        # -----------------------------
        # 4. Soortgeschiktheid
        # -----------------------------
        st.subheader("Soortgeschiktheid")
        
        soorten_results = qs["soorten"]  # JSON dict from database
        nieuwe_soorten = {}
        
        for group, species_data in SPECIES_GROUPS.items():
        
            huidige_waarde = soorten_results.get(group)
        
            # Determine if the group was previously marked suitable
            if isinstance(huidige_waarde, dict):
                # vogels → suitable if ANY subcategory was True or had selected species
                suitable_default = any(
                    (v is True) or (isinstance(v, list) and len(v) > 0)
                    for v in huidige_waarde.values()
                )
            else:
                suitable_default = (huidige_waarde is True or isinstance(huidige_waarde, list))
        
            suitable = st.toggle(
                f"Is het gebied geschikt voor {group}?",
                value=suitable_default,
                key=f"suitable_{group}_{qs['id']}"
            )
        
            # ---------------------------
            # CASE 1: group is NOT suitable
            # ---------------------------
            if not suitable:
                nieuwe_soorten[group] = False
                continue
        
            # ---------------------------
            # CASE 2: group has NO subcategories (simple list)
            # ---------------------------
            if isinstance(species_data, list):
        
                if species_data:
                    default_list = (
                        huidige_waarde if isinstance(huidige_waarde, list) else []
                    )
        
                    selected = st.multiselect(
                        f"Welke soorten binnen {group}?",
                        species_data,
                        default=default_list,
                        key=f"species_{group}_{qs['id']}"
                    )
        
                    nieuwe_soorten[group] = selected
        
                else:
                    nieuwe_soorten[group] = True
        
            # ---------------------------
            # CASE 3: group HAS subcategories (vogels)
            # ---------------------------
            elif isinstance(species_data, dict):
        
                subcat_results = {}
        
                # Indentation using columns
                main_col, sub_col = st.columns([1, 3])
        
                with sub_col:
                    st.markdown("### Subcategorieën")
        
                    for subcat, species_list in species_data.items():
        
                        # Determine default toggle state
                        huidige_sub = None
                        if isinstance(huidige_waarde, dict):
                            huidige_sub = huidige_waarde.get(subcat)
        
                        sub_default = (
                            huidige_sub is True or
                            (isinstance(huidige_sub, list) and len(huidige_sub) > 0)
                        )
        
                        sub_suitable = st.toggle(
                            f"{subcat}",
                            value=sub_default,
                            key=f"toggle_{group}_{subcat}_{qs['id']}"
                        )
        
                        if sub_suitable:
                            default_species = (
                                huidige_sub if isinstance(huidige_sub, list) else []
                            )
        
                            selected = st.multiselect(
                                f"Welke soorten binnen {subcat}?",
                                species_list,
                                default=default_species,
                                key=f"species_{group}_{subcat}_{qs['id']}"
                            )
        
                            subcat_results[subcat] = selected
        
                        else:
                            subcat_results[subcat] = False
        
                nieuwe_soorten[group] = subcat_results
        
            else:
                nieuwe_soorten[group] = True

        
        # -----------------------------
        # 5. Foto's beheren
        # -----------------------------
        st.subheader("Foto's")
        
        fotos_resp = supabase.table("new_app_quickscan_fotos") \
            .select("*") \
            .eq("quickscan_id", qs["id"]) \
            .execute()
        
        fotos = fotos_resp.data
        
        # Build available species/groups based on Quickscan suitability
        soorten_results = nieuwe_soorten
        beschikbare_soortgroepen = []
        
        for group, value in soorten_results.items():
        
            # CASE 1: group is simply True (no species list)
            if value is True:
                beschikbare_soortgroepen.append(group)
        
            # CASE 2: group is a list of selected species
            elif isinstance(value, list) and len(value) > 0:
                beschikbare_soortgroepen.extend(value)
        
            # CASE 3: group has subcategories (vogels)
            elif isinstance(value, dict):
                for subcat, subvalue in value.items():
        
                    # Subcategory marked suitable but no species selected
                    if subvalue is True:
                        beschikbare_soortgroepen.append(f"{group} – {subcat}")
        
                    # Species selected inside this subcategory
                    elif isinstance(subvalue, list) and len(subvalue) > 0:
                        beschikbare_soortgroepen.extend(subvalue)
        
                    # If subvalue is False → nothing added

        
        for foto in fotos:
            import os
            filename = os.path.basename(foto["foto_pad"])
        
        
            data = supabase.storage.from_("new_app").download(foto["foto_pad"])
            st.image(data)
    
            nieuwe_beschrijving = st.text_area(
                f"Beschrijving",
                value=foto.get("beschrijving", ""),
                key=f"beschrijving_{qs['id']}_{foto['id']}"
            )
    
            nieuwe_soorten_list = st.multiselect(
                f"Soortgroepen",
                beschikbare_soortgroepen,
                key=f"soorten_{qs['id']}_{foto['id']}"
            )
            
            col1, col2 = st.columns([1, 1])
            if col1.button("Opslaan wijzigingen", key=f"save_{qs['id']}_{foto['id']}"):
                supabase.table("new_app_quickscan_fotos") \
                    .update({
                        "beschrijving": nieuwe_beschrijving,
                        "soortgroep": nieuwe_soorten_list
                    }) \
                    .eq("id", foto["id"]) \
                    .execute()
    
                st.success("Foto metadata bijgewerkt.")
                st.rerun()
    
            if col2.button(f"Verwijder", key=f"delete_{qs['id']}_{foto['id']}"):
                supabase.storage.from_("new_app").remove(foto["foto_pad"])
                supabase.table("new_app_quickscan_fotos") \
                    .delete() \
                    .eq("id", foto["id"]) \
                    .execute()
    
                st.warning(f"verwijderd.")
                st.rerun()

            "---"


        if "upload_key" not in st.session_state:
            st.session_state.upload_key = f"upload_{qs['id']}"
        
        nieuwe_foto = st.file_uploader(
            "Nieuwe foto uploaden",
            type=["jpg", "jpeg", "png"],
            key=st.session_state.upload_key
        )

        
        if nieuwe_foto:
            import uuid
            unique_id = str(uuid.uuid4())
            safe_name = naam.replace(" ", "_")
        
            filename = f"quickscan/fotos/{unique_id}.jpg"
        
            # Upload to storage
            supabase.storage.from_("new_app").upload(
                filename,
                nieuwe_foto.read(),
                file_options={"content-type": "image/jpeg", "x-upsert": "true"}
            )
        
            # Insert metadata row
            supabase.table("new_app_quickscan_fotos").insert({
                "quickscan_id": qs["id"],
                "foto_pad": filename,
                "beschrijving": "",
                "soortgroep": []
            }).execute()
        
            st.success("Foto geüpload.")
            
           # Reset uploader key to clear the file
            st.session_state.upload_key = f"upload_{qs['id']}_{uuid.uuid4()}"
            
            st.rerun()

        
        # -----------------------------
        # 6. Opslaan
        # -----------------------------

        

        if st.button("Quickscan opslaan"):
            with st.spinner("Quickscan wordt opgeslagen…"):
                update_data = {
                    "naam": naam,
                    "opmerking": opmerking,
                    "datum": str(datum),
                    "veldwerker": veldwerker,
                    "starttijd": str(starttijd),
                    "eindtijd": str(eindtijd),
                    "temperatuur": temperatuur,
                    "windsnelheid": windsnelheid,
                    "regen": regen,
                    "soorten": nieuwe_soorten,
                }
            
                # Geometrie vervangen indien nieuwe getekend
                if nieuwe_geojson:
    
                    import json
                    
                    data = json.dumps(nieuwe_geojson).encode("utf-8")
                    path = f"quickscan/geometries/{qs['id']}.geojson"
                    supabase.storage.from_("new_app").upload(
                        path,
                        data,
                        file_options={"content-type": "application/geo+json", "x-upsert": "true"}
                    )
    
    
            
                supabase.table("new_app_quickscan").update(update_data).eq("id", qs["id"]).execute()
            
                st.success("Quickscan bijgewerkt.")
                st.session_state.edit_mode = False
                st.rerun()

        verwijder_quickscan(qs["id"], supabase)





    

    
    # with tab_view:
    elif menu == "Quickscan bekijken":
        # st.header("Quickscan bekijken",text_alignment="center",)
    
        # Load all quickscans
        all_qs = supabase.table("new_app_quickscan") \
            .select("naam, datum") \
            .order("datum", desc=True) \
            .execute()
    
        if not all_qs.data:
            st.info("Nog geen Quickscans beschikbaar.")
            st.stop()
    
        # Dropdown
        qs_labels = [f"{qs['naam']} ({qs['datum']})" for qs in all_qs.data]
        selected_label = st.selectbox("Kies een Quickscan:", qs_labels)
    
        selected_name = selected_label.split(" (")[0]
    
        # Load selected Quickscan
        qs = supabase.table("new_app_quickscan") \
            .select("*") \
            .eq("naam", selected_name) \
            .single() \
            .execute().data
    
        # Show info
        st.subheader("Projectinformatie")
        st.write(f"**Naam:** {qs['naam']}")
        st.write(f"**Datum:** {qs['datum']}")
        st.write(f"**Tijd:** {qs['starttijd']} - {qs['eindtijd']}")
        st.write(f"**Veldwerker:** {qs['veldwerker']}")
        st.write(f"**Beschrijving:** {qs['opmerking']}")
    
        st.subheader("Weersomstandigheden")
        st.write(f"**Temperatuur:** {qs['temperatuur']} °C")
        st.write(f"**Wind:** {qs['windsnelheid']} Bft")
        st.write(f"**Regen:** {qs['regen']}")
        
        "---"
        st.subheader("Soortgeschiktheid")
        
        soorten = qs["soorten"]
        
        rows = []
        
        for group, value in soorten.items():
        
            display_group = group.replace("_", " ").capitalize()
        
            # CASE 1: simple list of species
            if isinstance(value, list) and len(value) > 0:
                soorten_str = ", ".join([s.capitalize() for s in value])
                rows.append([display_group, soorten_str])
        
            # CASE 2: vogels with subcategories
            elif isinstance(value, dict):
                for subcat, subvalue in value.items():
        
                    display_subcat = subcat.replace("_", " ").capitalize()
        
                    # Only show rows that actually have species
                    if isinstance(subvalue, list) and len(subvalue) > 0:
                        soorten_str = ", ".join([s.capitalize() for s in subvalue])
                        rows.append([f"{display_group} – {display_subcat}", soorten_str])
        
        # Build DataFrame
        df = pd.DataFrame(rows, columns=["Soortgroep", "Soorten"])
        
        # Pretty display
        st.dataframe(
            df.style.set_properties(**{
                "text-align": "left",
                "font-size": "15px"
            }).hide(axis="index"),
            use_container_width=True
        )
    
        "---"
        st.subheader("Foto's")
        fotos = supabase.table("new_app_quickscan_fotos") \
            .select("*") \
            .eq("quickscan_id", qs["id"]) \
            .execute()
        
        if not fotos.data:
            st.info("Geen foto's toegevoegd.")
        else:
            import ast
        
            for foto in fotos.data:
                url = supabase.storage.from_("new_app").get_public_url(foto["foto_pad"])
                st.image(url, caption=foto["beschrijving"])
        
                soorten_list = foto["soortgroep"]
        
                # Convert JSON string → Python list
                if isinstance(soorten_list, str):
                    soorten_list = ast.literal_eval(soorten_list)
        
                st.write(f"**Potentieel geschikt voor:** {', '.join(soorten_list)}")
               

        "---"
        st.markdown("""
        ### Extra GIS‑analyse: NNN & Natura 2000
        
        Deze analyse toont twee kaarten die laten zien hoe het Quickscan‑gebied zich verhoudt tot belangrijke natuurgebieden in Nederland.
        
        #### 🟩 Natuurnetwerk Nederland (NNN)
        Het Natuurnetwerk Nederland (NNN) bestaat uit door provincies aangewezen natuurgebieden die samen een ecologisch netwerk vormen.  
        Voor deze kaart wordt een **zoekvenster van 15 km** rondom het Quickscan‑gebied gebruikt.  
        Binnen dit venster worden alle NNN‑gebieden geselecteerd en weergegeven.  
        Rond het centroid van het Quickscan‑gebied wordt een **buffer van 1 km** getoond.
        
        #### 🟥 Natura 2000‑gebieden
        Natura 2000 is een Europees netwerk van beschermde natuurgebieden.  
        Ook hier wordt een **zoekvenster van 15 km** toegepast om relevante gebieden te selecteren.  
        Rond het centroid wordt een **buffer van 3 km** weergegeven om de nabijheid van deze gebieden te visualiseren.
        
        Klik op de knop hieronder om beide kaarten te genereren.
        """)
        
        run_analysis = st.toggle(
            "Natuurgebieden rond het Quickscan‑gebied bekijken"
        )
        
        if run_analysis:
            with st.spinner("Bezig met het genereren van de kaarten..."):
        
                st.markdown("### 🟩 Kaart 1 — Natuurnetwerk Nederland (NNN)")
                voer_gis_analyse_nnn(qs)
                st.caption("Deze kaart toont alle NNN‑gebieden binnen 15 km, inclusief een 1 km buffer rond het centroid van het Quickscan‑gebied.")
        
                st.markdown("### 🟥 Kaart 2 — Natura 2000‑gebieden")
                voer_gis_analyse_natura2000(qs)
                st.caption("Deze kaart toont alle Natura 2000‑gebieden binnen 15 km, inclusief een 3 km buffer rond het centroid van het Quickscan‑gebied.")




        "---"
        st.markdown("### Conclusie van de Quickscan")
        
        # 1. Vraag of gebruiker een conclusie wil schrijven
        write_conclusion = st.toggle("Wil je een conclusie toevoegen of bewerken?")
        
        # Haal bestaande conclusie op (indien aanwezig)
        existing = supabase.table("new_app_quickscan_conclusions") \
            .select("*") \
            .eq("project_naam", qs["id"]) \
            .execute()
        
        existing_text = None
        existing_id = None
        
        if existing.data:
            existing_text = existing.data[0]["conclusie"]
            existing_id = existing.data[0]["id"]

        if write_conclusion:
                
            st.markdown("#### Schrijf of bewerk de conclusie")
        
            # Tekstvak met bestaande tekst indien aanwezig
            conclusion_text = st.text_area(
                "Conclusie:",
                value=existing_text if existing_text else "",
                placeholder="..."
            )
        
            # Als er al een conclusie bestaat → toon update-knop
            if existing_id:
        
                st.info("Er is al een conclusie opgeslagen voor dit project.")
        
                col1, col2, col3 = st.columns(3)
        
                # --- Bijwerken ---
                with col1:
                    if st.button("Conclusie bijwerken"):
                        if conclusion_text.strip() == "":
                            st.error("De conclusie mag niet leeg zijn.")
                        else:
                            supabase.table("new_app_quickscan_conclusions") \
                                .update({"conclusie": conclusion_text}) \
                                .eq("id", existing_id) \
                                .execute()
        
                            st.success("De conclusie is bijgewerkt.")
                            st.rerun()   # 🔄 reload
        
                # --- Verwijderen ---
                with col2:
                    if st.button("Conclusie verwijderen"):
                        supabase.table("new_app_quickscan_conclusions") \
                            .delete() \
                            .eq("id", existing_id) \
                            .execute()
        
                        st.warning("De conclusie is verwijderd.")
                        st.rerun()   # 🔄 reload
        
                # --- Handmatige reload ---
                with col3:
                    if st.button("Vernieuwen"):
                        st.rerun()   # 🔄 reload
        
            # Als er nog GEEN conclusie bestaat → toon opslaan-knop
            else:
                if st.button("Nieuwe conclusie opslaan"):
                    if conclusion_text.strip() == "":
                        st.error("De conclusie mag niet leeg zijn.")
                    else:
                        supabase.table("new_app_quickscan_conclusions") \
                            .insert({
                                "project_naam": qs["id"],
                                "conclusie": conclusion_text
                            }).execute()
        
                        st.success("De conclusie is succesvol opgeslagen.")
                        st.rerun()   # 🔄 reload

 
        "---"
        from docx import Document
        from docx.shared import Inches
        import io
        
        st.subheader("Download Quickscan Rapport (.docx)")
        
        # Haal conclusie op
        conclusion_data = supabase.table("new_app_quickscan_conclusions") \
            .select("*") \
            .eq("project_naam", qs["naam"]) \
            .execute()
        
        conclusion_text = (
            conclusion_data.data[0]["conclusie"]
            if conclusion_data.data else "Geen conclusie opgeslagen."
        )
        
        # Maak Word-document
        doc = Document()
        
        doc.add_heading("Quickscan Rapport", level=1)
        
        doc.add_heading("Projectinformatie", level=2)
        doc.add_paragraph(f"Naam: {qs['naam']}")
        doc.add_paragraph(f"Datum: {qs['datum']}")
        doc.add_paragraph(f"Veldwerker: {qs['veldwerker']}")
        doc.add_paragraph(f"Opmerking: {qs['opmerking']}")
        
        doc.add_heading("Weersomstandigheden", level=2)
        doc.add_paragraph(f"Temperatuur: {qs['temperatuur']} °C")
        doc.add_paragraph(f"Wind: {qs['windsnelheid']} Bft")
        doc.add_paragraph(f"Regen: {qs['regen']}")
        

        
        # Voeg foto toe (als aanwezig)
        if "foto_path" in qs:
            img_bytes = supabase.storage.from_("new_app").download(qs["foto_path"])
            doc.add_heading("Foto", level=2)
            doc.add_picture(io.BytesIO(img_bytes), width=Inches(4))
        
        # Document in geheugen opslaan
        buffer = io.BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        
        # Download-knop
        st.download_button(
            "Download Quickscan Rapport (.docx)",
            buffer,
            file_name=f"{qs['naam']}_quickscan.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )








