# utils/inventarisatie/info_renderer.py

import streamlit as st


def pretty_label(key: str) -> str:
    """Convert snake_case into 'Title Case' without underscores."""
    return " ".join(word.capitalize() for word in key.split("_"))


def render_nested_dict(title, data: dict):
    """Render nested dictionaries (like avond/ochtend/paarperiode) professionally."""

    st.markdown(f"### {title}")

    if not data:
        st.info("Geen informatie beschikbaar.")
        return

    for section, values in data.items():

        st.markdown(
            f"""
            <div style="
                padding: 14px 18px;
                margin-bottom: 12px;
                border-radius: 8px;
                background-color: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.15);
                backdrop-filter: blur(4px);
            ">
                <div style="font-size: 16px; font-weight: 600; margin-bottom: 8px;">
                    {pretty_label(section)}
                </div>
            """,
            unsafe_allow_html=True
        )

        for key, value in values.items():
            st.markdown(
                f"""
                <div style="
                    margin-left: 10px;
                    margin-bottom: 6px;
                    font-size: 14px;
                ">
                    <strong>{pretty_label(key)}:</strong> {value}
                </div>
                """,
                unsafe_allow_html=True
            )

        st.markdown("</div>", unsafe_allow_html=True)



def render_info_block(title, data: dict):
    st.markdown(f"### {title}")

    if not data:
        st.info("Geen informatie beschikbaar.")
        return

    for key, value in data.items():
        st.markdown(
            f"""
            <div style="
                padding: 12px 16px;
                margin-bottom: 10px;
                border-radius: 8px;
                background-color: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.15);
                backdrop-filter: blur(4px);
            ">
                <strong style="font-size: 15px;">
                    {pretty_label(key)}:
                </strong>
                <div style="margin-top: 4px; font-size: 14px;">
                    {value}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
