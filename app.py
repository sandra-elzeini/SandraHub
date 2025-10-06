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
        lines = re.split(r"[.\n]", raw_notes)
        lines = [l.strip() for l in lines if len(l.strip()) > 2]

        bullets = []

        for line in lines:
            # Pattern: find all sequences like "number + words" ignoring 'and'
            matches = re.findall(r'\d+\s+(?:[^\d]+?)(?=\s+\d|\s*$)', line)
            # Extract main text before first match
            first_match_index = line.find(matches[0]) if matches else -1
            main_text = line[:first_match_index].strip() if first_match_index > 0 else ""
            if main_text:
                bullets.append(f"- {main_text}")

            for m in matches:
                # Clean up trailing 'and' and extra spaces
                clean_m = m.replace("and", "").strip()
                if clean_m:
                    bullets.append(f"  - {clean_m}")

        # Display summary
        st.subheader("Summary:")
        for b in bullets:
            st.write(b)
