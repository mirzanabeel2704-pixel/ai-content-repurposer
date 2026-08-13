import os
import streamlit as st
from groq import Groq
from dotenv import load_dotenv
from pypdf import PdfReader
from docx import Document

load_dotenv()

# Page config
st.set_page_config(
    page_title="AI Content Repurposer Pro",
    page_icon="⚡",
    layout="wide"
)

# Custom Styling
st.markdown("""
<style>
    .main-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-title {
        font-size: 1.1rem;
        color: #4B5563;
        text-align: center;
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">⚡ AI Content Repurposer Pro</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Transform 1 piece of content into 5+ high-performing formats in seconds.</div>', unsafe_allow_html=True)

# API Key Retrieval
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    try:
        api_key = st.secrets["GROQ_API_KEY"]
    except Exception:
        api_key = None

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    if not api_key:
        api_key = st.text_input("Enter Groq API Key", type="password")
        st.info("Get your free key from [console.groq.com](https://console.groq.com)")
    else:
        st.success("API Key Loaded Successfully! ✅")

    model = st.selectbox(
        "Select Model",
        ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768"],
        index=0
    )

# Function to extract text from uploaded files
def extract_text(uploaded_file):
    text = ""
    if uploaded_file.type == "application/pdf":
        reader = PdfReader(uploaded_file)
        for page in reader.pages:
            if page.extract_text():
                text += page.extract_text() + "\n"
    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = Document(uploaded_file)
        for para in doc.paragraphs:
            text += para.text + "\n"
    elif uploaded_file.type == "text/plain":
        text = str(uploaded_file.read(), "utf-8")
    return text

# Main UI - Input Section
st.subheader("1. Input Your Source Content")

input_method = st.radio("Choose input method:", ["✍️ Paste Text", "📁 Upload File (PDF, Word, TXT)"], horizontal=True)

source_text = ""

if input_method == "✍️ Paste Text":
    source_text = st.text_area(
        "Paste your raw notes, article, video script, or blog post here:",
        height=200,
        placeholder="Paste your content here..."
    )
else:
    uploaded_file = st.file_uploader("Upload a document", type=["pdf", "docx", "txt"])
    if uploaded_file is not None:
        with st.spinner("Reading file content..."):
            source_text = extract_text(uploaded_file)
            st.success(f"Successfully loaded file: {uploaded_file.name} ({len(source_text)} characters)")
            with st.expander("Preview extracted text"):
                st.write(source_text[:1000] + "..." if len(source_text) > 1000 else source_text)

st.subheader("2. Choose Output Format")
format_choice = st.radio(
    "Select what you want to convert this into:",
    [
        "🚀 Viral Twitter / X Thread (5-7 tweets with hooks)",
        "💼 Engaging LinkedIn Post (Hook, value bullets, call to action)",
        "📧 Engaging Email Newsletter (Subject line, body, takeaway)",
        "💡 Actionable Bullet Summary (Key insights & main takeaways)",
        "🎬 TikTok / Reel Video Script (Visual cues + voiceover)"
    ],
    index=0
)

tone = st.select_slider(
    "Select Tone of Voice:",
    options=["Casual & Fun", "Conversational & Friendly", "Professional & Insightful", "Authoritative & Direct"],
    value="Conversational & Friendly"
)

prompts = {
    "🚀 Viral Twitter / X Thread (5-7 tweets with hooks)": "Convert the input into an engaging, viral Twitter/X thread. Format each tweet numbered (1/n, 2/n), use short punchy sentences, strong hook in tweet 1, and clear CTA in final tweet.",
    "💼 Engaging LinkedIn Post (Hook, value bullets, call to action)": "Turn the input into a high-engagement LinkedIn post. Start with a compelling hook line, break concepts into skimmable bullet points with white space, and end with an open question for comments.",
    "📧 Engaging Email Newsletter (Subject line, body, takeaway)": "Transform the input into an engaging email newsletter. Provide 3 catchy subject line options, a warm intro, concise structured body paragraphs, and a key takeaway.",
    "💡 Actionable Bullet Summary (Key insights & main takeaways)": "Distill the input into a crisp executive summary with bullet points highlighting only the top actionable insights.",
    "🎬 TikTok / Reel Video Script (Visual cues + voiceover)": "Create a 60-second video script for TikTok/Reels/Shorts based on this content. Include visual direction tags like [Visual] and spoken dialogue tags like [Voiceover]."
}

if st.button("✨ Repurpose Content", type="primary", use_container_width=True):
    if not api_key:
        st.error("Please provide a Groq API key in the sidebar or Streamlit Secrets!")
    elif not source_text.strip():
        st.warning("Please provide or upload some content first!")
    else:
        with st.spinner("Repurposing content with AI..."):
            try:
                client = Groq(api_key=api_key)
                system_instruction = f"""You are a world-class digital content strategist. 
Tone: {tone}
Goal: {prompts[format_choice]}

Ensure high quality, formatting, and zero fluff."""

                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": system_instruction},
                        {"role": "user", "content": source_text}
                    ],
                    temperature=0.7,
                    max_tokens=2048,
                )
                
                result = response.choices[0].message.content
                st.subheader("🎉 Repurposed Output")
                st.markdown(result)
                st.download_button("📥 Download Output", result, file_name="repurposed_content.txt", mime="text/plain")
            except Exception as e:
                st.error(f"Error generating content: {e}")
