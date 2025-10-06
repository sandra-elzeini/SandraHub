

import streamlit as st

st.title("SandraHub — Personal AI Assistant")
st.write("Welcome! Paste your raw notes below to get a simple summary.")

# Input box for raw notes
raw_notes = st.text_area("Paste your meeting notes here:")

# Button to summarize
if st.button("Summarize Notes"):
    if raw_notes.strip() == "":
        st.warning("Please enter some notes first!")
    else:
        # Simple summarizer: split by sentences and pick first 3 as bullet points
        sentences = raw_notes.split(".")
        bullets = [s.strip() for s in sentences if s.strip() != ""][:3]
        st.subheader("Summary:")
        for b in bullets:
            st.write(f"- {b}")
