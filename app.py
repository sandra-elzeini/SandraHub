import streamlit as st
from datetime import datetime, timedelta
from pymongo import MongoClient

# ---------------------------
# MongoDB Connection
# ---------------------------
mongo_uri = st.secrets["mongodb"]["uri"]  # Ensure correct URI in secrets.toml
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

def save_day_notes(week_key, day_str, day_notes):
    """Save notes for a specific day"""
    notes_collection.update_one(
        {"week": week_key},
        {"$set": {f"days.{day_str}": day_notes}}
    )

def all_weeks_in_year(year):
    """Return list of week start dates (Sundays) for the entire year"""
    d = datetime(year, 1, 1)
    weeks = []
    # Move to the first Sunday
    d += timedelta(days=(6 - d.weekday()) % 7)
    while d.year == year:
        weeks.append(d)
        d += timedelta(weeks=1)
    return weeks

# ---------------------------
# Main App
# ---------------------------
st.set_page_config(page_title="SandraHub — Weekly Notes", page_icon="📝")
st.title("SandraHub — Notes for the Week 📝")

# Sidebar: Select Year
current_year = datetime.today().year
selected_year = st.sidebar.selectbox("Select Year:", range(current_year - 5, current_year + 6), index=5)

# Sidebar: Select Week
st.sidebar.header("Select Week")
weeks_options = all_weeks_in_year(selected_year)
week_labels = [format_week_range(w) for w in weeks_options]
today = datetime.today()
# Default week = current week if in selected year
default_week_idx = next((i for i, w in enumerate(weeks_options) if get_week_start(today) == w), 0)
selected_week_idx = st.sidebar.selectbox("Choose a week:", range(len(weeks_options)), format_func=lambda i: week_labels[i], index=default_week_idx)
selected_week_start = weeks_options[selected_week_idx]

week_doc = get_or_create_week_notes(selected_week_start)
week_key = f"{selected_week_start.isocalendar()[0]}-W{selected_week_start.isocalendar()[1]}"

# Sidebar: Select Day
st.sidebar.header("Select Day")
week_days = [(selected_week_start + timedelta(days=i)) for i in range(7)]
day_labels = [d.strftime("%A (%b %d, %Y)") for d in week_days]
default_day_idx = (today - selected_week_start).days if today >= selected_week_start and today < selected_week_start + timedelta(days=7) else 0
selected_day_idx = st.sidebar.selectbox("Choose a day:", range(7), format_func=lambda i: day_labels[i], index=default_day_idx)
selected_day = week_days[selected_day_idx]
selected_day_str = selected_day.strftime("%Y-%m-%d")

# Display notes for the selected day
st.subheader(f"Notes for {selected_day.strftime('%A, %b %d, %Y')}")
day_notes = week_doc["days"].get(selected_day_str, [])

# Display existing notes with checkboxes and delete buttons
st.write("📝 Existing Notes:")
for i, note_item in enumerate(day_notes.copy()):
    if isinstance(note_item, dict):
        note_text = note_item.get("note", "")
        done_status = note_item.get("done", False)
    else:
        note_text = note_item
        done_status = False

    col1, col2 = st.columns([0.9, 0.1])
    with col1:
        done_checkbox = st.checkbox(note_text, value=done_status, key=f"{selected_day_str}_{i}")
    with col2:
        if st.button("❌", key=f"delete_{selected_day_str}_{i}"):
            day_notes.pop(i)
            save_day_notes(week_key, selected_day_str, day_notes)
            st.experimental_rerun()  # Refresh after deletion

    # Update done status
    if isinstance(note_item, dict):
        note_item["done"] = done_checkbox
    else:
        day_notes[i] = {"note": note_text, "done": done_checkbox}

# Save updated notes
save_day_notes(week_key, selected_day_str, day_notes)

# Add a new note
new_note = st.text_area("Add a new note:")
if st.button("💾 Save Note"):
    if new_note.strip():
        day_notes.append({"note": new_note.strip(), "done": False})
        save_day_notes(week_key, selected_day_str, day_notes)
        st.experimental_rerun()
    else:
        st.warning("Please enter a note before saving!")

# Optional: Download weekly notes
st.download_button(
    "💾 Download This Week's Notes",
    str(week_doc),
    file_name=f"notes_{week_key}.txt"
)
