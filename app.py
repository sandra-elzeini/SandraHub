import streamlit as st
from datetime import datetime, timedelta
from pymongo import MongoClient

# ---------------------------
# MongoDB Connection
# ---------------------------
mongo_uri = st.secrets["mongodb"]["uri"]  # Set in secrets.toml
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

def get_or_create_week_notes(year, week_number):
    """Get notes doc for a week, or create if missing"""
    week_key = f"{year}-W{week_number}"
    doc = notes_collection.find_one({"week": week_key})
    if not doc:
        # Initialize empty days for the week
        start_date = datetime.strptime(f'{year}-W{week_number}-0', "%Y-W%W-%w")  # Sunday
        days = { (start_date + timedelta(days=i)).strftime("%Y-%m-%d") : [] for i in range(7) }
        doc = {"week": week_key, "days": days}
        notes_collection.insert_one(doc)
    return doc

def save_week_notes(doc):
    """Update week notes in MongoDB"""
    notes_collection.update_one({"week": doc["week"]}, {"$set": {"days": doc["days"]}})

# ---------------------------
# Sidebar: Year and Week selection
# ---------------------------
st.sidebar.header("Select Year & Week")
current_year = datetime.today().year
selected_year = st.sidebar.selectbox("Year:", list(range(current_year-1, current_year+2)), index=1)

# Weeks in year
weeks_in_year = 52
week_numbers = list(range(1, weeks_in_year+1))
today = datetime.today()
current_week_number = today.isocalendar()[1] if today.year == selected_year else 1
selected_week_number = st.sidebar.selectbox("Week:", week_numbers, index=current_week_number-1)

# Load or create week notes
week_doc = get_or_create_week_notes(selected_year, selected_week_number)
week_start_date = datetime.strptime(f'{selected_year}-W{selected_week_number}-0', "%Y-W%W-%w")
week_str = format_week_range(week_start_date)

st.title("SandraHub — Notes for the Week 📝")
st.subheader(f"Week: {week_str}")

# ---------------------------
# Day selection
# ---------------------------
st.sidebar.header("Select Day")
week_dates = [week_start_date + timedelta(days=i) for i in range(7)]
selected_day = st.sidebar.selectbox(
    "Day:",
    week_dates,
    index=(today.weekday()+1 if today.weekday()!=6 else 0),
    format_func=lambda d: f"{d.strftime('%A')} ({d.strftime('%b %d, %Y')})"
)
selected_day_str = selected_day.strftime("%Y-%m-%d")

# ---------------------------
# Display notes for selected day
# ---------------------------
st.subheader(f"📝 Notes for {selected_day.strftime('%A, %b %d, %Y')}")

day_notes = week_doc["days"].get(selected_day_str, [])

# --- Display notes with delete button ---
delete_index = None
for i, note_item in enumerate(day_notes.copy()):
    note_text = note_item.get("note") if isinstance(note_item, dict) else note_item
    done_status = note_item.get("done", False) if isinstance(note_item, dict) else False

    col1, col2 = st.columns([0.9, 0.1])
    with col1:
        done_checkbox = st.checkbox(note_text, value=done_status, key=f"{selected_day_str}_{i}")
    with col2:
        if st.button("❌", key=f"delete_{selected_day_str}_{i}"):
            delete_index = i

    # Update done status
    if isinstance(note_item, dict):
        note_item["done"] = done_checkbox
    else:
        day_notes[i] = {"note": note_text, "done": done_checkbox}

# Delete note after loop
if delete_index is not None:
    day_notes.pop(delete_index)
    week_doc["days"][selected_day_str] = day_notes
    save_week_notes(week_doc)
    st.experimental_rerun()

# ---------------------------
# Add new note
# ---------------------------
new_note = st.text_area("Add a new note:")
if st.button("💾 Save Note"):
    if new_note.strip():
        day_notes.append({"note": new_note.strip(), "done": False})
        week_doc["days"][selected_day_str] = day_notes
        save_week_notes(week_doc)
        st.success("Note saved!")
        st.experimental_rerun()
    else:
        st.warning("Please enter a note before saving!")

# ---------------------------
# Optional: Download all notes
# ---------------------------
import json
all_notes_str = json.dumps(week_doc, indent=2)
st.download_button("💾 Download This Week's Notes", all_notes_str, file_name=f"weekly_notes_{selected_year}_W{selected_week_number}.json")
