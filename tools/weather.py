from __future__ import annotations

import functools
import logging
from datetime import date
from typing import Tuple, Dict, Any
from mcp_server import mcp

import requests

__all__ = [
    "get_today_weather",
    "get_current_temperature",
    "will_it_rain",
]

# ---------------------------------------------------------------------------
# Configuration & helpers
# ---------------------------------------------------------------------------
USER_AGENT = "WeatherClient/1.0 (+https://openai.com)"
HEADERS = {"User-Agent": USER_AGENT}
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"

logger = logging.getLogger(__name__)

class LocationNotFoundError(ValueError):
    """Raised when a place name cannot be geocoded."""

class WeatherAPIError(RuntimeError):
    """Raised when the weather API returns an unexpected response."""

@mcp.tool()
def _geocode(location: str) -> Tuple[float, float]:
    """Return *(latitude, longitude)* for a place *name* using Nominatim.

    The result is cached (LRU) to avoid repeated HTTP requests for the same
    location.
    """
    params = {"q": location, "format": "json", "limit": 1}
    logger.debug("Geocoding location %%s", location)
    r = requests.get(NOMINATIM_URL, params=params, headers=HEADERS, timeout=10)
    r.raise_for_status()
    data = r.json()
    if not data:
        raise LocationNotFoundError(f"Location '{location}' not found")
    lat, lon = float(data[0]["lat"]), float(data[0]["lon"])
    logger.debug("Geocode result: %%s → (%%.4f, %%.4f)", location, lat, lon)
    return lat, lon

# ---------------------------------------------------------------------------
# Public functions
# ---------------------------------------------------------------------------

@mcp.tool() 
def get_today_weather(location: str) -> Dict[str, Any]:
    """Return today’s weather *summary* for **location**.

    Keys in the returned dict:
        * location – echo of the input string
        * latitude, longitude – float coordinates
        * date – ISO‑8601 string (YYYY‑MM‑DD)
        * current_temperature – °C
        * current_wind_speed – km/h
        * temperature_max – °C (forecast max today)
        * temperature_min – °C (forecast min today)
        * precipitation_sum – mm (total rain/snow forecast for today)
    """
    lat, lon = _geocode(location)
    today = date.today().isoformat()
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
        "current_weather": "true",
        "timezone": "auto",
        "start_date": today,
        "end_date": today,
    }
    logger.debug("Requesting weather for %%s on %%s", location, today)
    r = requests.get(OPEN_METEO_URL, params=params, headers=HEADERS, timeout=10)
    r.raise_for_status()
    data = r.json()
    try:
        return {
            "location": location,
            "latitude": lat,
            "longitude": lon,
            "date": today,
            "current_temperature": round(data["current_weather"]["temperature"], 1),
            "current_wind_speed": data["current_weather"]["windspeed"],
            "temperature_max": data["daily"]["temperature_2m_max"][0],
            "temperature_min": data["daily"]["temperature_2m_min"][0],
            "precipitation_sum": data["daily"]["precipitation_sum"][0],
        }
    except (KeyError, IndexError, TypeError) as exc:
        raise WeatherAPIError("Unexpected response structure") from exc

@mcp.tool() 
def get_current_temperature(location: str) -> float:
    """Return the **current air temperature** in Celsius for *location*."""
    weather = get_today_weather(location)
    return weather["current_temperature"]

@mcp.tool()
def will_it_rain(location: str, threshold_mm: float = 0.1) -> bool:
    """Return **True** if forecast precipitation today ≥ *threshold_mm* (mm).

    The default *threshold_mm* of **0.1 mm** treats even light drizzle as
    “rain”. Increase it (e.g. *1.0*) to ignore negligible amounts.
    """
    weather = get_today_weather(location)
    return weather["precipitation_sum"] >= threshold_mm



