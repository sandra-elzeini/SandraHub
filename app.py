import streamlit as st
from datetime import datetime, timedelta
from pymongo import MongoClient

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
    """Return Sunday of the week for a given date"""
    return date - timedelta(days=date.weekday() + 1 if date.weekday() != 6 else 0)

def format_week_range(start_date):
    """Return string like Oct 05 - Oct 11, 2025"""
    end_date = start_date + timedelta(days=6)
    return f"{start_date.strftime('%b %d')} - {end_date.strftime('%b %d, %Y')}"

def get_or_create_week_notes(week_start):
    """Get notes doc for a week, or create if missing"""
    week_key = format_week_range(week_start)
    doc = notes_collection.find_one({"week": week_key})
    if not doc:
        days = {}
        for i in range(7):
            day = week_start + timedelta(days=i)
            days[day.strftime("%Y-%m-%d")] = []
        doc = {"week": week_key, "days": days}
        notes_collection.insert_one(doc)
    return doc

def save_week_notes(doc):
    notes_collection.update_one({"week": doc["week"]}, {"$set": {"days": doc["days"]}})

# ---------------------------
# Session State Defaults
# ---------------------------
today = datetime.today()
if "selected_date" not in st.session_state:
    st.session_state.selected_date = today

# ---------------------------
# Select Year
# ---------------------------
year_options = list(range(today.year - 1, today.year + 2))
selected_year = st.selectbox("Select Year", year_options, index=year_options.index(today.year))

# ---------------------------
# Week Navigation
# ---------------------------
current_week_start = get_week_start(st.session_state.selected_date)
week_doc = get_or_create_week_notes(current_week_start)

st.header("SandraHub — Notes for the Week 📝")
st.subheader(f"Week: {week_doc['week']}")

# ---------------------------
# Select Day
# ---------------------------
days = list(week_doc["days"].keys())
day_str = st.selectbox("Select Day", days, index=days.index(st.session_state.selected_date.strftime("%Y-%m-%d")))
day_notes = week_doc["days"][day_str]

st.subheader(f"📝 Notes for {datetime.strptime(day_str, '%Y-%m-%d').strftime('%A, %b %d, %Y')}")
st.text("📝 Existing Notes:")
for i, note in enumerate(day_notes):
    st.text(f"{i+1}. {note}")

# ---------------------------
# Add new note
# ---------------------------
new_note = st.text_area("Add a new note:")
if st.button("💾 Save Note"):
    if new_note.strip():
        day_notes.append(new_note.strip())
        week_doc["days"][day_str] = day_notes
        save_week_notes(week_doc)
        st.success("Note saved!")
        st.experimental_rerun()  # safe rerun only after saving

# ---------------------------
# Delete notes
# ---------------------------
for i, note in enumerate(day_notes.copy()):
    col1, col2 = st.columns([0.9, 0.1])
    with col1:
        st.text_input(f"Note {i+1}", value=note, key=f"{day_str}_{i}")
    with col2:
        if st.button("🗑️", key=f"delete_{day_str}_{i}"):
            day_notes.pop(i)
            week_doc["days"][day_str] = day_notes
            save_week_notes(week_doc)
            st.success("Note deleted!")
            st.experimental_rerun()  # safe rerun only after deleting
