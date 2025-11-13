import streamlit as st
from utils import fetch_posts
from streamlit_product_card import product_card 

def show_all_posts():
    st.markdown("<h2 style='text-align:center;'>Latest Posts</h2>", unsafe_allow_html=True)
    posts = fetch_posts()

    st.markdown('<div class="cards-container">', unsafe_allow_html=True)  # Start container
    col1, col2, col3 = st.columns([1, 3, 1])

    with col2:
        for post in posts:
            clicked = product_card(
                product_name=post['title'],
                description=post['content'][:150] + "....",
                price="",
                button_text="Read More",
                product_image=post['img_url'],
                key=f"post_{post['id']}",
                picture_position="right",
                image_aspect_ratio="30%",
                image_object_fit="contain",
                styles={
                    "button": {"background-color": "black", "color": "#fff", "font-weight": "bold"}
                }
            )

            if clicked:
                st.session_state["selected_post"] = post["id"]
                st.switch_page("pages/post_detail.py")
    st.markdown('</div>', unsafe_allow_html=True)

