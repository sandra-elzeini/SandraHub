import streamlit as st
import re
import io

st.set_page_config(page_title="SandraHub — Smart Summarizer", page_icon="🤖")

st.title("SandraHub — Personal AI Assistant 🤖")
st.write("Paste your meeting or notes below, and I'll organize them into a clean, structured summary!")

raw_notes = st.text_area("📝 Paste your meeting notes here:")

# Let user choose how the summary looks
style = st.selectbox("📋 Choose summary style:", ["Bulleted list", "Numbered list", "Short paragraph"])

if st.button("✨ Summarize Notes"):
    if not raw_notes.strip():
        st.warning("Please enter some notes first!")
    else:
        text = raw_notes.replace("\n", " ")  # Combine into one line
        text = re.sub(r'\s+', ' ', text).strip()

        bullets = []

        # Detect category
        category = "General text"
        if "car" in text.lower() or "mro" in text.lower():
            category = "Vehicle notes 🚗"
        elif "meeting" in text.lower():
            category = "Meeting notes 📝"
        elif "task" in text.lower() or "todo" in text.lower():
            category = "To-do list ✅"
        st.info(f"Detected category: {category}")

        # Extract car or number+name patterns
        car_matches = re.findall(r'\d+\s+(?:[^\d]+?)(?=\s+\d|$)', text)

        # Find intro before first number
        if car_matches:
            first_index = text.find(car_matches[0])
            intro_text = text[:first_index].strip()
            if intro_text:
                bullets.append(f"{intro_text}")

        # Add each car or item as a bullet
        for car in car_matches:
            clean_car = car.replace("and", "").strip()
            if clean_car:
                bullets.append(clean_car)

        # Task detection
        tasks = re.findall(r'(?:todo|to do|task|action):?\s*(.+?)(?:\.|$)', text, re.IGNORECASE)
        if tasks:
            bullets.append("🧾 Tasks Detected:")
            for t in tasks:
                bullets.append(f"  - {t.strip()}")

        # Date detection
        dates = re.findall(r'\b\d{1,2}/\d{1,2}/\d{2,4}\b', text)
        if dates:
            bullets.append("📅 Dates Found:")
            for d in dates:
                bullets.append(f"  - {d}")

        # Keyword detection
        keywords = re.findall(r'\b(ud|f1|rav4|mro|desktop)\b', text, re.IGNORECASE)
        if keywords:
            bullets.append("🔑 Keywords Found:")
            bullets.append(", ".join(sorted(set(keywords), key=str.lower)))

        # Format summary output
        st.subheader("🧠 Smart Summary:")
        if style == "Bulleted list":
            for b in bullets:
                st.write(f"- {b}")
        elif style == "Numbered list":
            for i, b in enumerate(bullets, 1):
                st.write(f"{i}. {b}")
        else:
            st.write(" ".join(bullets))

        # Save summary to text file
        summary_text = "\n".join(bullets)
        st.download_button(
            label="💾 Download Summary as TXT",
            data=summary_text.encode("utf-8"),
            file_name="summary.txt",
            mime="text/plain"
        )
