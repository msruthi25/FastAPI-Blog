import streamlit as st
from validators import base64
from utils import init_session, create_post, generate_ai_content, analyse_image, get_tech_news_stories, generate_from_news
from pages.header import render_header
import time
import tempfile
import soundfile as sf
import os
import whisper
import tempfile
import os
import platform
import pypdf
import io
import docx 
import base64


# --- 1. INITIALIZATION ---
init_session()

# Persistent state to keep modal open during reruns
if "show_chat_modal" not in st.session_state:
    st.session_state.show_chat_modal = False

if "show_hn_modal" not in st.session_state:
    st.session_state.show_hn_modal = False    

# State for the AI's current work-in-progress (inside modal)
if "ai_draft" not in st.session_state:
    st.session_state.ai_draft = None 

# State for the manual edit toggle inside modal
if "edit_mode" not in st.session_state:
    st.session_state.edit_mode = False

# State for the Final Form Data (what the main page sees)
if "form_data" not in st.session_state:
    st.session_state.form_data = {"title": "", "content": "", "img_url": ""}

if "show_news_modal" not in st.session_state:
    st.session_state.show_news_modal = False
if "news_stories" not in st.session_state:
    st.session_state.news_stories = []
if "selected_source" not in st.session_state:
    st.session_state.selected_source = "hackernews"    

with open("styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

#Helper function for extracting text from uploaded files
def extract_file_content(uploaded_file):
    file_type = uploaded_file.type    
    if "image" in file_type:
        return None, "image"    
    elif "pdf" in file_type:
        reader = pypdf.PdfReader(io.BytesIO(uploaded_file.read()))
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text.strip(), "pdf"
    
    elif "docx" in file_type or "word" in file_type:
        doc = docx.Document(io.BytesIO(uploaded_file.read()))
        text = "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
        return text.strip(), "docx"
    
    return None, "unknown"


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

        # Initialize states
        if "transcribed_text" not in st.session_state:
            st.session_state.transcribed_text = None
        if "awaiting_confirmation" not in st.session_state:
            st.session_state.awaiting_confirmation = False
        if "audio_key" not in st.session_state:
            st.session_state.audio_key = 0
        if "uploaded_image" not in st.session_state:
            st.session_state.uploaded_image = None
        if "uploaded_file_content" not in st.session_state:
            st.session_state.uploaded_file_content = None
        if "uploaded_file_type" not in st.session_state:
            st.session_state.uploaded_file_type = None
        if "uploaded_file" not in st.session_state:
            st.session_state.uploaded_file = None
        if "file_ready" not in st.session_state:
             st.session_state.file_ready = False    

        # --- CONFIRMATION STEP ---
        if st.session_state.awaiting_confirmation and st.session_state.transcribed_text:
            st.info(f"🎙️ Transcribed: **{st.session_state.transcribed_text}**")
            st.write("Is this correct?")

            col_yes, col_no = st.columns(2)

            with col_yes:
                if st.button("✅ Yes, generate post", use_container_width=True):
                    confirmed_text = st.session_state.transcribed_text
                    st.session_state.transcribed_text = None
                    st.session_state.awaiting_confirmation = False

                    st.session_state.messages.append({"role": "user", "content": confirmed_text})
                    with st.spinner("AI Agent is working..."):
                        result = generate_ai_content(confirmed_text, st.session_state.get("token"))
                        if result:
                            st.session_state.ai_draft = result
                            # Override image if user uploaded one
                            if st.session_state.uploaded_image:
                                st.session_state.ai_draft["img_url"] = st.session_state.uploaded_image
                            st.session_state.messages.append({"role": "assistant", "content": "Draft generated! Check it below."})
                        else:
                            st.error("Backend failed to return data.")
                    st.rerun()

            with col_no:
                if st.button("🔄 No, re-record", use_container_width=True):
                    st.session_state.transcribed_text = None
                    st.session_state.awaiting_confirmation = False
                    st.session_state.audio_key += 1
                    st.rerun()

        # --- INPUT ROW ---
        else:
            # Row 1: text input
            prompt = st.chat_input("What should the post be about?")

            # Row 2: mic + image upload side by side
            col_mic, col_img = st.columns([1, 1])

            with col_mic:
                audio_value = st.audio_input(
                    "🎙️ Record voice",
                    key=f"audio_{st.session_state.audio_key}"
                )

            with col_img:
                uploaded_file = st.file_uploader(
                    "📁 Upload file (image / PDF / Word)",
                    type=["jpg", "jpeg", "png", "webp", "pdf", "docx"],
                    label_visibility="visible"
                )
                if not uploaded_file:
                    st.session_state.uploaded_file_content = None
                    st.session_state.uploaded_file_type = None
                    st.session_state.file_ready = False

            if uploaded_file:
                st.session_state.uploaded_file_content = None
                st.session_state.uploaded_file_type = None
                st.session_state.file_ready = False

                file_type = uploaded_file.type
                st.write(f"📎 Uploaded: `{uploaded_file.name}`")

                if "image" in file_type:
                        st.image(uploaded_file, caption="Uploaded image", width=150)
                        with st.spinner("🔍 Analysing image..."):
                            img_bytes = uploaded_file.read()
                            img_b64 = base64.b64encode(img_bytes).decode()
                            description = analyse_image(img_b64, file_type, st.session_state.get("token"))
                            if description:
                                st.success("✅ Image analysed!")
                                st.caption(f"📝 {description[:200]}...")
                                st.session_state.uploaded_file_content = description
                                st.session_state.uploaded_file_type = "image"
                                st.session_state.file_ready = True
                            else:
                                st.error("❌ Could not analyse image")

                elif "pdf" in file_type:
                    content, ftype = extract_file_content(uploaded_file)
                    if content:
                        st.success(f"✅ PDF extracted — {len(content)} characters")
                        st.session_state.uploaded_file_content = content
                        st.session_state.uploaded_file_type = "pdf"
                        st.session_state.file_ready = True
                    else:
                        st.error("❌ Could not extract text from PDF")

                elif "docx" in file_type or "word" in file_type:
                    content, ftype = extract_file_content(uploaded_file)
                    if content:
                        st.success(f"✅ Word doc extracted — {len(content)} characters")
                        st.session_state.uploaded_file_content = content
                        st.session_state.uploaded_file_type = "docx"
                        st.session_state.file_ready = True
                    else:
                        st.error("❌ Could not extract text from Word doc")

            if st.session_state.file_ready and  st.session_state.uploaded_file_content and st.session_state.uploaded_file_type in ["image", "pdf", "docx"]:    
                # Show appropriate message based on file type
                if st.session_state.uploaded_file_type == "image":
                    button_label = "✨ Generate Post from Image"
                    default_prompt = "Generate a blog post based on this image"
                elif st.session_state.uploaded_file_type == "pdf":
                    button_label = "✨ Generate Post from PDF"
                    default_prompt = "Generate a blog post based on this document"
                else:
                    button_label = "✨ Generate Post from Document"
                    default_prompt = "Generate a blog post based on this document"

                if st.button(button_label, use_container_width=True):
                    file_content = st.session_state.uploaded_file_content
                    file_type = st.session_state.uploaded_file_type
                    # Step 2 - build prompt based on file type
                    if file_type == "image":
                        prompt_to_send = f"Generate a blog post.\n\nImage context: {file_content}"
                    else:
                        prompt_to_send = f"Generate a blog post.\n\nDocument content:\n{file_content}"
                    st.session_state.messages.append({"role": "user", "content": prompt_to_send})
                    with st.spinner("AI Agent is working..."):
                        result = generate_ai_content(prompt_to_send, st.session_state.get("token"))
                        if result:
                            st.session_state.ai_draft = result
                            st.session_state.messages.append({"role": "assistant", "content": "Draft generated! Check it below."})
                        else:
                            st.error("Backend failed to return data.")
                    st.rerun()
       

            # --- HANDLE VOICE ---
            if audio_value:
                with st.spinner("Transcribing..."):

                    if platform.system() == "Windows":
                        os.environ["PATH"] = r"C:\Users\sruth\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.0.1-full_build\bin" + os.pathsep + os.environ["PATH"]

                    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                        tmp.write(audio_value.read())
                        tmp_path = tmp.name

                    model = whisper.load_model("base")
                    result = model.transcribe(tmp_path)
                    st.session_state.transcribed_text = result["text"]
                    st.session_state.awaiting_confirmation = True
                    st.rerun()

            # --- HANDLE TEXT ---
            if prompt:
                st.session_state.messages.append({"role": "user", "content": prompt})
                with st.spinner("AI Agent is working..."):
                    result = generate_ai_content(prompt, st.session_state.get("token"))
                    if result:
                        st.session_state.ai_draft = result
                        # Override image if user uploaded one
                        if st.session_state.uploaded_image:
                            st.session_state.ai_draft["img_url"] = st.session_state.uploaded_image
                        st.session_state.messages.append({"role": "assistant", "content": "Draft generated! Check it below."})
                    else:
                        st.error("Backend failed to return data.")
                st.rerun()

@st.dialog("📰 Tech News", width="large")
def news_modal():

    # Source selector
    source = st.selectbox(
        "Select news source:",
        options=["hackernews", "techcrunch", "wired", "ars_technica", "google_tech"],
        format_func=lambda x: {
            "hackernews": "🔶 HackerNews",
            "techcrunch": "🟢 TechCrunch",
            "wired": "⚫ Wired",
            "ars_technica": "🔴 Ars Technica",
            "google_tech": "🔵 Google Tech News"
        }[x],
        key="news_source_select"
    )

    # Fetch button
    col_fetch, col_refresh = st.columns([3, 1])
    with col_fetch:
        fetch_clicked = st.button("🔍 Fetch Stories", use_container_width=True, type="primary")
    with col_refresh:
        if st.button("🔄", use_container_width=True):
            st.session_state.news_stories = []
            st.rerun()

    # Fetch stories
    if fetch_clicked or (st.session_state.news_stories and st.session_state.selected_source == source):
        if fetch_clicked or not st.session_state.news_stories:
            with st.spinner(f"Fetching stories from {source}..."):
                stories = get_tech_news_stories(st.session_state.get("token"), source=source)
                st.session_state.news_stories = stories
                st.session_state.selected_source = source

    # Display stories
    if st.session_state.news_stories:
        st.divider()
        st.write(f"**Top stories from {source}:**")
        for i, story in enumerate(st.session_state.news_stories):
            with st.container():
                col_story, col_btn = st.columns([4, 1])
                with col_story:
                    st.markdown(f"**{i+1}. {story['title']}**")
                    if story.get('summary'):
                        st.caption(f"{story['summary'][:150]}...")
                    if story.get('url'):
                        st.caption(f"🔗 {story['url'][:60]}...")
                with col_btn:
                    if st.button("✨", key=f"news_{i}", use_container_width=True, help="Generate post"):
                        with st.spinner(f"Generating post..."):
                            result = generate_from_news(
                                st.session_state.get("token"),
                                title=story["title"],
                                url=story.get("url", ""),
                                summary=story.get("summary", ""),
                                source=source
                            )
                            if result:
                                st.session_state.form_data = result
                                st.session_state.news_stories = []
                                st.session_state.show_news_modal = False
                                st.rerun()
                            else:
                                st.error("❌ Failed to generate post.")
                st.divider()
    elif fetch_clicked:
        st.error("❌ Could not fetch stories. Try again.")


# --- 3. MAIN PAGE UI ---
render_header()

if st.session_state.logged_in:
    col1, main_col, col3 = st.columns([1, 3, 1])

    with main_col:
        h_col1, h_col2, h_col3 = st.columns([4,1,1])
        with h_col1:
            st.title("📝 Create a New Post")
        with h_col2:
            # Trigger the modal flag
            if st.button("🤖 AI Generate", type="secondary"):
                st.session_state.show_chat_modal = True
                st.session_state.show_news_modal = False 
                st.rerun() 
        with h_col3:
            # Trigger the modal flag
            if st.button("📰 TechNews", type="secondary"):
                st.session_state.show_news_modal = True  
                st.session_state.show_chat_modal = False     
                st.rerun()

        # PERSISTENCE: If the flag is True, the modal is called on every rerun
        if st.session_state.show_news_modal:
            st.session_state.show_chat_modal = False
            news_modal()
        elif st.session_state.show_chat_modal:
            st.session_state.show_news_modal = False
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