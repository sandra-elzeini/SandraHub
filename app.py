import streamlit as st
import re

st.title("SandraHub — Personal AI Assistant")
st.write("Paste your meeting notes below to get a clean summary.")

raw_notes = st.text_area("Paste your meeting notes here:")

if st.button("Summarize Notes"):
    if not raw_notes.strip():
        st.warning("Please enter some notes first!")
    else:
        # Combine all lines into one string
        text = raw_notes.replace("\n", " ")

        bullets = []

        # Regex: match any sequence starting with a number followed by words until the next number
        matches = re.findall(r'\d+\s+(?:[^\d]+?)(?=\s+\d|$)', text)

        # Extract main text before first match
        first_match = matches[0] if matches else ""
        first_index = text.find(first_match)
        main_text = text[:first_index].strip() if first_index > 0 else ""
        if main_text:
            bullets.append(f"- {main_text}")

        # Add matches as bullets
        for m in matches:
            clean_m = m.replace("and", "").strip()
            if clean_m:
                bullets.append(f"- {clean_m}")

        # Display summary
        st.subheader("Summary:")
        for b in bullets:
            st.write(b)
