import os
import re
import requests
import streamlit as st
from groq import Groq
from dotenv import load_dotenv
from pypdf import PdfReader
from docx import Document
from youtube_transcript_api import YouTubeTranscriptApi
from bs4 import BeautifulSoup

load_dotenv()

# Page config
st.set_page_config(
    page_title="AI Content Repurposer Pro",
    page_icon="⚡",
    layout="wide"
)

# Initialize Session State for History
if "history" not in st.session_state:
    st.session_state.history = []

# Premium SaaS UI Styling & Animations
st.markdown("""
<style>
    .stApp {
        background-color: #F8FAFC;
    }
    
    /* Hero Banner */
    .hero-container {
        background: linear-gradient(135deg, #1E3A8A 0%, #2563EB 100%);
        padding: 2.2rem;
        border-radius: 14px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 25px -5px rgba(37, 99, 235, 0.25);
    }
    .hero-title {
        font-size: 2.5rem;
        font-weight: 800;
        margin-bottom: 0.3rem;
        color: white;
        letter-spacing: -0.5px;
    }
    .hero-subtitle {
        font-size: 1.1rem;
        font-weight: 400;
        color: #E2E8F0;
    }

    /* Card Box Design */
    .saas-card {
        background: #ffffff;
        padding: 1.8rem;
        border-radius: 12px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.02);
        margin-bottom: 1.5rem;
    }

    /* Section Headings inside Cards */
    .card-title {
        font-size: 1.2rem;
        font-weight: 700;
        color: #1E293B;
        margin-bottom: 1rem;
    }

    /* Custom Button Styling */
    div.stButton > button:first-child {
        background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%);
        color: white;
        font-weight: 600;
        font-size: 1.05rem;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 10px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.25);
    }
    div.stButton > button:first-child:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(37, 99, 235, 0.35);
    }
</style>

<div class="hero-container">
    <div class="hero-title">⚡ AI Content Repurposer Pro</div>
    <div class="hero-subtitle">Transform 1 piece of content into 5+ high-performing formats in seconds.</div>
</div>
""", unsafe_allow_html=True)

# API Key Retrieval
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    try:
        api_key = st.secrets["GROQ_API_KEY"]
    except Exception:
        api_key = None

# Sidebar Configuration, History & Professional Branding Footer
with st.sidebar:
    st.header("⚙️ Configuration")
    if not api_key:
        api_key = st.text_input("Enter Groq API Key", type="password")
        st.info("Get your free key from [console.groq.com](https://console.groq.com)")
    else:
        st.success("API Key Loaded Successfully! ✅")

   model = st.selectbox(
    "Select Model",
    ["llama-3.1-8b-instant", "mixtral-8x7b-32768"],
    index=0
)
    )
    
    st.divider()
    st.header("📜 Generation History")
    if len(st.session_state.history) == 0:
        st.info("No history yet. Generate some content!")
    else:
        for idx, item in enumerate(reversed(st.session_state.history)):
            with st.expander(f"{item['format']} ({idx+1})"):
                st.write(item['output'][:300] + "...")
                st.download_button(
                    "📥 Download",
                    item['output'],
                    file_name=f"history_{idx}.txt",
                    mime="text/plain",
                    key=f"dl_{idx}"
                )
    
    st.divider()
    st.markdown(
        "<div style='text-align: center; color: #64748B; font-size: 0.85rem;'>"
        "Built with ❤️ by <b>Mirza Nabeel</b><br>"
        "Powered by Groq & Streamlit"
        "</div>", 
        unsafe_allow_html=True
    )

# Helper functions to extract content from different sources
def extract_pdf(uploaded_file):
    text = ""
    reader = PdfReader(uploaded_file)
    for page in reader.pages:
        if page.extract_text():
            text += page.extract_text() + "\n"
    return text

def extract_docx(uploaded_file):
    text = ""
    doc = Document(uploaded_file)
    for para in doc.paragraphs:
        text += para.text + "\n"
    return text

def extract_youtube_transcript(url):
    video_id_match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", url)
    if not video_id_match:
        raise ValueError("Invalid YouTube URL")
    video_id = video_id_match.group(1)
    transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
    return " ".join([item["text"] for item in transcript_list])

def extract_web_article(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    paragraphs = soup.find_all("p")
    return "\n".join([p.get_text() for p in paragraphs])

# Main UI wrapped in Clean SaaS Cards
st.markdown('<div class="saas-card">', unsafe_allow_html=True)
st.markdown('<div class="card-title">1. Input Your Source Content</div>', unsafe_allow_html=True)

input_method = st.radio(
    "Choose input method:",
    ["✍️ Paste Text", "📁 Upload File", "🔗 YouTube / Blog URL"],
    horizontal=True,
    label_visibility="collapsed"
)

source_text = ""

if input_method == "✍️ Paste Text":
    source_text = st.text_area(
        "Paste your raw notes, article, video script, or blog post here:",
        height=200,
        placeholder="Paste your content here..."
    )
elif input_method == "📁 Upload File":
    uploaded_file = st.file_uploader("Upload a document", type=["pdf", "docx", "txt"])
    if uploaded_file is not None:
        with st.spinner("📁 Reading document contents securely..."):
            if uploaded_file.type == "application/pdf":
                source_text = extract_pdf(uploaded_file)
            elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                source_text = extract_docx(uploaded_file)
            elif uploaded_file.type == "text/plain":
                source_text = str(uploaded_file.read(), "utf-8")
            st.success(f"Successfully loaded file: {uploaded_file.name} ({len(source_text)} characters)")
            with st.expander("Preview extracted text"):
                st.write(source_text[:1000] + "..." if len(source_text) > 1000 else source_text)
else:
    url_input = st.text_input("Enter YouTube Video Link or Blog Article URL:")
    if url_input:
        if st.button("Fetch Content from URL"):
            with st.spinner("🔍 Extracting live transcript/article text..."):
                try:
                    if "youtube.com" in url_input or "youtu.be" in url_input:
                        source_text = extract_youtube_transcript(url_input)
                    else:
                        source_text = extract_web_article(url_input)
                    st.success(f"Successfully extracted {len(source_text)} characters!")
                except Exception as e:
                    st.error(f"Error fetching URL content: {e}")
        if source_text:
            with st.expander("Preview extracted content"):
                st.write(source_text[:1000] + "..." if len(source_text) > 1000 else source_text)

st.markdown('</div>', unsafe_allow_html=True)

# Card 2: Options & Configurations
st.markdown('<div class="saas-card">', unsafe_allow_html=True)
st.markdown('<div class="card-title">2. Choose Output Format, Language & Custom Tone</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    format_choice = st.selectbox(
        "Select Output Format:",
        [
            "🚀 Viral Twitter / X Thread (5-7 tweets with hooks)",
            "💼 Engaging LinkedIn Post (Hook, value bullets, call to action)",
            "📧 Engaging Email Newsletter (Subject line, body, takeaway)",
            "💡 Actionable Bullet Summary (Key insights & main takeaways)",
            "🎬 TikTok / Reel Video Script (Visual cues + voiceover)"
        ]
    )

with col2:
    language = st.selectbox(
        "Select Output Language:",
        ["English", "Roman Urdu", "Urdu"]
    )

custom_tone = st.text_input(
    "🎨 Custom Tone / Brand Voice (Optional):",
    placeholder="e.g., Funny & Sarcastic, Investor Pitch Style, Storyteller, Motivation Guru"
)

prompts = {
    "🚀 Viral Twitter / X Thread (5-7 tweets with hooks)": "Convert the input into an engaging, viral Twitter/X thread. Format each tweet numbered (1/n, 2/n), use short punchy sentences, strong hook in tweet 1, and clear CTA in final tweet.",
    "💼 Engaging LinkedIn Post (Hook, value bullets, call to action)": "Turn the input into a high-engagement LinkedIn post. Start with a compelling hook line, break concepts into skimmable bullet points with white space, and end with an open question for comments.",
    "📧 Engaging Email Newsletter (Subject line, body, takeaway)": "Transform the input into an engaging email newsletter. Provide 3 catchy subject line options, a warm intro, concise structured body paragraphs, and a key takeaway.",
    "💡 Actionable Bullet Summary (Key insights & main takeaways)": "Distill the input into a crisp executive summary with bullet points highlighting only the top actionable insights.",
    "🎬 TikTok / Reel Video Script (Visual cues + voiceover)": "Create a 60-second video script for TikTok/Reels/Shorts based on this content. Include visual direction tags like [Visual] and spoken dialogue tags like [Voiceover]."
}

st.markdown("<br>", unsafe_allow_html=True)

if st.button("✨ Repurpose Content", type="primary", use_container_width=True):
    if not api_key:
        st.error("Please provide a Groq API key in the sidebar or Streamlit Secrets!")
    elif not source_text.strip():
        st.warning("Please provide, upload, or fetch some content first!")
    else:
        with st.spinner("🤖 Crafting high-performance content with AI..."):
            try:
                client = Groq(api_key=api_key)
                tone_instruction = f"Custom Brand Tone: {custom_tone}" if custom_tone else "Tone: Conversational & Friendly"
                
                system_instruction = f"""You are a world-class digital content strategist. 
{tone_instruction}
Language/Script: Write the final output strictly in {language}.
Goal: {prompts[format_choice]}

Ensure high quality, correct formatting, and zero fluff."""

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
                
                # Save to History State
                st.session_state.history.append({
                    "format": format_choice.split(" ")[1],
                    "output": result
                })
                
                st.markdown('<div class="saas-card">', unsafe_allow_html=True)
                st.subheader("🎉 Repurposed Output")
                st.markdown(result)
                st.download_button("📥 Download Output", result, file_name="repurposed_content.txt", mime="text/plain")
                st.markdown('</div>', unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Error generating content: {e}")

st.markdown('</div>', unsafe_allow_html=True)
