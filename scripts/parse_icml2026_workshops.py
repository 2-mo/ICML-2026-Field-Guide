#!/usr/bin/env python3
"""Parse ICML 2026 workshop cards from the official virtual site."""

from __future__ import annotations

import csv
import html
import re
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "processed" / "icml2026_workshops.csv"
SOURCE_URL = "https://icml.cc/virtual/2026/events/workshop"

DATE_MAP = {
    "Jul 10": "2026-07-10",
    "Jul 11": "2026-07-11",
}


def clean(value: str) -> str:
    value = re.sub(r"<.*?>", " ", value, flags=re.S)
    return " ".join(html.unescape(value).split())


def parse_time(raw: str) -> tuple[str, str, str]:
    raw = clean(raw)
    date = ""
    for label, value in DATE_MAP.items():
        if raw.startswith(label):
            date = value
            break
    match = re.search(r",\s*([0-9:]+\s*[AP]M)\s*-\s*([0-9:]+\s*[AP]M)", raw)
    if not match:
        return date, "", ""
    return date, to_24h(match.group(1)), to_24h(match.group(2))


def to_24h(value: str) -> str:
    match = re.match(r"(\d{1,2})(?::(\d{2}))?\s*([AP]M)", value.strip(), re.I)
    if not match:
        return value
    hour = int(match.group(1))
    minute = int(match.group(2) or "00")
    ampm = match.group(3).upper()
    if ampm == "PM" and hour != 12:
        hour += 12
    if ampm == "AM" and hour == 12:
        hour = 0
    return f"{hour:02d}:{minute:02d}"


def field(pattern: str, text: str) -> str:
    match = re.search(pattern, text, re.S)
    return clean(match.group(1)) if match else ""


def parse(html_text: str) -> list[dict[str, str]]:
    rows = []
    for part in html_text.split('<div class="event-card touchup-date"')[1:]:
        card = '<div class="event-card touchup-date"' + part
        detail_path = field(r'<a href="(/virtual/2026/workshop/\d+)" class="view-details-link">', card)
        if not detail_path:
            continue
        workshop_id = field(r'data-event-id="(\d+)"', card)
        title = field(r'<h3 class="event-title">\s*<a href="/virtual/2026/workshop/\d+">(.*?)</a>', card)
        organizers = field(r'<div class="event-speakers">\s*(.*?)\s*</div>', card)
        raw_time = field(r'<span class="touchup-time">\s*(.*?)\s*</span>', card)
        room = field(r'<i class="fas fa-map-marker-alt"></i>\s*<span>(.*?)</span>', card)
        abstract = field(r'<div class="abstract-text" id="abstract-\d+">\s*(.*?)\s*</div>', card)
        date, start, end = parse_time(raw_time)
        rows.append(
            {
                "workshop_id": workshop_id,
                "date": date,
                "start_time": start,
                "end_time": end,
                "time_label": f"{start}-{end}" if start and end else raw_time,
                "title": title,
                "room": room,
                "organizers": organizers,
                "url": f"https://icml.cc{detail_path}",
                "abstract": abstract,
                "source_url": SOURCE_URL,
            }
        )
    return rows


def main() -> None:
    with urllib.request.urlopen(SOURCE_URL, timeout=90) as response:
        html_text = response.read().decode("utf-8", "replace")
    rows = parse(html_text)
    if len(rows) != 44:
        raise RuntimeError(f"Expected 44 workshops, parsed {len(rows)}")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} workshops to {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
