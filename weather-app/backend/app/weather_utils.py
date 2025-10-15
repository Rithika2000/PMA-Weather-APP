import requests
from typing import Optional

# ---------- Geocoding ----------
def geocode(query: str) -> Optional[dict]:
    """
    Returns {'name': str, 'lat': float, 'lon': float} or None.
    Accepts GPS input like 'lat,lon' directly.
    """
    q = (query or "").strip()
    if not q:
        return None

    # Allow raw GPS coordinates: "lat,lon"
    if "," in q:
        parts = [p.strip() for p in q.split(",")]
        if len(parts) == 2:
            try:
                lat = float(parts[0]); lon = float(parts[1])
                return {"name": f"GPS({lat:.4f},{lon:.4f})", "lat": lat, "lon": lon}
            except ValueError:
                pass  # fall through to API

    # Open-Meteo geocoding (free)
    url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {"name": q, "count": 1, "language": "en", "format": "json"}
    r = requests.get(url, params=params, timeout=15)
    r.raise_for_status()
    data = r.json()
    if not data.get("results"):
        return None
    top = data["results"][0]
    name = f'{top.get("name")}, {top.get("country_code")}'
    return {"name": name, "lat": top["latitude"], "lon": top["longitude"]}


# ---------- Weather ----------
def get_current_weather(lat: float, lon: float) -> dict:
    url = "https://api.open-meteo.com/v1/forecast"
    params = {"latitude": lat, "longitude": lon, "current_weather": True}
    r = requests.get(url, params=params, timeout=15)
    r.raise_for_status()
    return r.json()

def get_daily_forecast(lat: float, lon: float, days: int = 5) -> dict:
    """
    Returns a daily forecast block. Open-Meteo returns many days; the client can truncate to 5.
    """
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": "weathercode,temperature_2m_max,temperature_2m_min,precipitation_sum,windspeed_10m_max",
        "timezone": "auto",
    }
    r = requests.get(url, params=params, timeout=15)
    r.raise_for_status()
    return r.json()


# ---------- IP Geolocation (approx current location) ----------
def ip_geolocate() -> Optional[dict]:
    """
    Approximate location by public IP (free). Works well when running locally.
    """
    # ipapi.co is free for simple lookups (no key)
    r = requests.get("https://ipapi.co/json/", timeout=10)
    r.raise_for_status()
    data = r.json()
    lat = data.get("latitude"); lon = data.get("longitude")
    city = data.get("city"); country = data.get("country")
    if lat is None or lon is None:
        return None
    name = f"{city}, {country}" if city and country else "Approximate Location"
    return {"name": name, "lat": float(lat), "lon": float(lon)}
