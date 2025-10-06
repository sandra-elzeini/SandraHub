import streamlit as st

st.title("SandraHub — Personal AI Assistant")
st.write("Paste your meeting notes below to get a clean summary.")

raw_notes = st.text_area("Paste your meeting notes here:")

if st.button("Summarize Notes"):
    if raw_notes.strip() == "":
        st.warning("Please enter some notes first!")
    else:
        # 1. Join all lines into a single sequence of words
        words = [w for w in raw_notes.replace("\n", " ").split() if w.lower() != "and"]

        bullets = []
        temp_bullet = []
        i = 0

        while i < len(words):
            word = words[i]
            # 2. Start a new bullet if the word starts with a digit
            if word[0].isdigit():
                if temp_bullet:
                    bullets.append("  - " + " ".join(temp_bullet))
                    temp_bullet = []

                temp_bullet.append(word)
                i += 1
                # 3. Keep adding words until next word starts with a digit
                while i < len(words) and not words[i][0].isdigit():
                    temp_bullet.append(words[i])
                    i += 1

                bullets.append("  - " + " ".join(temp_bullet))
                temp_bullet = []
            else:
                temp_bullet.append(word)
                i += 1

        # 4. Add leftover text as a bullet
        if temp_bullet:
            bullets.append("  - " + " ".join(temp_bullet))

        # 5. Display summary
        st.subheader("Summary:")
        for b in bullets:
            st.write(b)
