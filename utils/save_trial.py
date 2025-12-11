import json
import os

def save_trial_end(user_id: str, trial_end: str):
    folder = "registro"
    if not os.path.exists(folder):
        os.makedirs(folder)

    path = os.path.join(folder, f"{user_id}_trial.json")

    with open(path, "w") as f:
        json.dump({"trial_end": trial_end}, f, indent=4)