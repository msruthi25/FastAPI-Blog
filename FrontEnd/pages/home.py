import streamlit as st
import requests
from pages.login import login_dialog,signup_dialog
from pages.posts import show_all_posts
from utils import init_session
from pages.header import render_header

init_session()
st.set_page_config(page_title="My Tech Blog", layout="wide")

with open("styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("🚫 You must be logged in to access this page.")
    st.stop()

render_header()
show_all_posts()

st.markdown("  ")
st.caption("© 2025 MyApp. All rights reserved.")
