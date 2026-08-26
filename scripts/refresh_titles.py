#!/usr/bin/env python3
"""Refresh doom_debates_titles.json from the Doom Debates YouTube uploads playlist.

Fetches newest uploads (playlistItems API), merges {id, title, date} entries into
the corpus (dedupes by id, updates changed titles), and prints the added/changed
entries as JSON so the caller can see exactly what's new.

Exit code 0 always on success (even with zero changes); nonzero on hard failure.
"""

import json
import os
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

CORPUS = Path.home() / "Desktop/ClaudeCode/doom_debates_titles.json"
ENV_FILE = Path.home() / "Desktop/ClaudeCode/youtube-dashboard/.env.local"
UPLOADS_PLAYLIST = "UUote8RH_wwSLza2Qb0GAQJw"  # Doom Debates channel UCote8RH_wwSLza2Qb0GAQJw
MAX_PAGES = 4


def api_key():
    key = os.environ.get("YOUTUBE_API_KEY")
    if key:
        return key
    for line in ENV_FILE.read_text().splitlines():
        line = line.strip()
        if line.startswith("YOUTUBE_API_KEY="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise SystemExit(f"YOUTUBE_API_KEY not found in env or {ENV_FILE}")


def fetch_uploads(key, known_ids):
    """Newest-first uploads; stop paginating once a page is entirely known ids."""
    items, page_token = [], None
    for _ in range(MAX_PAGES):
        params = {
            "part": "snippet",
            "playlistId": UPLOADS_PLAYLIST,
            "maxResults": "50",
            "key": key,
        }
        if page_token:
            params["pageToken"] = page_token
        url = "https://www.googleapis.com/youtube/v3/playlistItems?" + urllib.parse.urlencode(params)
        with urllib.request.urlopen(url, timeout=30) as resp:
            data = json.load(resp)
        page = [
            {
                "id": it["snippet"]["resourceId"]["videoId"],
                "title": it["snippet"]["title"],
                "date": it["snippet"]["publishedAt"][:10],
            }
            for it in data.get("items", [])
        ]
        items.extend(page)
        if page and all(p["id"] in known_ids for p in page):
            break
        page_token = data.get("nextPageToken")
        if not page_token:
            break
    return items


def parse_duration(iso):
    """ISO8601 PT#H#M#S -> seconds."""
    m = re.fullmatch(r"P(?:(\d+)D)?T?(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", iso or "")
    if not m:
        return 0
    d, h, mi, s = (int(g or 0) for g in m.groups())
    return d * 86400 + h * 3600 + mi * 60 + s


def classify(seconds):
    if seconds <= 183:
        return "short"
    if seconds < 900:
        return "clip"
    return "episode"


def fetch_durations(key, ids):
    out = {}
    for i in range(0, len(ids), 50):
        params = {"part": "contentDetails", "id": ",".join(ids[i : i + 50]), "key": key}
        url = "https://www.googleapis.com/youtube/v3/videos?" + urllib.parse.urlencode(params)
        with urllib.request.urlopen(url, timeout=30) as resp:
            data = json.load(resp)
        for it in data.get("items", []):
            out[it["id"]] = parse_duration(it["contentDetails"]["duration"])
    return out


def main():
    key = api_key()
    corpus = json.loads(CORPUS.read_text()) if CORPUS.exists() else []
    by_id = {e["id"]: e for e in corpus}
    fetched = fetch_uploads(key, set(by_id))

    changes = []
    for entry in fetched:
        old = by_id.get(entry["id"])
        if old is None:
            by_id[entry["id"]] = entry
            changes.append({**entry, "change": "added"})
        elif old["title"] != entry["title"]:
            changes.append({**entry, "change": "retitled", "old_title": old["title"]})
            old["title"] = entry["title"]

    # Backfill duration/type for any entry missing it (uploads playlist mixes
    # Shorts and clips in with full episodes; skills filter on type).
    missing = [vid for vid, e in by_id.items() if "duration_sec" not in e]
    dirty = bool(changes)
    if missing:
        durations = fetch_durations(key, missing)
        for vid, secs in durations.items():
            by_id[vid]["duration_sec"] = secs
            by_id[vid]["type"] = classify(secs)
        dirty = True
    for ch in changes:
        full = by_id[ch["id"]]
        ch["duration_sec"] = full.get("duration_sec")
        ch["type"] = full.get("type")

    if dirty:
        merged = sorted(by_id.values(), key=lambda e: e["date"], reverse=True)
        CORPUS.write_text(json.dumps(merged, indent=2, ensure_ascii=False) + "\n")

    summary = {
        "changes": changes,
        "corpus_size": len(by_id),
        "episodes": sum(1 for e in by_id.values() if e.get("type") == "episode"),
    }
    json.dump(summary, sys.stdout, indent=2, ensure_ascii=False)
    print()


if __name__ == "__main__":
    main()
