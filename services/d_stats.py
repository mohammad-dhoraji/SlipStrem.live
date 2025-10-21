import requests
import json
import time
from pathlib import Path

BASE_URL = "https://api.jolpi.ca/ergast/f1"

# ---------------- AppData Setup ----------------
APP_DIR = Path.home() / "AppData" / "Roaming" / "F1App"
APP_DIR.mkdir(exist_ok=True)

DRIVERS_FILE = APP_DIR / "drivers_stats.json"
SCHEDULE_FILE = APP_DIR / "race_schedule.json"
PROCESSED_FILE = APP_DIR / "processed_races.json"

# ---------- Helper Functions ----------

def safe_get(url, retries=3, delay=2):
    """GET request with retries and delay."""
    for attempt in range(retries):
        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            return resp
        except requests.exceptions.RequestException as e:
            print(f"Request failed ({attempt+1}/{retries}): {e}")
            time.sleep(delay)
    raise Exception(f"Failed to fetch {url} after {retries} retries")

def get_current_drivers():
    """Fetch current season's drivers list."""
    url = f"{BASE_URL}/2025/drivers.json?limit=1000"
    resp = safe_get(url)
    data = resp.json()
    return data['MRData']['DriverTable']['Drivers']

def get_all_races(driver_id, endpoint="results"):
    """Fetch all races for a driver (results or qualifying) with pagination."""
    results = []
    limit = 100
    offset = 0
    while True:
        url = f"{BASE_URL}/drivers/{driver_id}/{endpoint}.json?limit={limit}&offset={offset}"
        resp = safe_get(url)
        data = resp.json()
        races = data['MRData']['RaceTable']['Races']
        if not races:
            break
        results.extend(races)
        total = int(data['MRData']['total'])
        offset += limit
        if offset >= total:
            break
        time.sleep(0.2)
    return results

def calculate_driver_stats(driver, current_season="2025"):
    """Calculate comprehensive stats for a driver, including fastest lap points for past seasons only (2019+)."""
    driver_id = driver['driverId']
    print(f"Processing {driver['givenName']} {driver['familyName']}...")

    race_results = get_all_races(driver_id, "results")
    
    total_points = 0
    total_wins = 0
    total_podiums = 0
    fastest_laps_count = 0
    seasons_raced_set = set()

    for r in race_results:
        result = r['Results'][0]
        season = int(r['season'])
        points = float(result['points'])
        if 2019 <= season < int(current_season) and 'FastestLap' in result and int(result['position']) <= 10:
            points += 1
            fastest_laps_count += 1
        total_points += points

        # Wins / podiums
        pos = result['position']
        if pos == "1":
            total_wins += 1
        if pos in ["1", "2", "3"]:
            total_podiums += 1

        seasons_raced_set.add(season)

    # Qualifying results
    qualifying_results = get_all_races(driver_id, "qualifying")
    total_poles = sum(1 for r in qualifying_results if r['QualifyingResults'][0]['position'] == "1")

    return {
        "driverId": driver_id,
        "permanentNumber": driver.get("permanentNumber", ""),
        "code": driver.get("code", ""),
        "givenName": driver["givenName"],
        "familyName": driver["familyName"],
        "nationality": driver["nationality"],
        "dateOfBirth": driver["dateOfBirth"],
        "totalPoints": total_points,
        "totalPoles": total_poles,
        "totalWins": total_wins,
        "totalPodiums": total_podiums,
        "fastestLaps": fastest_laps_count,
        "seasonsRaced": len(seasons_raced_set)
    }


def save_to_json(data, filename=DRIVERS_FILE):
    """Save driver stats to JSON inside AppData."""
    with filename.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# ---------- Main ----------

def main():
    drivers = get_current_drivers()
    stats = []
    processed_races = {}

    for driver in drivers:
        driver_stats = calculate_driver_stats(driver)
        stats.append(driver_stats)

        driver_id = driver_stats['driverId']
        race_results = get_all_races(driver_id, "results")
        processed_races[driver_id] = [
            {"raceName": r["raceName"], "date": r["date"]} for r in race_results
        ]

        time.sleep(0.5)  # small delay to avoid server reset

    # Save stats
    save_to_json(stats, DRIVERS_FILE)
    print(f"✅ Driver stats saved to {DRIVERS_FILE}")

    # Save processed races 
    with PROCESSED_FILE.open("w", encoding="utf-8") as f:
        json.dump(processed_races, f, indent=4)
    print(f"✅ Processed races saved to {PROCESSED_FILE}")


if __name__ == "__main__":
    main()
