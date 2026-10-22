import streamlit as st
from utils.auth import check_password, logout
from utils.buttons import image_button
from utils.info_dialog import show_info_dialog
from utils.supabase_client import supabase
from utils.home.role_config import ROL_PAGINA_TOEGANG





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
    # Haal toegestane pagina’s op voor deze rol
    # ---------------------------------------------------------
    toegang = ROL_PAGINA_TOEGANG.get(rol, {})
    
    admin_pages = toegang.get("administratie", [])
    employee_pages = toegang.get("medewerkers", [])
    
    
    # ---------------------------------------------------------
    # ADMINISTRATIE MENU
    # ---------------------------------------------------------
    if admin_pages:   # alleen tonen als rol toegang heeft
        with st.expander("🔧 Administratie", expanded=False):
    
            col1, col2 = st.columns(2)
    
            if "Quickscan" in admin_pages:
                with col1:
                    if st.button("Quickscan", icon=":material/visibility:", use_container_width=True):
                        st.switch_page("pages/Quickscan.py")
    
            if "Inventarisatie" in admin_pages:
                with col2:
                    if st.button("Inventarisatie", icon=":material/note_alt:", use_container_width=True):
                        st.switch_page("pages/Inventarisatie.py")
    
            col3, col4 = st.columns(2)
    
            if "Control" in admin_pages:
                with col3:
                    if st.button("Control", icon=":material/manage_search:", use_container_width=True):
                        st.switch_page("pages/Control.py")
    
            if "Account aanmaken" in admin_pages:
                with col4:
                    if st.button("Account aanmaken", icon=":material/person_add:", use_container_width=True):
                        st.switch_page("pages/Medewerkers.py")
    
    
    # ---------------------------------------------------------
    # MEDEWERKERS MENU
    # ---------------------------------------------------------
    if employee_pages:
        with st.expander("🦺 Veldwerk", expanded=False):
    
            col5, col6 = st.columns(2)
    
            if "Planning" in employee_pages:
                with col5:
                    if st.button("Planning", icon=":material/event:", use_container_width=True):
                        st.switch_page("pages/Planning.py")












