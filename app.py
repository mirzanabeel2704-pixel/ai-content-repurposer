import streamlit as st
import os
from groq import Groq
from dotenv import load_dotenv

# Page Configuration
st.set_page_config(
    page_title="AI Content Repurposer Pro",
    page_icon="⚡",
    layout="wide"
)

# Initialize Session State for History
if "history" not in st.session_state:
    st.session_state.history = []

st.title("⚡ AI Content Repurposer Pro")
st.write("Transform 1 piece of content into 5+ high-performing formats in seconds.")

# Sidebar Configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    api_key = st.text_input("Enter Groq API Key", type="password")
    
    if not api_key:
        st.info("Get your free key from [console.groq.com](https://console.groq.com)")
    else:
        st.success("API Key Loaded Successfully! ✅")
        client = Groq(api_key=api_key)
        
        model = st.selectbox(
            "Select Model",
            ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768"],
            index=1
        )

st.divider()

# Input Section
st.subheader("1. Input Your Source Content")
content = st.text_area("Paste your raw notes, article, video script, or blog post here:", height=200)

# Settings Section
st.subheader("2. Choose Output Format, Language & Custom Tone")
col1, col2 = st.columns(2)
with col1:
    format_type = st.selectbox("Select Output Format:", 
                               ["Viral Twitter / X Thread", "LinkedIn Post", "Blog Post", "Newsletter", "YouTube Script"])
with col2:
    language = st.selectbox("Select Output Language:", ["English", "Urdu", "Hindi"])

tone = st.text_input("Custom Tone / Brand Voice (Optional):", placeholder="e.g., Funny, Professional, Motivation Guru")

# Repurpose Button
if st.button("🚀 Repurpose Content"):
    if not api_key:
        st.error("Please enter your Groq API Key in the sidebar!")
    elif not content:
        st.warning("Please provide some content to repurpose.")
    else:
        try:
            with st.spinner("Generating your content..."):
                prompt = f"Repurpose the following content into a {format_type} in {language}. Tone: {tone}. Content: {content}"
                
                chat_completion = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model=model,
                )
                
                result = chat_completion.choices[0].message.content
                st.session_state.history.append({"input": content, "output": result})
                st.markdown("### Generated Output:")
                st.write(result)
        except Exception as e:
            st.error(f"Error generating content: {e}")

# History Section
st.divider()
st.header("📜 Generation History")
for item in reversed(st.session_state.history):
    with st.expander("View past generation"):
        st.write("**Input:**", item["input"])
        st.write("**Output:**", item["output"])
