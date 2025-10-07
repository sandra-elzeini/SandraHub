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
        text = raw_notes.replace("\n", " ")
        text = re.sub(r'\s+', ' ', text).strip()

        bullets = []

        # Detect general topic category
        category = "General notes"
        if re.search(r'\bmeeting\b', text, re.IGNORECASE):
            category = "Meeting reminder 🗓️"
        elif re.search(r'\bevent\b', text, re.IGNORECASE):
            category = "Event or activity 🎉"
        elif re.search(r'\bcoffee|drink\b', text, re.IGNORECASE):
            category = "Personal reminder ☕"
        elif re.search(r'\bpray|prayer\b', text, re.IGNORECASE):
            category = "Faith reminder 🙏"

        st.info(f"Detected category: {category}")

        # 🕒 Extract time expressions safely (e.g., "8", "12 - 4", "8:30")
        times = re.findall(r'\b\d{1,2}(?::\d{2})?\s*(?:-\s*\d{1,2}(?::\d{2})?)?\b', text)
        if times:
            bullets.append("🕒 Times mentioned:")
            for t in times:
                bullets.append(f"  - {t.strip()}")

        # ✏️ Extract sentences or fragments for better bullet separation
        parts = re.split(r'(?<=[.!?])\s+|\s+and\s+', text)
        for p in parts:
            p = p.strip()
            if p:
                bullets.append(p)

        # 📅 Extract possible date formats (optional future use)
        dates = re.findall(r'\b\d{1,2}/\d{1,2}/\d{2,4}\b', text)
        if dates:
            bullets.append("📅 Dates found:")
            for d in dates:
                bullets.append(f"  - {d}")

        # 🧠 Display smart summary
        st.subheader("🧠 Smart Summary:")

        if style == "Bulleted list":
            for b in bullets:
                st.write(f"- {b}")
        elif style == "Numbered list":
            for i, b in enumerate(bullets, 1):
                st.write(f"{i}. {b}")
        else:
            st.write(" ".join(bullets))

        # 💾 Allow download
        summary_text = "\n".join(bullets)
        st.download_button(
            label="💾 Download Summary as TXT",
            data=summary_text.encode("utf-8"),
            file_name="summary.txt",
            mime="text/plain"
        )
