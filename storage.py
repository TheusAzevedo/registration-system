import json

FILE = "people.json"


def load():
    try:
        with open(FILE, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def save(people):
    with open(FILE, "w", encoding="utf-8") as f:
        json.dump(people, f, indent=4, ensure_ascii=False)