import streamlit as st
import requests
from utils import init_session


init_session()

@st.dialog("🔑 Login to My Tech Blog")
def login_dialog():
    email = st.text_input("Email", key="login_email")
    password = st.text_input("Password", type="password", key="login_password")

    if st.button("Login", key="login_submit"):
        if email  and password:
            response = requests.post(f"http://127.0.0.1:8000/login", json={"email": email, "password": password})
            if response.status_code == 200:
                token = response.json()["access_token"]
                username=response.json()["username"]
                st.session_state["token"] = token
                st.session_state["email"] = email
                st.session_state["user"] = username
                st.session_state["user_id"]=response.json()["user_id"]               
                st.session_state["logged_in"]=True      
                st.rerun()    
            else:
                st.error(response.json().get("detail", "Login failed"))        
        else:
            st.error("❌ Invalid credentials")

@st.dialog("🆕 Create Account")
def signup_dialog():
    new_username = st.text_input("Choose a username", key="signup_username")
    email = st.text_input("Email", key="signup_email")
    new_password = st.text_input("Create a password", type="password", key="signup_password")
    confirm_password = st.text_input("Confirm password", type="password", key="signup_confirm")
    agree = st.checkbox("I agree to the Terms and Conditions", key="terms")

    if st.button("Create Account", key="signup_submit"):
        if not agree:
            st.warning("⚠️ You must agree to the terms.")
        elif new_password != confirm_password:
            st.error("❌ Passwords do not match.")
        elif new_username and email and new_password:
            try:
                response = requests.post(
                    "http://127.0.0.1:8000/register",
                    json={"email": email, "username": new_username, "password": new_password},
                )                
                if response.status_code == 200:
                    st.session_state["account_register"]=True
                    st.rerun()
                elif response.status_code == 400:
                    st.error("❌ This email or username is already taken.")
                else:
                    st.error(f"❌ Error: {response.text}")
            except requests.exceptions.RequestException as e:
                st.error(f"⚠️ An error occurred: {str(e)}")        
        else:
            st.error("❌ Please fill out all fields.")
