import streamlit as st
from openai import OpenAI
import os

st.set_page_config(page_title="SandraHub — AI Summarizer", page_icon="🤖")

st.title("SandraHub — AI-Powered Meeting Summarizer 🤖")
st.write("Paste your meeting notes below and get a **concise, smart summary** using AI.")

api_key = st.text_input("🔑 Enter your OpenAI API Key:", type="password")

notes = st.text_area("📝 Paste your meeting notes here:")

if st.button("✨ Generate Smart Summary"):
    if not notes.strip():
        st.warning("Please paste some notes first.")
    elif not api_key.strip():
        st.warning("Please enter your API key.")
    else:
        try:
            client = OpenAI(api_key=api_key)

            st.info("Generating summary... please wait ⏳")

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that summarizes meeting notes clearly and briefly."},
                    {"role": "user", "content": f"Summarize these meeting notes into clear bullet points:\n\n{notes}"}
                ],
                temperature=0.5,
            )

            summary = response.choices[0].message.content.strip()
            st.subheader("🧠 Smart Summary:")
            st.write(summary)

            st.download_button(
                label="💾 Download Summary",
                data=summary.encode("utf-8"),
                file_name="smart_summary.txt",
                mime="text/plain"
            )

        except Exception as e:
            st.error(f"Error: {e}")
