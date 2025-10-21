# -- services/DriversStandings.py

from utils.api_helper import fetch_api
from config import settings

def get_driver_standings(season=settings.CURRENT_SEASON):
    
    data = fetch_api(f"{season}/driverstandings")
    d_standings = data.get("MRData", {}).get("StandingsTable", {}).get("StandingsLists", [])
    drivers = []
    if d_standings:
        for d in d_standings[0]["DriverStandings"]:
            driver = d["Driver"]
            constructor = d["Constructors"][0] if d.get("Constructors") else {}
            drivers.append({
                "position": d.get("position"),
                "positionText": d.get("positionText"),
                "points": d.get("points"),
                "wins": d.get("wins"),
                # --- Driver details ---
                "driverId": driver.get("driverId"),
                "permanentNumber": driver.get("permanentNumber"),
                "code": driver.get("code"),
                "driverUrl": driver.get("url"),
                "givenName": driver.get("givenName"),
                "familyName": driver.get("familyName"),
                "dateOfBirth": driver.get("dateOfBirth"),
                "nationality": driver.get("nationality"),
                "driverName": f"{driver.get('givenName')} {driver.get('familyName')}",
                # --- Constructor details ---
                "constructorId": constructor.get("constructorId"),
                "constructorName": constructor.get("name"),
                "constructorUrl": constructor.get("url"),
                "constructorNationality": constructor.get("nationality")
            })
    return drivers