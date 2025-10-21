import threading
from datetime import datetime, timedelta
import json
from pathlib import Path
import logging
from services import d_stats  # your driver stats module
from config import settings   # to get CURRENT_SEASON

# ---------------- Setup logging ----------------
# ---------------- AppData Setup ----------------
APP_DIR = Path.home() / "AppData" / "Roaming" / "F1App"
APP_DIR.mkdir(exist_ok=True)  # make sure the directory exists

# ---------------- Setup logging ----------------
log_file = APP_DIR / "update_json.log"
log_file.parent.mkdir(exist_ok=True)  # ensure folder exists

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),  # log to file
        logging.StreamHandler()                            # log to terminal
    ]
)
logger = logging.getLogger(__name__)

logger.info("Logger initialized. Log file: %s", log_file)

# ---------------- AppData Setup ----------------
APP_DIR = Path.home() / "AppData" / "Roaming" / "F1App"
APP_DIR.mkdir(exist_ok=True)

SEASON = settings.CURRENT_SEASON

SCHEDULE_FILE = APP_DIR / f"race_schedule.json"
PROCESSED_FILE = APP_DIR / f"processed_races.json"


def check_and_update_stats():
    """Check schedule and run d_stats if a race is 2 days old and not processed."""
    try:
        # Load schedule
        if not SCHEDULE_FILE.exists():
            logger.warning(f"Race schedule for {SEASON} not found: {SCHEDULE_FILE}")
            return

        with SCHEDULE_FILE.open("r", encoding="utf-8") as f:
            races = json.load(f)

        # Load processed 
        try:
            with PROCESSED_FILE.open("r", encoding="utf-8") as f:
                processed_data = json.load(f)
                if processed_data and isinstance(processed_data[0], dict):
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
            update_date = race_date + timedelta(days=1) 

            if today >= update_date and race_name not in processed:
                logger.info(f"📊 Updating stats after {race_name}...")
                d_stats.main()  
                processed.add(race_name)
                updated = True

        if updated:
            # Save updated processed races as a list of names
            with PROCESSED_FILE.open("w", encoding="utf-8") as f:
                json.dump(list(processed), f, indent=4)
            logger.info(f"✅ Processed file updated: {PROCESSED_FILE}")
        else:
            logger.info("ℹ️ No new races to process.")

    except Exception as e:
        logger.error("❌ Exception in update_json thread:", exc_info=True)


def run_in_background(wait_for_completion=False):
    """Run the update in a background thread.

    Args:
        wait_for_completion (bool): If True, wait for thread to finish (standalone mode)
    """
    thread = threading.Thread(target=check_and_update_stats, daemon=True)
    thread.start()
    if wait_for_completion:
        thread.join()


def main():
    # Standalone execution: wait for completion
    run_in_background(wait_for_completion=True)


if __name__ == "__main__":
    main()
