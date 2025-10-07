import streamlit as st
import re
from collections import defaultdict

st.title("SandraHub — Smart Meeting Minutes 🧠")
st.write("Paste your meeting notes to get clean, categorized meeting minutes.")

notes = st.text_area("📝 Paste your meeting notes here:")

if st.button("✨ Generate Meeting Minutes"):
    if not notes.strip():
        st.warning("Please paste some notes first.")
    else:
        # Step 1: Clean input
        clean_notes = re.sub(r'\n+', ' ', notes)  # replace newlines with space
        clean_notes = re.sub(r'\s+', ' ', clean_notes)  # collapse multiple spaces

        # Step 2: Split into sentences/bullets
        # Split at '.', '!', '?', 'and', 'then', or numbered list
        raw_sentences = re.split(r'(?<=[.!?])\s+|(?<=\d)\s', clean_notes)
        sentences = [s.strip() for s in raw_sentences if s.strip()]

        # Step 3: Initialize sections
        times = []
        events = []
        tasks_dict = defaultdict(list)

        # Step 4: Define keyword patterns
        time_pattern = re.compile(r'\b\d{1,2}(:\d{2})?\s*(AM|PM|am|pm)?\b|Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday|October|November|Oct|Nov|\bnext\b|\btoday\b|\btomorrow\b', re.IGNORECASE)
        event_pattern = re.compile(r'\b(meeting|launch|event|deadline|decision|starts|begins|confirmed|discussion|design|reassigned|priority|test|project)\b', re.IGNORECASE)
        task_pattern = re.compile(r'\b(Farah|Omar|Sandra|QA|assigned|prepare|provide|review|finalize|begin|complete|responsible)\b', re.IGNORECASE)

        # Step 5: Categorize each sentence only once
        for s in sentences:
            if re.search(time_pattern, s):
                times.append(s)
            elif re.search(task_pattern, s):
                # Assign to a person if name exists, else to General
                persons = re.findall(r'\b(Farah|Omar|Sandra|QA)\b', s, re.IGNORECASE)
                if persons:
                    for person in persons:
                        tasks_dict[person].append(s)
                else:
                    tasks_dict["General"].append(s)
            elif re.search(event_pattern, s):
                events.append(s)
            else:
                # If no keywords, classify as event by default
                events.append(s)

        # Step 6: Display structured summary
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
