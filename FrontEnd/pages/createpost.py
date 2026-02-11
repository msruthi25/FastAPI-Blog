import streamlit as st
from utils import init_session, create_post, generate_ai_content
from pages.header import render_header
import time

# --- 1. INITIALIZATION ---
init_session()

# Persistent state to keep modal open during reruns
if "show_chat_modal" not in st.session_state:
    st.session_state.show_chat_modal = False

# State for the AI's current work-in-progress (inside modal)
if "ai_draft" not in st.session_state:
    st.session_state.ai_draft = None 

# State for the manual edit toggle inside modal
if "edit_mode" not in st.session_state:
    st.session_state.edit_mode = False

# State for the Final Form Data (what the main page sees)
if "form_data" not in st.session_state:
    st.session_state.form_data = {"title": "", "content": "", "img_url": ""}

with open("styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# --- 2. THE MODAL LOGIC ---
@st.dialog("AI Content Assistant", width="large")
def chat_modal():
    message_container = st.container(height=250)
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display Chat History
    with message_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # --- REVIEW & EDIT PHASE (Appears after AI responds) ---
    if st.session_state.ai_draft:
        st.divider()
        
        if st.session_state.edit_mode:
            st.session_state.ai_draft["title"] = st.text_input("Edit Title", value=st.session_state.ai_draft["title"])
            st.session_state.ai_draft["content"] = st.text_area("Edit Content", value=st.session_state.ai_draft["content"], height=200)
            st.session_state.ai_draft["img_url"] = st.text_input("Edit Image URL", value=st.session_state.ai_draft["img_url"])
        else:
            st.subheader(f"Title: {st.session_state.ai_draft['title']}")
            if st.session_state.ai_draft["img_url"]:
                st.image(st.session_state.ai_draft["img_url"], caption="AI Suggested Image", width=400)
            st.markdown(st.session_state.ai_draft["content"])

        col_acc, col_reg, col_edt = st.columns(3)

        # ACTION: ACCEPT (Close modal and fill form)
        if col_acc.button("✅ Accept All", use_container_width=True):
            st.session_state.form_data = st.session_state.ai_draft
            st.session_state.ai_draft = None
            st.session_state.show_chat_modal = False  # Close the gate
            st.rerun()

        # ACTION: REGENERATE (Call backend again)
        if col_reg.button("🔄 Regenerate", use_container_width=True):
            with st.spinner("Agent is regenerating..."):
                last_prompt = next((m["content"] for m in reversed(st.session_state.messages) if m["role"]=="user"), "")
                st.session_state.ai_draft = generate_ai_content(last_prompt, st.session_state.get("token"))
                st.rerun()

        # ACTION: EDIT TOGGLE
        if col_edt.button("📝 Edit" if not st.session_state.edit_mode else "👁️ Preview", use_container_width=True):
            st.session_state.edit_mode = not st.session_state.edit_mode
            st.rerun()

    # --- INPUT PHASE ---
    if not st.session_state.ai_draft:
        if prompt := st.chat_input("What should the post be about?"): 
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.spinner("AI Agent is working..."):
                # Call your backend util (Expects dict with title, content, img_url)
                result = generate_ai_content(prompt, st.session_state.get("token"))
                if result:
                    st.session_state.ai_draft = result
                    st.session_state.messages.append({"role": "assistant", "content": "Draft generated! Check it below."})
                else:
                    st.error("Backend failed to return data.")
                st.rerun()

# --- 3. MAIN PAGE UI ---
render_header()

if st.session_state.logged_in:
    col1, main_col, col3 = st.columns([1, 3, 1])

    with main_col:
        h_col1, h_col2 = st.columns([3, 1])
        with h_col1:
            st.title("📝 Create a New Post")
        with h_col2:
            # Trigger the modal flag
            if st.button("✨ Generate Post using AI", type="secondary"):
                st.session_state.show_chat_modal = True

        # PERSISTENCE: If the flag is True, the modal is called on every rerun
        if st.session_state.show_chat_modal:
            chat_modal()

        # THE MAIN FORM
        with st.form("create_post_form", clear_on_submit=True):
            st.subheader("Post Details")
            
            # These values come from session_state.form_data (updated by the modal)
            f_title = st.text_input("Post Title", value=st.session_state.form_data["title"])
            f_content = st.text_area("Content", value=st.session_state.form_data["content"], height=300)
            f_img_url = st.text_input("Image URL", value=st.session_state.form_data["img_url"])
            
            submitted = st.form_submit_button("📤 Publish Post")

        if submitted:
            if not f_title.strip() or not f_content.strip():
                st.error("❌ Title and Content are required.")
            else:
                post_data = {
                    "title": f_title.strip(),
                    "content": f_content.strip(),
                    "img_url": f_img_url.strip() if f_img_url else None,
                    "published": True
                }
                response = create_post(post_data=post_data, token=st.session_state["token"])
                if response.status_code == 200:
                    st.success("✅ Post Created Successfully!")
                    # Clear form data for the next run
                    st.session_state.form_data = {"title": "", "content": "", "img_url": ""}
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error(f"Error: {response.text}")

else:
    st.warning("Please login to create a post.")