from utils.api_helper import fetch_api
from config import settings

def get_last_race_results():
    """
    Fetches the results of the last race in the current season.
    Returns a dictionary with race details and results.
    """
    data = fetch_api("current/last/results")
    races = data.get("MRData", {}).get("RaceTable", {}).get("Races", [])
    if not races:
        return None

    last_race = races[0]
    return {
        "raceName": last_race.get("raceName"),
        "circuit": last_race.get("Circuit", {}).get("circuitName"),
        "circuitId": last_race.get("Circuit", {}).get("circuitId", ""),
        "country": last_race.get("Circuit", {}).get("Location", {}).get("country"),
        "date": last_race.get("date"),
        "Results": last_race.get("Results", [])
    }


def get_all_race_winners(season=settings.CURRENT_SEASON):
    data = fetch_api(f"{season}/results/1?limit=1000")
    races = data.get("MRData", {}).get("RaceTable", {}).get("Races", [])
    
    winners = {}
    for race in races:
        result = race["Results"][0]  
        driver = result["Driver"]
        constructor = result["Constructor"]

        winners[race["round"]] = {
            "driverName": f"{driver.get('givenName')} {driver.get('familyName')}",
            "constructor": constructor.get("name"),
            "driverNationality": driver.get("nationality"),
            "driverCode": driver.get("code"),
        }

    return winners