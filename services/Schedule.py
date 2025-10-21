# --- services/schedule.py

from utils.api_helper import fetch_api
from config import settings

def get_race_schedule(season = settings.CURRENT_SEASON):
    data = fetch_api(f"{season}/races")
    races = data.get("MRData", {}).get("RaceTable", {}).get("Races", [])
    schedule = []
    for r in races:
        circuit = r.get("Circuit", {})
        location = circuit.get("Location", {})
        schedule.append({
            "round": r.get("round"),
            "raceName": r.get("raceName"),
            "raceUrl": r.get("url"),
            "date": r.get("date"),
            "circuitName": circuit.get("circuitName"),
            "time": r.get("time", "00:00:00"),
            "circuitId": circuit.get("circuitId"),
            "circuitUrl": circuit.get("url"),
            "lat": location.get("lat"),
            "long": location.get("long"),
            "locality": location.get("locality"),
            "country": location.get("country")
        })

    return schedule