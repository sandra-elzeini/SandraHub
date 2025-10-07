import streamlit as st
from datetime import datetime, timedelta
from pymongo import MongoClient

st.set_page_config(page_title="SandraHub — Weekly Notes", page_icon="📝")
st.title("SandraHub — Notes for the Week 📝")

# ---------------------
# MongoDB connection
# ---------------------
mongo_uri = st.secrets["mongodb"]["uri"]
client = MongoClient(mongo_uri)
db = client["sandrahub"]
notes_collection = db["weekly_notes"]

# ---------------------
# Helper functions
# ---------------------
def get_week_dates(start_date):
    """Return list of dates (datetime) from Sunday to Saturday of the week of start_date"""
    start_of_week = start_date - timedelta(days=start_date.weekday()+1 if start_date.weekday() != 6 else 0)
    return [start_of_week + timedelta(days=i) for i in range(7)]

def format_date(date_obj):
    return date_obj.strftime("%Y-%m-%d")

def load_day_notes(date_str):
    notes_doc = notes_collection.find_one({"date": date_str})
    return notes_doc["notes"] if notes_doc else []

def save_day_notes(date_str, notes_list):
    notes_collection.update_one(
        {"date": date_str},
        {"$set": {"notes": notes_list}},
        upsert=True
    )

# ---------------------
# Week and day selection
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
day_notes = load_day_notes(selected_day_str)

# Display existing notes with checkboxes
st.write("📝 Existing Notes:")
for i, note_item in enumerate(day_notes):
    note_text = note_item.get("note", "") if isinstance(note_item, dict) else note_item
    done_status = note_item.get("done", False) if isinstance(note_item, dict) else False

    done_checkbox = st.checkbox(note_text, value=done_status, key=f"{selected_day_str}_{i}")
    if isinstance(note_item, dict):
        note_item["done"] = done_checkbox
    else:
        day_notes[i] = {"note": note_text, "done": done_checkbox}

# Save updated done status
save_day_notes(selected_day_str, day_notes)

# Add new note
new_note = st.text_area("Add a new note:")
if st.button("💾 Save Note"):
    if not new_note.strip():
        st.warning("Please enter a note before saving!")
    else:
        day_notes.append({"note": new_note.strip(), "done": False})
        save_day_notes(selected_day_str, day_notes)
        st.success("Note saved!")

# Optional: Download all notes
all_notes = list(notes_collection.find())
st.download_button(
    "💾 Download All Notes",
    str(all_notes),
    file_name="weekly_notes.json"
)
