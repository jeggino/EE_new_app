# utils/inventarisatie/info_renderer.py

import streamlit as st

def format_value(value):
    if isinstance(value, dict):
        formatted = "<ul>"
        for k, v in value.items():
            formatted += f"<li><strong>{k}:</strong> {v}</li>"
        formatted += "</ul>"
        return formatted

    if isinstance(value, list):
        return ", ".join(str(v) for v in value)

    return str(value)


def render_info_block(title, data: dict):
    st.markdown(f"### {title}")

    if not data:
        st.info("Geen informatie beschikbaar.")
        return

    for key, value in data.items():
        st.markdown(
            f"""
            <div style="
                padding: 10px 15px;
                margin-bottom: 8px;
                border-radius: 6px;
                background-color: #f7f7f9;
                border: 1px solid #e0e0e0;
            ">
                <strong>{key.replace('_', ' ').title()}:</strong><br>
                {format_value(value)}
            </div>
            """,
            unsafe_allow_html=True
        )
