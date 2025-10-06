import streamlit as st

st.title("SandraHub — Personal AI Assistant")
st.write("Paste your meeting notes below to get a clean summary.")

raw_notes = st.text_area("Paste your meeting notes here:")

if st.button("Summarize Notes"):
    if raw_notes.strip() == "":
        st.warning("Please enter some notes first!")
    else:
        lines = [line.strip() for line in raw_notes.split("\n") if line.strip() != ""]
        bullets = []

        for line in lines:
            words = line.split()
            temp_bullet = []
            i = 0
            while i < len(words):
                word = words[i]
                if word.lower() == "and":
                    i += 1
                    continue  # skip 'and'

                # Start a bullet if word starts with a digit and next word exists
                if word[0].isdigit() and i + 1 < len(words):
                    if temp_bullet:
                        bullets.append("  - " + " ".join(temp_bullet))
                        temp_bullet = []

                    # Start collecting bullet
                    bullet_words = [word]
                    i += 1
                    while i < len(words) and not (words[i][0].isdigit() and (i+1 < len(words) and words[i+1].isalpha())):
                        if words[i].lower() != "and":
                            bullet_words.append(words[i])
                        i += 1
                    bullets.append("  - " + " ".join(bullet_words))
                else:
                    temp_bullet.append(word)
                    i += 1

            if temp_bullet:
                bullets.append("  - " + " ".join(temp_bullet))

        # Display summary
        st.subheader("Summary:")
        for b in bullets:
            st.write(b)
