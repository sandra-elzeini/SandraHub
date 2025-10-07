import streamlit as st
from datetime import datetime, timedelta
from pymongo import MongoClient
from bson import ObjectId
import json

# ---------------------------
# MongoDB Connection
# ---------------------------
mongo_uri = st.secrets["mongodb"]["uri"]
client = MongoClient(mongo_uri)
db = client["sandrahub_db"]
notes_collection = db["weekly_notes"]

# ---------------------------
# Helper Functions
# ---------------------------

def get_week_start(date):
    """Return the Sunday of the week for a given date"""
    return date - timedelta(days=date.weekday() + 1 if date.weekday() != 6 else 0)

def format_week_range(start_date):
    """Return string like Oct 05 - Oct 11, 2025"""
    end_date = start_date + timedelta(days=6)
    return f"{start_date.strftime('%b %d')} - {end_date.strftime('%b %d, %Y')}"

def get_or_create_week_notes(week_start):
    """Get notes doc for a week, or create if missing"""
    week_key = week_start.strftime("%Y-%m-%d")  # use the start date of the week as key
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

def convert_to_serializable(obj):
    if isinstance(obj, ObjectId):
        return str(obj)
    raise TypeError(f"Type {type(obj)} not serializable")

# ---------------------------
# App Layout
# ---------------------------
st.set_page_config(page_title="SandraHub — Notes", page_icon="📝")
st.title("SandraHub — Notes for the Week 📝")

# Year selection
current_year = datetime.today().year
selected_year = st.sidebar.selectbox(
    "Select Year",
    list(range(current_year-1, current_year+2)),
    index=1
)

# Calculate all Sundays in the selected year for week selection
def all_sundays(year):
    date = datetime(year, 1, 1)
    # find first Sunday
    while date.weekday() != 6:
        date += timedelta(days=1)
    sundays = []
    while date.year == year:
        sundays.append(date)
        date += timedelta(days=7)
    return sundays

sundays = all_sundays(selected_year)
week_ranges = [format_week_range(s) for s in sundays]
selected_week_range = st.sidebar.selectbox("Select Week", week_ranges)
week_start = sundays[week_ranges.index(selected_week_range)]

# Day selection
days = [week_start + timedelta(days=i) for i in range(7)]
selected_day = st.sidebar.selectbox(
    "Select Day",
    days,
    format_func=lambda d: d.strftime("%A (%b %d, %Y)")
)
selected_day_str = selected_day.strftime("%Y-%m-%d")

# Load or create notes for this week
week_doc = get_or_create_week_notes(week_start)
day_notes = week_doc["days"].get(selected_day_str, [])

# ---------------------------
# Display Notes
# ---------------------------
st.subheader(f"📝 Notes for {selected_day.strftime('%A, %b %d, %Y')}")
st.write("📝 Existing Notes:")

# Display existing notes with delete option
for i, note_item in enumerate(day_notes):
    col1, col2 = st.columns([0.9, 0.1])
    col1.write(f"- {note_item}")
    if col2.button("❌", key=f"delete_{i}"):
        day_notes.pop(i)
        notes_collection.update_one(
            {"week_start": week_start.strftime("%Y-%m-%d")},
            {"$set": {f"days.{selected_day_str}": day_notes}}
        )
        st.experimental_rerun()

# Add new note
new_note = st.text_area("Add a new note:")
if st.button("💾 Save Note"):
    if new_note.strip():
        day_notes.append(new_note.strip())
        notes_collection.update_one(
            {"week_start": week_start.strftime("%Y-%m-%d")},
            {"$set": {f"days.{selected_day_str}": day_notes}}
        )
        st.success("Note saved!")
        st.experimental_rerun()
    else:
        st.warning("Please enter a note before saving!")

# Download this week's notes
all_notes_str = json.dumps(week_doc, indent=2, default=convert_to_serializable)
st.download_button(
    "💾 Download This Week's Notes",
    all_notes_str,
    file_name=f"weekly_notes_{week_start.strftime('%Y-%m-%d')}.json"
)
