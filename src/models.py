"""Pydantic models for NatCat Event Monitor.

Defines the core data structures used across all layers:
- Earthquake: Seismic event data from USGS
- Treaty: Reinsurance treaty with geographic zone
- ExposureAlert: Alert when earthquake affects a treaty zone
"""

from datetime import datetime
from pydantic import BaseModel


class Earthquake(BaseModel):
    """Seismic event data from USGS API."""
    id: str
    magnitude: float
    latitude: float
    longitude: float
    place: str
    time: datetime
    depth_km: float


class Treaty(BaseModel):
    """Reinsurance treaty with geographic coverage zone."""
    id: str
    name: str
    peril: str
    region: str
    latitude: float
    longitude: float
    radius_km: float
    limit_usd: int


class ExposureAlert(BaseModel):
    """Alert indicating an earthquake affects a treaty zone."""
    earthquake: Earthquake
    treaty: Treaty
    distance_km: float
