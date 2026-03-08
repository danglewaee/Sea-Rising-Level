import json
from pathlib import Path


DEFAULT_CITY_REGISTRY = {
    "honolulu": {
        "station": "1612340",
        "display_name": "Honolulu, HI",
        "dem_path": "data/honolulu_dem.tif",
        "admin_boundary": None,
        "timezone": "Pacific/Honolulu",
    },
    "newyork": {
        "station": "8518750",
        "display_name": "The Battery, New York",
        "dem_path": None,
        "admin_boundary": None,
        "timezone": "America/New_York",
    },
    "miami": {
        "station": "8723214",
        "display_name": "Virginia Key, Miami",
        "dem_path": None,
        "admin_boundary": None,
        "timezone": "America/New_York",
    },
    "sanfrancisco": {
        "station": "9414290",
        "display_name": "San Francisco",
        "dem_path": None,
        "admin_boundary": None,
        "timezone": "America/Los_Angeles",
    },
}


def load_city_registry(path: str = "Backend/sea_level_risk/city_registry.json") -> dict:
    p = Path(path)
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8-sig"))

    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(DEFAULT_CITY_REGISTRY, indent=2), encoding="utf-8")
    return DEFAULT_CITY_REGISTRY
