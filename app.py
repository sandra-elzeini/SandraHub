# ---------------------------
# Add new note
# ---------------------------
if "save_trigger" not in st.session_state:
    st.session_state.save_trigger = False

new_note = st.text_area("Add a new note:")
if st.button("💾 Save Note"):
    if new_note.strip():
        day_notes.append(new_note.strip())
        week_doc["days"][day_str] = day_notes
        save_week_notes(week_doc)
        st.success("Note saved!")
        st.session_state.save_trigger = True  # trigger rerun safely

# ---------------------------
# Delete button for existing notes
# ---------------------------
for i, note in enumerate(day_notes):
    note_text = note if isinstance(note, str) else note.get("note", "")
    col1, col2 = st.columns([0.9, 0.1])
    with col1:
        st.text_input(f"Note {i+1}", value=note_text, key=f"{day_str}_{i}")
    with col2:
        if st.button("🗑️", key=f"delete_{day_str}_{i}"):
            day_notes.pop(i)
            week_doc["days"][day_str] = day_notes
            save_week_notes(week_doc)
            st.session_state.save_trigger = True  # trigger rerun safely

# ---------------------------
# Safe rerun if triggered
# ---------------------------
if st.session_state.save_trigger:
    st.session_state.save_trigger = False
    st.experimental_rerun()
