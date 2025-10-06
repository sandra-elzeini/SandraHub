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
            for word in words:
                if word.lower() == "and":
                    continue  # skip 'and'
                if word[0].isdigit():
                    if temp_bullet:
                        bullets.append("  - " + " ".join(temp_bullet))
                    temp_bullet = [word]
                else:
                    temp_bullet.append(word)
            if temp_bullet:
                bullets.append("  - " + " ".join(temp_bullet))

        # Display summary
        st.subheader("Summary:")
        for b in bullets:
            st.write(b)
