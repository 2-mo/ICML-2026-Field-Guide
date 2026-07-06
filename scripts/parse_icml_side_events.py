#!/usr/bin/env python3
"""Parse public ICML-week side-event hub into a structured CSV.

Primary source:
https://luma.com/7iiqamt2

The Luma page embeds a schema.org Event JSON-LD object whose description
contains the curated side-event schedule. This script extracts that schedule.
"""

from __future__ import annotations

import csv
import html
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "side_events" / "luma_cafe_icml.html"
OUT = ROOT / "data" / "processed" / "icml2026_side_events.csv"
SUMMARY = ROOT / "data" / "processed" / "icml2026_side_events_summary.csv"
SOURCE_URL = "https://luma.com/7iiqamt2"


@dataclass
class SideEvent:
    date_label: str
    date_2026: str
    start_time: str
    end_time: str
    timezone_note: str
    title: str
    organizer_guess: str
    event_kind: str
    rsvp_url: str
    platform: str
    detail_name: str
    detail_start: str
    detail_end: str
    location_name: str
    address_region: str
    address_country: str
    latitude: str
    longitude: str
    organizer_verified: str
    ticket_availability: str
    source_url: str
    source_updated: str
    confidence: str
    notes: str


MONTHS = {
    "Jun": "06",
    "Jul": "07",
}


def extract_json_ld(text: str) -> dict:
    events = extract_event_json_ld_blocks(text)
    for data in events:
        if "ICML" in data.get("name", ""):
            return data
    if events:
        return events[0]
    raise RuntimeError("Could not find JSON-LD event block")


def extract_event_json_ld_blocks(text: str) -> list[dict]:
    events = []
    for match in re.finditer(
        r'<script[^>]+type="application/ld\+json"[^>]*>(.*?)</script>',
        text,
        flags=re.S,
    ):
        raw = html.unescape(match.group(1))
        data = json.loads(raw)
        if data.get("@type") == "Event":
            events.append(data)
    return events


def parse_date(label: str) -> str:
    match = re.search(r"\b(Jun|Jul)\s+(\d{1,2})\b", label)
    if not match:
        return ""
    month, day = match.groups()
    return f"2026-{MONTHS[month]}-{int(day):02d}"


def normalize_url(url: str) -> str:
    url = url.strip().rstrip(".,")
    if url.startswith("http"):
        return url
    if url.startswith("//"):
        return "https:" + url
    return url


def platform(url: str) -> str:
    if "luma.com" in url:
        return "Luma"
    if "docs.google.com/forms" in url:
        return "Google Forms"
    if "gdg.community.dev" in url:
        return "GDG"
    return "Other"


def local_detail_path(url: str) -> Path | None:
    slug = ""
    if "luma.com/" in url:
        slug = url.split("luma.com/", 1)[1].split("?", 1)[0].strip("/")
    elif "gdg.community.dev" in url:
        slug = "gdg_deepmind"
    if not slug:
        return None
    candidates = [
        ROOT / "data" / "raw" / "side_events" / f"{slug}.html",
        ROOT / "data" / "raw" / "side_events" / f"{slug.replace('.', '_')}.html",
    ]
    aliases = {
        "azfldlz7": "openai_codex_meetup.html",
        "vessl-9xxv": "vessl_dinner.html",
        "xej0o2jr": "huggingface_seoul.html",
        "gdg_deepmind": "gdg_deepmind.html",
    }
    if slug in aliases:
        candidates.insert(0, ROOT / "data" / "raw" / "side_events" / aliases[slug])
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def detail_from_local_page(url: str) -> dict[str, str]:
    path = local_detail_path(url)
    if not path:
        return {}
    text = path.read_text(encoding="utf-8", errors="replace")
    try:
        data = extract_json_ld(text)
    except Exception:
        return {}
    location = data.get("location") or {}
    address = location.get("address") or {}
    organizers = data.get("organizer") or []
    if isinstance(organizers, dict):
        organizers = [organizers]
    offers = data.get("offers") or []
    if isinstance(offers, dict):
        offers = [offers]
    return {
        "detail_name": data.get("name") or "",
        "detail_start": data.get("startDate") or "",
        "detail_end": data.get("endDate") or "",
        "location_name": location.get("name") or "",
        "address_region": address.get("addressRegion") or "",
        "address_country": address.get("addressCountry") or "",
        "latitude": str(location.get("latitude") or ""),
        "longitude": str(location.get("longitude") or ""),
        "organizer_verified": " | ".join(org.get("name", "") for org in organizers if org.get("name")),
        "ticket_availability": " | ".join(offer.get("availability", "") for offer in offers if offer.get("availability")),
    }


def classify(title: str) -> str:
    t = title.lower()
    if any(word in t for word in ["dinner", "after-dinner"]):
        return "Dinner"
    if any(word in t for word in ["happy hour", "drinks", "cocktail", "jazz night", "night", "party", "afterparty", "after hours"]):
        return "Evening social"
    if any(word in t for word in ["cafe", "coffee", "cowork"]):
        return "Cafe / coworking"
    if any(word in t for word in ["meetup", "social", "networking mixer", "networking lunch"]):
        return "Meetup / networking"
    if any(word in t for word in ["summit", "workshop", "build day", "ralphthon", "probml"]):
        return "Workshop / summit"
    return "Side event"


def guess_organizer(title: str) -> str:
    known = [
        "OpenAI",
        "Google DeepMind",
        "Hugging Face",
        "AWS",
        "Jane Street",
        "Optiver",
        "Gensyn",
        "VESSL AI",
        "FriendliAI",
        "Furiosa",
        "Goodfire",
        "Turing",
        "Upstage",
        "Liner",
        "Cantina Labs",
        "GMI Cloud",
        "Sky9",
        "AttentionX",
        "Z Potentials",
        "NUS",
        "Deccan AI",
        "FAR.AI",
        "Exa AI",
        "Instruct.KR",
        "E14 Fund",
        "Axiom",
        "Quadrillion",
        "ML2",
        "Team Attention",
        "GDG",
        "VESSL",
    ]
    found = [name for name in known if name.lower() in title.lower()]
    if found:
        return " / ".join(found)
    # Common pattern: "X @ ICML" or "X — ICML ..."
    before = re.split(r"\s+(?:@|x|—|-)\s+ICML", title, maxsplit=1, flags=re.I)[0].strip()
    if 2 <= len(before) <= 60 and before.lower() != title.lower():
        return before
    return ""


def parse_time_and_title(line: str) -> tuple[str, str, str, str, str]:
    # Examples:
    # 7:00–10:00pm: Cafe Compute @ICML. RSVP: ...
    # 7:30pm–Tue Jul 7, 12:30am: ...
    # 6:00pm~: Trillion Frontier Night x ICML 2026. RSVP: ...
    line = line.strip()
    if " RSVP: " not in line or ": " not in line:
        return "", "", "", line, ""
    prefix, url = line.split(" RSVP: ", 1)
    time_part, title = prefix.split(": ", 1)
    timezone_note = ""
    if time_part.endswith(" PT"):
        timezone_note = "PT"
        time_part = time_part[:-3]
    start, end = split_time_range(time_part)
    return start, end, timezone_note, title.strip().rstrip("."), normalize_url(url)


def split_time_range(value: str) -> tuple[str, str]:
    value = value.strip()
    if "~" in value:
        return value.replace("~", "").strip(), ""
    if "–" in value:
        start, end = value.split("–", 1)
    elif "-" in value:
        start, end = value.split("-", 1)
    else:
        return value, ""
    return start.strip(), end.strip()


def parse_events(description: str, source_updated: str) -> list[SideEvent]:
    lines = [line.strip() for line in description.splitlines() if line.strip()]
    events: list[SideEvent] = []
    in_schedule = False
    current_date = ""
    for line in lines:
        if line == "Full Schedule by Date":
            in_schedule = True
            continue
        if not in_schedule:
            continue
        if line.startswith("More to be announced"):
            break
        if re.match(r"^(Tue|Wed|Thu|Fri|Sat|Sun|Mon)\s+(Jun|Jul)\s+\d{1,2}$", line):
            current_date = line
            continue
        if "RSVP:" not in line:
            continue
        start, end, timezone_note, title, url = parse_time_and_title(line)
        detail = detail_from_local_page(url)
        events.append(
            SideEvent(
                date_label=current_date,
                date_2026=parse_date(current_date),
                start_time=start,
                end_time=end,
                timezone_note=timezone_note,
                title=title,
                organizer_guess=guess_organizer(title),
                event_kind=classify(title),
                rsvp_url=url,
                platform=platform(url),
                detail_name=detail.get("detail_name", ""),
                detail_start=detail.get("detail_start", ""),
                detail_end=detail.get("detail_end", ""),
                location_name=detail.get("location_name", ""),
                address_region=detail.get("address_region", ""),
                address_country=detail.get("address_country", ""),
                latitude=detail.get("latitude", ""),
                longitude=detail.get("longitude", ""),
                organizer_verified=detail.get("organizer_verified", ""),
                ticket_availability=detail.get("ticket_availability", ""),
                source_url=SOURCE_URL,
                source_updated=source_updated,
                confidence="curated_public_hub+detail_page" if detail else "curated_public_hub",
                notes="Parsed from Team Attention Luma hub; verify individual RSVP page before attending.",
            )
        )
    return events


def main() -> None:
    text = RAW.read_text(encoding="utf-8", errors="replace")
    data = extract_json_ld(text)
    description = data["description"]
    update_match = re.search(r"Last updated:\s*(.+)", description)
    source_updated = update_match.group(1).strip() if update_match else ""
    rows = parse_events(description, source_updated)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(asdict(rows[0]).keys()))
        writer.writeheader()
        writer.writerows(asdict(row) for row in rows)

    summary = {}
    for row in rows:
        summary[row.event_kind] = summary.get(row.event_kind, 0) + 1
    with SUMMARY.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["kind", "count"])
        writer.writeheader()
        for kind, count in sorted(summary.items()):
            writer.writerow({"kind": kind, "count": count})

    print(f"side_events: {len(rows)}")
    print(f"source_updated: {source_updated}")


if __name__ == "__main__":
    main()
