import streamlit as st
import re

st.title("SandraHub — Personal AI Assistant")
st.write("Paste your meeting notes below to get a clean summary.")

raw_notes = st.text_area("Paste your meeting notes here:")

if st.button("Summarize Notes"):
    if raw_notes.strip() == "":
        st.warning("Please enter some notes first!")
    else:
        # Split notes by period or newline
        parts = re.split(r"[.\n]", raw_notes)
        # Filter out very short fragments
        parts = [p.strip() for p in parts if len(p.strip().split()) > 2]

        bullets = []

        for p in parts:
            # Look for number + word sequences (e.g., 2 Urban Cruise)
            matches = re.findall(r"\d+\s+[A-Za-z0-9\-]+(?:\s+[A-Za-z0-9\-]+)*", p)
            if matches:
                # Main text before the first match
                first_match_index = p.find(matches[0])
                main_text = p[:first_match_index].strip()
                if main_text:
                    bullets.append(f"- {main_text}")
                for m in matches:
                    bullets.append(f"  - {m}")
            else:
                bullets.append(f"- {p}")

        # Display summary
        st.subheader("Summary:")
        for b in bullets:
            st.write(b)
