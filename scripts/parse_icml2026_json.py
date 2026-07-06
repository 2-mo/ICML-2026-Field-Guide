#!/usr/bin/env python3
"""Build the primary ICML 2026 paper table from official static JSON.

Official sources:
- https://icml.cc/static/virtual/data/icml-2026-orals-posters.json
- https://icml.cc/static/virtual/data/icml-2026-abstracts.json

The JSON timestamps are stored with a -07:00 offset. This script converts them
to Asia/Seoul because the conference schedule is displayed in Seoul/KST time.
"""

from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "processed"
BASE_URL = "https://icml.cc"
KST = ZoneInfo("Asia/Seoul")


@dataclass
class JsonPaper:
    poster_id: str
    title: str
    authors: str
    institutions: str
    decision: str
    topic: str
    keywords: str
    abstract: str
    poster_url: str
    openreview_url: str
    code_or_project_url: str
    poster_position: str
    poster_session: str
    poster_session_id: str
    poster_room: str
    poster_start_kst: str
    poster_end_kst: str
    poster_date_kst: str
    poster_time_kst: str
    is_scheduled: str
    is_oral: str
    is_spotlight: str
    is_position: str
    is_journal_track: str
    oral_id: str
    oral_url: str
    oral_session: str
    oral_session_id: str
    oral_room: str
    oral_start_kst: str
    oral_end_kst: str
    oral_date_kst: str
    oral_time_kst: str
    slide_url: str
    poster_image_url: str
    source_json: str


def load_events() -> list[dict]:
    path = RAW / "icml-2026-orals-posters.json"
    with path.open(encoding="utf-8") as f:
        data = json.load(f)
    return data["results"]


def load_abstracts() -> dict[str, str]:
    path = RAW / "icml-2026-abstracts.json"
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def load_subset_ids(path: Path) -> set[str]:
    if not path.exists():
        return set()
    text = path.read_text(encoding="utf-8", errors="replace")
    import re

    return set(re.findall(r"/virtual/2026/poster/(\d+)", text))


def yesno(value: bool) -> str:
    return "yes" if value else "no"


def full_url(value: str | None) -> str:
    if not value:
        return ""
    if value.startswith("http://") or value.startswith("https://"):
        return value
    if value.startswith("/"):
        return BASE_URL + value
    return value


def kst(value: str | None) -> str:
    if not value:
        return ""
    return datetime.fromisoformat(value).astimezone(KST).isoformat(timespec="minutes")


def kst_date(value: str | None) -> str:
    if not value:
        return ""
    return datetime.fromisoformat(value).astimezone(KST).strftime("%Y-%m-%d")


def kst_time(value: str | None) -> str:
    if not value:
        return ""
    return datetime.fromisoformat(value).astimezone(KST).strftime("%H:%M")


def author_names(authors: list[dict]) -> str:
    return " | ".join(author.get("fullname", "") for author in authors if author.get("fullname"))


def institutions(authors: list[dict]) -> str:
    values = []
    seen = set()
    for author in authors:
        inst = author.get("institution") or ""
        if inst and inst not in seen:
            seen.add(inst)
            values.append(inst)
    return " | ".join(values)


def media_url(event: dict, media_type: str, name: str | None = None) -> str:
    for media in event.get("eventmedia") or []:
        if media.get("type") != media_type:
            continue
        if name and media.get("name") != name:
            continue
        return full_url(media.get("uri") or media.get("file"))
    return ""


def main() -> None:
    events = load_events()
    abstracts = load_abstracts()
    position_ids = load_subset_ids(RAW / "icml2026_position_papers.html")
    journal_ids = load_subset_ids(RAW / "icml2026_journal_track.html")

    posters = {str(event["id"]): event for event in events if event.get("eventtype") == "Poster"}
    orals = {str(event["id"]): event for event in events if event.get("eventtype") == "Oral"}

    oral_by_poster: dict[str, dict] = {}
    for oral in orals.values():
        for related_id in oral.get("related_events_ids") or []:
            oral_by_poster[str(related_id)] = oral

    rows: list[JsonPaper] = []
    for poster_id in sorted(posters, key=lambda value: int(value)):
        poster = posters[poster_id]
        oral = oral_by_poster.get(poster_id)
        decision = poster.get("decision") or ""
        rows.append(
            JsonPaper(
                poster_id=poster_id,
                title=poster.get("name") or "",
                authors=author_names(poster.get("authors") or []),
                institutions=institutions(poster.get("authors") or []),
                decision=decision,
                topic=poster.get("topic") or "",
                keywords=" | ".join(poster.get("keywords") or []),
                abstract=abstracts.get(poster_id, ""),
                poster_url=full_url(poster.get("virtualsite_url")),
                openreview_url=poster.get("paper_url") or "",
                code_or_project_url=poster.get("url") or "",
                poster_position=poster.get("poster_position") or "",
                poster_session=poster.get("session") or "",
                poster_session_id=str(poster.get("parent_id") or ""),
                poster_room=poster.get("room_name") or "",
                poster_start_kst=kst(poster.get("starttime")),
                poster_end_kst=kst(poster.get("endtime")),
                poster_date_kst=kst_date(poster.get("starttime")),
                poster_time_kst=format_time_range(poster.get("starttime"), poster.get("endtime")),
                is_scheduled=yesno(bool(poster.get("session"))),
                is_oral=yesno(bool(oral)),
                is_spotlight=yesno("spotlight" in decision.lower()),
                is_position=yesno(poster_id in position_ids),
                is_journal_track=yesno(poster_id in journal_ids),
                oral_id=str(oral.get("id")) if oral else "",
                oral_url=full_url(oral.get("virtualsite_url")) if oral else "",
                oral_session=oral.get("session") if oral else "",
                oral_session_id=str(oral.get("parent_id") or "") if oral else "",
                oral_room=oral.get("room_name") if oral else "",
                oral_start_kst=kst(oral.get("starttime")) if oral else "",
                oral_end_kst=kst(oral.get("endtime")) if oral else "",
                oral_date_kst=kst_date(oral.get("starttime")) if oral else "",
                oral_time_kst=format_time_range(oral.get("starttime"), oral.get("endtime")) if oral else "",
                slide_url=media_url(poster, "PDF", "Slides") or (media_url(oral, "PDF", "Slides") if oral else ""),
                poster_image_url=media_url(poster, "Poster", "Poster"),
                source_json=full_url("/static/virtual/data/icml-2026-orals-posters.json"),
            )
        )

    OUT.mkdir(parents=True, exist_ok=True)
    write_csv(OUT / "icml2026_papers_master.csv", rows)
    (OUT / "icml2026_papers_master.json").write_text(
        json.dumps([asdict(row) for row in rows], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"master_papers: {len(rows)}")
    print(f"orals: {sum(row.is_oral == 'yes' for row in rows)}")
    print(f"spotlights: {sum(row.is_spotlight == 'yes' for row in rows)}")
    print(f"scheduled: {sum(row.is_scheduled == 'yes' for row in rows)}")


def format_time_range(start: str | None, end: str | None) -> str:
    if not start:
        return ""
    if not end:
        return kst_time(start)
    return f"{kst_time(start)}-{kst_time(end)}"


def write_csv(path: Path, rows: list[JsonPaper]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(asdict(rows[0]).keys()))
        writer.writeheader()
        writer.writerows(asdict(row) for row in rows)


if __name__ == "__main__":
    main()
