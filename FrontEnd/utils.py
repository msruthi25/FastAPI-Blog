import requests
import streamlit as st

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
        response = requests.get("http://127.0.0.1:8000/posts")
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        st.error(f"Failed to fetch posts: {e}")
        return []
    
def fetch_posts_by_User_ID(user_id):
    try:
        url= f"http://127.0.0.1:8000/postsbyUser/{user_id}"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        st.error(f"Failed to fetch posts: {e}")
        return []
    
def fetch_post_by_id(id):
    try:
        url= f"http://127.0.0.1:8000/posts/{id}"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        st.error(f"Failed to fetch posts: {e}")
        return []

def fetch_comments(id):
    try:       
        url= f"http://127.0.0.1:8000/posts/{id}/comments"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        st.error(f"Failed to fetch posts: {e}")
        return []

def add_comment(content,id,token=None):
    url= f"http://127.0.0.1:8000/posts/{id}/addComment"
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
        headers = {}
        if token:             
            headers = {
                "Authorization": f"{token['token_type'].capitalize()} {token['access_token']}"
            }
        response = requests.post("http://127.0.0.1:8000/createPost", json=post_data,headers=headers)
        return response    
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Error connecting to backend: {e}")  


def update_post(id,post_data,token=None):
    try:
        url= f"http://127.0.0.1:8000/posts/{id}"
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
        url= f"http://127.0.0.1:8000/posts/{id}"
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
        url= f"http://127.0.0.1:8000/user/{user_id}/comments"
        headers = {}
        if token:             
            headers = {
                "Authorization": f"{token['token_type'].capitalize()} {token['access_token']}"
            }
        response = requests.get(url,headers=headers)
        response.raise_for_status()
        return response
    except requests.RequestException as e:
        st.error(f"Failed to fetch posts: {e}")
        return []   
    
def update_comment(comment_id, post_id,content, token=None):
    try:
        url= f"http://127.0.0.1:8000//posts/{post_id}/updateComment/{comment_id}"
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
        url= f"http://127.0.0.1:8000/deleteComment/{id}"
        headers = {}
        if token:             
            headers = {
                "Authorization": f"{token['token_type'].capitalize()} {token['access_token']}"
            }
        response = requests.delete(url,headers=headers)
        return response    
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Error connecting to backend: {e}")  