import streamlit as st
from datetime import datetime, timedelta
from pymongo import MongoClient
import json

st.set_page_config(page_title="SandraHub — Weekly Notes", page_icon="📝")
st.title("SandraHub — Notes for the Week 📝")

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
    week_key = week_start.strftime("%Y-%m-%d")
    doc = notes_collection.find_one({"week_start": week_key})
    if not doc:
        days = { (week_start + timedelta(days=i)).strftime("%Y-%m-%d"): [] for i in range(7) }
        doc = {"week_start": week_key, "days": days}
        notes_collection.insert_one(doc)
    return doc

def save_week_notes(doc):
    notes_collection.replace_one({"week_start": doc["week_start"]}, doc)

def clean_doc_for_json(doc):
    """Remove ObjectId so JSON can be serialized"""
    doc_clean = doc.copy()
    if "_id" in doc_clean:
        doc_clean["_id"] = str(doc_clean["_id"])
    return doc_clean

# ---------------------------
# Session State Defaults
# ---------------------------
if "week_index" not in st.session_state:
    st.session_state["week_index"] = None

if "day_index" not in st.session_state:
    st.session_state["day_index"] = None

# ---------------------------
# Sidebar: Year / Week / Day selection
# ---------------------------
current_year = datetime.today().year
year_selected = st.sidebar.selectbox(
    "Select Year", list(range(current_year-1, current_year+5)), index=1
)

# Generate weeks for the selected year
first_day = datetime(year_selected, 1, 1)
weeks = [get_week_start(first_day + timedelta(days=i*7)) for i in range(53)]
week_display = [format_week_range(w) for w in weeks]

# Default to current week if session state not set
if st.session_state["week_index"] is None:
    for i, w in enumerate(weeks):
        if w <= datetime.today() <= w + timedelta(days=6):
            st.session_state["week_index"] = i
            break
    if st.session_state["week_index"] is None:
        st.session_state["week_index"] = 0

week_selected_index = st.sidebar.selectbox(
    "Select Week", range(len(weeks)),
    format_func=lambda i: week_display[i],
    index=st.session_state["week_index"]
)
st.session_state["week_index"] = week_selected_index
week_start = weeks[week_selected_index]

# Generate days for selected week
days = [week_start + timedelta(days=i) for i in range(7)]

# Default to current day if session state not set
if st.session_state["day_index"] is None:
    for i, d in enumerate(days):
        if d.date() == datetime.today().date():
            st.session_state["day_index"] = i
            break
    if st.session_state["day_index"] is None:
        st.session_state["day_index"] = 0

day_selected_index = st.sidebar.selectbox(
    "Select Day", range(7),
    format_func=lambda i: days[i].strftime("%A, %b %d, %Y"),
    index=st.session_state["day_index"]
)
st.session_state["day_index"] = day_selected_index
day_selected = days[day_selected_index]
day_str = day_selected.strftime("%Y-%m-%d")

# ---------------------------
# Load or create week notes
# ---------------------------
week_doc = get_or_create_week_notes(week_start)
day_notes = week_doc["days"].get(day_str, [])

# ---------------------------
# Display notes and allow edits
# ---------------------------
st.subheader(f"Week: {format_week_range(week_start)}")
st.write(f"📝 Notes for {day_selected.strftime('%A, %b %d, %Y')}")

st.write("📝 Existing Notes:")
for i, note in enumerate(day_notes.copy()):
    note_text = note if isinstance(note, str) else note.get("note", "")
    col1, col2 = st.columns([0.9, 0.1])
    with col1:
        st.text_input(f"Note {i+1}", value=note_text, key=f"{day_str}_{i}")
    with col2:
        if st.button("🗑️", key=f"delete_{day_str}_{i}"):
            day_notes.pop(i)
            week_doc["days"][day_str] = day_notes
            save_week_notes(week_doc)
            st.success("Note deleted!")

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
    else:
        st.warning("Please enter a note before saving!")

# ---------------------------
# Download week notes
# ---------------------------
week_doc_clean = clean_doc_for_json(week_doc)
all_notes_str = json.dumps(week_doc_clean, indent=2)
st.download_button(
    "💾 Download Week Notes",
    all_notes_str,
    file_name=f"weekly_notes_{week_start.strftime('%Y-%m-%d')}.json"
)
