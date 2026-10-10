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
                



# ----------------- PUBLIC FUNCTION -----------------
def check_password():
    """
    This replaces your old password check.
    Now it handles full Supabase authentication.
    """

    restore_session()

    if not st.session_state.logged_in:
        show_login()
        return False

    return True


