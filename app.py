import streamlit as st
import re
from collections import defaultdict

st.set_page_config(page_title="SandraHub — Smart Meeting Minutes", page_icon="🧠")
st.title("SandraHub — Offline Smart Meeting Minutes 🧠")
st.write("Paste your meeting notes to get **clean, categorized, and grouped meeting minutes**.")

# Input area
notes = st.text_area("📝 Paste your meeting notes here:")

if st.button("✨ Generate Meeting Minutes"):
    if not notes.strip():
        st.warning("Please paste some notes first.")
    else:
        # Step 1: Clean input
        clean_notes = re.sub(r'\n+', ' ', notes)  # replace newlines with space
        clean_notes = re.sub(r'\s+', ' ', clean_notes)  # collapse multiple spaces

        # Step 2: Split into sentences/bullets
        raw_sentences = re.split(r'(?<=[.!?])\s+|(?<=\d)\s| and | then ', clean_notes)
        sentences = [s.strip() for s in raw_sentences if s.strip()]

        # Step 3: Initialize sections
        times = []
        events = []
        tasks_dict = defaultdict(list)

        # Step 4: Define keyword patterns
        time_pattern = re.compile(
            r'\b\d{1,2}(:\d{2})?\s*(AM|PM|am|pm)?\b|Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday|October|November|Oct|Nov|\bnext\b|\btoday\b|\btomorrow\b',
            re.IGNORECASE
        )
        event_pattern = re.compile(
            r'\b(meeting|launch|event|deadline|decision|starts|begins|confirmed|discussion|design|reassigned|priority|test|project)\b',
            re.IGNORECASE
        )
        task_pattern = re.compile(
            r'\b(Farah|Omar|Sandra|QA|assigned|prepare|provide|review|finalize|begin|complete|responsible)\b',
            re.IGNORECASE
        )

        # Step 5: Categorize each sentence
        for s in sentences:
            # Times / Dates
            if re.search(time_pattern, s):
                times.append(s)
            # Tasks
            elif re.search(task_pattern, s):
                # Assign to a person if name exists, else to General
                persons = re.findall(r'\b(Farah|Omar|Sandra|QA)\b', s, re.IGNORECASE)
                if persons:
                    for person in persons:
                        tasks_dict[person].append(s)
                else:
                    tasks_dict["General"].append(s)
            # Events / Decisions
            elif re.search(event_pattern, s):
                events.append(s)
            else:
                # Default to Events
                events.append(s)

        # Step 6: Display structured minutes with expanders
        if times:
            with st.expander("🕒 Times & Dates"):
                for t in times:
                    st.write(f"- {t}")

        if events:
            with st.expander("📌 Key Events / Decisions"):
                for e in events:
                    st.write(f"- {e}")

        if tasks_dict:
            with st.expander("✅ Tasks / Responsibilities"):
                for person, tasks in tasks_dict.items():
                    st.write(f"**{person}:**")
                    for t in tasks:
                        # Bold names in the task for clarity
                        t_bold = re.sub(r'\b(Farah|Omar|Sandra|QA)\b', r'**\1**', t)
                        st.write(f"- {t_bold}")

        # Step 7: Downloadable minutes
        all_minutes = ""
        if times:
            all_minutes += "🕒 Times & Dates:\n" + "\n".join(times) + "\n\n"
        if events:
            all_minutes += "📌 Key Events / Decisions:\n" + "\n".join(events) + "\n\n"
        if tasks_dict:
            all_minutes += "✅ Tasks / Responsibilities:\n"
            for person, tasks in tasks_dict.items():
                all_minutes += f"{person}:\n"
                for t in tasks:
                    all_minutes += f"- {t}\n"
        st.download_button("💾 Download Minutes as .txt", all_minutes, file_name="meeting_minutes.txt")
