import streamlit as st
from utils.auth import check_password
from utils.geometry_tools import draw_geometry
from utils.quickscan_tools import save_quickscan

if check_password():

    st.title("Quickscan")

    tab_create, tab_edit = st.tabs(["Nieuwe Quickscan", "Quickscan bewerken"])

    with tab_create:
        st.subheader("Nieuwe Quickscan")

        geojson = draw_geometry()

        project_name = st.text_input("Projectnaam")
        description = st.text_area("Beschrijving")

        if st.button("Project opslaan"):
            save_quickscan(project_name, description, geojson)
            st.success("Quickscan succesvol opgeslagen.")
            st.rerun()

    with tab_edit:
        st.subheader("Quickscan bewerken")
        st.info("Hier komt de lijst met bestaande Quickscans.")

