import streamlit as st
import re

st.title("SandraHub — Clean Offline Summarizer 🧠")
st.write("Paste your notes to get a short, well-organized summary!")

text = st.text_area("📝 Paste your notes here:")

if st.button("✨ Summarize Notes"):
    if not text.strip():
        st.warning("Please paste some notes first.")
    else:
        # Clean text
        text = re.sub(r'\s+', ' ', text)
        sentences = re.split(r'(?<=[.!?])\s+', text)

        times = []
        tasks = []
        events = []
        other = []

        # Patterns
        time_pattern = r'\b\d{1,2}(:\d{2})?\s*(AM|PM|am|pm)?\b|\b(next|today|tomorrow|October|November|Nov|Oct)\b'
        task_pattern = r'\b(Farah|Omar|Sandra|QA|assigned|prepare|provide|review|finalize|begin)\b'
        event_pattern = r'\b(meeting|launch|event|deadline|discussion|decision|starts|begins|confirmed)\b'

        for s in sentences:
            s_clean = s.strip()
            s_lower = s_clean.lower()
            if re.search(time_pattern, s_clean):
                times.append(s_clean)
            elif re.search(task_pattern, s_clean):
                tasks.append(s_clean)
            elif re.search(event_pattern, s_clean):
                events.append(s_clean)
            else:
                other.append(s_clean)

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

        if other:
            st.write("ℹ️ Other Notes:")
            for o in other:
                st.write(f"- {o}")
