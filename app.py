import streamlit as st
from datetime import datetime, timedelta, date
from pymongo import MongoClient

# ---------------------------
# MongoDB Connection
# ---------------------------
mongo_uri = st.secrets["mongodb"]["uri"]  # Your MongoDB URI in secrets.toml
client = MongoClient(mongo_uri)
db = client["sandrahub_db"]
notes_collection = db["weekly_notes"]

# ---------------------------
# Helper Functions
# ---------------------------

def get_week_start(date_obj):
    """Return the Sunday of the week for a given date"""
    return date_obj - timedelta(days=date_obj.weekday() + 1 if date_obj.weekday() != 6 else 0)

def format_week_range(start_date):
    """Return string like Oct 05 - Oct 11, 2025"""
    end_date = start_date + timedelta(days=6)
    return f"{start_date.strftime('%b %d')} - {end_date.strftime('%b %d, %Y')}"

def generate_all_weeks(year):
    """Return a list of week start dates (Sundays) for the whole year"""
    first_day = date(year, 1, 1)
    last_day = date(year, 12, 31)
    # Find first Sunday
    first_sunday = first_day - timedelta(days=first_day.weekday() + 1 if first_day.weekday() != 6 else 0)
    weeks = []
    current = first_sunday
    while current <= last_day:
        weeks.append(current)
        current += timedelta(days=7)
    return weeks

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

def save_day_notes(week_key, day_str, notes_list):
    """Save notes for a specific day"""
    notes_collection.update_one(
        {"week": week_key},
        {"$set": {f"days.{day_str}": notes_list}}
    )

# ---------------------------
# Streamlit Layout
# ---------------------------

st.set_page_config(page_title="SandraHub — Weekly Notes", page_icon="📝")
st.title("SandraHub — Notes for the Week 📝")

# Today
today = datetime.today().date()
all_weeks = generate_all_weeks(today.year)

# Sidebar: select week
# Automatically select the current week
default_idx = 0
for i, wk in enumerate(all_weeks):
    if get_week_start(today) == wk:
        default_idx = i
        break

selected_week_start = st.sidebar.radio(
    "Choose a week:",
    all_weeks,
    index=default_idx,
    format_func=lambda d: format_week_range(d)
)

# Load or create week in MongoDB
week_doc = get_or_create_week_notes(selected_week_start)
week_iso = selected_week_start.isocalendar()
week_key = f"{week_iso[0]}-W{week_iso[1]}"
week_days = week_doc["days"]

# Sidebar: select day
selected_day_str = st.sidebar.selectbox(
    "Choose a day:",
    list(week_days.keys()),
    index=(today - selected_week_start).days if selected_week_start <= today <= selected_week_start + timedelta(days=6) else 0
)

st.subheader(f"Notes for {datetime.strptime(selected_day_str, '%Y-%m-%d').strftime('%A, %b %d, %Y')}")

# Load day notes
day_notes = week_days.get(selected_day_str, [])

# Display existing notes with checkboxes
st.write("📝 Existing Notes:")
for i, note_item in enumerate(day_notes):
    if isinstance(note_item, dict):
        note_text = note_item.get("note", "")
        done_status = note_item.get("done", False)
    else:
        note_text = note_item
        done_status = False

    done_checkbox = st.checkbox(note_text, value=done_status, key=f"{selected_day_str}_{i}")
    if isinstance(note_item, dict):
        note_item["done"] = done_checkbox
    else:
        day_notes[i] = {"note": note_text, "done": done_checkbox}

# Save updated day notes
save_day_notes(week_key, selected_day_str, day_notes)

# Add new note
new_note = st.text_area("Add a new note:")

if st.button("💾 Save Note"):
    if not new_note.strip():
        st.warning("Please enter a note before saving!")
    else:
        day_notes.append({"note": new_note.strip(), "done": False})
        save_day_notes(week_key, selected_day_str, day_notes)
        st.success("Note saved!")

# Optional: Download all notes
all_notes_str = str(week_doc)
st.download_button("💾 Download This Week's Notes", all_notes_str, file_name=f"{week_key}_notes.json")
