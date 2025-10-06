import streamlit as st

st.title("SandraHub — Personal AI Assistant")
st.write("Paste your meeting notes below to get a simple summary.")

raw_notes = st.text_area("Paste your meeting notes here:")

if st.button("Summarize Notes"):
    if raw_notes.strip() == "":
        st.warning("Please enter some notes first!")
    else:
        # Split notes by period and newline
        import re
        sentences = re.split(r"[.\n]", raw_notes)
        # Filter out short sentences
        sentences = [s.strip() for s in sentences if len(s.strip().split()) > 2]
        # Pick top 5 sentences as summary
        summary = sentences[:5]

        st.subheader("Summary:")
        for s in summary:
            st.write(f"- {s}")
