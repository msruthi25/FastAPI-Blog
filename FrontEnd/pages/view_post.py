import streamlit as st
from utils import init_session,delete_post,create_post,fetch_posts_by_User_ID,fetch_post_by_id
from pages.header import render_header
from streamlit_product_card import product_card 
import requests


init_session()

with open("styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


render_header()

if st.session_state.post_deleted:
                st.success("✅ Posted Deleted successfully!")
                st.session_state.post_deleted = False  


@st.dialog("Confirm Deletion")
def confirm_delete(post_id):
    st.write("Are you sure you want to permanently delete this post? This action cannot be undone.")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Cancel", use_container_width=True):
            st.rerun() 

    with col2:
        if st.button("Delete", type="primary", use_container_width=True):            
            response=delete_post(post_id,token=st.session_state["token"])
            try:
                if response.status_code == 200:
                        data=response.json()                      
                        st.session_state.post_deleted=True      
                        st.rerun()
                else:
                     try:
                        data = response.json()
                        st.error(f"⚠️ Failed to delete post: {data.get('message', response.text)}")
                     except:
                        st.error(f"⚠️ Failed to delete post: {response.text}")          
            except Exception as e:
                st.error(f"⚠️ Failed to delete post: {e}")

if st.session_state.logged_in:
    st.markdown("<h2 style='text-align:center;'>📝  Your Posts</h2>", unsafe_allow_html=True)
    user_id=st.session_state["user_id"]
    posts =fetch_posts_by_User_ID(user_id,token=st.session_state["token"])
    headercol1,headercol2,headercol3 =st.columns([1,2,1])
    with headercol2:
        st.markdown('<div class="cards-container">', unsafe_allow_html=True)  # Start container
        for i,post in enumerate(posts):
            with st.container():
                container = st.container()
                col1, col2, col3, col4 = container.columns([6, 1, 1, 1])
                with col1:
                    st.write(f"**{post['title']}**")
                with col2:
                  if st.button("📖", help="View Post",key=f"view_{i}"):
                    st.session_state["selected_post"] = post["id"]
                    st.switch_page("pages/post_detail.py")                     
                with col3:
                   if st.button("✏️", help="Edit",key=f"edit_{i}"):
                        st.session_state["edit_post"]=post
                        st.switch_page("pages/editPost.py")
                with col4:
                    if st.button("🗑️",help="Delete",key=f"delete_{i}"):
                         confirm_delete(post_id=post["id"])
                         
                       
            st.markdown(f"""
                  
                <hr class="post-divider">
            """, unsafe_allow_html=True)             
        st.markdown('</div>', unsafe_allow_html=True)



else:
    st.warning("Login to View Your Post")    