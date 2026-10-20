import streamlit as st
from utils.auth import check_password, logout
from utils.buttons import image_button
from utils.info_dialog import show_info_dialog
from utils.supabase_client import supabase






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
    st.button("Uitloggen", icon=":material/logout:", on_click=logout, use_container_width=True)

    
    # # Create 3 equal columns
    # col1, col2 = st.columns(2)
    
    # # --- Quickscan ---
    # with col1:
    #     # st.image("utils/pictures/icons/quickscan.png", width=120)
    #     if st.button("Quickscan", icon=":material/visibility:", use_container_width=True,disabled=False):
    #         st.switch_page("pages/Quickscan.py")
    
    # # --- Inventarisatie ---
    # with col2:
    #     # st.image("utils/pictures/icons/inventarisatie.png", width=120)
    #     if st.button("Inventarisatie",disabled=False, icon=":material/note_alt:", use_container_width=True):
    #         st.switch_page("pages/Inventarisatie.py")
    
    # # --- Control ---
    # col3, col4 = st.columns(2)

    # with col3:
    #     # st.image("utils/pictures/icons/control.png", width=120)
    #     if st.button("Control",disabled=True, icon=":material/manage_search:", use_container_width=True):
    #         st.switch_page("pages/Control.py")

    # with col4:
    #     if st.button("Account aanmaken", icon=":material/person_add:", use_container_width=True,disabled=False):
    #         st.switch_page("pages/Medewerkers.py")

    # # --- Control ---
    # col5, col6 = st.columns(2)

    # with col5:
    #     # st.image("utils/pictures/icons/control.png", width=120)
    #     if st.button("Planning",disabled=False, icon=":material/event:", use_container_width=True):
    #         st.switch_page("pages/Planning.py")

    # ---------------------------------------------------------
    # Haal rol van gebruiker op
    # ---------------------------------------------------------
    user = st.session_state.get("user")
    user_email = user.email
    
    employee_record = supabase.table("new_app_employees") \
        .select("rol") \
        .eq("email", user_email) \
        .single() \
        .execute().data
    
    rol = employee_record["rol"] if employee_record else "gebruiker"
    
    
    # ---------------------------------------------------------
    # ADMINISTRATIE MENU
    # ---------------------------------------------------------
    with st.expander("🔧 Administratie", expanded=False):
    
        admin_disabled = (rol != "beheerder")
    
        col1, col2 = st.columns(2)
    
        with col1:
            if st.button("Quickscan", icon=":material/visibility:", use_container_width=True, disabled=admin_disabled):
                st.switch_page("pages/Quickscan.py")
    
        with col2:
            if st.button("Inventarisatie", icon=":material/note_alt:", use_container_width=True, disabled=admin_disabled):
                st.switch_page("pages/Inventarisatie.py")
    
        col3, col4 = st.columns(2)
    
        with col3:
            if st.button("Control", icon=":material/manage_search:", use_container_width=True, disabled=admin_disabled):
                st.switch_page("pages/Control.py")
    
        with col4:
            if st.button("Account aanmaken", icon=":material/person_add:", use_container_width=True, disabled=admin_disabled):
                st.switch_page("pages/Medewerkers.py")
    
    
    # ---------------------------------------------------------
    # MEDEWERKERS MENU
    # ---------------------------------------------------------
    with st.expander("👷 Medewerkers", expanded=False):
    
        col5, col6 = st.columns(2)
    
        with col5:
            if st.button("Planning", icon=":material/event:", use_container_width=True):
                st.switch_page("pages/Planning.py")











