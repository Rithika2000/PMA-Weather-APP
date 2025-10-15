from fastapi import APIRouter, HTTPException
import requests, urllib.parse
from ..config import settings

router = APIRouter(prefix="/integrations", tags=["integrations"])

@router.get("/youtube")
def youtube_search(q: str, max_results: int = 6):
    if not settings.YT_API_KEY:
        raise HTTPException(400, "YouTube API key missing in .env")
    r = requests.get("https://www.googleapis.com/youtube/v3/search", params={
        "part":"snippet","q":q,"type":"video","maxResults":max_results,
        "key":settings.YT_API_KEY,"safeSearch":"moderate"
    }, timeout=20)
    r.raise_for_status()
    return r.json()

@router.get("/google-search")
def google_search(q: str, num: int = 5):
    if not settings.CSE_API_KEY or not settings.CSE_CX:
        raise HTTPException(400, "Google CSE API key/CX missing in .env")
    r = requests.get("https://www.googleapis.com/customsearch/v1", params={
        "key": settings.CSE_API_KEY, "cx": settings.CSE_CX, "q": q, "num": num, "safe":"active"
    }, timeout=20)
    r.raise_for_status()
    return r.json()

@router.get("/map-embed")
def map_embed(lat: float | None = None, lon: float | None = None, q: str | None = None):
    if lat is not None and lon is not None:
        return {"embed": f"https://maps.google.com/maps?q={lat},{lon}&z=12&output=embed"}
    if q:
        return {"embed": f"https://maps.google.com/maps?q={urllib.parse.quote(q)}&z=12&output=embed"}
    raise HTTPException(400, "Provide lat/lon or q")
