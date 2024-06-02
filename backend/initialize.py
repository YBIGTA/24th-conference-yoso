import pathlib
import json
import requests


root_dir = pathlib.Path(__file__).parent.resolve()
with open(root_dir / "merged.json", "r") as f:
    data = json.load(f)

    for idx, elem in enumerate(data):
        res = requests.post(
            "http://localhost/api/v1/paper/create",
            json=elem
        )

        print(idx, res)
