import streamlit as st
from datetime import datetime, timedelta
from pymongo import MongoClient
import json

# ---------------------------
# MongoDB Connection
# ---------------------------
mongo_uri = st.secrets["mongodb"]["uri"]  # your secrets.toml must have [mongodb] uri
client = MongoClient(mongo_uri)
db = client["sandrahub_db"]
notes_collection = db["weekly_notes"]

# ---------------------------
# Helper Functions
# ---------------------------
def get_week_start(date):
    """Return Sunday of the week for a given date"""
    return date - timedelta(days=date.weekday() + 1 if date.weekday() != 6 else 0)

def format_week_range(start_date):
    """Return string like Oct 05 - Oct 11, 2025"""
    end_date = start_date + timedelta(days=6)
    return f"{start_date.strftime('%b %d')} - {end_date.strftime('%b %d, %Y')}"

def get_or_create_week_notes(week_start):
    """Get notes for a week, or create if missing"""
    week_key = week_start.strftime("%Y-%m-%d")  # use start date as key
    doc = notes_collection.find_one({"week_start": week_key})
    if not doc:
        # Initialize week with empty days
        days = {}
        for i in range(7):
            day = week_start + timedelta(days=i)
            days[day.strftime("%Y-%m-%d")] = []
        doc = {"week_start": week_key, "days": days}
        notes_collection.insert_one(doc)
    return doc

# ---------------------------
# Sidebar: Year, Week, Day Selection
# ---------------------------
st.sidebar.header("Select Year, Week & Day")

current_year = datetime.today().year
year = st.sidebar.selectbox("Year:", list(range(current_year, current_year + 5)), index=0)

# Generate all weeks for the selected year
first_day = datetime(year, 1, 1)
weeks = []
for i in range(0, 52):
    week_start = get_week_start(first_day + timedelta(days=i*7))
    weeks.append(week_start)
week_labels = [format_week_range(w) for w in weeks]
week_start = st.sidebar.selectbox("Week:", weeks, format_func=lambda d: format_week_range(d), index=0)

# Day selection
week_dates = [week_start + timedelta(days=i) for i in range(7)]
selected_day = st.sidebar.selectbox(
    "Day:",
    week_dates,
    format_func=lambda d: d.strftime("%A (%b %d, %Y)"),
    index=(datetime.today().weekday() if datetime.today() in week_dates else 0)
)
selected_day_str = selected_day.strftime("%Y-%m-%d")

# ---------------------------
# Load week notes
# ---------------------------
week_doc = get_or_create_week_notes(week_start)
day_notes = week_doc["days"][selected_day_str]

# ---------------------------
# Main App
# ---------------------------
st.title("SandraHub — Notes for the Week 📝")
st.subheader(f"Week: {format_week_range(week_start)}")
st.subheader(f"📝 Notes for {selected_day.strftime('%A, %b %d, %Y')}")

# Add new note
if "new_note" not in st.session_state:
    st.session_state.new_note = ""

st.session_state.new_note = st.text_area("Add a new note:", value=st.session_state.new_note)

if st.button("💾 Save Note"):
    if st.session_state.new_note.strip():
        day_notes.append(st.session_state.new_note.strip())
        notes_collection.update_one(
            {"week_start": week_start.strftime("%Y-%m-%d")},
            {"$set": {f"days.{selected_day_str}": day_notes}}
        )
        st.success("Note saved!")
        st.session_state.new_note = ""  # clear input
    else:
        st.warning("Please enter a note before saving!")

# Display existing notes with delete buttons
st.write("📝 Existing Notes:")
for i, note_item in enumerate(day_notes.copy()):  # copy to avoid loop issues
    col1, col2 = st.columns([0.9, 0.1])
    col1.write(f"- {note_item}")
    if col2.button("❌", key=f"delete_{i}"):
        day_notes.pop(i)
        notes_collection.update_one(
            {"week_start": week_start.strftime("%Y-%m-%d")},
            {"$set": {f"days.{selected_day_str}": day_notes}}
        )
        st.success("Note deleted!")

# Optional: Download notes for the week
all_notes_str = json.dumps(week_doc, indent=2)
st.download_button("💾 Download Week Notes", all_notes_str, file_name=f"weekly_notes_{week_start.strftime('%Y-%m-%d')}.json")
