import streamlit as st
import re
from heapq import nlargest

st.title("SandraHub — Simplified Offline Summarizer 🧠")
st.write("Paste your notes to get short, grouped, clear bullet points!")

text = st.text_area("📝 Paste your notes here:")

if st.button("✨ Summarize Notes"):
    if not text.strip():
        st.warning("Please paste some notes first.")
    else:
        # Clean text
        text = re.sub(r'\s+', ' ', text)
        sentences = re.split(r'(?<=[.!?])\s+', text)

        # Group sentences by category
        times = []
        tasks = []
        events = []
        other = []

        for s in sentences:
            s_lower = s.lower()
            if re.search(r'\b\d{1,2}(:\d{2})?\s*(am|pm)?\b', s_lower) or re.search(r'\bnext\b|\bnovember\b|\boctober\b', s_lower):
                times.append(s.strip())
            elif re.search(r'\b(task|to do|qa|farah|omar|sandra|assigned|prepare)\b', s_lower):
                tasks.append(s.strip())
            elif re.search(r'\b(meeting|launch|event|discussion|deadline)\b', s_lower):
                events.append(s.strip())
            else:
                other.append(s.strip())

        st.subheader("🧠 Simplified Summary:")

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

        if other:
            st.write("ℹ️ Other Notes:")
            for o in other:
                st.write(f"- {o}")
