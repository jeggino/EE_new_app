import streamlit as st
from utils.auth import check_password

st.set_page_config(page_title="Quickscan", page_icon="🗺️")

if check_password():

    st.title("Quickscan")

    tab_create, tab_edit = st.tabs(["Nieuwe Quickscan", "Quickscan bewerken"])

    with tab_create:
        st.subheader("Nieuwe Quickscan")
        st.write("Hier kun je een nieuwe Quickscan aanmaken.")

        st.info("Teken hier de geometrie.")
        st.info("Voer hier de projectgegevens in.")
        st.info("Upload hier foto's met beschrijving.")

    with tab_edit:
        st.subheader("Quickscan bewerken")
        st.write("Selecteer een bestaande Quickscan om te bewerken.")

        st.info("Hier komt een lijst met bestaande Quickscans.")
        st.info("Hier kun je de geometrie aanpassen.")
        st.info("Hier kun je de projectgegevens aanpassen.")
        st.info("Hier kun je foto's bekijken, toevoegen of verwijderen.")

