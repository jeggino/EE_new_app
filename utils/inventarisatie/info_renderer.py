import streamlit as st


def pretty_label(key: str) -> str:
    """Convert snake_case into 'Title Case' without underscores."""
    return " ".join(word.capitalize() for word in key.split("_"))


def render_nested_dict(title, data: dict):
    """Simple, safe renderer for nested survey info."""

    st.markdown(f"### {title}")

    # If empty or None → show nothing
    if not data:
        st.info("Geen survey informatie beschikbaar.")
        return

    # If not nested → show nothing
    if any(not isinstance(v, dict) for v in data.values()):
        st.info("Geen gedetailleerde survey informatie beschikbaar.")
        return

    # Render each section
    for section, values in data.items():
        st.markdown(f"**{pretty_label(section)}**")

        # Simple bullet list
        for key, value in values.items():
            st.markdown(f"- **{pretty_label(key)}:** {value}")

        st.markdown("---")  # simple divider


def render_info_block(title, data: dict):
    """Simple renderer for flat dictionaries."""

    st.markdown(f"### {title}")

    if not data:
        st.info("Geen informatie beschikbaar.")
        return

    for key, value in data.items():
        st.markdown(f"- **{pretty_label(key)}:** {value}")


