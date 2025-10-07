import streamlit as st
import re
from heapq import nlargest

st.title("SandraHub — Offline Smart Summarizer 🧠")
st.write("Paste your notes below and get a concise summary ")

text = st.text_area("📝 Paste meeting notes here:")

if st.button("✨ Summarize Notes"):
    if not text.strip():
        st.warning("Please paste some notes first.")
    else:
        # Clean text
        text = re.sub(r'\s+', ' ', text)
        sentences = re.split(r'(?<=[.!?])\s+', text)

        # Count word frequencies (ignoring common words)
        words = re.findall(r'\w+', text.lower())
        stopwords = {'the','a','an','in','on','and','to','for','of','at','by','is','was','it','that','this','as','be','with','from'}
        freq = {}
        for w in words:
            if w not in stopwords:
                freq[w] = freq.get(w, 0) + 1

        # Score each sentence by keyword frequency
        sentence_scores = {}
        for s in sentences:
            for word in re.findall(r'\w+', s.lower()):
                if word in freq:
                    sentence_scores[s] = sentence_scores.get(s, 0) + freq[word]

        # Pick the top 3–5 sentences
        summary_sentences = nlargest(5, sentence_scores, key=sentence_scores.get)
        summary = ' '.join(summary_sentences)

        st.subheader("🧠 Smart Summary:")
        st.write(summary)
