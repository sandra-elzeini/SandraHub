import streamlit as st

st.title("SandraHub — Personal AI Assistant")
st.write("Paste your meeting notes below to get a clean summary.")

raw_notes = st.text_area("Paste your meeting notes here:")

if st.button("Summarize Notes"):
    if raw_notes.strip() == "":
        st.warning("Please enter some notes first!")
    else:
        words = raw_notes.split()
        bullets = []
        temp_bullet = []

        i = 0
        while i < len(words):
            word = words[i]
            # Skip filler words
            if word.lower() == "and":
                i += 1
                continue

            # If word starts with a digit, start a new car bullet
            if word[0].isdigit():
                if temp_bullet:
                    bullets.append("  - " + " ".join(temp_bullet))
                    temp_bullet = []

                temp_bullet.append(word)
                i += 1
                # Include following words until next word that starts with a digit
                while i < len(words) and not words[i][0].isdigit():
                    temp_bullet.append(words[i])
                    i += 1
                bullets.append("  - " + " ".join(temp_bullet))
                temp_bullet = []
            else:
                temp_bullet.append(word)
                i += 1

        # Add any leftover text
        if temp_bullet:
            bullets.append("  - " + " ".join(temp_bullet))

        # Display summary
        st.subheader("Summary:")
        for b in bullets:
            st.write(b)
