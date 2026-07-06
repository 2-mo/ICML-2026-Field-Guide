#!/usr/bin/env python3
"""Parse ICML 2026 official HTML pages into structured tables.

Inputs are saved official pages. The parser intentionally uses only the Python
standard library so the pipeline can run in a clean environment.
"""

from __future__ import annotations

import csv
import html
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "processed"
BASE_URL = "https://icml.cc"


@dataclass
class Session:
    date: str
    day_label: str
    start_time: str
    end_time: str
    event_type: str
    title: str
    session_id: str
    session_url: str
    room: str
    source: str


@dataclass
class ScheduledItem:
    date: str
    day_label: str
    session_start_time: str
    session_end_time: str
    item_time: str
    event_type: str
    session_title: str
    session_id: str
    session_url: str
    room: str
    title: str
    item_id: str
    item_url: str
    source: str


@dataclass
class OralMeta:
    oral_id: str
    title: str
    authors: str
    time: str
    room: str
    abstract: str
    oral_url: str
    source: str


@dataclass
class EventCard:
    item_id: str
    event_type: str
    title: str
    authors: str
    time: str
    room: str
    abstract: str
    item_url: str
    source_label: str
    source: str


@dataclass
class Paper:
    item_id: str
    title: str
    item_url: str
    in_papers_page: str
    is_scheduled: str
    is_oral: str
    is_spotlight: str
    is_position: str
    is_journal_track: str
    date: str
    session_start_time: str
    session_end_time: str
    item_time: str
    session_title: str
    session_id: str
    session_url: str
    room: str
    oral_date: str
    oral_start_time: str
    oral_end_time: str
    oral_item_time: str
    oral_session_title: str
    oral_session_id: str
    oral_session_url: str
    oral_room: str
    oral_url: str
    authors: str
    abstract: str
    metadata_source: str


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def write_csv(path: Path, rows: Iterable[object]) -> None:
    rows = list(rows)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fields = list(asdict(rows[0]).keys())
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(asdict(row) for row in rows)


def write_json(path: Path, rows: Iterable[object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = [asdict(row) for row in rows]
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def strip_tags(fragment: str) -> str:
    text = re.sub(r"<script\b.*?</script>", " ", fragment, flags=re.S | re.I)
    text = re.sub(r"<style\b.*?</style>", " ", text, flags=re.S | re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    text = text.replace("\xa0", " ")
    return re.sub(r"\s+", " ", text).strip()


def absolutize(url: str) -> str:
    if not url:
        return ""
    if url.startswith("http://") or url.startswith("https://"):
        return url
    if url.startswith("/"):
        return BASE_URL + url
    return BASE_URL + "/" + url


def month_to_number(month: str) -> str:
    months = {
        "JAN": "01",
        "FEB": "02",
        "MAR": "03",
        "APR": "04",
        "MAY": "05",
        "JUN": "06",
        "JUL": "07",
        "AUG": "08",
        "SEP": "09",
        "OCT": "10",
        "NOV": "11",
        "DEC": "12",
    }
    return months[month.upper()]


def parse_day_label(label: str) -> str:
    # Example: "TUE 7 JUL" -> "2026-07-07"
    m = re.search(r"\b(\d{1,2})\s+([A-Za-z]{3})\b", label)
    if not m:
        return ""
    day, month = m.groups()
    return f"2026-{month_to_number(month)}-{int(day):02d}"


def class_names(tag: str) -> list[str]:
    m = re.search(r'class="([^"]+)"', tag)
    if not m:
        return []
    return [name for name in m.group(1).split() if name]


def room_from_classes(classes: list[str]) -> str:
    for cls in classes:
        if cls.startswith("room-"):
            return cls.removeprefix("room-").replace("-", " ").strip().upper()
    return ""


def event_type_from_classes(classes: list[str]) -> str:
    ignore = {"pad", "eventsession"}
    for cls in classes:
        if cls.endswith("-session"):
            return cls.replace("-", " ").title()
    for cls in classes:
        if cls not in ignore and not cls.startswith("room-"):
            return cls.replace("-", " ").title()
    return ""


def split_tag_blocks(text: str, tag_name: str, class_token: str) -> list[str]:
    """Return complete blocks for tags containing class_token.

    This is a tiny balanced-tag scanner for ICML's regular HTML. It is not a
    general HTML parser, but it avoids fragile non-greedy regex on nested divs.
    """
    blocks: list[str] = []
    token_re = re.compile(
        rf"<{tag_name}\b(?=[^>]*\bclass=\"[^\"]*\b{re.escape(class_token)}\b)",
        re.I,
    )
    tag_re = re.compile(rf"</?{tag_name}\b[^>]*>", re.I)
    for match in token_re.finditer(text):
        depth = 0
        for tag in tag_re.finditer(text, match.start()):
            if tag.group(0).startswith("</"):
                depth -= 1
            else:
                depth += 1
            if depth == 0:
                blocks.append(text[match.start() : tag.end()])
                break
    return blocks


def parse_calendar(path: Path) -> tuple[list[Session], list[ScheduledItem]]:
    text = read_text(path)
    sessions: list[Session] = []
    items: list[ScheduledItem] = []

    for day_block in split_tag_blocks(text, "div", "container2"):
        label_match = re.search(r'<div class="hdrbox">([^<]+)</div>', day_block)
        if not label_match:
            continue
        day_label = strip_tags(label_match.group(1))
        date = parse_day_label(day_label)

        for timebox in split_tag_blocks(day_block, "div", "timebox"):
            time_match = re.search(r'<div class="time">([^<]+)</div>', timebox)
            timebox_time = strip_tags(time_match.group(1)) if time_match else ""
            event_blocks = re.findall(
                r'<div class="((?:oral|poster)-session[^"]*)">(.*?)'
                r'(?=<div class="(?:oral|poster)-session|\Z)',
                timebox,
                flags=re.S,
            )
            # The regex above may miss the final close depth in deeply nested
            # blocks, so use the balanced scanner for each event class too.
            event_html_blocks = []
            event_html_blocks.extend(split_tag_blocks(timebox, "div", "oral-session"))
            event_html_blocks.extend(split_tag_blocks(timebox, "div", "poster-session"))
            if not event_html_blocks and event_blocks:
                event_html_blocks = [body for _, body in event_blocks]

            for event in event_html_blocks:
                opening = event.split(">", 1)[0] + ">"
                classes = class_names(opening)
                event_type = event_type_from_classes(classes)
                room = room_from_classes(classes)

                session_match = re.search(
                    r'<div class="sessiontitle">\s*<a href="([^"]+)">(.*?)</a>',
                    event,
                    flags=re.S,
                )
                if not session_match:
                    continue
                session_href, session_title_html = session_match.groups()
                session_title = strip_tags(
                    re.sub(r'<span class="sessiontime[^"]*">.*?</span>', "", session_title_html, flags=re.S)
                )
                session_id_match = re.search(r"/session/(\d+)", session_href)
                session_id = session_id_match.group(1) if session_id_match else ""
                session_url = absolutize(session_href)
                time_range_match = re.search(r"\[(.*?)\]", strip_tags(session_title_html))
                time_range = time_range_match.group(1) if time_range_match else ""
                start_time, end_time = split_range(time_range)
                start_time = start_time or timebox_time

                sessions.append(
                    Session(
                        date=date,
                        day_label=day_label,
                        start_time=start_time,
                        end_time=end_time,
                        event_type=event_type,
                        title=session_title,
                        session_id=session_id,
                        session_url=session_url,
                        room=room,
                        source=absolutize("/virtual/2026/calendar"),
                    )
                )

                for item in parse_event_items(event, event_type):
                    item_title, item_time, item_href, item_id = item
                    items.append(
                        ScheduledItem(
                            date=date,
                            day_label=day_label,
                            session_start_time=start_time,
                            session_end_time=end_time,
                            item_time=item_time,
                            event_type=event_type,
                            session_title=session_title,
                            session_id=session_id,
                            session_url=session_url,
                            room=room,
                            title=item_title,
                            item_id=item_id,
                            item_url=absolutize(item_href),
                            source=absolutize("/virtual/2026/calendar"),
                        )
                    )

    sessions = dedupe_dataclasses(sessions)
    items = dedupe_dataclasses(items)
    return sessions, items


def split_range(value: str) -> tuple[str, str]:
    if "-" not in value:
        return value.strip(), ""
    start, end = value.split("-", 1)
    return start.strip(), end.strip()


def parse_event_items(event: str, event_type: str) -> list[tuple[str, str, str, str]]:
    class_token = "oral" if "Oral" in event_type else "poster"
    results: list[tuple[str, str, str, str]] = []
    for item in split_tag_blocks(event, "div", class_token):
        opening = item.split(">", 1)[0]
        if f"content {class_token}" not in opening:
            continue
        href_match = re.search(r'<a href="([^"]+)">', item)
        href = href_match.group(1) if href_match else ""
        item_id_match = re.search(r"/(?:poster|oral)/(\d+)", href)
        item_id = item_id_match.group(1) if item_id_match else ""
        time_match = re.search(r"\[(\d{1,2}:\d{2})\]", strip_tags(item))
        item_time = time_match.group(1) if time_match else ""
        title = strip_tags(re.sub(r"\[\d{1,2}:\d{2}\]", "", item))
        if title:
            results.append((title, item_time, href, item_id))
    return results


def dedupe_dataclasses(rows: list[object]) -> list[object]:
    seen: set[tuple[tuple[str, object], ...]] = set()
    out = []
    for row in rows:
        key = tuple(asdict(row).items())
        if key in seen:
            continue
        seen.add(key)
        out.append(row)
    return out


def parse_oral_events(path: Path) -> list[OralMeta]:
    rows: list[OralMeta] = []
    for event in parse_event_cards(path, "oral"):
        rows.append(
            OralMeta(
                oral_id=event.item_id,
                title=event.title,
                authors=event.authors,
                time=event.time,
                room=event.room,
                abstract=event.abstract,
                oral_url=event.item_url,
                source=event.source,
            )
        )
    return dedupe_dataclasses(rows)


def parse_event_cards(path: Path, source_label: str) -> list[EventCard]:
    text = read_text(path)
    rows: list[EventCard] = []
    source_url = source_url_for_path(path)
    for card in split_tag_blocks(text, "div", "event-card"):
        type_match = re.search(r'data-event-type="([^"]+)"', card)
        event_type = strip_tags(type_match.group(1)) if type_match else ""
        id_match = re.search(r'id="event-(\d+)"', card)
        item_id = id_match.group(1) if id_match else ""
        title_match = re.search(r'<h3 class="event-title">\s*<a href="([^"]+)">(.*?)</a>', card, flags=re.S)
        if not title_match:
            continue
        href, title_html = title_match.groups()
        if not item_id:
            item_id_match = re.search(r"/(?:poster|oral)/(\d+)", href)
            item_id = item_id_match.group(1) if item_id_match else ""
        speakers_match = re.search(r'<div class="event-speakers">\s*(.*?)\s*</div>', card, flags=re.S)
        time_match = re.search(r'<span class="touchup-time">\s*(.*?)\s*</span>', card, flags=re.S)
        meta_spans = re.findall(r'<span class="meta-pill">\s*.*?<span>(.*?)</span>\s*</span>', card, flags=re.S)
        abstract_match = re.search(r'<div class="abstract-text" id="abstract-\d+">\s*(.*?)\s*</div>', card, flags=re.S)
        rows.append(
            EventCard(
                item_id=item_id,
                event_type=event_type,
                title=strip_tags(title_html),
                authors=strip_tags(speakers_match.group(1)) if speakers_match else "",
                time=strip_tags(time_match.group(1)) if time_match else "",
                room=strip_tags(meta_spans[-1]) if meta_spans else "",
                abstract=strip_tags(abstract_match.group(1)) if abstract_match else "",
                item_url=absolutize(href),
                source_label=source_label,
                source=source_url,
            )
        )
    return dedupe_dataclasses(rows)


def parse_papers_list(path: Path) -> list[EventCard]:
    text = read_text(path)
    rows: list[EventCard] = []
    seen: set[str] = set()
    for href, title_html in re.findall(r'<a href="(/virtual/2026/poster/\d+)">(.*?)</a>', text, flags=re.S):
        item_id = href.rsplit("/", 1)[-1]
        if item_id in seen:
            continue
        seen.add(item_id)
        rows.append(
            EventCard(
                item_id=item_id,
                event_type="Poster",
                title=strip_tags(title_html),
                authors="",
                time="",
                room="",
                abstract="",
                item_url=absolutize(href),
                source_label="papers",
                source=absolutize("/virtual/2026/papers.html"),
            )
        )
    return rows


def source_url_for_path(path: Path) -> str:
    name = path.name
    mapping = {
        "icml2026_events_oral.html": "/virtual/2026/events/oral",
        "icml2026_spotlight_posters.html": "/virtual/2026/events/2026SpotlightPosters",
        "icml2026_position_papers.html": "/virtual/2026/events/2026-position-papers",
        "icml2026_journal_track.html": "/virtual/2026/events/2026-journal-track",
        "icml2026_papers.html": "/virtual/2026/papers.html",
    }
    return absolutize(mapping.get(name, f"/virtual/2026/{name}"))


def normalize_title(title: str) -> str:
    normalized = html.unescape(title)
    normalized = normalized.lower()
    normalized = re.sub(r"[^a-z0-9]+", " ", normalized)
    return re.sub(r"\s+", " ", normalized).strip()


def build_enriched_papers(
    scheduled_items: list[ScheduledItem],
    papers_list: list[EventCard],
    event_cards: list[EventCard],
) -> list[Paper]:
    scheduled_by_id = {row.item_id: row for row in scheduled_items if row.item_id}
    scheduled_by_title = {
        normalize_title(row.title): row for row in scheduled_items if row.title and row.event_type == "Poster Session"
    }
    oral_by_title = {
        normalize_title(row.title): row for row in scheduled_items if row.title and row.event_type == "Oral Session"
    }

    card_by_id: dict[str, EventCard] = {}
    card_by_title: dict[str, EventCard] = {}
    cards_by_label: dict[str, dict[str, EventCard]] = {
        "spotlight": {},
        "position": {},
        "journal_track": {},
        "oral": {},
    }
    for card in event_cards:
        if card.item_id and card.item_id not in card_by_id:
            card_by_id[card.item_id] = card
        if card.title and normalize_title(card.title) not in card_by_title:
            card_by_title[normalize_title(card.title)] = card
        if card.item_id and card.source_label in cards_by_label:
            cards_by_label[card.source_label][card.item_id] = card

    paper_ids = {paper.item_id for paper in papers_list}
    paper_ids.update(row.item_id for row in scheduled_items if row.item_id)
    paper_ids.update(card.item_id for card in event_cards if card.item_id and card.event_type == "Poster")

    papers_by_id = {paper.item_id: paper for paper in papers_list}
    rows: list[Paper] = []
    for item_id in sorted(paper_ids):
        paper = papers_by_id.get(item_id)
        card = card_by_id.get(item_id)
        scheduled = scheduled_by_id.get(item_id)
        if not scheduled and paper:
            scheduled = scheduled_by_title.get(normalize_title(paper.title))
        title = (paper.title if paper else "") or (scheduled.title if scheduled else "") or (card.title if card else "")
        if not title:
            continue
        if not card and title:
            # Oral pages use a different ID namespace from poster pages.
            card = card_by_title.get(normalize_title(title))
        oral_scheduled = oral_by_title.get(normalize_title(title)) if title else None
        oral_card = card_by_title.get(normalize_title(title)) if title else None

        rows.append(
            Paper(
                item_id=item_id,
                title=title,
                item_url=(paper.item_url if paper else "") or (scheduled.item_url if scheduled else "") or (card.item_url if card else ""),
                in_papers_page=yesno(bool(paper)),
                is_scheduled=yesno(bool(scheduled)),
                is_oral=yesno(bool(oral_scheduled)),
                is_spotlight=yesno(item_id in cards_by_label["spotlight"]),
                is_position=yesno(item_id in cards_by_label["position"]),
                is_journal_track=yesno(item_id in cards_by_label["journal_track"]),
                date=scheduled.date if scheduled else "",
                session_start_time=scheduled.session_start_time if scheduled else "",
                session_end_time=scheduled.session_end_time if scheduled else "",
                item_time=scheduled.item_time if scheduled else "",
                session_title=scheduled.session_title if scheduled else "",
                session_id=scheduled.session_id if scheduled else "",
                session_url=scheduled.session_url if scheduled else "",
                room=scheduled.room if scheduled and scheduled.room else (card.room if card else ""),
                oral_date=oral_scheduled.date if oral_scheduled else "",
                oral_start_time=oral_scheduled.session_start_time if oral_scheduled else "",
                oral_end_time=oral_scheduled.session_end_time if oral_scheduled else "",
                oral_item_time=oral_scheduled.item_time if oral_scheduled else "",
                oral_session_title=oral_scheduled.session_title if oral_scheduled else "",
                oral_session_id=oral_scheduled.session_id if oral_scheduled else "",
                oral_session_url=oral_scheduled.session_url if oral_scheduled else "",
                oral_room=oral_scheduled.room if oral_scheduled else "",
                oral_url=oral_card.item_url if oral_card and oral_card.event_type == "Oral" else "",
                authors=card.authors if card else "",
                abstract=card.abstract if card else "",
                metadata_source=card.source if card else "",
            )
        )
    return rows


def yesno(value: bool) -> str:
    return "yes" if value else "no"


def main() -> None:
    calendar_path = RAW / "icml2026_calendar.html"
    oral_path = ROOT / "icml2026_events_oral.html"
    if not oral_path.exists():
        oral_path = RAW / "icml2026_events_oral.html"
    papers_path = RAW / "icml2026_papers.html"
    spotlight_path = RAW / "icml2026_spotlight_posters.html"
    position_path = RAW / "icml2026_position_papers.html"
    journal_path = RAW / "icml2026_journal_track.html"

    sessions, items = parse_calendar(calendar_path)
    oral_meta = parse_oral_events(oral_path) if oral_path.exists() else []
    papers_list = parse_papers_list(papers_path) if papers_path.exists() else []
    event_cards: list[EventCard] = []
    for source_label, path in [
        ("oral", oral_path),
        ("spotlight", spotlight_path),
        ("position", position_path),
        ("journal_track", journal_path),
    ]:
        if path.exists():
            event_cards.extend(parse_event_cards(path, source_label))
    enriched_papers = build_enriched_papers(items, papers_list, event_cards)

    write_csv(OUT / "icml2026_sessions.csv", sessions)
    write_csv(OUT / "icml2026_scheduled_items.csv", items)
    write_csv(OUT / "icml2026_oral_metadata.csv", oral_meta)
    write_csv(OUT / "icml2026_event_cards.csv", event_cards)
    write_csv(OUT / "icml2026_papers_enriched.csv", enriched_papers)
    write_json(OUT / "icml2026_sessions.json", sessions)
    write_json(OUT / "icml2026_scheduled_items.json", items)
    write_json(OUT / "icml2026_oral_metadata.json", oral_meta)
    write_json(OUT / "icml2026_event_cards.json", event_cards)
    write_json(OUT / "icml2026_papers_enriched.json", enriched_papers)

    print(f"sessions: {len(sessions)}")
    print(f"scheduled_items: {len(items)}")
    print(f"oral_metadata: {len(oral_meta)}")
    print(f"papers_list: {len(papers_list)}")
    print(f"event_cards: {len(event_cards)}")
    print(f"enriched_papers: {len(enriched_papers)}")


if __name__ == "__main__":
    main()
