import streamlit as st
import re

st.title("SandraHub — Personal AI Assistant")
st.write("Paste your meeting notes below to get a clean summary.")

raw_notes = st.text_area("Paste your meeting notes here:")

if st.button("Summarize Notes"):
    if raw_notes.strip() == "":
        st.warning("Please enter some notes first!")
    else:
        # Split notes by period, comma, or newline
        parts = re.split(r"[.\n,]", raw_notes)
        # Filter out very short fragments
        parts = [p.strip() for p in parts if len(p.strip().split()) > 2]

        # Format bullets: detect numbers for sub-points
        bullets = []
        for p in parts:
            # If numbers detected, split them for sub-bullets
            numbers = re.findall(r"\d+\s?\w*", p)
            if numbers and len(numbers) > 1:
                main_text = p.split(numbers[0])[0].strip()
                bullets.append(f"- {main_text}")
                for n in numbers:
                    bullets.append(f"  - {n}")
            else:
                bullets.append(f"- {p}")

        # Display summary
        st.subheader("Summary:")
        for b in bullets:
            st.write(b)
