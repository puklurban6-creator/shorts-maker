"""Reads ONLY public metadata (titles, views, tags) of popular Shorts.
No video, audio or script is downloaded - it is used just for pattern analysis."""
from datetime import datetime, timedelta, timezone

import requests

import config

API = "https://www.googleapis.com/youtube/v3"


def fetch(genre, max_results=25, days=14):
    key = config.get("YOUTUBE_API_KEY")
    if not key:
        print("  (no YouTube key - using general knowledge of trends)")
        return []
    since = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ")
    r = requests.get(f"{API}/search", params={
        "key": key, "part": "id", "type": "video", "videoDuration": "short",
        "order": "viewCount", "q": f"{genre} story #shorts", "publishedAfter": since,
        "maxResults": max_results, "regionCode": config.get("REGION"),
        "relevanceLanguage": "en",
    }, timeout=30)
    r.raise_for_status()
    ids = [i["id"]["videoId"] for i in r.json().get("items", [])]
    if not ids:
        return []
    r = requests.get(f"{API}/videos", params={
        "key": key, "part": "snippet,statistics", "id": ",".join(ids)}, timeout=30)
    r.raise_for_status()
    out = []
    for v in r.json().get("items", []):
        out.append({
            "title": v["snippet"]["title"],
            "tags": v["snippet"].get("tags", [])[:8],
            "views": int(v["statistics"].get("viewCount", 0)),
        })
    return sorted(out, key=lambda x: x["views"], reverse=True)
