import streamlit as st
import re
from collections import defaultdict

st.title("SandraHub — Offline Smart Meeting Minutes 🧠")
st.write("Paste your meeting notes to get concise, categorized, and grouped meeting minutes.")

notes = st.text_area("📝 Paste your meeting notes here:")

if st.button("✨ Generate Meeting Minutes"):
    if not notes.strip():
        st.warning("Please paste some notes first.")
    else:
        # ----------------------------
        # Step 1: Preprocess input
        # ----------------------------
        clean_notes = re.sub(r'\n+', ' ', notes)  # replace newlines with space
        clean_notes = re.sub(r'\s+', ' ', clean_notes)  # collapse multiple spaces

        # ----------------------------
        # Step 2: Aggressive splitting
        # ----------------------------
        # Split by '.', '?', '!', but also at recognized keywords like "and", "then", etc.
        raw_sentences = re.split(r'[.!?]|(?<=\s)(?=and\b|then\b|Next\b)', clean_notes)
        sentences = [s.strip() for s in raw_sentences if s.strip()]

        # ----------------------------
        # Step 3: Categorize sentences
        # ----------------------------
        times = []
        events = []
        tasks_dict = defaultdict(list)

        time_keywords = r'\b\d{1,2}(:\d{2})?\s*(AM|PM|am|pm)?\b|\b(next|today|tomorrow|Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday|October|November|Nov|Oct)\b'
        task_keywords = r'\b(Farah|Omar|Sandra|QA|assigned|prepare|provide|review|finalize|begin|complete|responsible)\b'
        event_keywords = r'\b(meeting|launch|event|deadline|decision|starts|begins|confirmed|discussion|design|reassigned|priority|test)\b'

        for s in sentences:
            person_found = re.findall(r'\b(Farah|Omar|Sandra|QA)\b', s, re.IGNORECASE)
            if person_found or re.search(task_keywords, s, re.IGNORECASE):
                if person_found:
                    for person in person_found:
                        tasks_dict[person].append(s)
                else:
                    tasks_dict["General"].append(s)
            elif re.search(event_keywords, s, re.IGNORECASE):
                events.append(s)
            elif re.search(time_keywords, s, re.IGNORECASE):
                times.append(s)
            else:
                events.append(s)  # default to events

        # ----------------------------
        # Step 4: Display structured summary
        # ----------------------------
        st.subheader("🧠 Smart Meeting Minutes")

        if times:
            st.write("🕒 Times & Dates:")
            for t in times:
                st.write(f"- {t}")

        if events:
            st.write("📌 Key Events / Decisions:")
            for e in events:
                st.write(f"- {e}")

        if tasks_dict:
            st.write("✅ Tasks / Responsibilities:")
            for person, tasks in tasks_dict.items():
                st.write(f"**{person}:**")
                for t in tasks:
                    st.write(f"- {t}")
