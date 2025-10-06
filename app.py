import streamlit as st
import re

st.title("SandraHub — Personal AI Assistant")
st.write("Paste your meeting notes below to get a clean summary.")

raw_notes = st.text_area("Paste your meeting notes here:")

if st.button("Summarize Notes"):
    if not raw_notes.strip():
        st.warning("Please enter some notes first!")
    else:
        text = raw_notes.replace("\n", " ")  # Combine everything into one line
        bullets = []

        # Regex: match all sequences like "number + words" until next number
        car_matches = re.findall(r'\d+\s+(?:[^\d]+?)(?=\s+\d|$)', text)

        # Find intro text before first car number
        if car_matches:
            first_index = text.find(car_matches[0])
            intro_text = text[:first_index].strip()
            if intro_text:
                bullets.append(f"- {intro_text}")

        # Add each car as a bullet
        for car in car_matches:
            clean_car = car.replace("and", "").strip()
            if clean_car:
                bullets.append(f"- {clean_car}")

        # Display summary
        st.subheader("Summary:")
        for b in bullets:
            st.write(b)
