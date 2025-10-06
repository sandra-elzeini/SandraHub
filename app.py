import streamlit as st

st.title("SandraHub — Personal AI Assistant")
st.write("Paste your meeting notes below to get a clean summary.")

raw_notes = st.text_area("Paste your meeting notes here:")

if st.button("Summarize Notes"):
    if raw_notes.strip() == "":
        st.warning("Please enter some notes first!")
    else:
        # Split into words across all lines
        words = [w for w in raw_notes.replace("\n", " ").split() if w.lower() != "and"]

        bullets = []
        temp_bullet = []
        i = 0

        while i < len(words):
            word = words[i]

            # If word starts with a digit, start a new bullet
            if word[0].isdigit():
                if temp_bullet:
                    bullets.append("  - " + " ".join(temp_bullet))
                    temp_bullet = []

                temp_bullet.append(word)
                i += 1
                # Collect following words until next word starts with a digit
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
