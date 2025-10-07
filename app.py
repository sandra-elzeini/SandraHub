import streamlit as st
from transformers import pipeline

st.title("SandraHub — Offline AI Summarizer 🤖")
st.write("Paste your meeting notes below to get a concise, human-readable summary.")

# Load the summarization model once
@st.cache_resource
def load_model():
    return pipeline("summarization", model="facebook/bart-large-cnn")

summarizer = load_model()

notes = st.text_area("📝 Paste your meeting notes here:")

if st.button("✨ Generate Smart Summary"):
    if not notes.strip():
        st.warning("Please paste some notes first.")
    else:
        with st.spinner("Generating summary... ⏳"):
            # Summarize notes (max_length can be adjusted)
            summary_list = summarizer(notes, max_length=200, min_length=50, do_sample=False)
            summary_text = summary_list[0]['summary_text']

        # Split summary into bullets by sentence
        bullets = summary_text.split(". ")
        st.subheader("🧠 Smart Summary:")
        for b in bullets:
            if b.strip():
                st.write(f"- {b.strip()}")
