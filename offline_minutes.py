import streamlit as st
import spacy
from collections import defaultdict

# Load spaCy English model
nlp = spacy.load("en_core_web_sm")

st.title("SandraHub — Offline NLP Smart Meeting Minutes 🧠")
st.write("Paste your meeting notes to get clean, categorized meeting minutes.")

# Text area for notes
notes = st.text_area("📝 Paste your meeting notes here:")

if st.button("Generate Meeting Minutes"):
    if not notes.strip():
        st.warning("Please paste some notes first.")
    else:
        # Process the notes with spaCy
        doc = nlp(notes)
        
        # Containers for output
        times = []
        events = []
        tasks_dict = defaultdict(list)

        # Step 1: Iterate over sentences
        for sent in doc.sents:
            sentence_text = sent.text.strip()

            # Step 2: Extract named entities
            sent_doc = nlp(sentence_text)
            ents = {ent.label_: ent.text for ent in sent_doc.ents}

            # Step 3: Categorize sentence
            # 3a. Times / Dates
            if 'TIME' in ents or 'DATE' in ents:
                times.append(sentence_text)
                continue

            # 3b. Tasks (PERSON + verb)
            persons = [ent.text for ent in sent_doc.ents if ent.label_ == 'PERSON']
            verbs = [token.lemma_ for token in sent_doc if token.pos_ == 'VERB']

            if persons and verbs:
                for person in persons:
                    tasks_dict[person].append(sentence_text)
                continue

            # 3c. Events / Decisions
            events.append(sentence_text)

        # Step 4: Display structured minutes
        if times:
            st.subheader("🕒 Times & Dates")
            for t in times:
                st.write(f"- {t}")

        if events:
            st.subheader("📌 Events / Decisions")
            for e in events:
                st.write(f"- {e}")

        if tasks_dict:
            st.subheader("✅ Tasks / Responsibilities")
            for person, tasks in tasks_dict.items():
                st.write(f"**{person}:**")
                for t in tasks:
                    st.write(f"- {t}")

