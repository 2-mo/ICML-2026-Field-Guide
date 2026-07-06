#!/usr/bin/env python3
"""Extract ICML 2026 papers that are accepted but not in current venue schedule."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
IN = ROOT / "data" / "processed" / "icml2026_papers_tagged.csv"
OUT = ROOT / "data" / "processed" / "icml2026_extra_attention.csv"
SUMMARY = ROOT / "data" / "processed" / "icml2026_extra_attention_topic_summary.csv"


def main() -> None:
    with IN.open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    extra = [row for row in rows if row["is_scheduled"] != "yes"]
    preferred_fields = [
        "poster_id",
        "title",
        "authors",
        "decision",
        "topic",
        "topic_tracks",
        "openreview_url",
        "poster_url",
        "code_or_project_url",
        "abstract",
    ]
    with OUT.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=preferred_fields)
        writer.writeheader()
        for row in extra:
            writer.writerow({field: row.get(field, "") for field in preferred_fields})

    topic_counts = Counter()
    decision_counts = Counter(row["decision"] or "(blank)" for row in extra)
    for row in extra:
        topics = [topic for topic in row["topic_tracks"].split(" | ") if topic]
        if not topics:
            topic_counts["Unmatched"] += 1
        for topic in topics:
            topic_counts[topic] += 1

    with SUMMARY.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["kind", "name", "count"])
        writer.writeheader()
        for name, count in topic_counts.most_common():
            writer.writerow({"kind": "topic_track", "name": name, "count": count})
        for name, count in decision_counts.most_common():
            writer.writerow({"kind": "decision", "name": name, "count": count})

    print(f"extra_attention: {len(extra)}")
    print(f"topic_summary_rows: {len(topic_counts)}")


if __name__ == "__main__":
    main()
