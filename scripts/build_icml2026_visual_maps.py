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

COLOR_VENUE = "#111827"
COLOR_AREX = "#1d4ed8"
COLOR_LINE9 = "#b98200"
COLOR_LINE2 = "#00a84d"
COLOR_BUS = "#ea580c"
COLOR_MALL = "#0f766e"


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
        Point("coex_mall", "nearby", "COEX Mall", "Starfield COEX Mall", "스타필드 코엑스몰", 37.5110, 127.0607, "Starfield COEX Mall, Seoul", "COEX 地下补给主轴，吃饭、咖啡、雨天动线都在这里。", "Main underground supply zone for food, coffee, and rain-safe movement."),
        Point("starfield_library", "nearby", "星空图书馆", "Starfield Library", "별마당도서관", 37.5103, 127.0597, "Starfield Library, Seoul", "会场内好找的集合点和短休息点。", "Easy indoor landmark for meeting up and short breaks."),
        Point("coex_aquarium", "nearby", "COEX Aquarium", "SEA LIFE COEX Aquarium", "코엑스 아쿠아리움", 37.5121, 127.0577, "SEA LIFE COEX, Seoul", "雨天或空档时的室内备选。", "Indoor fallback for weather or awkward schedule gaps."),
        Point("bongeunsa_temple", "nearby", "奉恩寺", "Bongeunsa Temple", "봉은사", 37.5153, 127.0570, "Bongeunsa Temple, Seoul", "COEX 北侧安静短走点。", "Quiet short-walk option directly north of COEX."),
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
        Route("arrival_icn", "airport", "AREX 仁川 T1 到金浦", "AREX ICN T1 to Gimpo", ("incheon_t1", "gimpo"), COLOR_AREX, "", "Incheon Airport Terminal 1, 272 Gonghang-ro, Yeongjong-gu, Incheon", "Gimpo International Airport Station", "transit", "仁川 T1 先坐 AREX 到金浦机场换乘。", "Take AREX from ICN T1 to Gimpo Airport transfer."),
        Route("airport_bus_6103", "bus", "6103 机场大巴", "6103 airport limousine bus", ("incheon_t1", "coex"), COLOR_BUS, "9 7", "Incheon International Airport Terminal 1", "COEX City Airport Terminal, Seoul", "transit", "行李多时可考虑 6103 机场大巴直达 COEX / 三成一侧。", "With luggage, consider the 6103 airport bus directly to the COEX / Samseong side."),
        Route("line2_core", "metro", "Line 2 核心线", "Line 2 core", ("hongdae", "seongsu", "samseong", "gangnam"), COLOR_LINE2, "", "Samseong Station, Seoul", "Gangnam Station, Seoul", "transit", "会场到江南、圣水、弘大都可用 Line 2 作为主轴。", "Line 2 is the main axis for Gangnam, Seongsu, and Hongdae."),
        Route("line9_core", "metro", "Line 9 金浦到奉恩寺", "Line 9 Gimpo to Bongeunsa", ("gimpo", "bongeunsa", "coex"), COLOR_LINE9, "", "Gimpo International Airport Station", COEX_QUERY, "transit", "金浦换乘 Line 9 到奉恩寺站，7 号出口到 COEX。", "Transfer to Line 9 at Gimpo, ride to Bongeunsa, then walk to COEX."),
        Route("hotel_line2", "metro", "Line 2 酒店到三成", "Line 2 hotel to Samseong", ("provista", "samseong", "coex"), COLOR_LINE2, "", "Hotel Provista Seoul, 338 Seocho-daero, Seocho-gu, Seoul 06632", COEX_QUERY, "transit", "普罗威斯塔酒店从教大/Line 2 到三成，再步行到 COEX。", "From Provista, use Line 2 toward Samseong, then walk to COEX."),
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
        "venue": (COLOR_VENUE, "#ffffff"),
        "station": ("#475569", "#ffffff"),
        "zone": ("#0f766e", "#ffffff"),
        "event": ("#7c3aed", "#ffffff"),
        "airport": (COLOR_BUS, "#ffffff"),
        "hotel": ("#be123c", "#ffffff"),
        "nearby": (COLOR_MALL, "#ffffff"),
    }
    return styles.get(category, ("#475569", "#ffffff"))


def point_marker_color(point: Point) -> str:
    colors = {
        "coex": COLOR_VENUE,
        "gimpo": COLOR_AREX,
        "bongeunsa": COLOR_LINE9,
        "samseong": COLOR_LINE2,
        "coex_mall": COLOR_MALL,
        "starfield_library": COLOR_MALL,
        "coex_aquarium": COLOR_MALL,
        "bongeunsa_temple": COLOR_MALL,
    }
    return colors.get(point.id, marker_style(point.category)[0])


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
        f'stroke="{COLOR_AREX}" stroke-width="2" stroke-dasharray="8 6" opacity="0.48"/>'
    )

    inset_route_chunks = []
    inset_route_chunks.append(draw_route(route_path(("gangnam", "yeoksam", "samseong"), p_inset), "#2a9d8f", 7))
    inset_route_chunks.append(draw_route(route_path(("bongeunsa", "coex"), p_inset), COLOR_LINE9, 7))
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
        (COLOR_VENUE, "主会场 / Venue"),
        (COLOR_AREX, "AREX"),
        (COLOR_LINE9, "Line 9"),
        (COLOR_LINE2, "Line 2"),
        ("#0f766e", "活动区域 / Event zone"),
        (COLOR_BUS, "机场路线 / Airport route"),
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
      <span><i class="swatch" style="background:{COLOR_VENUE}"></i>主会场 / Venue</span>
      <span><i class="swatch" style="background:{COLOR_AREX}"></i>AREX</span>
      <span><i class="swatch" style="background:{COLOR_LINE9}"></i>Line 9</span>
      <span><i class="swatch" style="background:{COLOR_LINE2}"></i>Line 2</span>
      <span><i class="swatch" style="background:{COLOR_MALL}"></i>活动区域 / Event zone</span>
      <span><i class="swatch" style="background:{COLOR_BUS}"></i>机场路线 / Airport route</span>
      <span><i class="swatch" style="background:#4361ee"></i>晚间路线 / Evening route</span>
    </div>
  </section>
  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
  <script>
    const points = {points_json};
    const routes = {routes_json};
    const colors = {{
      venue: "{COLOR_VENUE}", station: "#475569", zone: "{COLOR_MALL}", event: "#7c3aed",
      airport: "{COLOR_BUS}", hotel: "#be123c", nearby: "{COLOR_MALL}"
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

    def lnglat(point_id: str) -> list[float]:
        point = point_by_id[point_id]
        return [point.longitude, point.latitude]

    schematic_route_coordinates = {
        "arrival_icn": [
            lnglat("incheon_t1"),
            [126.5150, 37.4620],
            [126.6150, 37.5050],
            [126.7050, 37.5480],
            lnglat("gimpo"),
        ],
        "line9_core": [
            lnglat("gimpo"),
            [126.8580, 37.5520],
            [126.9360, 37.5425],
            [127.0100, 37.5240],
            lnglat("bongeunsa"),
            lnglat("coex"),
        ],
        "airport_bus_6103": [
            lnglat("incheon_t1"),
            [126.5420, 37.4300],
            [126.6820, 37.4440],
            [126.8580, 37.4770],
            [127.0050, 37.5005],
            [127.0480, 37.5068],
            lnglat("coex"),
        ],
        "line2_core": [
            lnglat("hongdae"),
            [126.9800, 37.5565],
            lnglat("seongsu"),
            [127.0660, 37.5290],
            lnglat("samseong"),
            lnglat("gangnam"),
        ],
        "hotel_line2": [
            lnglat("provista"),
            [127.0310, 37.4945],
            lnglat("samseong"),
            lnglat("coex"),
        ],
        "evening_gangnam": [
            lnglat("coex"),
            [127.0525, 37.5215],
            lnglat("dosan"),
            lnglat("gfc"),
            lnglat("yeoksam"),
            lnglat("gangnam"),
        ],
        "itaewon": [
            lnglat("coex"),
            [127.0380, 37.5200],
            [127.0180, 37.5260],
            lnglat("itaewon"),
        ],
        "pangyo": [
            lnglat("coex"),
            [127.0750, 37.4800],
            [127.0970, 37.4300],
            lnglat("pangyo"),
        ],
    }
    route_map_colors = {
        "arrival_icn": COLOR_AREX,
        "line9_core": COLOR_LINE9,
        "airport_bus_6103": COLOR_BUS,
        "line2_core": COLOR_LINE2,
        "hotel_line2": COLOR_LINE2,
        "evening_gangnam": "#7c3aed",
        "itaewon": "#0f766e",
        "pangyo": "#64748b",
    }
    route_labels = {
        "arrival_icn": ("AREX · 约40分", "ICN T1 -> Gimpo", 1),
        "line9_core": ("Line 9 · 约50分", "Gimpo -> Bongeunsa", 1),
        "airport_bus_6103": ("6103 bus · 70-90分", "直达 COEX", 2),
        "line2_core": ("Line 2", "Seoul east-west conference axis", 2),
        "evening_gangnam": ("Gangnam/Yeoksam", "Evening events zone", 3),
        "itaewon": ("Itaewon", "Dinner/bar direction", 4),
        "pangyo": ("Pangyo", "Long offsite buffer", 4),
    }

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
                    "marker_color": point_marker_color(point),
                    "label_title": "",
                    "label_detail": "",
                    "label_priority": 9,
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
        title, detail, priority = route_labels.get(route.id, (route.zh, route.en, 9))
        route_features.append(
            {
                "type": "Feature",
                "geometry": {
                    "type": "LineString",
                    "coordinates": schematic_route_coordinates.get(route.id, [lnglat(point_id) for point_id in route.points]),
                },
                "properties": {
                    **asdict(route),
                    "points": " -> ".join(route.points),
                    "label": route_label(route),
                    "label_title": title,
                    "label_detail": detail,
                    "label_priority": priority,
                    "google_maps_url": maps_directions_url(
                        route.google_maps_origin,
                        route.google_maps_destination,
                        route.travelmode,
                    ),
                    "dash": route.stroke_dasharray,
                    "dashed": bool(route.stroke_dasharray),
                    "map_color": route_map_colors.get(route.id, route.color),
                },
            }
        )

    guide_geojson = json.dumps(
        {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "LineString",
                        "coordinates": [
                            [126.7600, 37.5450],
                            [126.8900, 37.5350],
                            [126.9850, 37.5260],
                            [127.0580, 37.5210],
                            [127.1500, 37.5230],
                        ],
                    },
                    "properties": {"id": "han_river", "kind": "water", "focuses": "city coex"},
                },
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [
                            [
                                [127.0550, 37.5084],
                                [127.0646, 37.5084],
                                [127.0646, 37.5160],
                                [127.0550, 37.5160],
                                [127.0550, 37.5084],
                            ]
                        ],
                    },
                    "properties": {"id": "coex_walk_zone", "kind": "zone", "focuses": "city coex airport"},
                },
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "LineString",
                        "coordinates": [
                            [126.4407, 37.4602],
                            [126.6200, 37.5040],
                            [126.7945, 37.5587],
                            [127.0602, 37.5142],
                            [127.0592, 37.5118],
                        ],
                    },
                    "properties": {"id": "arrival_corridor", "kind": "axis", "focuses": "airport city"},
                },
            ],
        },
        ensure_ascii=False,
    )
    metro_geojson = json.dumps(
        {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "LineString",
                        "coordinates": [
                            lnglat("incheon_t1"),
                            [126.5150, 37.4620],
                            [126.6150, 37.5050],
                            [126.7050, 37.5480],
                            lnglat("gimpo"),
                        ],
                    },
                    "properties": {
                        "id": "metro_arex",
                        "focuses": "airport city",
                        "label": "AREX · 约40分",
                        "detail": "ICN T1 -> Gimpo · 约 40 分钟",
                        "color": COLOR_AREX,
                    },
                },
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "LineString",
                        "coordinates": [
                            lnglat("gimpo"),
                            [126.8580, 37.5520],
                            [126.9360, 37.5425],
                            [127.0100, 37.5240],
                            lnglat("bongeunsa"),
                            [127.0750, 37.5140],
                        ],
                    },
                    "properties": {
                        "id": "metro_line9",
                        "focuses": "airport city",
                        "label": "Line 9 · 约50分",
                        "detail": "Gimpo -> Bongeunsa · 约 50 分钟",
                        "color": COLOR_LINE9,
                    },
                },
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "LineString",
                        "coordinates": [
                            [127.0240, 37.4975],
                            [127.0440, 37.5030],
                            lnglat("samseong"),
                            [127.0830, 37.5120],
                        ],
                    },
                    "properties": {
                        "id": "metro_line2",
                        "focuses": "city",
                        "label": "Line 2",
                        "detail": "Samseong Station side",
                        "color": COLOR_LINE2,
                    },
                },
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "LineString",
                        "coordinates": [
                            [127.0536, 37.5142],
                            lnglat("bongeunsa"),
                            [127.0666, 37.5142],
                        ],
                    },
                    "properties": {
                        "id": "metro_line9_coex",
                        "focuses": "coex",
                        "label": "Line 9 · 奉恩寺出口7",
                        "detail": "Bongeunsa Station Exit 7",
                        "color": COLOR_LINE9,
                    },
                },
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "LineString",
                        "coordinates": [
                            [127.0540, 37.5088],
                            lnglat("samseong"),
                            [127.0668, 37.5088],
                        ],
                    },
                    "properties": {
                        "id": "metro_line2_coex",
                        "focuses": "airport coex",
                        "label": "Line 2 · 三成出口5/6",
                        "detail": "Samseong Station Exit 5/6",
                        "color": COLOR_LINE2,
                    },
                },
            ],
        },
        ensure_ascii=False,
    )
    walk_geojson = json.dumps(
        {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "LineString",
                        "coordinates": [lnglat("bongeunsa"), [127.0598, 37.5132], lnglat("coex")],
                    },
                    "properties": {
                        "id": "walk_bongeunsa_coex",
                        "focuses": "airport coex",
                        "label": "奉恩寺站 -> COEX",
                        "label_title": "350m · 步行4-6分",
                        "note_zh": "Line 9 奉恩寺站 7 号出口到 COEX 北侧入口，约 350m。",
                        "note_en": "About 350 m from Bongeunsa Station Exit 7 to the north side of COEX.",
                        "google_maps_url": maps_directions_url("Bongeunsa Station Exit 7, Seoul", COEX_QUERY, "walking"),
                    },
                },
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "LineString",
                        "coordinates": [lnglat("samseong"), [127.0622, 37.5100], lnglat("coex")],
                    },
                    "properties": {
                        "id": "walk_samseong_coex",
                        "focuses": "coex",
                        "label": "三成站 -> COEX",
                        "label_title": "450m · 步行6-8分",
                        "note_zh": "Line 2 三成站 5/6 号出口到 COEX 东南侧，约 450m。",
                        "note_en": "About 450 m from Samseong Station exits 5/6 to the southeast side of COEX.",
                        "google_maps_url": maps_directions_url("Samseong Station Exit 5, Seoul", COEX_QUERY, "walking"),
                    },
                },
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "LineString",
                        "coordinates": [lnglat("coex"), lnglat("coex_mall"), lnglat("starfield_library")],
                    },
                    "properties": {
                        "id": "walk_coex_mall_library",
                        "focuses": "coex",
                        "label": "COEX -> Mall / Library",
                        "label_title": "150-250m · 室内2-4分",
                        "note_zh": "COEX、Mall、星空图书馆在同一地下/室内动线内，适合作为短休和集合点。",
                        "note_en": "COEX, the mall, and Starfield Library sit on the same indoor route.",
                        "google_maps_url": maps_search_url("Starfield Library, Seoul"),
                    },
                },
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "LineString",
                        "coordinates": [lnglat("coex"), [127.0578, 37.5133], lnglat("bongeunsa_temple")],
                    },
                    "properties": {
                        "id": "walk_coex_temple",
                        "focuses": "coex",
                        "label": "COEX -> 奉恩寺",
                        "label_title": "650m · 步行8-10分",
                        "note_zh": "从 COEX 北侧出去到奉恩寺，适合会议间隙短走。",
                        "note_en": "A quiet short walk north of COEX, useful between sessions.",
                        "google_maps_url": maps_directions_url(COEX_QUERY, "Bongeunsa Temple, Seoul", "walking"),
                    },
                },
            ],
        },
        ensure_ascii=False,
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
    html, body, #map { margin: 0; width: 100%; height: 100%; overflow: hidden; }
    body {
      background: #edf3f6;
      color: #111827;
      font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", sans-serif;
      letter-spacing: 0;
    }
    #map { min-height: 100vh; }
    .route-overlay {
      position: absolute;
      inset: 0;
      z-index: 2;
      width: 100%;
      height: 100%;
      pointer-events: none;
    }
    .panel, .notice, .fallback {
      position: absolute;
      z-index: 5;
      background: rgba(255,255,255,.94);
      border: 1px solid rgba(203,213,225,.9);
      box-shadow: 0 14px 36px rgba(15,23,42,.14);
      backdrop-filter: blur(12px);
    }
    .panel {
      left: 12px;
      top: 12px;
      width: min(270px, calc(100% - 24px));
      border-radius: 12px;
      padding: 10px 11px;
    }
    .panel h1 { margin: 0 0 6px; font-size: 14px; line-height: 1.2; }
    .panel p { margin: 0 0 8px; font-size: 11px; line-height: 1.35; color: #475569; }
    .legend { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 6px 8px; font-size: 10.5px; color: #334155; }
    .legend span { display: inline-flex; align-items: center; gap: 6px; min-width: 0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .swatch { width: 9px; height: 9px; border-radius: 50%; flex: 0 0 auto; }
    .pill-marker {
      width: var(--pill-width, 24px);
      height: 14px;
      display: flex;
      align-items: stretch;
      overflow: hidden;
      padding: 0;
      border: 1px solid rgba(255,255,255,.82);
      border-radius: 999px;
      background: transparent;
      box-shadow: 0 1px 4px rgba(15,23,42,.24);
      appearance: none;
      cursor: pointer;
    }
    .pill-marker span { flex: 1 1 0; min-width: 9px; background: var(--segment-color, #334155); }
    .pill-marker:focus-visible { outline: 2px solid rgba(37,99,235,.55); outline-offset: 2px; }
    .map-html-label,
    .map-route-label {
      border: 1px solid rgba(148,163,184,.5);
      background: rgba(255,255,255,.93);
      box-shadow: 0 7px 18px rgba(15,23,42,.15);
      color: var(--label-color, #111827);
      font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", sans-serif;
      letter-spacing: 0;
    }
    .map-html-label {
      display: grid;
      gap: 2px;
      max-width: 154px;
      padding: 5px 7px;
      border-radius: 9px;
      line-height: 1.08;
      cursor: pointer;
      pointer-events: auto;
    }
    .map-html-label strong {
      display: block;
      color: var(--label-color, #111827);
      font-size: 10.5px;
      font-weight: 900;
      white-space: nowrap;
    }
    .map-html-label span {
      display: block;
      color: #475569;
      font-size: 9px;
      font-weight: 750;
      white-space: nowrap;
    }
    .map-html-label.group strong { font-size: 10px; }
    .map-route-label {
      padding: 3px 7px;
      border-radius: 999px;
      font-size: 10px;
      font-weight: 900;
      line-height: 1;
      white-space: nowrap;
      pointer-events: none;
    }
    .notice {
      right: 10px;
      top: 10px;
      max-width: min(310px, calc(100% - 20px));
      border-radius: 10px;
      padding: 9px 11px;
      font-size: 11px;
      line-height: 1.35;
      color: #475569;
    }
    .notice strong { display: block; color: #111827; font-size: 12px; margin-bottom: 2px; }
    .notice a, .fallback a, .popup a { color: #2563eb; font-weight: 850; text-decoration: none; }
    .fallback {
      inset: 12px;
      z-index: 10;
      display: none;
      place-content: center;
      border-radius: 12px;
      padding: 18px;
      background:
        linear-gradient(90deg, rgba(37,99,235,.16), transparent 34%, rgba(22,163,74,.15) 66%, transparent),
        linear-gradient(#f8fafc, #eaf2f5);
    }
    .fallback-card {
      max-width: 410px;
      border-radius: 10px;
      border: 1px solid rgba(203,213,225,.95);
      background: rgba(255,255,255,.94);
      box-shadow: 0 18px 45px rgba(15,23,42,.16);
      padding: 18px;
    }
    .fallback h2 { margin: 0 0 8px; font-size: 18px; line-height: 1.2; }
    .fallback p { margin: 0 0 12px; color: #475569; font-size: 13px; line-height: 1.45; }
    .fallback-list { display: grid; gap: 7px; margin: 0 0 14px; padding: 0; list-style: none; font-size: 12px; color: #334155; }
    .popup h2 { margin: 0 0 7px; font-size: 16px; color: #0f172a; }
    .popup p { margin: 0 0 9px; color: #475569; line-height: 1.42; }
    .popup-list { display: grid; gap: 5px; margin: 0 0 10px; padding: 0; list-style: none; color: #475569; font-size: 12px; }
    .popup-list li { display: flex; align-items: center; gap: 7px; }
    .popup-list i { width: 9px; height: 9px; border-radius: 50%; flex: 0 0 auto; background: var(--item-color, #334155); }
    .maplibregl-popup-content { border-radius: 13px; box-shadow: 0 14px 35px rgba(15,23,42,.18); padding: 14px 16px; }
    .maplibregl-marker { z-index: 4; }
    .pill-marker { z-index: 5; }
    .map-html-label, .map-route-label { z-index: 6; }
    body.is-focused .panel, body.is-focused .maplibregl-ctrl-bottom-left { display: none; }
    body.has-map .fallback { display: none; }
    body.is-fallback .fallback { display: grid; }
    [hidden] { display: none !important; }
    @media (max-width: 520px) {
      .panel { left: 8px; top: 8px; width: min(235px, calc(100% - 16px)); padding: 8px 9px; }
      .panel h1 { font-size: 12.5px; }
      .panel p { display: none; }
      .legend { grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 4px 6px; font-size: 9.5px; }
      .notice { left: 8px; right: 8px; top: auto; bottom: 8px; max-width: none; }
      .map-html-label { max-width: 132px; padding: 4px 6px; }
      .map-html-label strong { font-size: 9.5px; }
      .map-html-label span { font-size: 8.2px; }
      .map-route-label { font-size: 8.5px; padding: 3px 5px; }
    }
  </style>
</head>
<body>
  <div id="map"></div>
  <svg id="routeOverlay" class="route-overlay" aria-hidden="true"></svg>
  <section class="panel" aria-label="Map legend">
    <h1>ICML 2026 首尔导览图<br/>Seoul Practical Map</h1>
    <p>路线是会议周导览示意，精确导航请打开 Google Maps。</p>
    <div class="legend">
      <span><i class="swatch" style="background:#111827"></i>Venue</span>
      <span><i class="swatch" style="background:#1d4ed8"></i>AREX</span>
      <span><i class="swatch" style="background:#b98200"></i>Line 9</span>
      <span><i class="swatch" style="background:#00a84d"></i>Line 2</span>
      <span><i class="swatch" style="background:#ea580c"></i>Bus</span>
      <span><i class="swatch" style="background:#0f766e"></i>Food/break</span>
      <span><i class="swatch" style="background:#7c3aed"></i>Event zone</span>
      <span><i class="swatch" style="background:#64748b"></i>Offsite</span>
    </div>
  </section>
  <div id="mapNotice" class="notice" hidden>
    <strong>地图底图加载不稳定</strong>
    点位和路线仍可用；如需实时导航，请打开 <a id="noticeLink" target="_blank" rel="noopener">Google Maps</a>。
  </div>
  <section id="fallback" class="fallback" aria-live="polite">
    <div class="fallback-card">
      <h2 id="fallbackTitle">地图暂时无法加载</h2>
      <p id="fallbackText">外部地图脚本或瓦片加载失败。这里保留会议周可用的路线摘要和 Google Maps 入口。</p>
      <ul id="fallbackList" class="fallback-list"></ul>
      <a id="fallbackLink" target="_blank" rel="noopener">打开 Google Maps / Open Google Maps</a>
    </div>
  </section>
  <script src="https://unpkg.com/maplibre-gl@5.9.0/dist/maplibre-gl.js" onerror="window.__maplibreLoadFailed = true"></script>
  <script>
    const points = __POINTS_GEOJSON__;
    const routes = __ROUTES_GEOJSON__;
    const guide = __GUIDE_GEOJSON__;
    const metroLines = __METRO_GEOJSON__;
    const walks = __WALK_GEOJSON__;
    const params = new URLSearchParams(window.location.search);
    const focus = params.get("focus") || "city";
    const isCompact = window.innerWidth < 560;
    document.body.classList.toggle("is-focused", focus !== "city");

    const fallbackLinks = {
      airport: "https://www.google.com/maps/dir/?api=1&origin=Incheon+Airport+Terminal+1&destination=COEX+Convention+%26+Exhibition+Center,+Seoul&travelmode=transit",
      coex: "https://www.google.com/maps/search/?api=1&query=COEX+Convention+%26+Exhibition+Center,+Seoul",
      city: "https://www.google.com/maps/search/?api=1&query=COEX+Convention+%26+Exhibition+Center,+Seoul"
    };

    const focusConfig = {
      airport: {
        pointIds: ["incheon_t1", "gimpo", "bongeunsa", "samseong", "coex"],
        labelIds: ["airport_icn", "airport_gimpo", "airport_seoul_cluster"],
        compactLabelIds: ["airport_icn", "airport_gimpo", "airport_seoul_cluster"],
        pillGroups: [
          { id: "airport_icn", ids: ["incheon_t1"], label: "仁川机场 T1\\nAREX 起点", coordinates: [126.4407, 37.4602], anchor: "top", offset: [0, 1.0] },
          { id: "airport_gimpo", ids: ["gimpo"], label: "金浦换乘\\nAREX → Line 9", coordinates: [126.7945, 37.5587], anchor: "top", offset: [0, 1.0], pxOffset: [0, -8] },
          { id: "airport_seoul_cluster", ids: ["coex", "bongeunsa", "samseong"], label: "COEX\\nLine 9 出口7\\nLine 2 出口5·6", coordinates: [127.0605, 37.5119], anchor: "top", offset: [0, 1.0], pxOffset: [-32, -30], segmentColors: ["#111827", "#b98200", "#00a84d"] }
        ],
        routeIds: ["arrival_icn", "line9_core", "airport_bus_6103"],
        bounds: [[126.365, 37.418], [127.080, 37.586]],
        padding: { top: 34, left: 38, right: 190, bottom: 40 },
        compactPadding: { top: 28, left: 18, right: 18, bottom: 34 },
        center: [126.748, 37.512],
        zoom: 9.2,
        fallbackItems: ["ICN T1 -> AREX -> Gimpo · 约 40 分钟", "Gimpo -> Line 9 -> Bongeunsa · 约 50 分钟", "Bongeunsa Exit 7 -> COEX · 约 350m / 4-6 分钟", "6103 bus direct · 约 70-90 分钟"]
      },
      coex: {
        pointIds: ["coex", "samseong", "bongeunsa", "coex_mall", "starfield_library", "coex_aquarium", "parnas", "bongeunsa_temple"],
        labelIds: ["coex_cluster", "samseong_parnas", "bongeunsa", "bongeunsa_temple"],
        compactLabelIds: ["coex_cluster", "samseong_parnas", "bongeunsa"],
        pillGroups: [
          { id: "coex_cluster", ids: ["coex", "coex_mall", "starfield_library", "coex_aquarium"], label: "COEX / Mall\\n会场+馆内动线", coordinates: [127.05955, 37.51128], anchor: "left", offset: [-1.05, 0], pxOffset: [-10, -16], segmentColors: ["#111827", "#0f766e", "#0f766e", "#0f766e"] },
          { id: "samseong_parnas", ids: ["samseong", "parnas"], label: "三成站 / Parnas\\nLine 2 · 出口5/6", coordinates: [127.06255, 37.50885], anchor: "bottom", offset: [0, -1.0], pxOffset: [-10, 10], segmentColors: ["#00a84d", "#be123c"] }
        ],
        routeIds: [],
        bounds: [[127.0540, 37.5071], [127.0647, 37.5162]],
        padding: { top: 34, left: 42, right: 48, bottom: 70 },
        compactPadding: { top: 34, left: 30, right: 30, bottom: 72 },
        center: [127.0599, 37.5120],
        zoom: 15.45,
        fallbackItems: ["Bongeunsa Exit 7 -> COEX · 约 350m / 4-6 分钟", "Samseong Exit 5/6 -> COEX · 约 450m / 6-8 分钟", "COEX -> Mall/星空图书馆 · 室内约 150-250m / 2-4 分钟", "COEX -> 奉恩寺 · 约 650m / 8-10 分钟"]
      },
      city: {
        pointIds: ["incheon_t1", "gimpo", "coex", "bongeunsa", "samseong", "gangnam", "dosan", "seongsu", "hongdae", "itaewon", "pangyo"],
        labelIds: ["coex", "gimpo", "gangnam", "seongsu", "hongdae", "itaewon", "pangyo"],
        compactLabelIds: ["coex", "gimpo", "gangnam", "seongsu"],
        routeIds: ["evening_gangnam", "itaewon", "pangyo"],
        bounds: [[126.405, 37.390], [127.158, 37.603]],
        padding: { top: 42, left: 316, right: 58, bottom: 52 },
        compactPadding: { top: 118, left: 22, right: 22, bottom: 64 },
        center: [127.010, 37.515],
        zoom: 10.25,
        fallbackItems: ["COEX is the conference anchor", "Gangnam/Yeoksam/Dosan are the close evening zones", "Hongdae, Itaewon, Seongsu, and Pangyo need larger buffers"]
      }
    };
    const activeConfig = focusConfig[focus] || focusConfig.city;

    function collectionByIds(collection, ids) {
      const idSet = new Set(ids);
      return { ...collection, features: collection.features.filter((feature) => idSet.has(feature.properties.id)) };
    }
    function guideForFocus() {
      return {
        ...guide,
        features: guide.features.filter((feature) => (feature.properties.focuses || "").split(" ").includes(focus))
      };
    }
    function focusFeatures(collection) {
      return {
        ...collection,
        features: collection.features.filter((feature) => (feature.properties.focuses || "").split(" ").includes(focus))
      };
    }
    const visiblePoints = collectionByIds(points, activeConfig.pointIds);
    const visibleRoutes = collectionByIds(routes, activeConfig.routeIds);
    const visibleMetro = focusFeatures(metroLines);
    const visibleWalks = focusFeatures(walks);
    const pointById = Object.fromEntries(points.features.map((feature) => [feature.properties.id, feature]));
    const groupedPointIds = new Set((activeConfig.pillGroups || []).flatMap((group) => group.ids));
    const pillMarkers = { type: "FeatureCollection", features: (activeConfig.pillGroups || []).map((group, index) => {
      const members = group.ids.map((id) => pointById[id]).filter(Boolean);
      return {
        type: "Feature",
        geometry: { type: "Point", coordinates: group.coordinates },
        properties: {
          id: group.id,
          label: group.label.replace("\\n", " / "),
          map_label: group.label,
          category: "group",
          marker_color: "#111827",
          label_anchor: group.anchor || "top",
          label_offset: group.offset || [0, 1.0],
          label_px_offset: group.pxOffset || [0, 0],
          label_rank: index + 1,
          google_maps_url: members[0]?.properties.google_maps_url || fallbackLinks[focus] || fallbackLinks.city,
          members: members.map((feature, memberIndex) => ({
            id: feature.properties.id,
            label: feature.properties.label,
            color: group.segmentColors?.[memberIndex] || feature.properties.marker_color,
            note_zh: feature.properties.note_zh,
            note_en: feature.properties.note_en,
            google_maps_url: feature.properties.google_maps_url
          }))
        }
      };
    })};
    const labelIds = isCompact ? activeConfig.compactLabelIds : activeConfig.labelIds;
    const pointLabelFeatures = collectionByIds(points, labelIds).features
      .filter((feature) => !groupedPointIds.has(feature.properties.id))
      .map((feature, index) => ({
        ...feature,
        properties: {
          ...feature.properties,
          label_rank: index + 20,
          map_label: pointLabel(feature.properties, focus),
          label_anchor: labelAnchor(feature.properties),
          label_offset: labelOffset(feature.properties),
          label_px_offset: labelPixelOffset(feature.properties)
        }
      }));
    const pillLabelFeatures = pillMarkers.features.filter((feature) => labelIds.includes(feature.properties.id));
    const labelPoints = [...pillLabelFeatures, ...pointLabelFeatures];
    const pointLabels = { type: "FeatureCollection", features: labelPoints };
    const visiblePointMarkers = { ...visiblePoints, features: visiblePoints.features.filter((feature) => !groupedPointIds.has(feature.properties.id)) };
    window.icmlMapData = { focus, visiblePoints, visiblePointMarkers, visibleRoutes, visibleMetro, visibleWalks, pointLabels, pillMarkers };

    document.getElementById("noticeLink").href = fallbackLinks[focus] || fallbackLinks.city;
    document.getElementById("fallbackLink").href = fallbackLinks[focus] || fallbackLinks.city;
    document.getElementById("fallbackList").replaceChildren(...activeConfig.fallbackItems.map((item) => {
      const li = document.createElement("li");
      li.textContent = item;
      return li;
    }));

    function pointLabel(props, mode) {
      const labels = {
        coex: "COEX 会场\\nVenue",
        incheon_t1: "仁川机场 T1\\nICN T1",
        gimpo: "金浦换乘\\nGimpo transfer",
        bongeunsa: "奉恩寺站\\nLine 9 · 出口7",
        samseong: "三成站\\nLine 2 · 出口5/6",
        coex_mall: "COEX Mall\\n星空图书馆方向",
        starfield_library: "星空图书馆\\nStarfield Library",
        bongeunsa_temple: "奉恩寺\\nTemple",
        gangnam: "江南站\\nGangnam",
        dosan: "岛山/清潭\\nDinner zone",
        seongsu: "圣水\\nSeongsu",
        hongdae: "弘大\\nHongdae",
        itaewon: "梨泰院\\nItaewon",
        pangyo: "板桥\\nPangyo"
      };
      return labels[props.id] || `${props.zh}\\n${props.en}`;
    }
    function labelAnchor(props) {
      const anchors = {
        bongeunsa: "right",
        bongeunsa_temple: "right",
        coex: "left",
        gimpo: "top",
        gangnam: "bottom",
        seongsu: "top",
        hongdae: "top",
        itaewon: "bottom",
        pangyo: "bottom"
      };
      return props.label_anchor || anchors[props.id] || "top";
    }
    function labelOffset(props) {
      const offsets = {
        bongeunsa: [1.0, 0],
        bongeunsa_temple: [1.0, 0],
        coex: [-1.05, 0],
        gimpo: [0, 1.0],
        gangnam: [0, -1.0],
        seongsu: [0, 1.0],
        hongdae: [0, 1.0],
        itaewon: [0, -1.0],
        pangyo: [0, -1.0]
      };
      return props.label_offset || offsets[props.id] || [0, 1.0];
    }
    function labelPixelOffset(props) {
      const offsets = {
        bongeunsa: focus === "coex" ? [30, -28] : [0, -10],
        samseong: focus === "coex" ? [-10, 18] : [0, 0],
        coex: focus === "airport" ? [-18, -24] : [-10, -16],
      };
      return offsets[props.id] || [0, 0];
    }

    function escapeHtml(value = "") {
      return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;");
    }
    function labelColor(props) {
      return props.marker_color || props.color || props.map_color || "#111827";
    }
    function labelLines(text = "") {
      return String(text || "").split("\\n").map((line) => line.trim()).filter(Boolean);
    }
    function htmlLabelElement(feature) {
      const props = feature.properties || {};
      const lines = labelLines(props.map_label || props.label);
      const node = document.createElement("button");
      node.type = "button";
      node.className = `map-html-label ${props.category || ""}`;
      node.style.setProperty("--label-color", labelColor(props));
      node.setAttribute("aria-label", lines.join(" / "));
      node.innerHTML = `<strong>${escapeHtml(lines[0] || props.label || "")}</strong>${lines.slice(1, 3).map((line) => `<span>${escapeHtml(line)}</span>`).join("")}`;
      return node;
    }
    function domAnchorForTextAnchor(anchor = "top", pxOffset = [0, 0]) {
      const map = {
        left: ["right", [-12, 0]],
        right: ["left", [12, 0]],
        top: ["bottom", [0, -12]],
        bottom: ["top", [0, 12]],
      };
      const [domAnchor, baseOffset] = map[anchor] || ["bottom", [0, -12]];
      return [domAnchor, [baseOffset[0] + (pxOffset[0] || 0), baseOffset[1] + (pxOffset[1] || 0)]];
    }
    function addHtmlLabels(map) {
      if (window.__icmlHtmlLabelsAdded) return;
      window.__icmlHtmlLabelsAdded = true;
      for (const feature of pointLabels.features) {
        const props = feature.properties || {};
        const node = htmlLabelElement(feature);
        const [anchor, offset] = domAnchorForTextAnchor(props.label_anchor, props.label_px_offset);
        node.addEventListener("click", () => {
          const html = props.members ? pillPopupHtml(props) : popupHtml(props);
          new maplibregl.Popup({ closeButton: true })
            .setLngLat(feature.geometry.coordinates)
            .setHTML(html)
            .addTo(map);
        });
        new maplibregl.Marker({ element: node, anchor, offset })
          .setLngLat(feature.geometry.coordinates)
          .addTo(map);
      }
    }
    function lineMidpoint(coordinates = []) {
      if (!coordinates.length) return null;
      return coordinates[Math.floor((coordinates.length - 1) / 2)];
    }
    function routeLabelElement(feature, kind) {
      const props = feature.properties || {};
      const node = document.createElement("div");
      node.className = `map-route-label ${kind}`;
      node.style.setProperty("--label-color", props.color || props.map_color || "#334155");
      const compactLabels = {
        metro_arex: "AREX",
        metro_line9: "Line 9",
        metro_line2: "Line 2",
        metro_line9_coex: "L9 出口7",
        metro_line2_coex: "L2 出口5/6",
        airport_bus_6103: "6103",
        walk_bongeunsa_coex: "350m",
        walk_samseong_coex: "450m",
        walk_coex_mall_library: "Mall",
        walk_coex_temple: "650m",
      };
      node.textContent = isCompact && compactLabels[props.id] ? compactLabels[props.id] : props.label_title || props.label || "";
      return node;
    }
    function overlayRouteFeatures() {
      const metroRouteIds = new Set(["arrival_icn", "line2_core", "line9_core", "hotel_line2"]);
      return [
        ...visibleMetro.features.map((feature) => ({ feature, kind: "metro", width: focus === "coex" ? 7 : 6, casing: focus === "coex" ? 12 : 11 })),
        ...visibleRoutes.features
          .filter((feature) => !metroRouteIds.has(feature.properties.id))
          .map((feature) => ({ feature, kind: feature.properties.category || "route", width: feature.properties.dashed ? 5 : 5.5, casing: 10 })),
        ...visibleWalks.features.map((feature) => ({ feature, kind: "walk", width: focus === "coex" ? 3.2 : 2.6, casing: focus === "coex" ? 7 : 6 })),
      ];
    }
    function addRouteLabels(map) {
      if (window.__icmlRouteLabelsAdded) return;
      window.__icmlRouteLabelsAdded = true;
      const items = overlayRouteFeatures()
        .filter(({ feature, kind }) => kind !== "walk" || focus === "coex")
        .filter(({ feature }) => !(focus === "airport" && feature.properties.id === "metro_line2_coex"))
        .filter(({ feature }) => feature.properties.label_title || feature.properties.label);
      for (const { feature, kind } of items) {
        const midpoint = lineMidpoint(feature.geometry.coordinates);
        if (!midpoint) continue;
        const node = routeLabelElement(feature, kind);
        new maplibregl.Marker({ element: node, anchor: "center" })
          .setLngLat(midpoint)
          .addTo(map);
      }
    }
    function setupRouteOverlay(map) {
      const overlay = document.getElementById("routeOverlay");
      if (!overlay || window.__icmlRouteOverlayReady) return;
      window.__icmlRouteOverlayReady = true;
      const ns = "http://www.w3.org/2000/svg";
      let frame = 0;
      function drawPolyline(line, className, color, width, opacity, dash) {
        const points = line.feature.geometry.coordinates
          .map((coord) => map.project(coord))
          .map((point) => `${point.x.toFixed(1)},${point.y.toFixed(1)}`)
          .join(" ");
        const node = document.createElementNS(ns, "polyline");
        node.setAttribute("points", points);
        node.setAttribute("fill", "none");
        node.setAttribute("stroke", color);
        node.setAttribute("stroke-width", String(width));
        node.setAttribute("stroke-linecap", "round");
        node.setAttribute("stroke-linejoin", "round");
        node.setAttribute("opacity", String(opacity));
        node.setAttribute("class", className);
        if (dash) node.setAttribute("stroke-dasharray", dash);
        overlay.append(node);
      }
      function render() {
        frame = 0;
        overlay.setAttribute("viewBox", `0 0 ${window.innerWidth} ${window.innerHeight}`);
        overlay.replaceChildren();
        const lines = overlayRouteFeatures();
        window.__icmlRouteOverlayCount = lines.length;
        for (const line of lines) {
          const props = line.feature.properties || {};
          const color = props.color || props.map_color || "#334155";
          const dash = props.dashed || line.kind === "walk" ? (line.kind === "walk" ? "4 4" : "9 7") : "";
          drawPolyline(line, `route-casing ${line.kind}`, "#ffffff", line.casing, line.kind === "walk" ? 0.8 : 0.88, dash);
        }
        for (const line of lines) {
          const props = line.feature.properties || {};
          const color = props.color || props.map_color || "#334155";
          const dash = props.dashed || line.kind === "walk" ? (line.kind === "walk" ? "4 4" : "9 7") : "";
          drawPolyline(line, `route-line ${line.kind}`, color, line.width, line.kind === "walk" ? 0.9 : 0.96, dash);
        }
      }
      function requestRender() {
        if (frame) return;
        frame = window.requestAnimationFrame(render);
      }
      map.on("move", requestRender);
      map.on("zoom", requestRender);
      map.on("resize", requestRender);
      map.on("moveend", requestRender);
      render();
    }

    function popupHtml(props) {
      return `<div class="popup"><h2>${props.label}</h2><p>${props.note_zh || ""}<br/>${props.note_en || ""}</p><a target="_blank" rel="noopener" href="${props.google_maps_url}">打开 Google Maps / Open Google Maps</a></div>`;
    }
    function pillPopupHtml(props) {
      const items = (props.members || []).map((member) => {
        const note = member.note_zh ? ` · ${member.note_zh}` : "";
        return `<li><i style="--item-color:${member.color}"></i><span>${member.label}${note}</span></li>`;
      }).join("");
      return `<div class="popup"><h2>${props.label}</h2><ul class="popup-list">${items}</ul><a target="_blank" rel="noopener" href="${props.google_maps_url}">打开 Google Maps / Open Google Maps</a></div>`;
    }
    function addPillMarkers(map) {
      for (const feature of pillMarkers.features) {
        const members = feature.properties.members || [];
        if (!members.length) continue;
        const node = document.createElement("button");
        node.className = "pill-marker";
        node.type = "button";
        node.setAttribute("aria-label", feature.properties.label);
        node.style.setProperty("--pill-width", `${Math.max(2, members.length) * 12}px`);
        for (const member of members) {
          const segment = document.createElement("span");
          segment.style.setProperty("--segment-color", member.color);
          node.append(segment);
        }
        node.addEventListener("click", () => {
          new maplibregl.Popup({ closeButton: true })
            .setLngLat(feature.geometry.coordinates)
            .setHTML(pillPopupHtml(feature.properties))
            .addTo(map);
        });
        new maplibregl.Marker({ element: node, anchor: "center" })
          .setLngLat(feature.geometry.coordinates)
          .addTo(map);
      }
    }
    function fallbackMode(title) {
      document.body.classList.add("is-fallback");
      document.getElementById("fallbackTitle").textContent = title;
    }
    function showTileNotice() {
      document.getElementById("mapNotice").hidden = false;
    }
    if (window.__maplibreLoadFailed || !window.maplibregl) {
      fallbackMode("地图脚本加载失败");
    } else {
      const map = new maplibregl.Map({
        container: "map",
        center: activeConfig.center,
        zoom: activeConfig.zoom,
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
            { id: "background", type: "background", paint: { "background-color": "#eaf2f5" } },
            { id: "carto", type: "raster", source: "carto", paint: { "raster-opacity": 0.62, "raster-saturation": -0.82, "raster-contrast": -0.08 } }
          ]
        }
      });
      window.icmlMap = map;
      map.addControl(new maplibregl.NavigationControl({ visualizePitch: false }), focus === "city" ? "bottom-right" : "top-left");
      let resourceErrorCount = 0;
      map.on("error", (event) => {
        const message = String(event?.error?.message || "");
        if (/tile|glyph|resource|network|ajax|Failed/i.test(message)) {
          resourceErrorCount += 1;
          if (document.body.classList.contains("has-map") && resourceErrorCount >= 8) showTileNotice();
        }
      });
      window.setTimeout(() => {
        if (!document.body.classList.contains("has-map")) fallbackMode("地图资源加载超时");
      }, 30000);

      function initializeLayers() {
        if (window.__icmlMapInitialized) return;
        if (!map.isStyleLoaded()) return;
        window.__icmlMapInitialized = true;
        document.body.classList.add("has-map");
        map.addSource("guide", { type: "geojson", data: guideForFocus() });
        map.addSource("metro", { type: "geojson", data: visibleMetro });
        map.addSource("walks", { type: "geojson", data: visibleWalks });
        map.addSource("routes", { type: "geojson", data: visibleRoutes });
        map.addSource("points", { type: "geojson", data: visiblePointMarkers });
        map.addSource("point-labels", { type: "geojson", data: pointLabels });

        map.addLayer({
          id: "guide-zone",
          type: "fill",
          source: "guide",
          filter: ["==", ["get", "kind"], "zone"],
          paint: { "fill-color": "#dbeafe", "fill-opacity": focus === "coex" ? 0.25 : 0.16 }
        });
        map.addLayer({
          id: "guide-water",
          type: "line",
          source: "guide",
          filter: ["==", ["get", "kind"], "water"],
          paint: {
            "line-color": "#7cc8dc",
            "line-opacity": focus === "city" ? 0.34 : 0.2,
            "line-width": focus === "city" ? 18 : 10,
            "line-blur": 1.5
          },
          layout: { "line-cap": "round", "line-join": "round" }
        });
        map.addLayer({
          id: "guide-axis",
          type: "line",
          source: "guide",
          filter: ["==", ["get", "kind"], "axis"],
          paint: { "line-color": "#94a3b8", "line-opacity": 0.18, "line-width": 10, "line-blur": 3 },
          layout: { "line-cap": "round", "line-join": "round" }
        });
        map.addLayer({
          id: "metro-line-casing",
          type: "line",
          source: "metro",
          paint: {
            "line-color": "#ffffff",
            "line-opacity": focus === "coex" ? 0.86 : 0.58,
            "line-width": focus === "coex" ? 11 : 11
          },
          layout: { "line-cap": "round", "line-join": "round" }
        });
        map.addLayer({
          id: "metro-lines",
          type: "line",
          source: "metro",
          paint: {
            "line-color": ["get", "color"],
            "line-opacity": focus === "coex" ? 0.98 : 0.88,
            "line-width": focus === "coex" ? 5.8 : 5.2
          },
          layout: { "line-cap": "round", "line-join": "round" }
        });
        map.addLayer({
          id: "metro-labels",
          type: "symbol",
          source: "metro",
          layout: {
            "symbol-placement": "line-center",
            "text-field": ["get", "label"],
            "text-font": ["Open Sans Semibold", "Arial Unicode MS Bold"],
            "text-size": focus === "coex" ? 12 : 12,
            "text-allow-overlap": true,
            "text-ignore-placement": true
          },
          paint: {
            "text-color": ["get", "color"],
            "text-halo-color": "rgba(255,255,255,.72)",
            "text-halo-width": 1.2
          }
        });
        map.addLayer({
          id: "routes-glow",
          type: "line",
          source: "routes",
          paint: {
            "line-color": ["coalesce", ["get", "map_color"], ["get", "color"]],
            "line-width": focus === "airport" ? 12 : 8,
            "line-opacity": focus === "airport" ? 0.16 : 0.14,
            "line-blur": 3.5
          },
          layout: { "line-cap": "round", "line-join": "round" }
        });
        map.addLayer({
          id: "routes-line-solid",
          type: "line",
          source: "routes",
          filter: ["!=", ["get", "dashed"], true],
          paint: {
            "line-color": ["coalesce", ["get", "map_color"], ["get", "color"]],
            "line-width": focus === "airport" ? 4.8 : 4.2,
            "line-opacity": focus === "airport" ? 0.78 : 0.72
          },
          layout: { "line-cap": "round", "line-join": "round" }
        });
        map.addLayer({
          id: "routes-line-dashed",
          type: "line",
          source: "routes",
          filter: ["==", ["get", "dashed"], true],
          paint: {
            "line-color": ["coalesce", ["get", "map_color"], ["get", "color"]],
            "line-width": focus === "airport" ? 4.6 : 4.2,
            "line-opacity": 0.88,
            "line-dasharray": [1.2, 1.1]
          },
          layout: { "line-cap": "round", "line-join": "round" }
        });
        map.addLayer({
          id: "route-labels",
          type: "symbol",
          source: "routes",
          filter: focus === "airport" ? ["!=", ["get", "category"], "metro"] : ["has", "label_title"],
          layout: {
            "symbol-placement": "line-center",
            "text-field": ["get", "label_title"],
            "text-font": ["Open Sans Semibold", "Arial Unicode MS Bold"],
            "text-size": focus === "airport" ? 11 : 10.5,
            "text-allow-overlap": true,
            "text-ignore-placement": true,
            "symbol-sort-key": ["get", "label_priority"]
          },
          paint: { "text-color": "#334155", "text-halo-color": "rgba(255,255,255,.68)", "text-halo-width": 1.2 }
        });
        map.addLayer({
          id: "walk-lines",
          type: "line",
          source: "walks",
          paint: {
            "line-color": "#475569",
            "line-opacity": 0.86,
            "line-width": focus === "coex" ? 2.8 : 2,
            "line-dasharray": [1, 1.1]
          },
          layout: { "line-cap": "round", "line-join": "round" }
        });
        map.addLayer({
          id: "walk-labels",
          type: "symbol",
          source: "walks",
          layout: {
            "symbol-placement": "line-center",
            "text-field": ["get", "label_title"],
            "text-font": ["Open Sans Semibold", "Arial Unicode MS Bold"],
            "text-size": isCompact ? 10 : 11.5,
            "text-allow-overlap": true,
            "text-ignore-placement": true
          },
          paint: {
            "text-color": "#334155",
            "text-halo-color": "rgba(255,255,255,.72)",
            "text-halo-width": 1.1
          }
        });
        map.addLayer({
          id: "points-halo",
          type: "circle",
          source: "points",
          paint: {
            "circle-radius": ["case", ["==", ["get", "category"], "venue"], 15, ["==", ["get", "category"], "station"], 11, 9],
            "circle-color": "#ffffff",
            "circle-opacity": 0.62
          }
        });
        map.addLayer({
          id: "points-circle",
          type: "circle",
          source: "points",
          paint: {
            "circle-radius": ["case", ["==", ["get", "category"], "venue"], 10, ["==", ["get", "category"], "station"], 7.5, 6.5],
            "circle-color": ["get", "marker_color"],
            "circle-stroke-color": "#ffffff",
            "circle-stroke-width": 1
          }
        });
        map.addLayer({
          id: "point-symbol-labels",
          type: "symbol",
          source: "point-labels",
          layout: {
            "text-field": ["get", "map_label"],
            "text-font": ["Open Sans Semibold", "Arial Unicode MS Bold"],
            "text-size": ["case", ["==", ["get", "category"], "venue"], 12, 10.5],
            "text-line-height": 1.05,
            "text-anchor": ["get", "label_anchor"],
            "text-offset": ["get", "label_offset"],
            "text-allow-overlap": true,
            "text-ignore-placement": true,
            "symbol-sort-key": ["get", "label_rank"]
          },
          paint: {
            "text-color": ["case", ["==", ["get", "category"], "venue"], "#111827", ["coalesce", ["get", "marker_color"], "#111827"]],
            "text-halo-color": "rgba(255,255,255,.68)",
            "text-halo-width": 1.2
          }
        });

        map.fitBounds(activeConfig.bounds, {
          padding: isCompact ? activeConfig.compactPadding : activeConfig.padding,
          duration: 0
        });
        addPillMarkers(map);
        setupRouteOverlay(map);
        addHtmlLabels(map);
        addRouteLabels(map);

        map.on("click", "points-circle", (event) => openPopup("points-circle", event));
        map.on("click", "routes-line-solid", (event) => openPopup("routes-line-solid", event));
        map.on("click", "routes-line-dashed", (event) => openPopup("routes-line-dashed", event));
        map.on("click", "walk-lines", (event) => openPopup("walk-lines", event));
        ["points-circle", "routes-line-solid", "routes-line-dashed", "walk-lines"].forEach((layerId) => {
          map.on("mouseenter", layerId, () => map.getCanvas().style.cursor = "pointer");
          map.on("mouseleave", layerId, () => map.getCanvas().style.cursor = "");
        });
      }

      function openPopup(layerId, event) {
        const feature = event.features && event.features[0];
        if (!feature) return;
        new maplibregl.Popup({ closeButton: true })
          .setLngLat(event.lngLat || feature.geometry.coordinates)
          .setHTML(popupHtml(feature.properties))
          .addTo(map);
      }
      map.on("style.load", initializeLayers);
      map.on("load", initializeLayers);
      window.setTimeout(initializeLayers, 1800);
    }
  </script>
</body>
</html>'''

    return (
        html_doc.replace("__POINTS_GEOJSON__", points_geojson)
        .replace("__ROUTES_GEOJSON__", routes_geojson)
        .replace("__GUIDE_GEOJSON__", guide_geojson)
        .replace("__METRO_GEOJSON__", metro_geojson)
        .replace("__WALK_GEOJSON__", walk_geojson)
    )


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
