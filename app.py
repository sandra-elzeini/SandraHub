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
