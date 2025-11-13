import streamlit as st
from utils import init_session,create_post
from pages.header import render_header
import requests

init_session()


with open("styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

render_header()

if st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 3, 1])

    with col2:
        st.title("📝 Create a New Post")        
        with st.form("create_post_form",clear_on_submit=True):
            st.subheader("Enter Post Details")
            title = st.text_input("Post Title", placeholder="Enter your post title")
            content = st.text_area("Content", placeholder="Write your post content here...", height=200)
            img_url = st.text_input("Image URL (Required)", placeholder="https://example.com/image.jpg")            
            submitted = st.form_submit_button("📤 Submit Post")
        if submitted:
            if not title.strip() or not content.strip():
                st.error("❌ Please fill in both Title and Content.")
            else:            
                post_data = {
                    "title": title.strip(),
                    "content": content.strip(),
                    "img_url": img_url.strip() if img_url else None,
                    "published":True
                }
                response=create_post(post_data=post_data,token=st.session_state["token"])
                if response.status_code == 200:
                    data=response.json()
                    if data["status"] == "success":   
                        st.session_state.create_post=True             
                        st.rerun()
                    else:
                        st.error(f"⚠️ Failed to create post: {response.text}")
        if st.session_state.create_post:
                st.success("✅ Comment posted successfully!")
                st.session_state.create_post = False                  
else:
    st.warning("Login to Create Post")
        
  