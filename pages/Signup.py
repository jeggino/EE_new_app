import streamlit as st
from utils.supabase_client import supabase

# Hide sidebar
st.markdown("""
    <style>
        [data-testid="stSidebar"] {display: none;}
        [data-testid="stSidebarNav"] {display: none;}
    </style>
""", unsafe_allow_html=True)

def show_signup():
    st.title("Account aanmaken")

    with st.form("signup_form"):
        email = st.text_input("Email")
        password = st.text_input("Wachtwoord", type="password")
        full_name = st.text_input("Volledige naam")
        category = st.selectbox("Categorie", ["junior", "intermediate", "senior", "expert"])
        role = st.selectbox("Rol", ["guest", "user", "creator"])

        submitted = st.form_submit_button("Aanmaken")

        if submitted:
            try:
                res = supabase.auth.sign_up({
                    "email": email,
                    "password": password,
                    "options": {
                        "data": {
                            "full_name": full_name,
                            "category": category,
                            "role": role
                        }
                    }
                })

                st.success("Account aangemaakt! Je kunt nu inloggen.")
                st.session_state.show_signup = False
                st.rerun()

            except Exception as e:
                st.error(f"Fout bij aanmaken: {e}")

show_signup()
