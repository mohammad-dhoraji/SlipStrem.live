# main.py

from services.results import get_last_race_results
from services.results import get_all_race_winners

def main():
    results = get_last_race_results()
    if results:
        print("=== Last Race Results (Raw Data) ===")
        print(results)   # raw dictionary with everything from the API
    else:
        print("No race results found.")
        
    Winners  = get_all_race_winners()
    if Winners:
        print("=== all Race winners (Raw Data) ===")
        print(Winners)   # raw dictionary with everything from the API
    else:
        print("No race results found.")

if __name__ == "__main__":
    main()
