from turtle import pd
import streamlit as st
from utils import init_session,view_my_comment, update_comment
from pages.header import render_header

init_session()


with open("styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

render_header()


if st.session_state.logged_in:
    response = view_my_comment(st.session_state["user_id"], token=st.session_state["token"])
    col1, col2, col3 = st.columns([1, 3, 1])
    
    with col2:
        data = response.json()
        try:
            if data.get("status") == "success":
                posts = data.get("data", {})
                col1, col2, col3 = st.columns([0.5, 3, 0.5])
                with col2:
                    st.title("📝 View My Comments")                
                for post_id, post_info in posts.items():                    
                    st.markdown(f"### {post_info.get('post_title', 'Untitled Post')}")                   
                    for i, comment in enumerate(post_info.get("comments", []), start=1):
                        comment_id = comment.get("comment_id")  
                        comment_content = comment.get("content") 
                        success_key = f"edit_success_{post_id}_{comment_id}"                      
                        if st.session_state.get(success_key, False):
                            st.success(f"Comment successfully edited!")
                            st.session_state[success_key] = False                         
                        with st.container():
                            col1, col2, col3 = st.columns([6, 0.5, 1])                      
                            edit_key = f"edit_{post_id}_{i}"
                            
                            with col1:                               
                                if st.session_state.get(edit_key, False):  
                                    comment_text = st.text_area(
                                        f"Edit Comment here",
                                        value=comment_content,
                                        key=f"textarea_{post_id}_{i}",
                                        height=100
                                    )                                    
                                    if st.button(f"Save Comment", key=f"save_{post_id}_{i}"):
                                        st.session_state[edit_key] = False 
                                        st.session_state[f"comment_{post_id}_{i}"] = comment_text
                                        
                                        data = {"content": st.session_state[f"comment_{post_id}_{i}"]}
                                        response = update_comment(comment_id, post_id, data, token=st.session_state["token"])
                                        
                                        if response.status_code == 200:
                                            data = response.json()
                                            if data["status"] == "success":
                                                st.session_state[success_key] = True  
                                            else:
                                                st.error(f"⚠️ Failed to edit comment: {response.text}")
                                        st.rerun() 
                                else:                                    
                                    st.markdown(f"""
                                    <div style='padding:10px; margin-bottom:5px; background-color:#f0f2f6; 
                                                border-radius:5px'>
                                        {comment_content}
                                    </div>
                                    """, unsafe_allow_html=True)
                            with col2:
                                # Edit button
                                if st.button("✏️", key=f"edit_button_{post_id}_{i}", help="Edit"):
                                    st.session_state[edit_key] = True
                                    st.rerun() 
                            with col3:
                                # Delete button
                                if st.button("🗑️", key=f"delete_button_{post_id}_{i}", help="Delete"):
                                    st.warning(f"Delete clicked for comment in post")                                    
                    st.markdown("<hr>", unsafe_allow_html=True)
            else:
                st.warning("No comments found.")
        except Exception as e:
            st.error(f"⚠️ Failed to View Comment: {e}")
        
        st.markdown(f"""<hr class="post-divider">""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
else:
    st.warning("Login to View Your Post")

