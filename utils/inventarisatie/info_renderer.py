import streamlit as st


def pretty_label(key: str) -> str:
    """Convert snake_case into 'Title Case' without underscores."""
    return " ".join(word.capitalize() for word in key.split("_"))


def render_survey_info(title, data: dict):
    """Render ANY survey structure safely and cleanly."""

    st.markdown(f"### {title}")

    if not data:
        st.info("Geen survey informatie beschikbaar.")
        return

    # Loop through top-level categories (vleermuizen, gierzwaluwen, etc.)
    for category, value in data.items():
        st.markdown(f"**{pretty_label(category)}**")

        # Case 1: value is None
        if value is None:
            st.write("- Geen gegevens")
            st.markdown("---")
            continue

        # Case 2: value is a flat dict
        if isinstance(value, dict) and all(not isinstance(v, dict) for v in value.values()):
            for key, val in value.items():
                st.write(f"- **{pretty_label(key)}:** {val}")
            st.markdown("---")
            continue

        # Case 3: value is a nested dict (avond/ochtend/paarperiode)
        if isinstance(value, dict):
            for subkey, subval in value.items():
                st.markdown(f"- **{pretty_label(subkey)}**")
                if isinstance(subval, dict):
                    for k, v in subval.items():
                        st.write(f"  - **{pretty_label(k)}:** {v}")
                else:
                    st.write(f"  - {subval}")
            st.markdown("---")
            continue

        # Case 4: fallback for unexpected types
        st.write(f"- {value}")
        st.markdown("---")




def render_info_block(title, data: dict):
    """Simple, safe renderer for flat dictionaries (klant info)."""

    st.markdown(f"### {title}")

    # If empty or None → show friendly message
    if not data:
        st.info("Geen informatie beschikbaar.")
        return

    # Loop through fields
    for key, value in data.items():

        # None → show friendly message
        if value is None:
            st.write(f"- **{pretty_label(key)}:** Geen gegevens")
            continue

        # Lists → join nicely
        if isinstance(value, list):
            st.write(f"- **{pretty_label(key)}:** {', '.join(str(v) for v in value)}")
            continue

        # Everything else → print normally
        st.write(f"- **{pretty_label(key)}:** {value}")









