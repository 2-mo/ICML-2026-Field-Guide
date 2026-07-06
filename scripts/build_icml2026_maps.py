#!/usr/bin/env python3
"""Build Google Maps links, transport notes, and nearby picks for ICML 2026."""

from __future__ import annotations

import csv
from dataclasses import asdict, dataclass
from pathlib import Path
from urllib.parse import quote_plus, urlencode


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "data" / "processed"

PLACES_OUT = OUT_DIR / "icml2026_map_places.csv"
ROUTES_OUT = OUT_DIR / "icml2026_route_links.csv"
TRANSPORT_OUT = OUT_DIR / "icml2026_transport.csv"
NEARBY_OUT = OUT_DIR / "icml2026_nearby_picks.csv"
SCREENSHOT_TARGETS_OUT = OUT_DIR / "icml2026_google_maps_screenshot_targets.csv"

GOOGLE_MAPS_SEARCH = "https://www.google.com/maps/search/?api=1"
GOOGLE_MAPS_DIRECTIONS = "https://www.google.com/maps/dir/?api=1"

COEX_QUERY = "COEX Convention & Exhibition Center, 513 Yeongdong-daero, Gangnam-gu, Seoul"


@dataclass(frozen=True)
class Place:
    group: str
    name: str
    maps_query: str
    latitude: str = ""
    longitude: str = ""
    confidence: str = "google_maps_query"
    source: str = "Google Maps user-facing place query"
    notes: str = ""


@dataclass(frozen=True)
class Route:
    group: str
    name: str
    origin: str
    destination: str
    travelmode: str
    why: str
    source: str
    notes: str = ""


@dataclass(frozen=True)
class Transport:
    group: str
    route: str
    recommended_for: str
    official_note: str
    google_maps_origin: str
    google_maps_destination: str
    google_maps_travelmode: str
    source: str
    caveat: str


@dataclass(frozen=True)
class NearbyPick:
    zone: str
    name: str
    kind: str
    when_to_go: str
    from_coex: str
    google_maps_query: str
    source: str
    notes: str


def maps_search_url(query: str) -> str:
    return f"{GOOGLE_MAPS_SEARCH}&{urlencode({'query': query})}"


def maps_directions_url(origin: str, destination: str, travelmode: str = "transit") -> str:
    return f"{GOOGLE_MAPS_DIRECTIONS}&{urlencode({'origin': origin, 'destination': destination, 'travelmode': travelmode})}"


def maps_coord_query(latitude: str, longitude: str) -> str:
    return f"{latitude},{longitude}"


def row_with_maps(place: Place) -> dict[str, str]:
    data = asdict(place)
    data["google_maps_url"] = maps_search_url(place.maps_query)
    return data


def row_with_route(route: Route) -> dict[str, str]:
    data = asdict(route)
    data["google_maps_directions_url"] = maps_directions_url(
        route.origin, route.destination, route.travelmode
    )
    return data


def row_with_transport(item: Transport) -> dict[str, str]:
    data = asdict(item)
    data["google_maps_directions_url"] = maps_directions_url(
        item.google_maps_origin,
        item.google_maps_destination,
        item.google_maps_travelmode,
    )
    return data


def row_with_nearby(item: NearbyPick) -> dict[str, str]:
    data = asdict(item)
    data["google_maps_url"] = maps_search_url(item.google_maps_query)
    data["google_maps_directions_url"] = maps_directions_url(COEX_QUERY, item.google_maps_query)
    return data


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        raise RuntimeError(f"No rows for {path}")
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def build_places() -> list[Place]:
    return [
        Place(
            "anchor",
            "ICML 2026 main venue: COEX",
            COEX_QUERY,
            source="ICML 2026 venue page; COEX official address; Google Maps query",
            notes="Use as the default origin for conference-week route planning.",
        ),
        Place(
            "anchor",
            "Grand InterContinental Seoul Parnas",
            "Grand InterContinental Seoul Parnas, 521 Teheran-ro, Gangnam-gu, Seoul",
            source="IHG official hotel directions; Google Maps query",
            notes="Useful hotel anchor next to COEX/Parnas Mall.",
        ),
        Place(
            "station",
            "Samseong Station Exit 5/6",
            "Samseong Station Exit 5, Seoul",
            source="COEX official subway directions; Google Maps query",
            notes="COEX official subway page recommends Line 2 Samseong exits 5/6.",
        ),
        Place(
            "station",
            "Bongeunsa Station Exit 7",
            "Bongeunsa Station Exit 7, Seoul",
            source="COEX official subway directions; Google Maps query",
            notes="Line 9 access to COEX via ASEM Plaza.",
        ),
        Place(
            "station",
            "Cheongdam Station",
            "Cheongdam Station, Seoul",
            source="COEX official subway directions; Google Maps query",
            notes="COEX lists Line 7 Cheongdam as a longer walking option.",
        ),
        Place("airport", "Incheon International Airport Terminal 1", "Incheon Airport Terminal 1, 272 Gonghang-ro, Yeongjong-gu, Incheon"),
        Place("airport", "Incheon International Airport Terminal 2", "Incheon Airport Terminal 2, 446 Je2terminal-daero, Yeongjong-gu, Incheon"),
        Place("airport", "Gimpo International Airport", "Gimpo International Airport"),
        Place("side_event_zone", "Gangnam Station", "Gangnam Station, Seoul"),
        Place("side_event_zone", "Sinnonhyeon Station", "Sinnonhyeon Station, Seoul"),
        Place("side_event_zone", "Seongsu Station", "Seongsu Station, Seoul"),
        Place("side_event_zone", "Seoul Forest", "Seoul Forest, Seoul"),
        Place("side_event_zone", "Hongik Univ. Station", "Hongik University Station, Seoul"),
        Place("side_event_zone", "Itaewon Station", "Itaewon Station, Seoul"),
        Place("side_event_zone", "Hangangjin Station", "Hangangjin Station, Seoul"),
        Place("side_event_zone", "Pangyo Station", "Pangyo Station, Seongnam"),
        Place(
            "known_side_event",
            "VESSL AI x Goodfire ICML Dinner",
            "Dosan-daero 81-gil, Gangnam-gu, Seoul",
            latitude="37.52800202944724",
            longitude="127.04698702228185",
            confidence="luma_detail_obfuscated_area",
            source="Luma event detail JSON-LD obfuscated location; Google Maps area query",
            notes="Luma marks the exact address as guests-only; register and replace with the final address before going.",
        ),
        Place(
            "known_side_event",
            "OpenAI Codex Meetup - Seoul",
            "Yeoksam-ro, Gangnam-gu, Seoul",
            latitude="37.496702101498414",
            longitude="127.03801727334812",
            confidence="luma_detail_obfuscated_area",
            source="Luma event detail JSON-LD obfuscated location; Google Maps area query",
            notes="Luma marks the exact address as guests-only; register and replace with the final address before going.",
        ),
        Place(
            "known_side_event",
            "Hugging Face Seoul Meetup",
            "Yeoksam-dong, Gangnam-gu, Seoul",
            latitude="37.504815646101235",
            longitude="127.0430764791983",
            confidence="luma_detail_obfuscated_area",
            source="Luma event detail JSON-LD obfuscated location; Google Maps area query",
            notes="Luma marks the exact address as guests-only; register and replace with the final address before going.",
        ),
        Place(
            "known_side_event",
            "Google DeepMind x GDG Cloud Korea side event",
            "Gangnam Finance Center 24F, 152 Teheran-ro, Gangnam-gu, Seoul",
            confidence="gdg_detail_address",
            source="GDG event detail address; Google Maps query",
            notes="Public event page lists Gangnam Finance Center 24F.",
        ),
    ]


def build_routes() -> list[Route]:
    sources = "Google Maps Directions URL; official transit anchors from COEX/CALT/IHG/VisitKorea"
    return [
        Route("airport", "ICN T1 to COEX", "Incheon Airport Terminal 1, 272 Gonghang-ro, Yeongjong-gu, Incheon", COEX_QUERY, "transit", "Arrival route; compare 6103 bus and subway in live Google Maps.", sources),
        Route("airport", "ICN T2 to COEX", "Incheon Airport Terminal 2, 446 Je2terminal-daero, Yeongjong-gu, Incheon", COEX_QUERY, "transit", "Arrival route; terminal 2 bus/subway timing differs from terminal 1.", sources),
        Route("airport", "Gimpo Airport to COEX", "Gimpo International Airport", COEX_QUERY, "transit", "Shorter airport route; Line 9/Line 2 options vary by time.", sources),
        Route("venue_access", "Samseong Station to COEX walk", "Samseong Station Exit 5, Seoul", COEX_QUERY, "walking", "COEX official direct-access subway anchor.", sources),
        Route("venue_access", "Bongeunsa Station to COEX walk", "Bongeunsa Station Exit 7, Seoul", COEX_QUERY, "walking", "Line 9 access via ASEM Plaza.", sources),
        Route("side_event_zone", "COEX to Gangnam Station", COEX_QUERY, "Gangnam Station, Seoul", "transit", "High-density dinner/meetup zone near many tech-company events.", sources),
        Route("side_event_zone", "COEX to Sinnonhyeon Station", COEX_QUERY, "Sinnonhyeon Station, Seoul", "transit", "Useful for Gangnam/Sinnonhyeon evening venues.", sources),
        Route("side_event_zone", "COEX to Seongsu", COEX_QUERY, "Seongsu Station, Seoul", "transit", "Cafe/brand-event zone; Line 2 route is usually simple.", sources),
        Route("side_event_zone", "COEX to Hongdae", COEX_QUERY, "Hongik University Station, Seoul", "transit", "Nightlife and Mapo/Hapjeong side-event fallback zone.", sources),
        Route("side_event_zone", "COEX to Itaewon", COEX_QUERY, "Itaewon Station, Seoul", "transit", "Useful for Hannam/Hangangjin social venues; check late-night taxi option.", sources),
        Route("side_event_zone", "COEX to Pangyo Techno Valley", COEX_QUERY, "Pangyo Techno Valley, Seongnam", "transit", "Possible company-campus/offsite zone; requires a longer trip.", sources),
        Route("known_side_event", "COEX to OpenAI Codex Meetup", COEX_QUERY, "Yeoksam-ro, Gangnam-gu, Seoul", "transit", "Public RSVP page exposes only an obfuscated area; replace destination with the registered attendee address.", "Luma detail obfuscated location; Google Maps Directions URL"),
        Route("known_side_event", "COEX to VESSL AI dinner", COEX_QUERY, "Dosan-daero 81-gil, Gangnam-gu, Seoul", "transit", "Public RSVP page exposes only an obfuscated area; replace destination with the registered attendee address.", "Luma detail obfuscated location; Google Maps Directions URL"),
        Route("known_side_event", "COEX to Hugging Face Seoul Meetup", COEX_QUERY, "Yeoksam-dong, Gangnam-gu, Seoul", "transit", "Public RSVP page exposes only an obfuscated area; replace destination with the registered attendee address.", "Luma detail obfuscated location; Google Maps Directions URL"),
        Route("known_side_event", "COEX to Google DeepMind x GDG", COEX_QUERY, "Gangnam Finance Center 24F, 152 Teheran-ro, Gangnam-gu, Seoul", "transit", "Known public event address from GDG event page.", "GDG public event address; Google Maps Directions URL"),
    ]


def build_transport() -> list[Transport]:
    return [
        Transport(
            "venue_access",
            "Line 2 Samseong Station Exit 5/6 -> COEX",
            "Daily conference commute from Line 2 hotels and Gangnam/Seongsu/Hongdae areas.",
            "COEX official subway directions recommend Samseong Station exits 5/6 for direct COEX access.",
            "Samseong Station Exit 5, Seoul",
            COEX_QUERY,
            "walking",
            "https://www.coexcenter.com/directions-map-subway/",
            "Google Maps live routing should decide the exact exit and indoor walking path.",
        ),
        Transport(
            "venue_access",
            "Line 9 Bongeunsa Station Exit 7 -> COEX",
            "Arriving from Gimpo, Gangnam Line 9 corridor, or hotels north/east of COEX.",
            "COEX official subway directions list Bongeunsa Station exit 7 via ASEM Plaza.",
            "Bongeunsa Station Exit 7, Seoul",
            COEX_QUERY,
            "walking",
            "https://www.coexcenter.com/directions-map-subway/",
            "Good fallback when Line 9 is faster than Line 2.",
        ),
        Transport(
            "airport",
            "ICN -> COEX by 6103 airport limousine bus",
            "First arrival with luggage; simple one-seat ride to COEX City Airport / Samseong area.",
            "COEX/CALT list airport limousine bus 6103 between Incheon Airport and COEX City Airport; published ride time is approximate and traffic-dependent.",
            "Incheon International Airport Terminal 1",
            "COEX City Airport Terminal, Seoul",
            "transit",
            "https://www.coexcenter.com/directions-map-airport-2/ | https://www.calt.co.kr/m/EN/limousine/04.php",
            "Use Google Maps on the day for live departures; road traffic can dominate.",
        ),
        Transport(
            "airport",
            "ICN -> COEX by AREX/subway",
            "Traffic-robust arrival if carrying light luggage.",
            "Official Seoul/COEX guidance routes Incheon Airport rail into the Seoul subway network; Line 9 Bongeunsa or Line 2 Samseong are common COEX anchors.",
            "Incheon International Airport Terminal 1",
            COEX_QUERY,
            "transit",
            "https://english.seoul.go.kr/service/entry/getting-to-seoul-from-incheon-airport/ | https://www.coexcenter.com/directions-map-subway/",
            "Transfer choice changes by departure terminal and time; follow Google Maps live routing.",
        ),
        Transport(
            "airport",
            "GMP -> COEX by subway",
            "Domestic/regional arrival; usually subway is practical.",
            "COEX official directions list Gimpo Airport subway access toward Samseong/Bongeunsa.",
            "Gimpo International Airport",
            COEX_QUERY,
            "transit",
            "https://www.coexcenter.com/directions-map-airport-2/ | https://www.coexcenter.com/directions-map-subway/",
            "Check Line 9 express/local differences in Google Maps.",
        ),
        Transport(
            "side_event_zone",
            "COEX -> Gangnam/Sinnonhyeon",
            "Evening dinners, meetups, and company socials around Gangnam.",
            "Samseong is two Line 2 stops from Gangnam; Bongeunsa Line 9 is also useful for Sinnonhyeon.",
            COEX_QUERY,
            "Gangnam Station, Seoul",
            "transit",
            "https://www.coexcenter.com/directions-map-subway/",
            "Taxi may be more comfortable late at night or in heavy rain.",
        ),
        Transport(
            "side_event_zone",
            "COEX -> Seongsu/Ttukseom",
            "Cafe blocks, brand/event spaces, and Seoul Forest add-on.",
            "Samseong and Seongsu are both on Line 2, making this one of the simpler non-Gangnam trips.",
            COEX_QUERY,
            "Seongsu Station, Seoul",
            "transit",
            "https://english.visitkorea.or.kr/svc/contents/contentsView.do?vcontsId=140660",
            "Good for a half-day break; avoid scheduling too tightly before an evening RSVP.",
        ),
        Transport(
            "side_event_zone",
            "COEX -> Hongdae/Mapo/Hapjeong",
            "Nightlife and late socials; not ideal for short lunch gaps.",
            "Line 2 connects Samseong to Hongik Univ./Hapjeong, while AREX also serves Hongik Univ.",
            COEX_QUERY,
            "Hongik University Station, Seoul",
            "transit",
            "https://english.visitkorea.or.kr/svc/contents/contentsView.do?vcontsId=112801",
            "Build buffer into the schedule; the cross-city ride is materially longer than Gangnam/Seongsu.",
        ),
        Transport(
            "side_event_zone",
            "COEX -> Pangyo Techno Valley",
            "Offsite company/AI infra events outside central Seoul.",
            "Pangyo Techno Valley official information centers the zone around Pangyo/Startup Campus.",
            COEX_QUERY,
            "Pangyo Techno Valley, Seongnam",
            "transit",
            "https://www.pangyotechnovalley.org/eng/contents/view?contentsNo=36&menuLevel=3&menuNo=31",
            "Longer trip; only schedule if the event is important or you have a full evening open.",
        ),
    ]


def build_nearby() -> list[NearbyPick]:
    return [
        NearbyPick("COEX", "Starfield COEX Mall", "mall / food / logistics", "Between sessions, lunch, rain backup", "Inside/adjacent to COEX", "Starfield COEX Mall, Seoul", "https://english.visitkorea.or.kr/svc/contents/contentsView.do?vcontsId=60729", "Best low-friction default around the venue."),
        NearbyPick("COEX", "Starfield Library", "library / landmark", "Short photo/rest stop", "Inside Starfield COEX Mall", "Starfield Library, Seoul", "https://english.visitkorea.or.kr/svc/contents/contentsView.do?vcontsId=60729", "Public landmark; easy to combine with mall meals."),
        NearbyPick("COEX", "Bongeunsa Temple", "temple / quiet walk", "Morning, sunset, decompression break", "Walkable from COEX/Bongeunsa Station", "Bongeunsa Temple, Seoul", "https://english.visitkorea.or.kr/svc/contents/contentsView.do?vcontsId=104722", "Close enough for a real break without leaving Gangnam."),
        NearbyPick("COEX", "SEA LIFE COEX Aquarium", "indoor attraction", "Rainy free slot or family add-on", "Inside COEX/Starfield area", "SEA LIFE COEX Aquarium, Seoul", "https://www.visitsealife.com/seoul/en/", "Check same-day closing and last-entry time before going."),
        NearbyPick("COEX", "Parnas Mall", "mall / food", "Meal fallback near conference hotels", "Adjacent to Grand InterContinental Seoul Parnas", "Parnas Mall, Seoul", "https://english.visitkorea.or.kr/svc/contents/contentsView.do?vcontsId=73474", "Useful if staying at or meeting near Parnas."),
        NearbyPick("COEX", "Hyundai Department Store Trade Center", "department store / food hall", "Shopping, food hall, gifts", "Walkable from Samseong/COEX", "Hyundai Department Store Trade Center, Seoul", "https://www.ehyundai.com/newPortal/DP/DP000000_V.do?branchCd=B00147000", "Practical indoor option near the venue."),
        NearbyPick("Gangnam", "Gangnam Station / Gangnam-daero", "evening food / side-event zone", "After posters, dinners, socials", "Short transit/taxi from COEX", "Gangnam Station, Seoul", "https://english.visitkorea.or.kr/svc/whereToGo/locIntrdn/rgnContentsView.do?vcontsId=86853", "High density but busy; confirm exact venue."),
        NearbyPick("Seongsu", "Seongsu Cafe Street", "cafes / shops", "Half-day break or casual meetup", "Line 2 from Samseong to Seongsu", "Seongsu Cafe Street, Seoul", "https://english.visitkorea.or.kr/svc/contents/contentsView.do?vcontsId=140660", "Good candidate for a lighter day away from COEX."),
        NearbyPick("Seongsu", "Seoul Forest", "park", "Longer daylight break", "Near Seongsu/Ttukseom", "Seoul Forest, Seoul", "https://english.visitkorea.or.kr/svc/contents/contentsView.do?vcontsId=140660", "Pair with Seongsu cafes rather than making a separate trip."),
        NearbyPick("Hongdae", "Hongik Univ. Street", "nightlife / music / food", "Late evening only if energy allows", "Cross-city ride from COEX", "Hongik University Street, Seoul", "https://english.visitkorea.or.kr/svc/contents/contentsView.do?vcontsId=112801", "Worth listing as optional, not a core conference-day stop."),
        NearbyPick("Itaewon", "Itaewon / Hannam / Hangangjin", "restaurants / bars / galleries", "Dinner or late social", "Transit with transfer or taxi from COEX", "Itaewon Station, Seoul", "https://english.visitkorea.or.kr/svc/whereToGo/locIntrdn/rgnContentsView.do?vcontsId=111543", "Check route live; taxi can be simpler late night."),
        NearbyPick("Airport", "COEX City Airport Terminal / CALT", "airport bus anchor", "Arrival/departure logistics", "Adjacent to COEX/Samseong area", "COEX City Airport Terminal, Seoul", "https://www.calt.co.kr/m/EN/limousine/04.php", "Use for 6103 airport bus planning; verify current service on CALT."),
    ]


def build_screenshot_targets(routes: list[Route]) -> list[dict[str, str]]:
    selected = [
        "ICN T1 to COEX",
        "Gimpo Airport to COEX",
        "COEX to Gangnam Station",
        "COEX to OpenAI Codex Meetup",
        "COEX to Google DeepMind x GDG",
    ]
    by_name = {route.name: route for route in routes}
    rows = []
    for index, name in enumerate(selected, start=1):
        route = by_name[name]
        slug = (
            name.lower()
            .replace(" ", "-")
            .replace("/", "-")
            .replace("x", "x")
            .replace(".", "")
        )
        rows.append(
            {
                "priority": str(index),
                "name": name,
                "google_maps_directions_url": maps_directions_url(
                    route.origin, route.destination, route.travelmode
                ),
                "suggested_png": f"data/maps/screenshots/{index:02d}-{quote_plus(slug).replace('+', '-')}.png",
                "notes": "Open in browser and capture after Google Maps finishes live route rendering.",
            }
        )
    return rows


def main() -> None:
    places = build_places()
    routes = build_routes()
    transport = build_transport()
    nearby = build_nearby()

    write_csv(PLACES_OUT, [row_with_maps(place) for place in places])
    write_csv(ROUTES_OUT, [row_with_route(route) for route in routes])
    write_csv(TRANSPORT_OUT, [row_with_transport(item) for item in transport])
    write_csv(NEARBY_OUT, [row_with_nearby(item) for item in nearby])
    write_csv(SCREENSHOT_TARGETS_OUT, build_screenshot_targets(routes))

    print(f"Wrote {len(places)} map places -> {PLACES_OUT.relative_to(ROOT)}")
    print(f"Wrote {len(routes)} route links -> {ROUTES_OUT.relative_to(ROOT)}")
    print(f"Wrote {len(transport)} transport notes -> {TRANSPORT_OUT.relative_to(ROOT)}")
    print(f"Wrote {len(nearby)} nearby picks -> {NEARBY_OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
