import streamlit as st
from datetime import datetime, timedelta
import json
import os

st.set_page_config(page_title="SandraHub — Weekly Notes", page_icon="📝")
st.title("SandraHub — Notes Planner 📝")

# ---------------------
# Helper Functions
# ---------------------
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

def get_week_start(date_obj):
    # Sunday as start of week
    start_of_week = date_obj - timedelta(days=date_obj.weekday()+1 if date_obj.weekday() != 6 else 0)
    return start_of_week

def week_range(start_date):
    # Return all 7 dates in the week
    return [start_date + timedelta(days=i) for i in range(7)]

# ---------------------
# Load notes
# ---------------------
notes_data = load_notes()

# ---------------------
# Sidebar: Select Week
# ---------------------
all_dates = sorted(notes_data.keys())
weeks_dict = {}  # map week_start_str -> list of date strings in that week

# Populate weeks_dict from saved notes
for date_str in all_dates:
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    week_start = get_week_start(dt).strftime("%Y-%m-%d")
    weeks_dict.setdefault(week_start, []).append(date_str)

# Always include current week
today = datetime.today()
current_week_start = get_week_start(today).strftime("%Y-%m-%d")
if current_week_start not in weeks_dict:
    weeks_dict[current_week_start] = [format_date(d) for d in week_range(get_week_start(today))]

# Sidebar week selector
selected_week_start = st.sidebar.selectbox(
    "Select a week:",
    sorted(weeks_dict.keys(), reverse=True),
    format_func=lambda ws: f"Week starting {datetime.strptime(ws, '%Y-%m-%d').strftime('%b %d, %Y')}"
)

# Sidebar day selector
selected_week_dates = sorted(weeks_dict[selected_week_start])
selected_day = st.sidebar.selectbox(
    "Select a day:",
    selected_week_dates,
    format_func=lambda d: datetime.strptime(d, "%Y-%m-%d").strftime("%A (%b %d, %Y)")
)

# ---------------------
# Notes Area
# ---------------------
st.subheader(f"Notes for {datetime.strptime(selected_day, '%Y-%m-%d').strftime('%A, %b %d, %Y')}")
day_notes = notes_data.get(selected_day, [])

# Display existing notes with checkboxes
updated_notes = []
st.write("📝 Existing Notes:")
for i, note_item in enumerate(day_notes):
    if isinstance(note_item, dict):
        note_text = note_item.get("note", "")
        done_status = note_item.get("done", False)
    else:
        note_text = note_item
        done_status = False

    done_checkbox = st.checkbox(note_text, value=done_status, key=f"{selected_day}_{i}")
    updated_notes.append({"note": note_text, "done": done_checkbox})

# Save updated notes
notes_data[selected_day] = updated_notes
save_notes(notes_data)

# Add new note
new_note = st.text_area("Add a new note:")
if st.button("💾 Save Note"):
    if not new_note.strip():
        st.warning("Please enter a note before saving!")
    else:
        updated_notes.append({"note": new_note.strip(), "done": False})
        notes_data[selected_day] = updated_notes
        save_notes(notes_data)
        st.success("Note saved!")

# ---------------------
# Optional: Download all notes
# ---------------------
all_notes_str = json.dumps(notes_data, indent=2)
st.download_button("💾 Download All Notes", all_notes_str, file_name="weekly_notes.json")
