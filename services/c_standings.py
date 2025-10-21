# -- services/ConstStandings.py

from utils.api_helper import fetch_api
from config import settings

def get_constructors_standings(season=settings.CURRENT_SEASON):
    
    data = fetch_api(f"{season}/constructorstandings")
    c_standings = data.get("MRData", {}).get("StandingsTable", {}).get("StandingsLists", [])
    constructors = []
    if c_standings :
        for c in c_standings[0]["ConstructorStandings"]:
            constructor = c.get("Constructor", {})
            constructors.append({
                "position": c.get("position"),
                "positionText": c.get("positionText"),
                "points": c.get("points"),
                "wins": c.get("wins"),
                # --- Constructor details --- 
                "constructorId": constructor.get("constructorId"),
                "constructorName": constructor.get("name"),
                "constructorUrl": constructor.get("url"),
                "constructorNationality": constructor.get("nationality")
            })

    return constructors


              