import streamlit as st
from transformers import pipeline
import re
from collections import defaultdict

st.title("SandraHub — Professional Meeting Minutes 🧠")
st.write("Paste your meeting notes to get concise, categorized, and grouped meeting minutes.")

# Load the summarization model once
@st.cache_resource
def load_model():
    return pipeline("summarization", model="facebook/bart-large-cnn")

summarizer = load_model()

notes = st.text_area("📝 Paste your meeting notes here:")

if st.button("✨ Generate Meeting Minutes"):
    if not notes.strip():
        st.warning("Please paste some notes first.")
    else:
        with st.spinner("Generating summary... ⏳"):
            # ----------------------------
            # Step 1: Preprocess input
            # ----------------------------
            clean_notes = re.sub(r'\n+', ' ', notes)  # replace newlines with space
            clean_notes = re.sub(r'\s+', ' ', clean_notes)  # collapse multiple spaces

            # ----------------------------
            # Step 2: Generate summary
            # ----------------------------
            summary_list = summarizer(clean_notes, max_length=250, min_length=50, do_sample=False)
            summary_text = summary_list[0]['summary_text']

            # ----------------------------
            # Step 3: Clean summary
            # ----------------------------
            summary_text = re.sub(r'\n+', ' ', summary_text)  # remove newlines in summary
            summary_text = re.sub(r'\s+', ' ', summary_text)  # collapse multiple spaces

            # ----------------------------
            # Step 4: Aggressive splitting
            # ----------------------------
            raw_sentences = re.split(r'[.!?]', summary_text)
            sentences = []
            for s in raw_sentences:
                for part in re.split(r' - | : |(?<=[a-z\)])\s+(?=[A-Z])', s):
                    part_clean = part.strip()
                    if part_clean:
                        sentences.append(part_clean)

            # ----------------------------
            # Step 5: Categorize sentences
            # ----------------------------
            times = []
            events = []
            tasks_dict = defaultdict(list)

            time_keywords = r'\b\d{1,2}(:\d{2})?\s*(AM|PM|am|pm)?\b|\b(next|today|tomorrow|Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday|October|November|Nov|Oct)\b'
            task_keywords = r'\b(Farah|Omar|Sandra|QA|assigned|prepare|provide|review|finalize|begin|complete|responsible)\b'
            event_keywords = r'\b(meeting|launch|event|deadline|decision|starts|begins|confirmed|discussion|design)\b'

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
                    events.append(s)  # Default to events

            # ----------------------------
            # Step 6: Display structured summary
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
