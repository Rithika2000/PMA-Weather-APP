from fastapi import APIRouter, HTTPException
from datetime import date, timedelta
import requests

from ..schemas import RangeRequest, GeoOut, WeatherPayload
from ..weather_utils import geocode as base_geocode, get_current_weather, get_daily_forecast, ip_geolocate

router = APIRouter(prefix="/weather", tags=["weather"])

# expose tech1 endpoints too (so frontend can point here)
@router.get("/geocode", response_model=GeoOut)
def geocode(q: str):
    g = base_geocode(q)
    if not g:
        raise HTTPException(404, "Location not found")
    return g

@router.get("/current", response_model=WeatherPayload)
def current(lat: float, lon: float):
    return {"payload": get_current_weather(lat, lon)}

@router.get("/forecast", response_model=WeatherPayload)
def forecast(lat: float, lon: float, days: int = 5):
    return {"payload": get_daily_forecast(lat, lon, days=days)}

@router.get("/ip", response_model=GeoOut)
def geo_ip():
    g = ip_geolocate()
    if not g:
        raise HTTPException(404, "IP geolocation failed")
    return g

# --- HYBRID range: past -> archive, today/future -> forecast, crossing -> split & merge ---
@router.post("/range", response_model=WeatherPayload)
def range_weather(body: RangeRequest):
    g = base_geocode(body.input_location)
    if not g:
        raise HTTPException(404, "Location not found")

    def _archive(lat, lon, s, e):
        url = "https://archive-api.open-meteo.com/v1/archive"
        params = {
            "latitude": lat, "longitude": lon,
            "start_date": s.isoformat(), "end_date": e.isoformat(),
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
            "timezone": "auto",
        }
        r = requests.get(url, params=params, timeout=20)
        r.raise_for_status()
        return r.json()

    def _forecast(lat, lon, s, e):
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": lat, "longitude": lon,
            "start_date": s.isoformat(), "end_date": e.isoformat(),
            "daily": "weathercode,temperature_2m_max,temperature_2m_min,precipitation_sum,windspeed_10m_max",
            "timezone": "auto",
        }
        r = requests.get(url, params=params, timeout=20)
        r.raise_for_status()
        return r.json()

    def _merge_daily(d1: dict, d2: dict) -> dict:
        out, keys = {}, set()
        if d1: keys |= set(d1.keys())
        if d2: keys |= set(d2.keys())
        for k in keys:
            a = d1.get(k, []) if d1 else []
            b = d2.get(k, []) if d2 else []
            out[k] = a + b if k != "time" else a + [t for t in b if t not in a]
        return out

    s, e = body.start_date, body.end_date
    today_utc = date.today()

    if e < s:
        raise HTTPException(400, "end_date must be on/after start_date")

    if e < today_utc:
        payload = _archive(g["lat"], g["lon"], s, e)
    elif s >= today_utc:
        payload = _forecast(g["lat"], g["lon"], s, e)
    else:
        past_end = today_utc - timedelta(days=1)
        past = _archive(g["lat"], g["lon"], s, past_end)
        future = _forecast(g["lat"], g["lon"], today_utc, e)
        merged = _merge_daily(past.get("daily", {}), future.get("daily", {}))
        payload = {"daily": merged}

    return {"payload": {"resolved": g, **payload}}
