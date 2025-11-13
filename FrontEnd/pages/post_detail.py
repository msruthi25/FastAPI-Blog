import streamlit as st
from utils import fetch_post_by_id,fetch_comments,add_comment
from pages.header import render_header
from datetime import datetime 
from utils import init_session
from pages.login import login_dialog

init_session()

# --- Load custom CSS ---
with open("styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)



render_header()

post_id=st.session_state["selected_post"]
post = fetch_post_by_id(post_id)
if not post:
    st.error("Post not found!")
    st.stop()

if st.session_state.edit_post_flag:
                st.success("✅ Your Post Updated successfully!")
                st.session_state.edit_post_flag = False   

created_at_str = str(post['created_at']).replace('T', ' ')  # normalize ISO format
try:
    post_date = datetime.strptime(created_at_str, "%Y-%m-%d %H:%M:%S").strftime("%B %d, %Y")
except ValueError:
    post_date = datetime.strptime(created_at_str, "%Y-%m-%d").strftime("%B %d, %Y")

username = post['username'].capitalize()
st.markdown(f"""
<div class="post-detail-container">
    <h1 class="post-title">{post['title']}</h1>
    <p class="meta-info">By <strong style="color:purple">{username} </strong>| {post_date}</p>
    <img src="{post['img_url']}" class="post-detail-image" alt="Post image">
    <div class="post-content-full">{post['content']}</div>
</div>
""", unsafe_allow_html=True)



st.markdown(f"""<hr class="section-divider"></p>""", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 2, 1])

with col2:    
    st.markdown(
        """
        <div style="
            padding :0px;
        ">
            <h3 style= color:#333; margin:0px 15px 0px;">💬 Leave a Comment</h3>
        </div>
        """,
        unsafe_allow_html=True
    )
    user_token = st.session_state.get("token") 
    if st.session_state["user"] and st.session_state["logged_in"]==True:
        new_comment = st.text_area("Write your comment here...", height=200)  
        
        if st.button("Add Comment", use_container_width=True):
            if new_comment.strip():
                response=add_comment(new_comment.strip(),post_id,token=user_token)
                if response['status']=="success":
                 st.session_state.comment_posted = True             
                 st.rerun()
                else:
                 st.warning("⚠️ Issue with posting Comment! Try Again")                   
            else:
                st.warning("⚠️ Comment cannot be empty.")
        if st.session_state.comment_posted:
            st.success("✅ Comment posted successfully!")
            st.session_state.comment_posted = False        
    else: 
        CSS = """
        /* Make Streamlit button look like a gray block */
        div[class*="st-key-block_signin"] .stButton button {
            background-color:  #2b2b2b;                    
            padding: 12px 16px;             
            border-radius: 6px;
            font-family: "Source Sans Pro", sans-serif;
            font-size: 1em;
            display: flex;                  /* Align icon + text */
            align-items: center;
            justify-content: flex-start;
            cursor: pointer;
            border: none;
            transition: background-color 0.2s ease;
            width: 100%;                    /* Full width block */
            text-align: left;
        }

        /* Hover effect */
        div[class*="st-key-block_signin"] .stButton button:hover {
            background-color: #9e9c9c;
        }

        /* Emoji / icon styling */
        div[class*="st-key-block_signin"] .stButton button span.icon {
            margin-right: 10px;
            font-size: 1.2em;
        }
        """
        st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)

    
        button_html = f"⚠️ Do you want to comment on this article? You need to be  :red[**signed in**]  for this feature."

        if st.button(button_html, key="block_signin"):
            login_dialog()




# --- Comments Section ---
comments=fetch_comments(post_id)
st.markdown('<div class="comment-section"><h3>Comments</h3><hr style="margin:0px; border:none solid #ccc;">', unsafe_allow_html=True)
st.markdown('<div class="comments-list-container">', unsafe_allow_html=True)
if len(comments)>0:
    for comment in comments:
        created_at_str = str(comment["created_at"]).replace("T", " ")
        try:
            comment_date = datetime.strptime(created_at_str, "%Y-%m-%d %H:%M:%S").strftime("%B %d, %Y at %I:%M %p")
        except ValueError:
            comment_date = datetime.strptime(created_at_str, "%Y-%m-%d").strftime("%B %d, %Y")

        author = comment["username"].upper()

        st.markdown(f"""
        <div class="comments-list-container">         
            <p class="comment-author">{author}</p>
            <p class="comment-date">{comment_date}</p>
            <p class="comment-content">{comment['content']}</p>
            <hr class="comment-divider"></p>
        """, unsafe_allow_html=True)
else:
    st.markdown(f"""
        <div class="comments-list-container">         
            <p class="comment-author">No Comments Yet!</p>
           
        """, unsafe_allow_html=True)   
    
st.markdown("</div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)