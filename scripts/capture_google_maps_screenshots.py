#!/usr/bin/env python3
"""Capture Google Maps route screenshots listed in the screenshot target CSV."""

from __future__ import annotations

import argparse
import csv
import os
import subprocess
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[1]
TARGETS = ROOT / "data" / "processed" / "icml2026_google_maps_screenshot_targets.csv"
SCREENSHOTS_OUT = ROOT / "data" / "processed" / "icml2026_google_maps_screenshots.csv"
DEFAULT_CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
MIN_SCREENSHOT_BYTES = 100_000


def chrome_binary() -> str:
    return os.environ.get("CHROME_BIN") or DEFAULT_CHROME


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def screenshot_status(path: Path) -> tuple[str, int]:
    if not path.exists():
        return "missing", 0
    size = path.stat().st_size
    if size < MIN_SCREENSHOT_BYTES:
        return "too_small", size
    return "available", size


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--existing-only",
        action="store_true",
        help="Only scan existing screenshot files and write the manifest.",
    )
    parser.add_argument(
        "--timeout-seconds",
        type=int,
        default=int(os.environ.get("CHROME_TIMEOUT_SECONDS", "45")),
        help="Per-route Chrome timeout for capture mode.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    chrome = chrome_binary()
    if not args.existing_only and not Path(chrome).exists():
        raise RuntimeError(f"Chrome binary not found: {chrome}")

    with TARGETS.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        raise RuntimeError(f"No screenshot targets in {TARGETS}")

    manifest_rows = []
    captured_at = datetime.now(ZoneInfo("Asia/Seoul")).isoformat(timespec="seconds")
    for row in rows:
        out = ROOT / row["suggested_png"]
        out.parent.mkdir(parents=True, exist_ok=True)
        capture_status = "existing_only"
        if not args.existing_only:
            cmd = [
                chrome,
                "--headless=new",
                "--disable-gpu",
                "--no-first-run",
                "--no-default-browser-check",
                "--window-size=1440,1000",
                "--hide-scrollbars",
                "--virtual-time-budget=12000",
                f"--screenshot={out}",
                row["google_maps_directions_url"],
            ]
            try:
                result = subprocess.run(
                    cmd,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    timeout=args.timeout_seconds,
                )
                capture_status = "chrome_ok" if result.returncode == 0 else f"chrome_exit_{result.returncode}"
            except subprocess.TimeoutExpired:
                capture_status = "chrome_timeout"

        file_status, size = screenshot_status(out)
        if file_status == "available" and capture_status == "chrome_timeout":
            status = "available_after_timeout"
        elif file_status == "available":
            status = "available"
        elif capture_status != "existing_only":
            status = capture_status
        else:
            status = file_status

        manifest_rows.append(
            {
                "priority": row["priority"],
                "name": row["name"],
                "google_maps_directions_url": row["google_maps_directions_url"],
                "screenshot_path": row["suggested_png"],
                "status": status,
                "size_bytes": str(size),
                "captured_at_kst": captured_at if status.startswith("available") else "",
                "notes": row["notes"],
            }
        )
        print(f"{row['priority']}. {row['name']} -> {row['suggested_png']} [{status}, {size} bytes]")

    write_csv(SCREENSHOTS_OUT, manifest_rows)
    print(f"Wrote screenshot manifest -> {SCREENSHOTS_OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
