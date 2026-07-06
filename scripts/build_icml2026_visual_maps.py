#!/usr/bin/env python3
"""Build code-drawn bilingual maps for the ICML 2026 guide.

Outputs:
- data/maps/icml2026_seoul_schematic.svg
- data/maps/icml2026_seoul_schematic.png, when Chrome is available
- data/maps/icml2026_seoul_maplibre.html
- data/maps/icml2026_seoul_maplibre.png, when Chrome is available
- data/maps/icml2026_seoul_leaflet.html
- data/maps/icml2026_seoul_leaflet.png, when Chrome is available
- data/processed/icml2026_visual_map_points.csv
- data/processed/icml2026_visual_map_routes.csv
"""

from __future__ import annotations

import argparse
import csv
import html
import json
import os
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path
from urllib.parse import urlencode


ROOT = Path(__file__).resolve().parents[1]
MAP_DIR = ROOT / "data" / "maps"
OUT_DIR = ROOT / "data" / "processed"
SVG_OUT = MAP_DIR / "icml2026_seoul_schematic.svg"
SVG_PNG_OUT = MAP_DIR / "icml2026_seoul_schematic.png"
MAPLIBRE_OUT = MAP_DIR / "icml2026_seoul_maplibre.html"
MAPLIBRE_PNG_OUT = MAP_DIR / "icml2026_seoul_maplibre.png"
LEAFLET_OUT = MAP_DIR / "icml2026_seoul_leaflet.html"
LEAFLET_PNG_OUT = MAP_DIR / "icml2026_seoul_leaflet.png"
POINTS_OUT = OUT_DIR / "icml2026_visual_map_points.csv"
ROUTES_OUT = OUT_DIR / "icml2026_visual_map_routes.csv"

DEFAULT_CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
GOOGLE_MAPS_SEARCH = "https://www.google.com/maps/search/?api=1"
GOOGLE_MAPS_DIRECTIONS = "https://www.google.com/maps/dir/?api=1"
COEX_QUERY = "COEX Convention & Exhibition Center, 513 Yeongdong-daero, Gangnam-gu, Seoul"

WIDTH = 1600
HEIGHT = 1000
PLOT_LEFT = 70
PLOT_RIGHT = 410
PLOT_TOP = 120
PLOT_BOTTOM = 90

LON_MIN = 126.36
LON_MAX = 127.18
LAT_MIN = 37.38
LAT_MAX = 37.64


@dataclass(frozen=True)
class Point:
    id: str
    category: str
    zh: str
    en: str
    ko_note: str
    latitude: float
    longitude: float
    google_maps_query: str
    note_zh: str
    note_en: str


@dataclass(frozen=True)
class Route:
    id: str
    category: str
    zh: str
    en: str
    points: tuple[str, ...]
    color: str
    stroke_dasharray: str
    google_maps_origin: str
    google_maps_destination: str
    travelmode: str
    note_zh: str
    note_en: str


def maps_search_url(query: str) -> str:
    return f"{GOOGLE_MAPS_SEARCH}&{urlencode({'query': query})}"


def maps_directions_url(origin: str, destination: str, travelmode: str = "transit") -> str:
    return f"{GOOGLE_MAPS_DIRECTIONS}&{urlencode({'origin': origin, 'destination': destination, 'travelmode': travelmode})}"


def label(point: Point) -> str:
    suffix = f" ({point.ko_note})" if point.ko_note else ""
    return f"{point.zh} / {point.en}{suffix}"


def route_label(route: Route) -> str:
    return f"{route.zh} / {route.en}"


def project(latitude: float, longitude: float) -> tuple[float, float]:
    x = PLOT_LEFT + (longitude - LON_MIN) / (LON_MAX - LON_MIN) * (WIDTH - PLOT_LEFT - PLOT_RIGHT)
    y = PLOT_TOP + (LAT_MAX - latitude) / (LAT_MAX - LAT_MIN) * (HEIGHT - PLOT_TOP - PLOT_BOTTOM)
    return x, y


def project_to_box(
    latitude: float,
    longitude: float,
    bounds: tuple[float, float, float, float],
    box: tuple[float, float, float, float],
) -> tuple[float, float]:
    lon_min, lon_max, lat_min, lat_max = bounds
    x, y, width, height = box
    px = x + (longitude - lon_min) / (lon_max - lon_min) * width
    py = y + (lat_max - latitude) / (lat_max - lat_min) * height
    return px, py


def build_points() -> list[Point]:
    return [
        Point("coex", "venue", "COEX 会场", "COEX venue", "코엑스", 37.5118, 127.0592, COEX_QUERY, "主会场与默认出发点。", "Main venue and default origin."),
        Point("parnas", "hotel", "Parnas 酒店区", "Parnas hotel area", "", 37.5089, 127.0611, "Grand InterContinental Seoul Parnas, 521 Teheran-ro, Seoul", "会场酒店与餐饮锚点。", "Hotel and food anchor next to COEX."),
        Point("provista", "hotel", "普罗威斯塔酒店", "Provista Hotel", "", 37.4932, 127.0157, "Hotel Provista Seoul, 338 Seocho-daero, Seocho-gu, Seoul 06632", "住处：338 Seocho-daero, Seocho-gu, Seoul 06632。", "Hotel base: 338 Seocho-daero, Seocho-gu, Seoul 06632."),
        Point("samseong", "station", "三成站", "Samseong Station", "삼성", 37.5088, 127.0631, "Samseong Station Exit 5, Seoul", "Line 2，COEX 官方建议 5/6 号出口。", "Line 2; COEX recommends exits 5/6."),
        Point("bongeunsa", "station", "奉恩寺站", "Bongeunsa Station", "봉은사", 37.5142, 127.0602, "Bongeunsa Station Exit 7, Seoul", "Line 9，COEX 官方建议 7 号出口。", "Line 9; COEX recommends exit 7."),
        Point("gangnam", "zone", "江南站", "Gangnam Station", "강남", 37.4979, 127.0276, "Gangnam Station, Seoul", "晚宴、meetup、饭局高密度区域。", "High-density dinner and meetup area."),
        Point("yeoksam", "zone", "驿三区域", "Yeoksam area", "역삼", 37.5013, 127.0396, "Yeoksam-ro, Gangnam-gu, Seoul", "OpenAI/Hugging Face 等活动公开页只到区域级。", "Some RSVP pages expose only this obfuscated area."),
        Point("gfc", "event", "江南金融中心", "Gangnam Finance Center", "", 37.5002, 127.0364, "Gangnam Finance Center 24F, 152 Teheran-ro, Gangnam-gu, Seoul", "Google DeepMind x GDG 活动公开地址。", "Public address for the Google DeepMind x GDG event."),
        Point("dosan", "zone", "岛山大路 81 街区域", "Dosan-daero 81-gil area", "", 37.5280, 127.0470, "Dosan-daero 81-gil, Gangnam-gu, Seoul", "VESSL 晚宴公开页只到区域级。", "VESSL dinner public page exposes only an obfuscated area."),
        Point("seongsu", "zone", "圣水", "Seongsu", "성수", 37.5446, 127.0559, "Seongsu Station, Seoul", "咖啡、品牌空间、轻松半日行程。", "Cafe and brand-space zone for a lighter half day."),
        Point("seoul_forest", "nearby", "首尔林", "Seoul Forest", "서울숲", 37.5444, 127.0374, "Seoul Forest, Seoul", "可和圣水一起安排。", "Pair with Seongsu rather than a separate trip."),
        Point("hongdae", "zone", "弘大", "Hongdae", "홍대", 37.5572, 126.9245, "Hongik University Station, Seoul", "夜生活备选，不适合短午休。", "Nightlife fallback; not ideal for a short lunch gap."),
        Point("itaewon", "zone", "梨泰院", "Itaewon", "이태원", 37.5345, 126.9946, "Itaewon Station, Seoul", "晚餐、酒吧、Hannam/Hangangjin 方向。", "Dinner, bars, Hannam/Hangangjin direction."),
        Point("gimpo", "airport", "金浦机场换乘", "Gimpo transfer", "김포", 37.5587, 126.7945, "Gimpo International Airport Station", "AREX 换乘 Line 9 的节点。", "Transfer from AREX to Line 9."),
        Point("incheon_t1", "airport", "仁川机场 T1", "Incheon Airport T1", "인천", 37.4602, 126.4407, "Incheon Airport Terminal 1, 272 Gonghang-ro, Yeongjong-gu, Incheon", "国际到达，注意 T1/T2。", "International arrival; confirm T1/T2."),
        Point("pangyo", "zone", "板桥科技谷", "Pangyo Techno Valley", "판교", 37.3947, 127.1112, "Pangyo Techno Valley, Seongnam", "较远的公司/园区活动方向。", "Longer offsite company-campus direction."),
    ]


def build_routes() -> list[Route]:
    return [
        Route("arrival_icn", "airport", "AREX 仁川 T1 到金浦", "AREX ICN T1 to Gimpo", ("incheon_t1", "gimpo"), "#2563eb", "", "Incheon Airport Terminal 1, 272 Gonghang-ro, Yeongjong-gu, Incheon", "Gimpo International Airport Station", "transit", "仁川 T1 先坐 AREX 到金浦机场换乘。", "Take AREX from ICN T1 to Gimpo Airport transfer."),
        Route("line2_core", "metro", "Line 2 核心线", "Line 2 core", ("hongdae", "seongsu", "samseong", "gangnam"), "#2a9d8f", "", "Samseong Station, Seoul", "Gangnam Station, Seoul", "transit", "会场到江南、圣水、弘大都可用 Line 2 作为主轴。", "Line 2 is the main axis for Gangnam, Seongsu, and Hongdae."),
        Route("line9_core", "metro", "Line 9 金浦到奉恩寺", "Line 9 Gimpo to Bongeunsa", ("gimpo", "bongeunsa", "coex"), "#b78714", "", "Gimpo International Airport Station", COEX_QUERY, "transit", "金浦换乘 Line 9 到奉恩寺站，7 号出口到 COEX。", "Transfer to Line 9 at Gimpo, ride to Bongeunsa, then walk to COEX."),
        Route("hotel_line2", "metro", "Line 2 酒店到三成", "Line 2 hotel to Samseong", ("provista", "samseong", "coex"), "#2a9d8f", "", "Hotel Provista Seoul, 338 Seocho-daero, Seocho-gu, Seoul 06632", COEX_QUERY, "transit", "普罗威斯塔酒店从教大/Line 2 到三成，再步行到 COEX。", "From Provista, use Line 2 toward Samseong, then walk to COEX."),
        Route("evening_gangnam", "evening", "江南晚间圈", "Gangnam evening loop", ("coex", "dosan", "gfc", "yeoksam", "gangnam"), "#4361ee", "", COEX_QUERY, "Gangnam Station, Seoul", "transit", "大多数科技公司社交、晚宴、meetup 的第一候选区域。", "First-choice zone for many tech socials, dinners, and meetups."),
        Route("itaewon", "evening", "梨泰院方向", "Itaewon direction", ("coex", "itaewon"), "#7209b7", "7 6", COEX_QUERY, "Itaewon Station, Seoul", "transit", "晚餐和酒吧可选，深夜可考虑出租车。", "Good for dinner and bars; taxi may be simpler late night."),
        Route("pangyo", "offsite", "板桥远端活动", "Pangyo offsite", ("coex", "pangyo"), "#6c757d", "12 8", COEX_QUERY, "Pangyo Techno Valley, Seongnam", "transit", "只建议给重要 offsite 留整晚。", "Reserve a full evening only for important offsites."),
    ]


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def point_rows(points: list[Point]) -> list[dict[str, str]]:
    rows = []
    for point in points:
        row = asdict(point)
        row["label"] = label(point)
        row["google_maps_url"] = maps_search_url(point.google_maps_query)
        rows.append(row)
    return rows


def route_rows(routes: list[Route]) -> list[dict[str, str]]:
    rows = []
    for route in routes:
        row = asdict(route)
        row["points"] = " -> ".join(route.points)
        row["label"] = route_label(route)
        row["google_maps_directions_url"] = maps_directions_url(
            route.google_maps_origin, route.google_maps_destination, route.travelmode
        )
        rows.append(row)
    return rows


def svg_path_for_route(route: Route, point_by_id: dict[str, Point]) -> str:
    coords = [project(point_by_id[pid].latitude, point_by_id[pid].longitude) for pid in route.points]
    if len(coords) == 2:
        return f"M {coords[0][0]:.1f} {coords[0][1]:.1f} L {coords[1][0]:.1f} {coords[1][1]:.1f}"
    chunks = [f"M {coords[0][0]:.1f} {coords[0][1]:.1f}"]
    for x, y in coords[1:]:
        chunks.append(f"L {x:.1f} {y:.1f}")
    return " ".join(chunks)


def marker_style(category: str) -> tuple[str, str]:
    styles = {
        "venue": ("#111827", "#ffffff"),
        "station": ("#2563eb", "#ffffff"),
        "zone": ("#0f766e", "#ffffff"),
        "event": ("#7c3aed", "#ffffff"),
        "airport": ("#ea580c", "#ffffff"),
        "hotel": ("#be123c", "#ffffff"),
        "nearby": ("#16a34a", "#ffffff"),
    }
    return styles.get(category, ("#475569", "#ffffff"))


def label_offset(point_id: str) -> tuple[float, float, str]:
    offsets = {
        "coex": (14, -20, "start"),
        "parnas": (12, 18, "start"),
        "samseong": (12, 34, "start"),
        "bongeunsa": (12, -34, "start"),
        "gangnam": (-16, 34, "end"),
        "yeoksam": (-18, -22, "end"),
        "gfc": (-18, -42, "end"),
        "dosan": (-18, -18, "end"),
        "seongsu": (12, -28, "start"),
        "seoul_forest": (-18, 28, "end"),
        "hongdae": (12, -20, "start"),
        "itaewon": (-16, 24, "end"),
        "gimpo": (14, -22, "start"),
        "incheon_t1": (14, 0, "start"),
        "pangyo": (-16, 0, "end"),
    }
    return offsets.get(point_id, (12, -12, "start"))


def build_svg(points: list[Point], routes: list[Route]) -> str:
    point_by_id = {point.id: point for point in points}
    overview_box = (60.0, 124.0, 950.0, 816.0)
    overview_bounds = (126.36, 127.18, 37.38, 37.64)
    inset_box = (1084.0, 365.0, 390.0, 260.0)
    inset_bounds = (127.020, 127.068, 37.493, 37.532)

    def p_over(point_id: str) -> tuple[float, float]:
        point = point_by_id[point_id]
        return project_to_box(point.latitude, point.longitude, overview_bounds, overview_box)

    def p_inset(point_id: str) -> tuple[float, float]:
        point = point_by_id[point_id]
        return project_to_box(point.latitude, point.longitude, inset_bounds, inset_box)

    def route_path(ids: tuple[str, ...], projector) -> str:
        coords = [projector(point_id) for point_id in ids]
        chunks = [f"M {coords[0][0]:.1f} {coords[0][1]:.1f}"]
        chunks.extend(f"L {x:.1f} {y:.1f}" for x, y in coords[1:])
        return " ".join(chunks)

    def draw_route(path: str, color: str, width: int = 8, dash: str = "", opacity: float = 0.82) -> str:
        dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
        return (
            f'<path d="{path}" fill="none" stroke="{color}" stroke-width="{width}" '
            f'stroke-linecap="round" stroke-linejoin="round" opacity="{opacity}"{dash_attr}/>'
            f'<path d="{path}" fill="none" stroke="white" stroke-width="{max(2, width // 3)}" '
            f'stroke-linecap="round" stroke-linejoin="round" opacity="0.68"{dash_attr}/>'
        )

    def draw_marker(point_id: str, x: float, y: float, radius: int = 14) -> str:
        point = point_by_id[point_id]
        fill, text_color = marker_style(point.category)
        initial = {
            "coex": "C",
            "parnas": "P",
            "samseong": "S",
            "bongeunsa": "B",
            "gangnam": "G",
            "yeoksam": "Y",
            "gfc": "F",
            "dosan": "D",
            "seongsu": "S",
            "seoul_forest": "F",
            "hongdae": "H",
            "itaewon": "I",
            "gimpo": "G",
            "incheon_t1": "I",
            "pangyo": "P",
        }.get(point_id, point.en[:1])
        return (
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{radius}" fill="{fill}" stroke="white" stroke-width="4"/>'
            f'<text x="{x:.1f}" y="{y + 5:.1f}" text-anchor="middle" font-size="{12 if radius < 18 else 15}" '
            f'font-weight="900" fill="{text_color}">{html.escape(initial)}</text>'
        )

    def draw_label(x: float, y: float, lines: list[str], anchor: str = "start", size: int = 18, weight: int = 750) -> str:
        tspans = []
        for i, line in enumerate(lines):
            dy = 0 if i == 0 else size + 5
            tspans.append(f'<tspan x="{x:.1f}" dy="{dy}">{html.escape(line)}</tspan>')
        return (
            f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" font-size="{size}" font-weight="{weight}" '
            f'fill="#111827" paint-order="stroke" stroke="#f8fafc" stroke-width="5" stroke-linejoin="round">'
            f'{"".join(tspans)}</text>'
        )

    han_points = [
        project_to_box(37.545, 126.76, overview_bounds, overview_box),
        project_to_box(37.535, 126.89, overview_bounds, overview_box),
        project_to_box(37.525, 126.98, overview_bounds, overview_box),
        project_to_box(37.522, 127.06, overview_bounds, overview_box),
        project_to_box(37.520, 127.16, overview_bounds, overview_box),
    ]
    han_path = (
        f"M {han_points[0][0]:.1f} {han_points[0][1]:.1f} "
        f"C {han_points[1][0]:.1f} {han_points[1][1]:.1f}, {han_points[2][0]:.1f} {han_points[2][1]:.1f}, {han_points[3][0]:.1f} {han_points[3][1]:.1f} "
        f"S {han_points[4][0]:.1f} {han_points[4][1]:.1f}, {han_points[4][0] + 80:.1f} {han_points[4][1] - 6:.1f}"
    )

    overview_route_chunks = []
    for route in routes:
        if route.id in {"arrival_icn", "line2_core", "line9_core", "hotel_line2", "itaewon", "pangyo"}:
            overview_route_chunks.append(
                draw_route(route_path(route.points, p_over), route.color, 8, route.stroke_dasharray)
            )

    overview_markers = []
    overview_labels = [
        ("incheon_t1", ["仁川 T1 / ICN T1 (인천)"], 18, 4, "start"),
        ("gimpo", ["金浦机场 / Gimpo Airport (김포)"], 12, -24, "start"),
        ("hongdae", ["弘大 / Hongdae (홍대)"], -16, -24, "end"),
        ("seongsu", ["圣水 / Seongsu (성수)", "首尔林 / Seoul Forest (서울숲)"], 16, -26, "start"),
        ("itaewon", ["梨泰院 / Itaewon (이태원)"], -18, -22, "end"),
        ("coex", ["COEX 会场 / Venue", "江南晚间圈 / Gangnam evening zone"], 18, 26, "start"),
        ("pangyo", ["板桥科技谷 / Pangyo Techno Valley (판교)"], -18, 6, "end"),
    ]
    for point_id, lines, dx, dy, anchor in overview_labels:
        x, y = p_over(point_id)
        overview_markers.append(draw_marker(point_id, x, y, 18 if point_id == "coex" else 14))
        overview_markers.append(draw_label(x + dx, y + dy, lines, anchor, 17 if point_id != "coex" else 18))

    overview_markers.append(
        f'<circle cx="{p_over("coex")[0]:.1f}" cy="{p_over("coex")[1]:.1f}" r="76" fill="#dbeafe" '
        f'stroke="#2563eb" stroke-width="2" stroke-dasharray="8 6" opacity="0.48"/>'
    )

    inset_route_chunks = []
    inset_route_chunks.append(draw_route(route_path(("gangnam", "yeoksam", "samseong"), p_inset), "#2a9d8f", 7))
    inset_route_chunks.append(draw_route(route_path(("bongeunsa", "coex"), p_inset), "#b78714", 7))
    inset_route_chunks.append(draw_route(route_path(("coex", "dosan", "gfc", "yeoksam", "gangnam"), p_inset), "#4361ee", 7))
    inset_route_chunks.append(draw_route(route_path(("coex", "parnas", "samseong"), p_inset), "#be123c", 5, "5 5", 0.72))

    inset_items = [
        ("coex", ["COEX 会场 / Venue", "(코엑스)"], 14, -18, "start", 14),
        ("bongeunsa", ["奉恩寺站 / Bongeunsa", "(봉은사)"], 12, -16, "start", 12),
        ("samseong", ["三成站 / Samseong", "(삼성)"], 12, 23, "start", 12),
        ("parnas", ["Parnas 酒店区", "Parnas hotel area"], 10, 36, "start", 12),
        ("gangnam", ["江南站 / Gangnam", "(강남)"], -14, 30, "end", 12),
        ("yeoksam", ["驿三区域 / Yeoksam", "(역삼)"], -14, -18, "end", 12),
        ("gfc", ["江南金融中心 / GFC"], -14, -34, "end", 12),
        ("dosan", ["岛山大路 81 街区域", "Dosan-daero 81-gil"], -14, -14, "end", 12),
    ]
    inset_markers = []
    for point_id, lines, dx, dy, anchor, size in inset_items:
        x, y = p_inset(point_id)
        inset_markers.append(draw_marker(point_id, x, y, 17 if point_id == "coex" else 12))
        inset_markers.append(draw_label(x + dx, y + dy, lines, anchor, size, 720))

    legend = [
        ("#111827", "主会场 / Venue"),
        ("#2563eb", "地铁入口 / Subway"),
        ("#0f766e", "活动区域 / Event zone"),
        ("#ea580c", "机场路线 / Airport route"),
        ("#4361ee", "晚间路线 / Evening route"),
    ]
    legend_chunks = []
    for i, (color, text) in enumerate(legend):
        y = 178 + i * 30
        legend_chunks.append(f'<circle cx="1078" cy="{y}" r="8" fill="{color}"/>')
        legend_chunks.append(f'<text x="1096" y="{y + 6}" font-size="18" font-weight="700" fill="#1f2937">{html.escape(text)}</text>')

    reading_lines = [
        ("到达 / Arrival", "ICN T1 -> AREX -> Line 9 -> COEX."),
        ("日常 / Daily", "Use Samseong Line 2 or Bongeunsa Line 9 for the venue."),
        ("晚间 / Evening", "Gangnam, Yeoksam, Dosan are the first dinner/social zones."),
        ("远端 / Optional", "Hongdae, Itaewon, Seongsu, Pangyo need larger buffers."),
    ]
    reading_chunks = []
    for i, (title, body) in enumerate(reading_lines):
        y = 705 + i * 48
        reading_chunks.append(f'<text x="1070" y="{y}" font-size="17" font-weight="850" fill="#111827">{html.escape(title)}</text>')
        reading_chunks.append(f'<text x="1070" y="{y + 23}" font-size="13.5" fill="#475569">{html.escape(body)}</text>')

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#f8fafc"/>
      <stop offset="1" stop-color="#eef6f3"/>
    </linearGradient>
    <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="12" stdDeviation="18" flood-color="#0f172a" flood-opacity="0.12"/>
    </filter>
  </defs>
  <style>
    text {{ font-family: "PingFang SC", "Noto Sans CJK SC", "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; letter-spacing: 0; }}
  </style>
  <rect width="100%" height="100%" fill="url(#bg)"/>
  <rect x="46" y="102" width="990" height="850" rx="28" fill="#ffffff" stroke="#dbe4ea" filter="url(#shadow)"/>
  <rect x="1048" y="102" width="500" height="850" rx="28" fill="#ffffff" stroke="#dbe4ea" filter="url(#shadow)"/>
  <path d="{han_path}" fill="none" stroke="#b9e4f2" stroke-width="48" stroke-linecap="round" opacity="0.85"/>
  <path d="{han_path}" fill="none" stroke="#7cc8dc" stroke-width="3" stroke-linecap="round" opacity="0.9"/>
  <text x="735" y="455" font-size="22" font-weight="800" fill="#3b82a0" opacity="0.72">汉江 / Han River</text>
  {''.join(overview_route_chunks)}
  {''.join(overview_markers)}
  <text x="62" y="58" font-size="36" font-weight="900" fill="#0f172a">ICML 2026 首尔逛会地图 / Seoul Conference Map</text>
  <text x="62" y="88" font-size="18" fill="#64748b">中文 + English；韩文仅作括号注释 / Chinese + English; Korean only in parentheses</text>
  <text x="78" y="142" font-size="20" font-weight="850" fill="#0f172a">区域总览 / City Overview</text>
  <text x="78" y="166" font-size="14.5" fill="#64748b">线条是规划示意，不替代实时导航 / Planning sketch, not live navigation</text>
  <text x="1065" y="147" font-size="28" font-weight="900" fill="#0f172a">图例 / Legend</text>
  {''.join(legend_chunks)}
  <text x="1065" y="318" font-size="22" font-weight="900" fill="#0f172a">COEX / 江南放大图</text>
  <text x="1065" y="342" font-size="14" fill="#64748b">COEX &amp; Gangnam inset</text>
  <rect x="1065" y="350" width="450" height="300" rx="18" fill="#f8fafc" stroke="#dbe4ea"/>
  <path d="M 1080 455 C 1150 430, 1240 410, 1510 384" fill="none" stroke="#b9e4f2" stroke-width="16" opacity="0.55"/>
  <text x="1360" y="393" font-size="12" font-weight="700" fill="#3b82a0">汉江 / Han River</text>
  {''.join(inset_route_chunks)}
  {''.join(inset_markers)}
  <text x="1065" y="680" font-size="22" font-weight="900" fill="#0f172a">推荐读法 / How to read</text>
  {''.join(reading_chunks)}
  <text x="78" y="918" font-size="14.5" fill="#64748b">Luma guests-only 活动只画公开区域；报名后用精确地址替换 / Obfuscated RSVP locations are drawn as public areas only.</text>
  <text x="1065" y="922" font-size="14" fill="#64748b">精确导航仍打开 Google Maps 链接 / Use Google Maps links for exact routing.</text>
</svg>'''


def build_leaflet_html(points: list[Point], routes: list[Route]) -> str:
    point_by_id = {point.id: point for point in points}
    points_json = json.dumps(
        [
            {
                **asdict(point),
                "label": label(point),
                "google_maps_url": maps_search_url(point.google_maps_query),
            }
            for point in points
        ],
        ensure_ascii=False,
    )
    routes_json = json.dumps(
        [
            {
                **asdict(route),
                "points": [[point_by_id[pid].latitude, point_by_id[pid].longitude] for pid in route.points],
                "label": route_label(route),
                "google_maps_url": maps_directions_url(route.google_maps_origin, route.google_maps_destination, route.travelmode),
            }
            for route in routes
        ],
        ensure_ascii=False,
    )
    return f'''<!doctype html>
<html lang="zh-Hans">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>ICML 2026 首尔地图 / Seoul Map</title>
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
  <style>
    html, body, #map {{ margin: 0; width: 100%; height: 100%; font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }}
    body {{ background: #f8fafc; }}
    #map {{ min-height: 100vh; }}
    .panel {{
      position: absolute; z-index: 500; top: 22px; left: 22px; width: 390px;
      background: rgba(255,255,255,.94); border: 1px solid #dbe4ea; border-radius: 18px;
      box-shadow: 0 18px 50px rgba(15,23,42,.16); padding: 20px 22px;
    }}
    .panel h1 {{ margin: 0 0 8px; font-size: 25px; line-height: 1.18; color: #0f172a; }}
    .panel p {{ margin: 0 0 14px; font-size: 14px; line-height: 1.45; color: #475569; }}
    .legend {{ display: grid; gap: 8px; font-size: 14px; color: #1f2937; }}
    .legend span {{ display: inline-flex; align-items: center; gap: 8px; }}
    .swatch {{ width: 12px; height: 12px; border-radius: 50%; display: inline-block; }}
    .leaflet-tooltip.label {{
      background: rgba(255,255,255,.92); color: #111827; border: 1px solid rgba(148,163,184,.55);
      border-radius: 10px; box-shadow: 0 6px 18px rgba(15,23,42,.12); padding: 5px 8px;
      font-weight: 700; font-size: 13px;
    }}
    .pin {{ width: 18px; height: 18px; border-radius: 50%; border: 3px solid white; box-shadow: 0 5px 14px rgba(15,23,42,.25); }}
    .popup h2 {{ margin: 0 0 6px; font-size: 16px; }}
    .popup p {{ margin: 0 0 8px; font-size: 13px; line-height: 1.4; color: #374151; }}
    .popup a {{ color: #2563eb; font-weight: 700; text-decoration: none; }}
  </style>
</head>
<body>
  <div id="map"></div>
  <section class="panel">
    <h1>ICML 2026 首尔逛会地图<br/>Seoul Conference Map</h1>
    <p>中文和英文为主，韩文仅作站名括注。<br/>Chinese and English first; Korean appears only as station-name notes.</p>
    <div class="legend">
      <span><i class="swatch" style="background:#111827"></i>主会场 / Venue</span>
      <span><i class="swatch" style="background:#2563eb"></i>地铁入口 / Subway</span>
      <span><i class="swatch" style="background:#0f766e"></i>活动区域 / Event zone</span>
      <span><i class="swatch" style="background:#ea580c"></i>机场路线 / Airport route</span>
      <span><i class="swatch" style="background:#4361ee"></i>晚间路线 / Evening route</span>
    </div>
  </section>
  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
  <script>
    const points = {points_json};
    const routes = {routes_json};
    const colors = {{
      venue: "#111827", station: "#2563eb", zone: "#0f766e", event: "#7c3aed",
      airport: "#ea580c", hotel: "#be123c", nearby: "#16a34a"
    }};
    const map = L.map("map", {{ zoomControl: false, attributionControl: true }}).setView([37.515, 127.02], 11);
    L.control.zoom({{ position: "bottomright" }}).addTo(map);
    L.tileLayer("https://{{s}}.basemaps.cartocdn.com/light_all/{{z}}/{{x}}/{{y}}{{r}}.png", {{
      maxZoom: 19,
      attribution: "&copy; OpenStreetMap contributors &copy; CARTO"
    }}).addTo(map);

    for (const route of routes) {{
      L.polyline(route.points, {{
        color: route.color,
        weight: route.category === "metro" ? 6 : 5,
        opacity: .82,
        dashArray: route.stroke_dasharray || null,
        lineJoin: "round"
      }}).addTo(map).bindTooltip(route.label, {{ sticky: true }});
    }}

    for (const point of points) {{
      const color = colors[point.category] || "#475569";
      const icon = L.divIcon({{
        className: "",
        html: `<div class="pin" style="background:${{color}}"></div>`,
        iconSize: [24, 24],
        iconAnchor: [12, 12]
      }});
      L.marker([point.latitude, point.longitude], {{ icon }}).addTo(map)
        .bindTooltip(point.label, {{ permanent: true, direction: "top", offset: [0, -12], className: "label" }})
        .bindPopup(`<div class="popup"><h2>${{point.label}}</h2><p>${{point.note_zh}}<br/>${{point.note_en}}</p><a href="${{point.google_maps_url}}" target="_blank">打开 Google Maps / Open Google Maps</a></div>`);
    }}
  </script>
</body>
</html>'''


def build_maplibre_html(points: list[Point], routes: list[Route]) -> str:
    point_by_id = {point.id: point for point in points}
    point_features = []
    for point in points:
        point_features.append(
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [point.longitude, point.latitude]},
                "properties": {
                    **asdict(point),
                    "label": label(point),
                    "google_maps_url": maps_search_url(point.google_maps_query),
                    "marker_color": marker_style(point.category)[0],
                    "rank": {
                        "venue": 1,
                        "station": 2,
                        "event": 3,
                        "zone": 4,
                        "airport": 5,
                        "hotel": 6,
                        "nearby": 7,
                    }.get(point.category, 9),
                },
            }
        )

    route_features = []
    for route in routes:
        route_features.append(
            {
                "type": "Feature",
                "geometry": {
                    "type": "LineString",
                    "coordinates": [
                        [point_by_id[point_id].longitude, point_by_id[point_id].latitude]
                        for point_id in route.points
                    ],
                },
                "properties": {
                    **asdict(route),
                    "points": " -> ".join(route.points),
                    "label": route_label(route),
                    "google_maps_url": maps_directions_url(
                        route.google_maps_origin,
                        route.google_maps_destination,
                        route.travelmode,
                    ),
                    "dash": route.stroke_dasharray,
                },
            }
        )

    points_geojson = json.dumps({"type": "FeatureCollection", "features": point_features}, ensure_ascii=False)
    routes_geojson = json.dumps({"type": "FeatureCollection", "features": route_features}, ensure_ascii=False)

    html_doc = '''<!doctype html>
<html lang="zh-Hans">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>ICML 2026 首尔地图 / Seoul Map</title>
  <link rel="stylesheet" href="https://unpkg.com/maplibre-gl@5.9.0/dist/maplibre-gl.css"/>
  <style>
    html, body, #map { margin: 0; width: 100%; height: 100%; overflow: hidden; font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }
    body { background: #f8fafc; }
    #map { min-height: 100vh; }
    .panel {
      position: absolute; z-index: 4; left: 10px; top: 10px; width: min(240px, calc(100% - 20px));
      overflow: hidden; background: rgba(255,255,255,.88); border: 1px solid rgba(203,213,225,.86);
      box-shadow: 0 14px 40px rgba(15,23,42,.12); border-radius: 12px; padding: 8px 9px;
      backdrop-filter: blur(12px);
    }
    .panel h1 { margin: 0 0 5px; font-size: 13px; line-height: 1.15; color: #0f172a; }
    .panel p { margin: 0 0 7px; font-size: 10.5px; line-height: 1.32; color: #475569; }
    .legend { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 5px 7px; font-size: 10px; color: #334155; }
    .legend span { display: inline-flex; align-items: center; gap: 5px; min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
    .swatch { width: 8px; height: 8px; border-radius: 50%; display: inline-block; flex: 0 0 auto; }
    .popup h2 { margin: 0 0 7px; font-size: 16px; color: #0f172a; }
    .popup p { margin: 0 0 9px; color: #475569; line-height: 1.42; }
    .popup a { color: #2563eb; text-decoration: none; font-weight: 800; }
    .maplibregl-popup-content { border-radius: 13px; box-shadow: 0 14px 35px rgba(15,23,42,.18); padding: 14px 16px; }
    body.is-focused .panel,
    body.is-focused .maplibregl-ctrl-bottom-left { display: none; }
  </style>
</head>
<body>
  <div id="map"></div>
  <section class="panel">
    <h1>ICML 2026 首尔逛会地图<br/>Seoul Conference Map</h1>
    <p>中文和英文为主，韩文仅作括号注释。<br/>Chinese and English first; Korean appears only in parentheses.</p>
    <div class="legend">
      <span><i class="swatch" style="background:#111827"></i>Venue</span>
      <span><i class="swatch" style="background:#2563eb"></i>Subway</span>
      <span><i class="swatch" style="background:#0f766e"></i>Zone</span>
      <span><i class="swatch" style="background:#7c3aed"></i>Event</span>
      <span><i class="swatch" style="background:#ea580c"></i>Airport</span>
      <span><i class="swatch" style="background:#4361ee"></i>Evening</span>
    </div>
  </section>
  <script src="https://unpkg.com/maplibre-gl@5.9.0/dist/maplibre-gl.js"></script>
  <script>
    const points = __POINTS_GEOJSON__;
    const routes = __ROUTES_GEOJSON__;
    const params = new URLSearchParams(window.location.search);
    const focus = params.get("focus") || "city";
    document.body.classList.toggle("is-focused", focus !== "city");

    const focusConfig = {
      airport: {
        pointIds: ["incheon_t1", "gimpo", "bongeunsa", "coex"],
        routeIds: ["arrival_icn", "line9_core"],
        bounds: [[126.36, 37.425], [127.18, 37.585]],
        compactPadding: { top: 18, left: 18, right: 28, bottom: 24 },
        padding: { top: 26, left: 32, right: 46, bottom: 32 },
        center: [126.75, 37.51],
        zoom: 9.45
      },
      coex: {
        pointIds: ["coex", "samseong", "bongeunsa", "parnas"],
        routeIds: ["line2_core", "line9_core"],
        bounds: [[127.055, 37.507], [127.065, 37.517]],
        compactPadding: { top: 18, left: 18, right: 28, bottom: 22 },
        padding: { top: 28, left: 36, right: 48, bottom: 32 },
        center: [127.060, 37.512],
        zoom: 15
      }
    };
    const activeConfig = focusConfig[focus] || null;
    function filteredCollection(collection, ids) {
      if (!ids) return collection;
      const idSet = new Set(ids);
      return { ...collection, features: collection.features.filter((feature) => idSet.has(feature.properties.id)) };
    }
    const visiblePoints = activeConfig ? filteredCollection(points, activeConfig.pointIds) : points;
    const visibleRoutes = activeConfig ? filteredCollection(routes, activeConfig.routeIds) : routes;
    window.icmlMapData = { focus, visiblePoints, visibleRoutes };

    const map = new maplibregl.Map({
      container: "map",
      center: activeConfig?.center || [127.015, 37.515],
      zoom: activeConfig?.zoom || 10.65,
      pitch: 0,
      bearing: 0,
      hash: false,
      style: {
        version: 8,
        glyphs: "https://demotiles.maplibre.org/font/{fontstack}/{range}.pbf",
        sources: {
          carto: {
            type: "raster",
            tiles: [
              "https://a.basemaps.cartocdn.com/light_all/{z}/{x}/{y}@2x.png",
              "https://b.basemaps.cartocdn.com/light_all/{z}/{x}/{y}@2x.png",
              "https://c.basemaps.cartocdn.com/light_all/{z}/{x}/{y}@2x.png"
            ],
            tileSize: 256,
            attribution: "© OpenStreetMap contributors © CARTO"
          }
        },
        layers: [
          { id: "background", type: "background", paint: { "background-color": "#eef4f7" } },
          { id: "carto", type: "raster", source: "carto", paint: { "raster-opacity": 0.88 } }
        ]
      }
    });
    window.icmlMap = map;
    map.addControl(new maplibregl.NavigationControl({ visualizePitch: false }), "bottom-right");

    function popupHtml(props) {
      return `<div class="popup"><h2>${props.label}</h2><p>${props.note_zh}<br/>${props.note_en}</p><a target="_blank" href="${props.google_maps_url}">打开 Google Maps / Open Google Maps</a></div>`;
    }

    map.on("load", () => {
      map.addSource("routes", { type: "geojson", data: visibleRoutes });
      map.addSource("points", { type: "geojson", data: visiblePoints });

      map.addLayer({
        id: "routes-glow",
        type: "line",
        source: "routes",
        paint: {
          "line-color": ["get", "color"],
          "line-width": ["case", ["==", ["get", "category"], "metro"], 10, 8],
          "line-opacity": 0.18,
          "line-blur": 4
        }
      });
      map.addLayer({
        id: "routes-line",
        type: "line",
        source: "routes",
        paint: {
          "line-color": ["get", "color"],
          "line-width": ["case", ["==", ["get", "category"], "metro"], 5.5, 4.5],
          "line-opacity": 0.84
        },
        layout: { "line-cap": "round", "line-join": "round" }
      });
      map.addLayer({
        id: "route-labels",
        type: "symbol",
        source: "routes",
        layout: {
          "symbol-placement": "line",
          "text-field": [
            "case",
            ["==", focus, "airport"],
            ["case", ["==", ["get", "id"], "arrival_icn"], "AREX", ["==", ["get", "id"], "line9_core"], "Line 9", ["get", "en"]],
            ["==", focus, "coex"],
            ["case", ["==", ["get", "id"], "line2_core"], "Line 2", ["==", ["get", "id"], "line9_core"], "Line 9", ["get", "en"]],
            ["get", "label"]
          ],
          "text-font": ["Noto Sans Regular"],
          "text-size": ["case", ["==", focus, "city"], 13, 11],
          "text-allow-overlap": false,
          "text-ignore-placement": false
        },
        paint: {
          "text-color": "#334155",
          "text-halo-color": "#ffffff",
          "text-halo-width": 3
        }
      });
      map.addLayer({
        id: "points-halo",
        type: "circle",
        source: "points",
        paint: {
          "circle-radius": ["case", ["==", ["get", "category"], "venue"], 15, 10],
          "circle-color": "#ffffff",
          "circle-opacity": 0.98
        }
      });
      map.addLayer({
        id: "points-circle",
        type: "circle",
        source: "points",
        paint: {
          "circle-radius": ["case", ["==", ["get", "category"], "venue"], 11, 7],
          "circle-color": ["get", "marker_color"],
          "circle-stroke-color": "#ffffff",
          "circle-stroke-width": 2
        }
      });
      map.addLayer({
        id: "point-labels",
        type: "symbol",
        source: "points",
        layout: {
          "text-field": [
            "case",
            ["==", focus, "airport"],
            ["case",
              ["==", ["get", "id"], "incheon_t1"], "ICN T1",
              ["==", ["get", "id"], "gimpo"], "Gimpo",
              ["==", ["get", "id"], "bongeunsa"], "Bongeunsa",
              ["==", ["get", "id"], "coex"], "COEX venue",
              ["get", "en"]
            ],
            ["==", focus, "coex"],
            ["case",
              ["==", ["get", "id"], "coex"], "COEX venue",
              ["==", ["get", "id"], "samseong"], "Samseong",
              ["==", ["get", "id"], "bongeunsa"], "Bongeunsa",
              ["==", ["get", "id"], "parnas"], "Parnas",
              ["get", "en"]
            ],
            ["get", "label"]
          ],
          "text-font": ["Noto Sans Bold"],
          "text-size": ["case", ["==", focus, "city"], ["case", ["==", ["get", "category"], "venue"], 15, 12], ["==", ["get", "category"], "venue"], 13, 10.5],
          "text-offset": [0, 1.25],
          "text-anchor": "top",
          "text-allow-overlap": false,
          "text-ignore-placement": false
        },
        paint: {
          "text-color": ["get", "marker_color"],
          "text-halo-color": "#ffffff",
          "text-halo-width": 3
        }
      });

      const compact = window.innerWidth < 520;
      const bounds = activeConfig?.bounds || [[126.41, 37.39], [127.16, 37.60]];
      const padding = activeConfig
        ? (compact ? activeConfig.compactPadding : activeConfig.padding)
        : (compact ? { top: 210, left: 24, right: 24, bottom: 96 } : { top: 40, left: 470, right: 60, bottom: 58 });
      map.fitBounds(bounds, { padding, duration: 0 });
    });

    map.on("click", "points-circle", (event) => {
      const feature = event.features[0];
      new maplibregl.Popup({ closeButton: true })
        .setLngLat(feature.geometry.coordinates)
        .setHTML(popupHtml(feature.properties))
        .addTo(map);
    });
    map.on("click", "routes-line", (event) => {
      const feature = event.features[0];
      new maplibregl.Popup({ closeButton: true })
        .setLngLat(event.lngLat)
        .setHTML(popupHtml(feature.properties))
        .addTo(map);
    });
    map.on("mouseenter", "points-circle", () => map.getCanvas().style.cursor = "pointer");
    map.on("mouseleave", "points-circle", () => map.getCanvas().style.cursor = "");
    map.on("mouseenter", "routes-line", () => map.getCanvas().style.cursor = "pointer");
    map.on("mouseleave", "routes-line", () => map.getCanvas().style.cursor = "");
  </script>
</body>
</html>'''

    return html_doc.replace("__POINTS_GEOJSON__", points_geojson).replace("__ROUTES_GEOJSON__", routes_geojson)


def render_with_chrome(source: Path, output: Path, window_size: str, timeout_seconds: int) -> str:
    chrome = os.environ.get("CHROME_BIN") or DEFAULT_CHROME
    if not Path(chrome).exists():
        return "chrome_missing"
    output.parent.mkdir(parents=True, exist_ok=True)
    url = source.resolve().as_uri()
    cmd = [
        chrome,
        "--headless=new",
        "--disable-gpu",
        "--enable-unsafe-swiftshader",
        "--use-gl=swiftshader",
        "--no-first-run",
        "--no-default-browser-check",
        f"--window-size={window_size}",
        "--hide-scrollbars",
        "--virtual-time-budget=8000",
        f"--screenshot={output}",
        url,
    ]
    try:
        result = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=timeout_seconds)
    except subprocess.TimeoutExpired:
        return "chrome_timeout"
    if result.returncode != 0:
        return f"chrome_exit_{result.returncode}"
    return "available" if output.exists() and output.stat().st_size > 100_000 else "too_small"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--render", action="store_true", help="Render SVG and Leaflet HTML to PNG with Chrome when available.")
    parser.add_argument("--timeout-seconds", type=int, default=45)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    points = build_points()
    routes = build_routes()

    MAP_DIR.mkdir(parents=True, exist_ok=True)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    SVG_OUT.write_text(build_svg(points, routes), encoding="utf-8")
    MAPLIBRE_OUT.write_text(build_maplibre_html(points, routes), encoding="utf-8")
    LEAFLET_OUT.write_text(build_leaflet_html(points, routes), encoding="utf-8")
    write_csv(POINTS_OUT, point_rows(points))
    write_csv(ROUTES_OUT, route_rows(routes))

    print(f"Wrote schematic SVG -> {SVG_OUT.relative_to(ROOT)}")
    print(f"Wrote MapLibre map -> {MAPLIBRE_OUT.relative_to(ROOT)}")
    print(f"Wrote Leaflet map -> {LEAFLET_OUT.relative_to(ROOT)}")
    print(f"Wrote {len(points)} visual points -> {POINTS_OUT.relative_to(ROOT)}")
    print(f"Wrote {len(routes)} visual routes -> {ROUTES_OUT.relative_to(ROOT)}")

    if args.render:
        svg_status = render_with_chrome(SVG_OUT, SVG_PNG_OUT, f"{WIDTH},{HEIGHT}", args.timeout_seconds)
        maplibre_status = render_with_chrome(MAPLIBRE_OUT, MAPLIBRE_PNG_OUT, "1600,1000", args.timeout_seconds)
        leaflet_status = render_with_chrome(LEAFLET_OUT, LEAFLET_PNG_OUT, "1600,1000", args.timeout_seconds)
        print(f"Rendered SVG PNG -> {SVG_PNG_OUT.relative_to(ROOT)} [{svg_status}]")
        print(f"Rendered MapLibre PNG -> {MAPLIBRE_PNG_OUT.relative_to(ROOT)} [{maplibre_status}]")
        print(f"Rendered Leaflet PNG -> {LEAFLET_PNG_OUT.relative_to(ROOT)} [{leaflet_status}]")


if __name__ == "__main__":
    main()
