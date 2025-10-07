import streamlit as st
from datetime import datetime, timedelta
from pymongo import MongoClient

# ---------------------------
# MongoDB Connection
# ---------------------------
mongo_uri = st.secrets["mongodb"]["uri"]  # Make sure your secrets.toml has the correct uri
client = MongoClient(mongo_uri)
db = client["sandrahub_db"]
notes_collection = db["weekly_notes"]

# ---------------------------
# Helper Functions
# ---------------------------
def get_week_start_from_date(date):
    """Return the Sunday of the week for a given date"""
    return date - timedelta(days=date.weekday() + 1 if date.weekday() != 6 else 0)

def format_week_range(start_date):
    """Return string like Oct 05 - Oct 11, 2025"""
    end_date = start_date + timedelta(days=6)
    return f"{start_date.strftime('%b %d')} - {end_date.strftime('%b %d, %Y')}"

def get_or_create_week_notes(year, week_number):
    """Get notes doc for a specific year and week number, or create if missing"""
    week_key = f"{year}-W{week_number}"
    doc = notes_collection.find_one({"week": week_key})
    if not doc:
        # Initialize week with empty days
        # Get the Sunday of that week
        first_day = datetime.strptime(f'{year}-W{week_number}-0', "%Y-W%W-%w")
        days = {}
        for i in range(7):
            day = first_day + timedelta(days=i)
            days[day.strftime("%Y-%m-%d")] = []
        doc = {"week": week_key, "days": days}
        notes_collection.insert_one(doc)
    return doc

def save_week_notes(doc):
    notes_collection.replace_one({"_id": doc["_id"]}, doc)

# ---------------------------
# Sidebar: Year & Week Selection
# ---------------------------
st.sidebar.header("Select Year and Week")
current_year = datetime.today().year
selected_year = st.sidebar.number_input("Year", min_value=2020, max_value=2100, value=current_year, step=1)

today = datetime.today()
current_week = today.isocalendar()[1]
selected_week = st.sidebar.number_input("Week Number", min_value=1, max_value=53, value=current_week, step=1)

week_doc = get_or_create_week_notes(selected_year, selected_week)

# ---------------------------
# Sidebar: Day Selection
# ---------------------------
week_days = list(week_doc["days"].keys())
week_day_labels = [datetime.strptime(d, "%Y-%m-%d").strftime("%A (%b %d, %Y)") for d in week_days]

selected_day_idx = st.sidebar.radio("Select Day", range(7), format_func=lambda i: week_day_labels[i])
selected_day_str = week_days[selected_day_idx]

# Highlight current day/week
is_current_week = selected_year == today.year and selected_week == today.isocalendar()[1]
is_current_day = selected_day_str == today.strftime("%Y-%m-%d")

st.title("SandraHub — Notes for the Week 📝")
if is_current_week:
    st.markdown(f"**📅 Current Week: {format_week_range(datetime.strptime(week_days[0], '%Y-%m-%d'))}**")
else:
    st.markdown(f"Week: {format_week_range(datetime.strptime(week_days[0], '%Y-%m-%d'))}")

if is_current_day:
    st.subheader(f"📝 Notes for Today ({datetime.strptime(selected_day_str, '%Y-%m-%d').strftime('%A, %b %d, %Y')})")
else:
    st.subheader(f"Notes for {datetime.strptime(selected_day_str, '%Y-%m-%d').strftime('%A, %b %d, %Y')}")

# ---------------------------
# Display Existing Notes
# ---------------------------
day_notes = week_doc["days"].get(selected_day_str, [])

delete_idx = None

st.write("📝 Existing Notes:")
for i, note_item in enumerate(day_notes.copy()):
    note_text = note_item.get("note", "") if isinstance(note_item, dict) else note_item
    done_status = note_item.get("done", False) if isinstance(note_item, dict) else False

    col1, col2 = st.columns([0.9, 0.1])
    with col1:
        done_checkbox = st.checkbox(note_text, value=done_status, key=f"{selected_day_str}_{i}")
    with col2:
        if st.button("❌", key=f"delete_{selected_day_str}_{i}"):
            delete_idx = i  # mark for deletion

    # Update done status
    if isinstance(note_item, dict):
        note_item["done"] = done_checkbox
    else:
        day_notes[i] = {"note": note_text, "done": done_checkbox}

# Delete note if clicked
if delete_idx is not None:
    day_notes.pop(delete_idx)
    week_doc["days"][selected_day_str] = day_notes
    save_week_notes(week_doc)
    st.experimental_rerun()

# ---------------------------
# Add New Note
# ---------------------------
new_note = st.text_area("Add a new note:")

if st.button("💾 Save Note"):
    if not new_note.strip():
        st.warning("Please enter a note before saving!")
    else:
        day_notes.append({"note": new_note.strip(), "done": False})
        week_doc["days"][selected_day_str] = day_notes
        save_week_notes(week_doc)
        st.success("Note saved!")
        st.experimental_rerun()

# ---------------------------
# Optional: Download all notes
# ---------------------------
import json
all_notes_str = json.dumps(notes_collection.find_one({"week": week_doc["week"]}), default=str, indent=2)
st.download_button("💾 Download This Week's Notes", all_notes_str, file_name=f"weekly_notes_{week_doc['week']}.json")
