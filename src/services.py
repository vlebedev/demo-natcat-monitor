"""Business logic for NatCat Event Monitor.

Pure functions for exposure calculation - no I/O, no UI dependencies.
"""

import math
from src.models import Earthquake, Treaty, ExposureAlert


def calculate_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate the great-circle distance between two points using Haversine formula.

    Args:
        lat1: Latitude of first point in degrees
        lon1: Longitude of first point in degrees
        lat2: Latitude of second point in degrees
        lon2: Longitude of second point in degrees

    Returns:
        Distance in kilometers
    """
    R = 6371.0  # Earth's radius in kilometers

    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)

    a = math.sin(delta_lat / 2) ** 2 + \
        math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


def find_exposed_treaties(
    earthquake: Earthquake,
    treaties: list[Treaty]
) -> list[ExposureAlert]:
    """Find all treaties potentially affected by an earthquake.

    A treaty is affected if the earthquake epicenter falls within the treaty's
    coverage zone (defined by latitude, longitude, and radius).

    Args:
        earthquake: The seismic event to check
        treaties: List of treaties to evaluate

    Returns:
        List of ExposureAlert objects for affected treaties, sorted by distance
    """
    alerts = []

    for treaty in treaties:
        distance = calculate_distance_km(
            earthquake.latitude, earthquake.longitude,
            treaty.latitude, treaty.longitude
        )

        if distance <= treaty.radius_km:
            alert = ExposureAlert(
                earthquake=earthquake,
                treaty=treaty,
                distance_km=round(distance, 2)
            )
            alerts.append(alert)

    # Sort by distance (closest first)
    alerts.sort(key=lambda a: a.distance_km)
    return alerts


def summarize_exposure(alerts: list[ExposureAlert]) -> dict:
    """Generate summary statistics for exposure alerts.

    Args:
        alerts: List of exposure alerts to summarize

    Returns:
        Dictionary with summary statistics:
        - total_alerts: Number of alerts
        - total_exposure_usd: Sum of treaty limits
        - affected_treaties: List of unique treaty names
        - by_region: Breakdown by region
    """
    if not alerts:
        return {
            "total_alerts": 0,
            "total_exposure_usd": 0,
            "affected_treaties": [],
            "by_region": {}
        }

    seen_treaties = set()
    total_exposure = 0
    by_region: dict[str, int] = {}
    treaty_names = []

    for alert in alerts:
        treaty = alert.treaty
        if treaty.id not in seen_treaties:
            seen_treaties.add(treaty.id)
            total_exposure += treaty.limit_usd
            treaty_names.append(treaty.name)

            if treaty.region not in by_region:
                by_region[treaty.region] = 0
            by_region[treaty.region] += treaty.limit_usd

    return {
        "total_alerts": len(alerts),
        "total_exposure_usd": total_exposure,
        "affected_treaties": treaty_names,
        "by_region": by_region
    }
