import streamlit as st

def section_title(title, subtitle=None):
    st.subheader(title)
    if subtitle: st.caption(subtitle)
