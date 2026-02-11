import requests
import streamlit as st
import os
from dotenv import load_dotenv


load_dotenv()

def init_session():
    st.session_state.setdefault("logged_in", False)
    st.session_state.setdefault("user", None)
    st.session_state.setdefault("user_id", None)
    st.session_state.setdefault("token", None)
    st.session_state.setdefault("email", None)
    st.session_state.setdefault("comment_posted", None)
    st.session_state.setdefault("create_post",None)
    st.session_state.setdefault("edit_post",None)
    st.session_state.setdefault("edit_post_flag",None)
    st.session_state.setdefault("selected_post",None)
    st.session_state.setdefault("post_deleted",None)
    st.session_state.setdefault("comment_input",None)
    st.session_state.setdefault("comment_delete",None)
    st.session_state.setdefault("success_key",None)
    st.session_state.setdefault("account_register",None)
    st.session_state.setdefault("success_key_comment",None)


def fetch_posts():
    try:
        API_URL=os.getenv("API_URL")
        response = requests.get(f"{API_URL}/posts")
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        st.error(f"Failed to fetch posts: {e}")
        return []
    
def fetch_posts_by_User_ID(user_id,token=None):
    try:
        API_URL=os.getenv("API_URL")
        url= f"{API_URL}/postsbyUser/{user_id}"
        headers = {}
        if token:             
            headers = {
                "Authorization": f"{token['token_type'].capitalize()} {token['access_token']}"
            }
        response = requests.get(url, headers=headers)
        if response.status_code==404:
            st.warning("No posts created")
            return []
        response.raise_for_status()    
        return response.json()
    except requests.RequestException as e:
        st.error(f"Failed to fetch posts: {e}")
        return []
    
def fetch_post_by_id(id):
    try:
        API_URL=os.getenv("API_URL")
        url= f"{API_URL}/posts/{id}"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        st.error(f"Failed to fetch posts: {e}")
        return []

def fetch_comments(id):
    try:       
        API_URL=os.getenv("API_URL")
        url= f"{API_URL}/posts/{id}/comments"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        st.error(f"Failed to fetch posts: {e}")
        return []

def add_comment(content,id,token=None):
    API_URL=os.getenv("API_URL")
    url= f"{API_URL}/posts/{id}/addComment"
    data = {
        "content": content
    }
    headers = {}
    if token:             
        headers = {
            "Authorization": f"{token['token_type'].capitalize()} {token['access_token']}"
        }
    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()  
        return response.json()       
    except requests.RequestException as e:
        st.error(f"Failed to post comment: {e}")
        return None

def create_post(post_data,token=None):
    try:
        API_URL=os.getenv("API_URL")
        headers = {}
        if token:             
            headers = {
                "Authorization": f"{token['token_type'].capitalize()} {token['access_token']}"
            }
        response = requests.post(f"{API_URL}/createPost", json=post_data,headers=headers)
        return response    
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Error connecting to backend: {e}")  


def update_post(id,post_data,token=None):
    try:
        API_URL=os.getenv("API_URL")
        url= f"{API_URL}/posts/{id}"
        headers = {}
        if token:             
            headers = {
                "Authorization": f"{token['token_type'].capitalize()} {token['access_token']}"
            }
        response = requests.put(url,json=post_data,headers=headers)
        return response    
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Error connecting to backend: {e}")  


def delete_post(id,token=None):
    try:
        API_URL=os.getenv("API_URL")
        url= f"{API_URL}/posts/{id}"
        headers = {}
        if token:             
            headers = {
                "Authorization": f"{token['token_type'].capitalize()} {token['access_token']}"
            }
        response = requests.delete(url,headers=headers)
        return response    
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Error connecting to backend: {e}")  



def view_my_comment(user_id,token):     
    try:
        API_URL=os.getenv("API_URL")
        url= f"{API_URL}/user/{user_id}/comments"
        headers = {}
        if token:             
            headers = {
                "Authorization": f"{token['token_type'].capitalize()} {token['access_token']}"
            }
        response = requests.get(url,headers=headers)
        if response.status_code==404:
            st.warning("No Comments created")
            return []
        response.raise_for_status()
        return response
    except requests.RequestException as e:
        st.error(f"Failed to fetch posts: {e}")
        return []   
    
def update_comment(comment_id, post_id,content, token=None):
    try:
        API_URL=os.getenv("API_URL")
        url= f"{API_URL}/posts/{post_id}/updateComment/{comment_id}"
        headers = {}
        if token:             
            headers = {
                "Authorization": f"{token['token_type'].capitalize()} {token['access_token']}"
            }
        response = requests.put(url,json=content,headers=headers)
        return response    
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Error connecting to backend: {e}")  


def delete_comment(id,token=None):
    try:
        API_URL=os.getenv("API_URL")
        url= f"{API_URL}/deleteComment/{id}"
        headers = {}
        if token:             
            headers = {
                "Authorization": f"{token['token_type'].capitalize()} {token['access_token']}"
            }
        response = requests.delete(url,headers=headers)
        return response    
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Error connecting to backend: {e}")  


#AI Agent Code
def generate_ai_content(prompt, token):
    API_URL=os.getenv("API_URL")
    url= f"{API_URL}/agent"
    headers = {}
    payload = {"input":prompt}
    if token:             
        headers = {
            "Authorization": f"{token['token_type'].capitalize()} {token['access_token']}"
        }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
           data = response.json()
           return {
                "title": data.get("title", ""),
                "content": data.get("content", ""),
                "img_url": data.get("img_url", "")
            }
    except Exception as e:
        return f"Connection Failed: {str(e)}"        