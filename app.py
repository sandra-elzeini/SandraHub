import streamlit as st
from transformers import pipeline
import re

st.title("SandraHub — Structured Offline Summarizer 🤖")
st.write("Paste your meeting notes to get a concise, categorized summary.")

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
            # Summarize notes (adjust max/min length if needed)
            summary_list = summarizer(notes, max_length=200, min_length=50, do_sample=False)
            summary_text = summary_list[0]['summary_text']

        # Split into sentences
        sentences = re.split(r'(?<=[.!?])\s+', summary_text)

        # Prepare categories
        times = []
        events = []
        tasks = []

        # Simple keyword-based categorization
        time_keywords = r'\b\d{1,2}(:\d{2})?\s*(AM|PM|am|pm)?\b|\b(next|today|tomorrow|October|November|Nov|Oct)\b'
        task_keywords = r'\b(assign|assigned|task|qa|prepare|provide|review|finalize|begin|complete|responsible|Farah|Omar|Sandra)\b'
        event_keywords = r'\b(meeting|launch|event|deadline|decision|starts|begins|confirmed|discussion|design)\b'

        for s in sentences:
            s_clean = s.strip()
            s_lower = s_clean.lower()
            if re.search(time_keywords, s_clean):
                times.append(s_clean)
            elif re.search(task_keywords, s_clean):
                tasks.append(s_clean)
            elif re.search(event_keywords, s_clean):
                events.append(s_clean)

        # Display structured summary
        st.subheader("🧠 Smart Summary")

        if times:
            st.write("🕒 Times & Dates:")
            for t in times:
                st.write(f"- {t}")

        if events:
            st.write("📌 Key Events / Decisions:")
            for e in events:
                st.write(f"- {e}")

        if tasks:
            st.write("✅ Tasks / Responsibilities:")
            for t in tasks:
                st.write(f"- {t}")
