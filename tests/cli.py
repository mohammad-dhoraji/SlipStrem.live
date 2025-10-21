# test_cli.py
from services.d_standings import get_driver_standings
from services.c_standings import get_constructors_standings
from services.Schedule import get_race_schedule
from services.results import get_last_race_results

def test():
    print("=== DRIVER STANDINGS ===")
    drivers = get_driver_standings()
    for d in drivers:
        print(f"{d['position']} | {d['driverName']} | #{d['permanentNumber']} | {d['points']} pts | {d['constructorName']}")

    print("\n=== CONSTRUCTOR STANDINGS ===")
    constructors = get_constructors_standings()
    for c in constructors:
        print(f"{c['position']} | {c['constructorName']} | {c['points']} pts | Wins: {c['wins']}")

    print("\n=== RACE SCHEDULE ===")
    races = get_race_schedule()
    for r in races:
        print(f"Round {r['round']} | {r['raceName']} | {r['date']} | {r['circuitName']} | {r['country']}")

    print("\n=== ALL RACE RESULTS ===")
    results = get_last_race_results()
    for r in results:
        print(f"Round {r['round']} | {r['raceName']} | Pos {r['position']} | {r['driverName']} | #{r['driverPermanentNumber']} | {r['constructorName']} | {r['points']} pts | Time: {r.get('raceTimeFormatted')} | Fastest Lap: {r.get('fastestLapTime')}")

if __name__ == "__main__":
    test()
