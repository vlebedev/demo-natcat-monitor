"""Data layer for NatCat Event Monitor.

Handles external I/O: USGS API calls and treaty data loading.
"""

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import httpx

from .models import Earthquake, Treaty


USGS_API_BASE = "https://earthquake.usgs.gov/fdsnws/event/1/query"
DATA_DIR = Path(__file__).parent.parent / "data"


def fetch_earthquakes(min_magnitude: float = 4.0, days: int = 7) -> list[Earthquake]:
    """Fetch earthquake events from USGS API.

    Args:
        min_magnitude: Minimum magnitude to filter events (default 4.0).
        days: Number of days to look back (default 7).

    Returns:
        List of Earthquake objects matching the criteria.

    Raises:
        httpx.HTTPError: If the API request fails.
    """
    end_time = datetime.now(timezone.utc)
    start_time = end_time - timedelta(days=days)

    params = {
        "format": "geojson",
        "starttime": start_time.strftime("%Y-%m-%d"),
        "endtime": end_time.strftime("%Y-%m-%d"),
        "minmagnitude": min_magnitude,
        "orderby": "magnitude",
    }

    response = httpx.get(USGS_API_BASE, params=params, timeout=10.0)
    response.raise_for_status()

    data = response.json()
    earthquakes = []

    for feature in data.get("features", []):
        props = feature.get("properties", {})
        coords = feature.get("geometry", {}).get("coordinates", [0, 0, 0])

        # USGS returns time in milliseconds since epoch
        event_time = datetime.fromtimestamp(
            props.get("time", 0) / 1000, tz=timezone.utc
        )

        earthquake = Earthquake(
            id=feature.get("id", ""),
            magnitude=props.get("mag", 0.0),
            latitude=coords[1],
            longitude=coords[0],
            place=props.get("place", "Unknown"),
            time=event_time,
            depth_km=coords[2],
        )
        earthquakes.append(earthquake)

    return earthquakes


def load_treaties() -> list[Treaty]:
    """Load mock treaty data from JSON file.

    Returns:
        List of Treaty objects.

    Raises:
        FileNotFoundError: If treaties.json is not found.
        json.JSONDecodeError: If the file contains invalid JSON.
    """
    treaties_path = DATA_DIR / "treaties.json"

    with open(treaties_path, "r") as f:
        data = json.load(f)

    return [Treaty(**treaty) for treaty in data]
