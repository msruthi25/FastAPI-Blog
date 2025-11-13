import streamlit as st
from utils import init_session,create_post,update_post
from pages.header import render_header
import requests

init_session()


with open("styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

render_header()

if st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 3, 1])

    with col2:
        post=st.session_state["edit_post"] 
        st.title("📝 Edit Post")        
        with st.form("create_post_form",clear_on_submit=True):
            st.subheader("Edit Post Details")
            title = st.text_input("Post Title", value=post["title"])
            content = st.text_area("Content", value=post["content"], height=400)
            img_url = st.text_input("Image URL (Required)", value=post["img_url"])           
            submitted = st.form_submit_button("💾 Save Changes")
            if submitted:                    
                    post["title"] = title
                    post["content"] = content
                    post["img_url"] = img_url
                    response=update_post(post["id"],post,token=st.session_state.token)
                    if response.status_code == 200:
                        data=response.json()
                        if data["status"] == "success":   
                            st.session_state.edit_post_flag=True      
                            st.session_state["selected_post"] = post["id"]       
                            st.switch_page("pages/post_detail.py")
                        else:
                            st.error(f"⚠️ Failed to create post: {response.text}")                             
                    
else:
    st.warning("Login to Edit Post")