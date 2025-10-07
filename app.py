import streamlit as st
from datetime import datetime, timedelta
from pymongo import MongoClient

# ---------------------------
# MongoDB Connection
# ---------------------------
mongo_uri = st.secrets["mongodb"]["uri"]  # Ensure your secrets.toml has your URI
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
    week_iso = week_start.isocalendar()  # year, week number, weekday
    week_key = f"{week_iso[0]}-W{week_iso[1]}"

    doc = notes_collection.find_one({"week": week_key})
    if not doc:
        # Initialize week with empty days
        days = {}
        for i in range(7):
            day = week_start + timedelta(days=i)
            days[day.strftime("%Y-%m-%d")] = []
        doc = {"week": week_key, "days": days}
        notes_collection.insert_one(doc)
    return doc

def save_day_note(week_key, day_str, note_text):
    """Append a note to a specific day in the week"""
    notes_collection.update_one(
        {"week": week_key},
        {"$push": {f"days.{day_str}": note_text}}
    )

# ---------------------------
# Streamlit UI
# ---------------------------

st.set_page_config(page_title="SandraHub — Weekly Notes", page_icon="📝")
st.title("SandraHub — Notes for the Week 📝")

today = datetime.today()

# ---------------------------
# Generate list of weeks for selection (past and future weeks)
# ---------------------------
start_year = datetime(today.year, 1, 1)
weeks_list = []
for i in range(0, 52):  # Adjust as needed for more weeks
    week_start = get_week_start(start_year + timedelta(weeks=i))
    weeks_list.append(week_start)

# Sidebar: choose a week
selected_week_start = st.sidebar.selectbox(
    "Choose a week:",
    weeks_list,
    format_func=lambda d: format_week_range(d)
)

# Load or create the week in MongoDB
week_doc = get_or_create_week_notes(selected_week_start)
week_key = week_doc["week"]

# Sidebar: choose a day
selected_day = st.sidebar.selectbox(
    "Choose a day:",
    [selected_week_start + timedelta(days=i) for i in range(7)],
    format_func=lambda d: f"{d.strftime('%A')} ({d.strftime('%b %d, %Y')})"
)

day_str = selected_day.strftime("%Y-%m-%d")
day_notes = week_doc["days"].get(day_str, [])

# ---------------------------
# Display notes
# ---------------------------
st.subheader(f"Notes for {selected_day.strftime('%A, %b %d, %Y')}")

if day_notes:
    st.write("📝 Existing Notes:")
    for note in day_notes:
        st.write(f"- {note}")
else:
    st.write("No notes yet for this day.")

# Add new note
new_note = st.text_area("Add a new note:")

if st.button("💾 Save Note"):
    if new_note.strip():
        save_day_note(week_key, day_str, new_note.strip())
        st.success("Note saved! Refresh the page to see it.")
    else:
        st.warning("Please enter a note before saving!")

# Optional: download all notes
if st.button("💾 Download All Notes"):
    import json
    all_notes = list(notes_collection.find({}, {"_id": 0}))
    st.download_button("Download JSON", json.dumps(all_notes, indent=2), file_name="all_notes.json")
