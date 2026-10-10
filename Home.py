import streamlit as st
from utils.auth import check_password
from utils.buttons import image_button
from utils.info_dialog import show_info_dialog






st.set_page_config(page_title="Ecologisch Advies - Home", page_icon="🌿",initial_sidebar_state="collapsed")

st.markdown("""
    <style>
        [data-testid="stSidebar"] {display: none;}
        [data-testid="stSidebarNav"] {display: none;}
    </style>
""", unsafe_allow_html=True)

if check_password():

    st.image(
        "utils/pictures/signal-2026-08-31-14-39-37-051 (1).jpg",
        use_column_width=True
    )

    st.button("ℹ️ Info", on_click=show_info_dialog, use_container_width=True)

    
    # Create 3 equal columns
    col1, col2 = st.columns(2)
    
    # --- Quickscan ---
    with col1:
        # st.image("utils/pictures/icons/quickscan.png", width=120)
        if st.button("Quickscan", icon=":material/visibility:", use_container_width=True):
            st.switch_page("pages/Quickscan.py")
    
    # --- Inventarisatie ---
    with col2:
        # st.image("utils/pictures/icons/inventarisatie.png", width=120)
        if st.button("Inventarisatie",disabled=True, icon=":material/note_alt:", use_container_width=True):
            st.switch_page("pages/Inventarisatie.py")
    
    # --- Control ---
    col3, col4 = st.columns(2)

    with col3:
        # st.image("utils/pictures/icons/control.png", width=120)
        if st.button("Control",disabled=True, icon=":material/manage_search:", use_container_width=True):
            st.switch_page("pages/Control.py")











