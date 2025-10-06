import streamlit as st

st.title("SandraHub — Personal AI Assistant")
st.write("Paste your meeting notes below to get a clean summary.")

raw_notes = st.text_area("Paste your meeting notes here:")

if st.button("Summarize Notes"):
    if raw_notes.strip() == "":
        st.warning("Please enter some notes first!")
    else:
        bullets = []

        # Split input into lines
        lines = [line.strip() for line in raw_notes.split("\n") if line.strip() != ""]
        
        for line in lines:
            words = line.split()
            i = 0
            temp_bullet = []

            while i < len(words):
                word = words[i]
                # Skip filler words
                if word.lower() == "and":
                    i += 1
                    continue

                # Start new bullet if temp_bullet is empty and word starts with number
                if not temp_bullet and word[0].isdigit():
                    temp_bullet.append(word)
                    i += 1
                    # Add following words until next number that starts a new item
                    while i < len(words):
                        next_word = words[i]
                        # If next word starts with digit AND previous word is also a number -> keep together
                        if next_word[0].isdigit() and temp_bullet[-1][0].isdigit():
                            temp_bullet.append(next_word)
                        # If next word starts with digit AND previous word is NOT a number -> break
                        elif next_word[0].isdigit() and not temp_bullet[-1][0].isdigit():
                            break
                        else:
                            temp_bullet.append(next_word)
                        i += 1
                    bullets.append("  - " + " ".join(temp_bullet))
                    temp_bullet = []
                else:
                    temp_bullet.append(word)
                    i += 1

            if temp_bullet:
                bullets.append("  - " + " ".join(temp_bullet))

        # Display summary
        st.subheader("Summary:")
        for b in bullets:
            st.write(b)
