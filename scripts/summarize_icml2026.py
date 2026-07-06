#!/usr/bin/env python3
"""Create compact summaries for planning ICML 2026 routes."""

from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
IN = ROOT / "data" / "processed" / "icml2026_papers_tagged.csv"
OUT = ROOT / "data" / "processed" / "icml2026_topic_session_summary.csv"


def main() -> None:
    with IN.open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    grouped: dict[tuple[str, str, str, str, str, str, str], Counter] = defaultdict(Counter)
    for row in rows:
        if row["is_scheduled"] != "yes":
            continue
        topics = [topic for topic in row["topic_tracks"].split(" | ") if topic]
        if not topics:
            topics = ["Unmatched"]
        session_url = f"https://icml.cc/virtual/2026/session/{row['poster_session_id']}" if row["poster_session_id"] else ""
        session_key = (
            row["poster_date_kst"],
            row["poster_time_kst"].split("-", 1)[0],
            row["poster_time_kst"].split("-", 1)[1] if "-" in row["poster_time_kst"] else "",
            row["poster_session"],
            row["poster_session_id"],
            session_url,
            row["poster_room"],
        )
        for topic in topics:
            key = (topic,) + session_key
            grouped[key]["papers"] += 1
            grouped[key]["oral"] += row["is_oral"] == "yes"
            grouped[key]["spotlight"] += row["is_spotlight"] == "yes"
            grouped[key]["position"] += row["is_position"] == "yes"
            grouped[key]["journal_track"] += row["is_journal_track"] == "yes"

    fieldnames = [
        "topic_track",
        "date",
        "session_start_time",
        "session_end_time",
        "session_title",
        "session_id",
        "session_url",
        "room",
        "papers",
        "oral",
        "spotlight",
        "position",
        "journal_track",
    ]
    out_rows = []
    for key, counts in grouped.items():
        out_rows.append(
            {
                "topic_track": key[0],
                "date": key[1],
                "session_start_time": key[2],
                "session_end_time": key[3],
                "session_title": key[4],
                "session_id": key[5],
                "session_url": key[6],
                "room": key[7],
                "papers": counts["papers"],
                "oral": counts["oral"],
                "spotlight": counts["spotlight"],
                "position": counts["position"],
                "journal_track": counts["journal_track"],
            }
        )
    out_rows.sort(
        key=lambda row: (
            row["topic_track"],
            row["date"] or "9999",
            row["session_start_time"],
            -int(row["spotlight"]),
            -int(row["papers"]),
        )
    )

    with OUT.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(out_rows)

    print(f"topic_session_rows: {len(out_rows)}")


if __name__ == "__main__":
    main()
