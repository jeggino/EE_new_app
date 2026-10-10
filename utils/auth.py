import streamlit as st
from utils.supabase_client import supabase


# ----------------- SESSION DEFAULTS -----------------
DEFAULTS = {
    "logged_in": False,
    "user": None,
    "session": None,
    "show_signup": False,
}

for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ----------------- AUTH CORE -----------------
def restore_session():
    session = supabase.auth.get_session()
    if session and session.user:
        st.session_state.logged_in = True
        st.session_state.user = session.user
        st.session_state.session = session
    else:
        st.session_state.logged_in = False

def login(email, password):
    try:
        res = supabase.auth.sign_in_with_password({"email": email, "password": password})
        return res
    except Exception:
        return None

def logout():
    supabase.auth.sign_out()
    st.session_state.clear()
    for k, v in DEFAULTS.items():
        st.session_state[k] = v
    st.rerun()

# ----------------- UI -----------------
def show_login():
    st.title("Login")

    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Wachtwoord", type="password")
        submitted = st.form_submit_button("Login")

        if submitted:
            res = login(email, password)
            if res and res.user:
                st.session_state.logged_in = True
                st.session_state.user = res.user
                st.session_state.session = res.session
                st.rerun()
            else:
                st.error("Email of wachtwoord klopt niet.")
                


    if st.button("Account aanmaken"):
        st.session_state.show_signup = True
        st.rerun()

def show_signup():
    st.title("Account aanmaken")

    with st.form("signup_form"):
        email = st.text_input("Email")
        password = st.text_input("Wachtwoord", type="password")
        full_name = st.text_input("Volledige naam")
        category = st.selectbox("Categorie", ["beginner", "senior"])
        role = st.selectbox("Rol", ["guest", "user", "creator"])

        submitted = st.form_submit_button("Aanmaken")

        if submitted:
            try:
                supabase.auth.admin.create_user({
                    "email": email,
                    "password": password,
                    "user_metadata": {
                        "full_name": full_name,
                        "category": category,
                        "role": role
                    }
                })
                st.success("Account aangemaakt! Je kunt nu inloggen.")
                st.session_state.show_signup = False
                st.rerun()
            except Exception as e:
                st.error(f"Fout bij aanmaken: {e}")

    if st.button("Terug naar login"):
        st.session_state.show_signup = False
        st.rerun()

# ----------------- PUBLIC FUNCTION -----------------
def check_password():
    """
    This replaces your old password check.
    Now it handles full Supabase authentication.
    """

    restore_session()

    if not st.session_state.logged_in:
        if st.session_state.show_signup:
            show_signup()
        else:
            show_login()
        return False

    return True


