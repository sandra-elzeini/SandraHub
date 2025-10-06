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

                # Start new bullet if word starts with a digit
                if word[0].isdigit():
                    if temp_bullet:
                        bullets.append("  - " + " ".join(temp_bullet))
                    temp_bullet = [word]

                    # Append following words that do not start with a digit
                    i += 1
                    while i < len(words) and not words[i][0].isdigit() and words[i].lower() != "and":
                        temp_bullet.append(words[i])
                        i += 1
                    bullets.append("  - " + " ".join(temp_bullet))
                    temp_bullet = []
                else:
                    temp_bullet.append(word)
                    i += 1

            # Add leftover words if any
            if temp_bullet:
                bullets.append("  - " + " ".join(temp_bullet))

        # Display summary
        st.subheader("Summary:")
        for b in bullets:
            st.write(b)
