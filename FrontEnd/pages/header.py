import streamlit as st
from pages.login import login_dialog, signup_dialog
from utils import init_session
from streamlit_extras.stylable_container import stylable_container

init_session()
with open("styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
def render_header():
    header_col1, header_col2,header_col3 = st.columns([1,2,1])
    with header_col1:
        st.markdown("<h1  style='font-size:28px;'>🧠 My Tech Blog</h1>", unsafe_allow_html=True)
    with header_col2:
        with st.container(horizontal=True): 
                st.space("stretch")
                if  st.session_state.logged_in:
                    col1, col2, col3, col4= st.columns([1,1,1,1])  
                    with col1:                         
                        CSS = """
                        div[class*="st-key-group1"] .stButton button {
                            background: #ffffff;
                            border: none; 
                            color:#31333f !important;                               
                            text-align: center;
                            text-decoration: none;
                            display: inline-block;
                            font-size: 16px;                                
                            transition-duration: 0.4s;
                            cursor: pointer; 
                        }div[class*="st-key-group1"] .stButton button:hover{
                                background-color: #ffffff !important;                     
                            }                         
                        """
                        st.html(f"<style>{CSS}</style>")
                        if st.button(f"**Comment**", key="group1-i"):                                 
                                    st.switch_page("pages/view_comments.py")                      
                            
                    with col2:
                        if st.button(f"**All posts**", key="group1-f"):                                 
                                    st.switch_page("pages/home.py") 
                    with col3:
                        if st.button(f"**My posts**", key="group1-g"):                                 
                                    st.switch_page("pages/view_post.py")
                    with col4:
                        if st.button(f"**Write Post**", key="group1-h"):                                 
                                    st.switch_page("pages/createpost.py")
    with header_col3:  
       with st.container(horizontal=True): 
            st.space("stretch") 
            if not st.session_state.logged_in:
                if st.button("🔐 Login"):
                    login_dialog()
            if not st.session_state.logged_in:
                if st.button("🆕 Sign Up"):
                    signup_dialog()                             
            if  st.session_state.logged_in:        
                col1, col2 = st.columns([1,1])                                 
                with col1:
                    with stylable_container(
                            key="black_popover",
                            css_styles="""
                                button{
                                    background-color: black;
                                    color: white;
                                    padding: 0.6rem 1.2rem;
                                    font-size: 16px;
                                    border: none;
                                    border-radius: 8px;
                                    cursor: pointer;
                                    transition: background-color 0.6s ease;                      
                                }
                                button:hover{
                                    background-color: #2b2828 !important;                     
                                }"""):
                            po = st.popover(label='My Account')                           
                            po.markdown(f"**Hi, {st.session_state['user'].capitalize()}**") 
                            if po.button(f"📃**View All posts**", key="group1-a"):                                 
                                 st.switch_page("pages/home.py")
                            po.markdown("""<hr class="popover-divider">""", unsafe_allow_html=True)
                            if po.button(f"📃**View My posts**", key="group1-b"):                                 
                                  st.switch_page("pages/view_post.py")
                            po.markdown("""<hr class="popover-divider">""", unsafe_allow_html=True) 
                            if po.button(f"💬**View My Comments**", key="group1-c"):                                 
                                 st.switch_page("pages/view_comments.py")
                            po.markdown("""<hr class="popover-divider">""", unsafe_allow_html=True)         
                            if po.button(f"**📝Write Post**", key="group1-e"):                                 
                                  st.switch_page("pages/createpost.py")
                            po.markdown("""<hr class="popover-divider">""", unsafe_allow_html=True)     
                            if po.button(f"🔓**Sign Out**", key="group1-d"):
                                st.session_state.logged_in = False
                                st.session_state.token = ""
                                st.session_state.user = None
                                st.switch_page("app.py")                                                      
                    
                with col2:
                        if st.button("Logout"):
                            st.session_state.logged_in = False
                            st.session_state.token = ""
                            st.session_state.user = None
                            st.switch_page("app.py")  
    st.markdown(
    """
    <hr style="border: 0; height: 1px; background-color: #e0e0e0; margin: 20px 0;">
    """,
    unsafe_allow_html=True
)

