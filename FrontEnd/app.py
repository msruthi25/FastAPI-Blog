import streamlit as st
import requests
from pages.login import login_dialog, signup_dialog
from pages.posts import show_all_posts
from pages.header import render_header
from utils import init_session


init_session()
st.set_page_config(page_title="My Tech Blog", layout="wide")

with open("styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
 

render_header()

if st.session_state["account_register"]:
    st.success("Account Created Successfully! Login to access Account")
    st.session_state["account_register"]=False

show_all_posts()
st.markdown("<br>", unsafe_allow_html=True)
st.caption("© 2025 MyApp. All rights reserved.")