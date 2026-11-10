#!/usr/bin/env python3
"""Fetch public Eventernote events and atomically update snapshot only on success."""
from pathlib import Path
from datetime import date
import json, sys
from server import fetch_events

path = Path(__file__).with_name('event_snapshot.json')
try:
    events = fetch_events()
    if not isinstance(events, list) or not events:
        raise ValueError('No events fetched; refusing to overwrite snapshot')
    cleaned = []
    seen = set()
    for e in events:
        if not isinstance(e, dict) or not isinstance(e.get('date'), str) or not isinstance(e.get('title'), str):
            continue
        date.fromisoformat(e['date'])
        key = e.get('url') or (e['date'], e['title'])
        if key in seen: continue
        seen.add(key)
        cleaned.append({k: str(e.get(k, '')) for k in ('date','title','venue','time','url')})
    if not cleaned:
        raise ValueError('No valid events; refusing to overwrite snapshot')
    # The website applies its own 3-month past / 5-month future filter.
    temp = path.with_suffix('.json.tmp')
    temp.write_text(json.dumps(cleaned, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    temp.replace(path)
    print(f'Saved {len(cleaned)} events')
except Exception as exc:
    print(f'Eventernote sync failed: {exc}', file=sys.stderr)
    sys.exit(1)
