import streamlit as st
import os
from groq import Groq

# 1. Page Configuration & Custom CSS Styling
st.set_page_config(
    page_title="AI Content Repurposer Pro",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Premium SaaS Look
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
    }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        font-weight: 600;
        background: linear-gradient(90deg, #4f46e5 0%, #3b82f6 100%);
        color: white;
        border: none;
        padding: 0.6rem 1rem;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        opacity: 0.9;
        transform: translateY(-1px);
    }
    .metric-card {
        background-color: #161b22;
        padding: 1.2rem;
        border-radius: 10px;
        border: 1px solid #30363d;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize Session State
if "history" not in st.session_state:
    st.session_state.history = []

# Header Section
st.markdown("<h1 style='text-align: center; color: #ffffff;'>⚡ AI Content Repurposer <span style='color: #3b82f6;'>Pro</span></h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #8b949e; font-size: 1.1rem;'>Transform a single piece of content into high-converting multi-platform assets instantly.</p>", unsafe_allow_html=True)
st.divider()

# Sidebar Setup
with st.sidebar:
    st.image("https://img.icons8.com/clouds/200/lightning-bolt.png", width=100)
    st.header("🔐 Access & Settings")
    
    # Optional Environment variable lookup or manual entry
    api_key = st.text_input("Enter Groq API Key", type="password", help="Get your free key from console.groq.com")
    
    if api_key:
        st.success("API Connected Successfully!", icon="🟢")
        client = Groq(api_key=api_key)
    else:
        st.warning("Please enter your API key to activate the engine.")
    
    st.divider()
    st.subheader("🎛️ Engine Config")
    # Using stable active models
    model = st.selectbox(
        "Select AI Model",
        ["llama-3.1-8b-instant", "mixtral-8x7b-32768"],
        index=0
    )
    
    st.markdown("---")
    st.markdown("### 💎 Pro Features")
    st.markdown("✔️ Unlimited Repurposing\n✔️ Multi-Language Support\n✔️ Advanced Tone Control")

# Main Dashboard Container
if not api_key:
    st.info("👈 Please enter your Groq API Key in the sidebar to start generating professional content.")
else:
    col_input, col_settings = st.columns([1.2, 0.8], gap="large")
    
    with col_input:
        st.subheader("📥 1. Source Input")
        content_source = st.text_area(
            "Paste your notes, article, transcript, or ideas here:",
            height=250,
            placeholder="Type or paste your raw content here..."
        )
        
    with col_settings:
        st.subheader("⚙️ 2. Output Parameters")
        tone = st.selectbox(
            "Select Brand Tone:",
            ["Professional & Authoritative", "Engaging & Conversational", "Wit & Humorous", "Direct & Concise", "Storytelling / Narrative"]
        )
        
        language = st.selectbox(
            "Target Language:",
            ["English", "Urdu", "Roman Urdu", "Hindi"]
        )
        
        target_audience = st.text_input("Target Audience (Optional):", placeholder="e.g., Founders, Developers, Marketers")

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Action Button
    generate_btn = st.button("🚀 Generate Multi-Platform Content Suite")

    if generate_btn:
        if not content_source.strip():
            st.error("⚠️ Please provide source content before generating.")
        else:
            with st.spinner("✨ Crafting high-performance content formats across platforms..."):
                try:
                    # Defining multi-format generation prompts
                    formats = {
                        "🐦 Twitter / X Thread": "Create a viral 5 to 7 part Twitter/X thread with strong hooks and spacing.",
                        "💼 LinkedIn Post": "Create a professional, high-engagement LinkedIn post with storytelling and bullet points.",
                        "📝 Blog Outline": "Create a structured SEO-optimized blog post outline with headings and key takeaways.",
                        "✉️ Newsletter": "Create a concise, high-value email newsletter block.",
                        "🎥 YouTube Script": "Create a snappy 60-second YouTube Shorts / video script with visual cues."
                    }
                    
                    results = {}
                    
                    for format_name, format_instruction0 in formats.items():
                        prompt = f"""
                        You are an elite copywriter and content strategist. 
                        Task: {format_instruction0}
                        Tone: {tone}
                        Language: {language}
                        Target Audience: {target_audience if target_audience else 'General'}
                        
                        Source Content:
                        {content_source}
                        """
                        
                        completion = client.chat.completions.create(
                            messages=[{"role": "user", "content": prompt}],
                            model=model,
                        )
                        results[format_name] = completion.choices[0].message.content

                    # Save to history session state
                    st.session_state.history.insert(0, {"input": content_source[:100] + "...", "results": results})

                    st.success("🎉 Content suite generated successfully!")
                    st.divider()

                    # Display Tabs for Outputs
                    st.subheader("📊 Generated Content Suite")
                    tabs = st.tabs(list(results.keys()))
                    
                    for tab, (fmt_name, content_text) in zip(tabs, results.items()):
                        with tab:
                            st.markdown(f"### {fmt_name}")
                            st.code(content_text, language="markdown")
                            
                except Exception as e:
                    st.error(f"❌ Error generating content: {e}")

    # History Section
    if st.session_state.history:
        st.divider()
        with st.expander("📜 View Past Generations History"):
            for i, hist in enumerate(st.session_state.history[:5]):
                st.markdown(f"**Session {i+1}** (Source: {hist['input']})")
                for f_name, f_val in hist['results'].items():
                    if st.checkbox(f"Show {f_name} - #{i+1}", key=f"hist_{i}_{f_name}"):
                        st.write(f_val)
                st.divider()
