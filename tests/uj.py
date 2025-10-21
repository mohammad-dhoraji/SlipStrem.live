import threading
from datetime import datetime, timedelta
import json
from pathlib import Path
from services import d_stats  # your driver stats module
from config import settings   # to get CURRENT_SEASON

# ---------------- AppData Setup ----------------
APP_DIR = Path.home() / "AppData" / "Roaming" / "F1App"
APP_DIR.mkdir(exist_ok=True)

# --- Use the same season your app uses ---
SEASON = settings.CURRENT_SEASON

SCHEDULE_FILE = APP_DIR / f"race_schedule.json"
PROCESSED_FILE = APP_DIR / f"processed_races.json"


def check_and_update_stats():
    """Check schedule and run d_stats if a race is 2 days old and not processed."""
    # Load schedule
    if not SCHEDULE_FILE.exists():
        print(f"⚠️ Race schedule for {SEASON} not found: {SCHEDULE_FILE}")
        return

    with SCHEDULE_FILE.open("r", encoding="utf-8") as f:
        races = json.load(f)

    # Load processed races safely
    try:
        with PROCESSED_FILE.open("r", encoding="utf-8") as f:
            processed_data = json.load(f)
            if processed_data and isinstance(processed_data[0], dict):
                # If the JSON contains dicts, extract race names
                processed = set(r["raceName"] for r in processed_data)
            else:
                processed = set(processed_data)
    except FileNotFoundError:
        processed = set()

    today = datetime.today()
    updated = False

    for race in races:
        race_name = race["raceName"]
        race_date = datetime.strptime(race["date"], "%Y-%m-%d")
        update_date = race_date + timedelta(days=1)  # run stats 2 days after race

        if today >= update_date and race_name not in processed:
            print(f"📊 Updating stats after {race_name}...")
            d_stats.main()  # Run your stats update
            processed.add(race_name)
            updated = True

    if updated:
        # Save updated processed races as a list of names
        with PROCESSED_FILE.open("w", encoding="utf-8") as f:
            json.dump(list(processed), f, indent=4)
        print(f"✅ Processed file updated: {PROCESSED_FILE}")
    else:
        print("ℹ️ No new races to process.")


def main():
    # Run in a background thread
    thread = threading.Thread(target=check_and_update_stats)
    thread.start()
    thread.join()  # Wait for completion when running standalone


if __name__ == "__main__":
    main()
