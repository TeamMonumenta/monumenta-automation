import os
import json
from pathlib import Path
import copy

bad_advancements = [
    "monumenta:pois/r1/amped/antipodean_tower",
    "monumenta:pois/r1/amped/cindered_cave",
    "monumenta:pois/r1/amped/earthquake_shrine",
    "monumenta:pois/r1/amped/ezariahs_tomb",
    "monumenta:pois/r1/amped/festive_fortress",
    "monumenta:pois/r1/amped/forsworn_cave",
    "monumenta:pois/r1/amped/ice_shrine",
    "monumenta:pois/r1/amped/mercenary_mine",
    "monumenta:pois/r1/amped/purrfect_winter_retreat",
    "monumenta:pois/r1/amped/root",
    "monumenta:pois/r1/amped/tempest_shrine",
    "monumenta:pois/r1/amped/twisted_cave",
    "monumenta:pois/r1/amped/whirlpool_shrine",
]

def load_advancement_data(current_path: str, old_path: str, output_path: str):
    """Fixes advancement data that was nuked in a weekly update"""
    for filename in os.listdir(current_path):
        if not filename.endswith("json"):
            continue
        file_path = os.path.join(current_path, filename)
        old_file_path = os.path.join(old_path, filename)
        output_data = {}
        # Create output directory
        if not os.path.exists(output_path):
            Path(output_path).mkdir(parents=True, exist_ok=True)
        # usb: set to false to only write changed files, otherwise true to write all files
        with open(file_path, "r", encoding="utf-8") as current_file:
            currentAdvancementData = json.load(current_file)
            output_data = copy.deepcopy(currentAdvancementData)
            if os.path.exists(old_file_path):
                with open(old_file_path, "r", encoding="utf-8") as old_file:
                    oldAdvancementData = json.load(old_file)
                    for key in bad_advancements:
                        if key in oldAdvancementData and key not in currentAdvancementData:
                            print(f"{filename}: {key} - {oldAdvancementData[key]}")
                            output_data[key] = oldAdvancementData[key]
        if len(output_data) > 0:
            output_file_path = os.path.join(output_path, filename)
            with open(output_file_path, "w+", encoding="utf-8") as output_file:
                json.dump(output_data, output_file, separators=(",", ":"))


if __name__ == "__main__":
    current_path = "/home/epic/usb/advancements_test_data_2024_10_14/play_server_snapshot_2024_10_14/advancements/"
    old_path = "/home/epic/usb/advancements_test_data_2024_10_14/play_server_update_2024_10_10/advancements/"
    output_path = "/home/epic/usb/maow/"
    load_advancement_data(current_path, old_path, output_path)
