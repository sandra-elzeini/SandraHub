import streamlit as st
from datetime import datetime, timedelta
import json
import os

st.set_page_config(page_title="SandraHub — Weekly Notes", page_icon="📝")
st.title("SandraHub — Notes for the Week 📝")

# ---------------------
# Helper Functions
# ---------------------
def get_week_dates(start_date):
    """Return list of dates (datetime) from Sunday to Saturday of the week of start_date"""
    start_of_week = start_date - timedelta(days=start_date.weekday()+1 if start_date.weekday() != 6 else 0)
    return [start_of_week + timedelta(days=i) for i in range(7)]

def format_date(date_obj):
    return date_obj.strftime("%Y-%m-%d")

def load_notes(file_path="weekly_notes.json"):
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            return json.load(f)
    return {}

def save_notes(data, file_path="weekly_notes.json"):
    with open(file_path, "w") as f:
        json.dump(data, f, indent=2)

# ---------------------
# Load or initialize notes
# ---------------------
notes_data = load_notes()

# ---------------------
# Week selection
# ---------------------
today = datetime.today()
week_dates = get_week_dates(today)
week_str = f"{week_dates[0].strftime('%b %d')} - {week_dates[-1].strftime('%b %d, %Y')}"

st.sidebar.header(f"Notes for the Week ({week_str})")
selected_day = st.sidebar.selectbox(
    "Choose a day:",
    week_dates,
    format_func=lambda d: f"{d.strftime('%A')} ({d.strftime('%b %d, %Y')})"
)

selected_day_str = format_date(selected_day)

# ---------------------
# Notes area
# ---------------------
st.subheader(f"Notes for {selected_day.strftime('%A, %b %d, %Y')}")

# Initialize day notes if not present
day_notes = notes_data.get(selected_day_str, [])

# Display existing notes with checkboxes
st.write("📝 Existing Notes:")
for i, note_item in enumerate(day_notes):
    # note_item can be string or dict with done status
    if isinstance(note_item, dict):
        note_text = note_item.get("note", "")
        done_status = note_item.get("done", False)
    else:
        note_text = note_item
        done_status = False

    done_checkbox = st.checkbox(note_text, value=done_status, key=f"{selected_day_str}_{i}")
    # Update done status
    if isinstance(note_item, dict):
        note_item["done"] = done_checkbox
    else:
        day_notes[i] = {"note": note_text, "done": done_checkbox}

# Save updated done status
notes_data[selected_day_str] = day_notes
save_notes(notes_data)

# Add new note
new_note = st.text_area("Add a new note:")

if st.button("💾 Save Note"):
    if not new_note.strip():
        st.warning("Please enter a note before saving!")
    else:
        day_notes.append({"note": new_note.strip(), "done": False})
        notes_data[selected_day_str] = day_notes
        save_notes(notes_data)
        st.success("Note saved!")

# ---------------------
# Optional: Download all notes
# ---------------------
all_notes_str = json.dumps(notes_data, indent=2)
st.download_button("💾 Download All Notes", all_notes_str, file_name="weekly_notes.json")
