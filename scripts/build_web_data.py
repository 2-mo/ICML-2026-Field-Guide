#!/usr/bin/env python3
"""Build small JSON bundles for the GitHub Pages guide."""

from __future__ import annotations

import csv
import json
import re
import shutil
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import urlencode


ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"
RESEARCH = ROOT / "data" / "research"
MAPS = ROOT / "data" / "maps"
DOCS = ROOT / "docs"
OUT = DOCS / "data"
MAP_OUT = DOCS / "maps"

FLOOR_MAP_URL = "https://media.icml.cc/Conferences/ICML2026/coex_map.svg"
COEX_QUERY = "COEX Convention & Exhibition Center, 513 Yeongdong-daero, Gangnam-gu, Seoul"
PROVISTA_QUERY = "Hotel Provista Seoul, 338 Seocho-daero, Seocho-gu, Seoul 06632"
PROVISTA_ADDRESS = "338 Seocho-daero, Seocho-gu, Seoul 06632"
COEX_AIRPORT_SOURCE = "https://www.coexcenter.com/directions-map-airport-2/"
COEX_SUBWAY_SOURCE = "https://www.coexcenter.com/directions-map-subway/"
SEOUL_AIRPORT_SOURCE = "https://english.seoul.go.kr/service/entry/getting-to-seoul-from-incheon-airport/"
PROVISTA_SOURCE = "https://english.visitkorea.or.kr/svc/contents/contentsView.do?vcontsId=86218"

PAPER_ARXIV_URLS = {
    "Learning to Watch: Active Video Anomaly Understanding via Interleaved Policy Optimization": "https://arxiv.org/abs/2607.00622",
    "Linguistic Relative Policy Optimization for Video Anomaly Reasoning": "https://arxiv.org/abs/2607.00654",
}

FOCUS_GROUP_TITLES = [
    (
        "video_anomaly_understanding",
        "Video Anomaly Understanding",
        [
            "Learning to Watch: Active Video Anomaly Understanding via Interleaved Policy Optimization",
            "Linguistic Relative Policy Optimization for Video Anomaly Reasoning",
            "PRISM: Training-Free Video Anomaly Detection via Intrinsic Statistical Modeling",
            "Privacy-Aware Video Anomaly Detection: Guided Orthogonal Projection and a Comprehensive Evaluation Framework",
            "TD-VAD: Breaking Visual Dependence in Video Anomaly Detection with Text-Driven Learning",
            "Towards Trustworthy Video Anomaly Understanding: A Class-Guided Chain-of-Evaluation Metric and An Anomaly-focused Meta-Benchmark",
        ],
    ),
    (
        "multimodal_llms",
        "Multimodal LLMs",
        [
            "Decomposed On-Policy Distillation for Vision-Language Reasoning: Steering Gradients for Visual Grounding",
            "Debate with Images: Detecting Deceptive Behaviors in Multimodal Large Language Models",
            "VERA-V: Variational Inference Framework for Jailbreaking Vision-Language Models",
            "RSAgent: Learning to Reason and Act via Multi-Turn Tool Invocations for Text-Guided Segmentation",
            "On Robustness and Chain-of-Thought Consistency of RL-Finetuned VLMs",
            "Vision-aligned Latent Reasoning for Multi-Modal Large Language Model",
            "FG-CLIP 2: A Bilingual Fine-grained Vision-Language Alignment Model",
        ],
    ),
    (
        "reasoning_models",
        "Reasoning Models",
        [
            "ForesightKV: Optimizing KV Cache Eviction for Reasoning Models by Learning Long-Term Contribution",
            "Does Your Reasoning Model Implicitly Know When to Stop Thinking?",
            "Stop When Further Reasoning Won’t Help: Attention-State Adaptive Generation in Reasoning Models",
            "Learning Useful Supervision for Reinforcement Learning in Reasoning Models",
            "Dynamic Thinking-Token Selection for Efficient Reasoning in Large Reasoning Models",
            "Are Large Reasoning Models Interruptible?",
            "Reasoning Models Struggle to Control their Chains of Thought",
            "Base Models Know How to Reason, Thinking Models Learn When",
        ],
    ),
    (
        "video_understanding",
        "Video Understanding",
        [
            "Q-CLIP: Unleashing the Power of Vision-Language Models for Video Quality Assessment through Unified Cross-Modal Adaptation",
            "Motion Attribution for Video Generation",
            "MetaphorVU: Towards Metaphorical Video Understanding",
            "Physics from Video: Identifiability of Time-Invariant Second-Order ODEs under Minimal Trajectory Conditions",
            "Learning to Decode Against Compositional Hallucination in Video Multimodal Large Language Models",
            "Foreground-Aware Token Routing Vision Transformer for Real-Time Satellite Video Tracking",
        ],
    ),
    (
        "anomaly_detection",
        "Anomaly Detection",
        [
            "Anomaly-Preference Image Generation",
            "CoGeoAD: Hierarchical Color-Geometric Fusion with Multi-View Attention for Zero-Shot 3D Anomaly Detection",
            "Counterfactual Occlusion-Aware Learning via Visibility Intervention for LiDAR Anomaly Detection",
            "Formally Exploring Visual Anomaly Detection Evaluation Metrics",
            "Is Training Necessary for Anomaly Detection?",
            "Memory-Distilled Selection for Noise-Robust Anomaly Detection",
            "Mixture Prototype Flow Matching for Open-Set Supervised Anomaly Detection",
        ],
    ),
]

PERSONAL_ROUTE_GROUPS = [
    {
        "id": "coex_quick",
        "title_zh": "会场周边",
        "title_en": "COEX quick loop",
        "when": "10-45 min",
        "route_hint": "COEX -> COEX Mall B1 -> Starfield Library",
        "destination_query": "Starfield Library, Seoul",
        "spots": [
            ("COEX会展中心", "COEX Convention & Exhibition Center", "Venue", "ICML 2026 main venue.", COEX_QUERY, "https://www.coexcenter.com/"),
            ("COEX Mall", "Starfield COEX Mall", "Food / shopping", "Underground mall for meals, coffee, supplies, and rain-safe movement.", "Starfield COEX Mall, Seoul", "https://www.starfield.co.kr/coexmall/main.do"),
            ("星空图书馆", "Starfield Library", "Meet / photo", "Easy B1 landmark inside COEX Mall for a quick reset or meeting point.", "Starfield Library, Seoul", "https://www.starfield.co.kr/coexmall/main.do"),
            ("奉恩寺", "Bongeunsa Temple", "Short walk", "Quiet temple directly north of COEX; good for a 20-30 minute break.", "Bongeunsa Temple, Seoul", "https://english.visitkorea.or.kr/svc/contents/contentsView.do?vcontsId=104722"),
            ("COEX Aquarium", "SEA LIFE COEX Aquarium", "Rain backup", "Indoor aquarium inside COEX Mall when the weather or schedule is awkward.", "SEA LIFE COEX, Seoul", "https://www.visitsealife.com/coex-seoul/en/"),
        ],
    },
    {
        "id": "palace_bukchon",
        "title_zh": "景福宫、北村、仁寺洞",
        "title_en": "Palace walk",
        "when": "half day",
        "route_hint": "COEX -> Gyeongbokgung -> Gwanghwamun -> Bukchon -> Insadong",
        "destination_query": "Gyeongbokgung Palace, Seoul",
        "spots": [
            ("景福宫", "Gyeongbokgung Palace", "Palace", "Largest Joseon palace; pair with Gwanghwamun and Bukchon.", "Gyeongbokgung Palace, Seoul", "https://english.visitkorea.or.kr/svc/contents/contentsView.do?vcontsId=87740"),
            ("光化门", "Gwanghwamun Gate", "Landmark", "Main gate and plaza anchor for the palace area.", "Gwanghwamun Gate, Seoul"),
            ("青瓦台", "Cheong Wa Dae", "History", "Former presidential office north of Gyeongbokgung.", "Cheong Wa Dae, Seoul"),
            ("北村韩屋村", "Bukchon Hanok Village", "Hanok walk", "Traditional hanok neighborhood between the royal palaces.", "Bukchon Hanok Village, Seoul", "https://english.visitkorea.or.kr/svc/whereToGo/locIntrdn/rgnContentsView.do?vcontsId=97932"),
            ("国立现代美术馆", "MMCA Seoul", "Museum", "Modern art museum across from the palace.", "National Museum of Modern and Contemporary Art Seoul"),
            ("阿拉里奥美术馆", "Arario Museum in Space", "Architecture", "Small museum where the building is part of the draw.", "Arario Museum in Space, Seoul"),
            ("仁寺洞", "Insadong", "Tea / craft", "Galleries, tea houses, and easy souvenir stops.", "Insadong, Seoul"),
            ("德寿宫", "Deoksugung Palace", "Palace", "Central palace near City Hall; easy to combine with Cheonggyecheon.", "Deoksugung Palace, Seoul"),
            ("昌德宫", "Changdeokgung Palace", "UNESCO", "Well-preserved Joseon palace; Secret Garden needs separate planning.", "Changdeokgung Palace, Seoul", "https://english.visitkorea.or.kr/svc/whereToGo/locIntrdn/rgnContentsView.do?vcontsId=94399"),
            ("南山谷韩屋村", "Namsangol Hanok Village", "Hanok", "Hanok village at the foot of Namsan.", "Namsangol Hanok Village, Seoul"),
        ],
    },
    {
        "id": "namsan_myeongdong",
        "title_zh": "南山、明洞",
        "title_en": "Namsan & Myeongdong",
        "when": "evening",
        "route_hint": "COEX -> Myeongdong -> Namsan Cable Car -> N Seoul Tower",
        "destination_query": "N Seoul Tower, Seoul",
        "spots": [
            ("明洞", "Myeongdong", "Shopping", "Primary shopping district and easy food stop before Namsan.", "Myeongdong, Seoul", "https://english.visitkorea.or.kr/svc/contents/contentsView.do?vcontsId=88011"),
            ("南山缆车", "Namsan Cable Car", "City view", "Classic approach to the tower if the queue is reasonable.", "Namsan Cable Car, Seoul", "https://english.visitkorea.or.kr/svc/contents/contentsView.do?vcontsId=96828"),
            ("N首尔塔", "N Seoul Tower", "Skyline", "Iconic Seoul lookout; best as a clear-evening option.", "N Seoul Tower, Seoul", "https://english.visitkorea.or.kr/svc/contents/contentsView.do?vcontsId=88026"),
            ("南山谷韩屋村", "Namsangol Hanok Village", "Hanok", "Lower-friction hanok stop near Namsan.", "Namsangol Hanok Village, Seoul"),
        ],
    },
    {
        "id": "hanriver_yeouido",
        "title_zh": "汝矣岛、汉江、63大厦",
        "title_en": "Han River & Yeouido",
        "when": "evening / dinner day",
        "route_hint": "COEX -> Yeouido -> 63 Building -> Han River Park",
        "destination_query": "63 Building, Seoul",
        "spots": [
            ("国会议事堂", "National Assembly", "Architecture", "Use only if it fits a Yeouido route.", "National Assembly, Seoul"),
            ("63大厦", "63 Building", "Skyline", "Han River skyline anchor near Yeouido.", "63 Building, Seoul"),
            ("蓬皮杜分馆", "Centre Pompidou Hanwha Seoul", "Museum", "Check current opening details before making it the anchor.", "Centre Pompidou Hanwha Seoul 63 Building"),
            ("汉江公园", "Hangang Park", "River walk", "Low-effort night walk along the Han River.", "Yeouido Hangang Park, Seoul", "https://english.visitkorea.or.kr/svc/whereToGo/locIntrdn/rgnContentsView.do?vcontsId=77674"),
        ],
    },
    {
        "id": "ddp_city_walk",
        "title_zh": "DDP、清溪川、市中心",
        "title_en": "DDP & City Walk",
        "when": "night walk",
        "route_hint": "COEX -> DDP -> Cheonggyecheon -> Myeongdong",
        "destination_query": "Dongdaemun Design Plaza, Seoul",
        "spots": [
            ("东大门设计广场", "Dongdaemun Design Plaza", "Architecture", "Zaha Hadid landmark; stronger at night.", "Dongdaemun Design Plaza, Seoul", "https://english.visitkorea.or.kr/svc/contents/contentsView.do?menuSn=351&vcontsId=67162"),
            ("清溪川", "Cheonggyecheon Stream", "Night walk", "Easy central walk after DDP or Myeongdong.", "Cheonggyecheon Stream, Seoul"),
            ("明洞", "Myeongdong", "Shopping", "Shopping and street-food finish.", "Myeongdong, Seoul", "https://english.visitkorea.or.kr/svc/contents/contentsView.do?vcontsId=88011"),
            ("首尔路7017", "Seoullo 7017", "Walkway", "Elevated walkway near Seoul Station.", "Seoullo 7017, Seoul"),
        ],
    },
    {
        "id": "jamsil_skyline",
        "title_zh": "蚕室、乐天世界塔",
        "title_en": "Jamsil Skyline",
        "when": "clear evening",
        "route_hint": "COEX -> Jamsil -> Lotte World Tower -> Seokchon Lake",
        "destination_query": "Lotte World Tower, Seoul",
        "spots": [
            ("乐天世界塔", "Lotte World Tower", "Skyline", "555m tower with Seoul Sky observatory and mall.", "Lotte World Tower, Seoul", "https://english.visitkorea.or.kr/svc/contents/contentsView.do?vcontsId=72115"),
            ("首尔天空", "Seoul Sky", "Observatory", "Observation floors inside Lotte World Tower.", "Seoul Sky, Seoul", "https://english.visitkorea.or.kr/svc/contents/contentsView.do?vcontsId=65854"),
            ("石村湖", "Seokchon Lake", "Walk", "Flat lake walk beside Jamsil.", "Seokchon Lake, Seoul"),
            ("乐天世界", "Lotte World Adventure", "Theme park", "Only worth it if you actually want a theme-park block.", "Lotte World Adventure, Seoul", "https://english.visitkorea.or.kr/svc/contents/contentsView.do?vcontsId=111276"),
        ],
    },
    {
        "id": "shopping_evening",
        "title_zh": "购物和晚饭区",
        "title_en": "Shopping & evening",
        "when": "after posters",
        "route_hint": "COEX -> Gangnam / Itaewon / Myeongdong / Times Square",
        "destination_query": "Gangnam Station, Seoul",
        "spots": [
            ("江南站", "Gangnam Station", "Dinner / events", "High-density dinner and company-event area near COEX.", "Gangnam Station, Seoul"),
            ("梨泰院", "Itaewon", "Bars / dinner", "Useful for evening plans around Hannam and Hangangjin.", "Itaewon Station, Seoul"),
            ("明洞", "Myeongdong", "Shopping", "Shopping, street food, and duty-free stores.", "Myeongdong, Seoul", "https://english.visitkorea.or.kr/svc/contents/contentsView.do?vcontsId=88011"),
            ("仁寺洞", "Insadong", "Tea / craft", "Galleries, tea houses, and gifts.", "Insadong, Seoul"),
            ("首尔时代广场", "Times Square Seoul", "Shopping", "Large mall option if your hotel or dinner plan points west.", "Times Square Mall Seoul"),
        ],
    },
]

VERIFIED_SIDE_EVENTS = [
    {
        "date_label": "Wed Jul 8",
        "date_2026": "2026-07-08",
        "start_time": "6:00",
        "end_time": "9:30pm",
        "timezone_note": "KST",
        "title": "K-Star STARRY NIGHT / 快手 x ICML 2026 晚宴报名",
        "organizer_guess": "Kuaishou / 快手 K-Star",
        "event_kind": "Dinner",
        "rsvp_url": "https://www.wjx.cn/vm/rN1U64h.aspx",
        "platform": "WJX",
        "detail_name": "快手 x ICML 2026 晚宴报名",
        "detail_start": "2026-07-08T18:00:00+09:00",
        "detail_end": "2026-07-08T21:30:00+09:00",
        "location_name": "Yeouido Dock, Seoul",
        "address_region": "Yeouido Dock",
        "address_country": "KR",
        "latitude": "",
        "longitude": "",
        "organizer_verified": "Kuaishou / 快手 K-Star",
        "ticket_availability": "Invite / registration closed",
        "source_url": "https://www.wjx.cn/vm/rN1U64h.aspx",
        "source_updated": "2026-07-02",
        "confidence": "manual_verified_public_page",
        "notes": "Public WJX page says during ICML 2026; invitation-based dinner, registration deadline Jul 1 24:00 Beijing time.",
    },
    {
        "date_label": "Thu Jul 9",
        "date_2026": "2026-07-09",
        "start_time": "6:30",
        "end_time": "9:00pm",
        "timezone_note": "KST",
        "title": "Qwen Meetup Seoul #3 - Agent AI",
        "organizer_guess": "Qwen / Alibaba Cloud Korea / Team Sparta",
        "event_kind": "Meetup / networking",
        "rsvp_url": "https://luma.com/pd7uf8d8",
        "platform": "Luma",
        "detail_name": "Qwen Meetup Seoul #3 - Agent AI",
        "detail_start": "2026-07-09T18:30:00+09:00",
        "detail_end": "2026-07-09T21:00:00+09:00",
        "location_name": "Team Sparta",
        "address_region": "Seoul",
        "address_country": "KR",
        "latitude": "",
        "longitude": "",
        "organizer_verified": "Qwen / Alibaba Cloud Korea",
        "ticket_availability": "RSVP",
        "source_url": "https://luma.com/qwen",
        "source_updated": "2026-07-02",
        "confidence": "manual_verified_public_page",
        "notes": "Public Qwen/Alibaba Cloud Korea event during ICML Seoul week; title/page does not explicitly say ICML.",
    }
]

UNCONFIRMED_COMPANY_WATCH = [
    {
        "company": "ByteDance / 字节 / Seed",
        "status": "未找到公开 ICML 2026 Seoul dinner / RSVP",
        "note": "截至 2026-07-02 只找到 CVPR Denver 相关 Seed 晚宴媒体语境，没有 ICML Seoul 公开活动页。",
    },
    {
        "company": "Huawei / 华为 / Noah",
        "status": "有 Huawei Talent Night 线索，时间地点缺失",
        "note": "公开 LinkedIn 线索提到 Huawei Talent Night at ICML 2026，但文字没有给出具体时间地点。",
    },
    {
        "company": "Xiaomi / 小米",
        "status": "微信标题线索，正文被验证拦截",
        "note": "搜到“小米 ICML2026 顶尖人才技术交流晚宴报名开启”，未核到时间、地点、报名截止；Jul 6 官方 Expo demo 已列。",
    },
    {
        "company": "Tencent / 腾讯",
        "status": "媒体称 Jul 8 有 ICML 晚宴，未找到公开 RSVP",
        "note": "腾讯青云官方页存在，但没有公开 ICML Seoul 晚宴详情页；不要直接导航。",
    },
    {
        "company": "Alibaba / 阿里 / Qwen",
        "status": "Qwen Meetup 已核实；阿里晚宴为媒体线索",
        "note": "Qwen Meetup Seoul #3 有公开 Luma / OnOffMix；阿里 ICML 晚宴仅媒体称同日举办，未找到公开 RSVP。",
    },
]

ROOM_GUIDE = {
    "HALL A": "Hall A 在 1F，是 poster 主场；从 Samseong/Parnas/COEX Mall 侧进来按 Hall A / West Gate 方向走。",
    "HALL B1": "Hall B1 在 1F Hall B 区，是 sponsor/exhibitor 主场；先找 Hall B Foyer，再下/进 B1 区域。",
    "HALL B2": "Hall B2 靠 Hall B Foyer / East Gate 动线；从注册台或 Help Desk 后过去最顺。",
    "HALL C": "Hall C 在 3F South，和 Room E 同侧；从馆内扶梯/电梯上 3F 后按 Hall C 指示走。",
    "HALL D1": "Hall D 在 3F，靠 Auditorium / Bongeunsa / ASEM 一侧；Hall D1/D2 相邻，适合连看。",
    "HALL D2": "Hall D 在 3F，靠 Auditorium / Bongeunsa / ASEM 一侧；Hall D1/D2 相邻，适合连看。",
    "GRAND BALLROOM": "Grand Ballroom 101-105 在 1F North，靠 ASEM/Auditorium 一侧；从 Hall A/B 横切过去要预留时间。",
    "GRAND BALLROOM 101 105": "Grand Ballroom 101-105 在 1F North，靠 ASEM/Auditorium 一侧；从 Hall A/B 横切过去要预留时间。",
    "ASEM BALLROOM": "ASEM Ballroom 在 2F；去 ASEM 相关房间优先记“2F ASEM”，不要往 Hall B/Grand Ballroom 里找。",
    "ASEM BALLROOM 201 203": "ASEM Ballroom 201-203 在 2F；去 ASEM 相关房间优先记“2F ASEM”。",
    "ROOM E1-E4": "Room E 在 3F South，和 Hall C 同侧；从主 Hall 区过去先上 3F。",
    "ROOM E5-E6": "Room E 在 3F South，和 Hall C 同侧；从主 Hall 区过去先上 3F。",
    "ROOM 300": "Room 300 区域；适合 affinity/community 活动，和 Hall A poster 不要无脑连跳。",
}


def room_hint(room: str) -> str:
    normalized = (room or "").upper().replace("/", " ")
    for key, hint in ROOM_GUIDE.items():
        if key in normalized:
            return hint
    if "HALL" in normalized:
        return "Hall 区活动；用官方 COEX map 确认具体入口和楼层。"
    if "ROOM" in normalized or "BALLROOM" in normalized:
        return "会议室/ballroom 区活动；从 Hall A poster 区切换要预留时间。"
    return "打开官方地图确认位置；不要只凭 room name 现场横跳。"


PERSONA_HINTS = {
    "LLM / Foundation Models": "适合做大模型训练、后训练、推理、数据选择的人。",
    "Agents / Tool Use / GUI": "适合关注 agent benchmark、软件工程 agent、工具调用和真实任务评测的人。",
    "AI Safety / Alignment / Reliability": "适合关注 alignment、jailbreak、可靠性、风险评估的人。",
    "Efficient ML / Systems / Hardware": "适合做训练/推理效率、量化、内存、硬件和系统优化的人。",
    "Robotics / Embodied AI": "适合做 VLA、控制、模仿学习、具身智能的人。",
    "Theory / Optimization / Learning Foundations": "适合想看理论、优化、泛化、采样和学习基础的人。",
    "AI for Science / Bio / Medicine": "适合看 AI4Science、蛋白/基因组、生物医学和科学发现的人。",
    "Vision / Multimodal / Audio": "适合看视觉语言、多模态、视频和音频模型的人。",
}


def persona_for(topic: str) -> str:
    if topic in PERSONA_HINTS:
        return PERSONA_HINTS[topic]
    lowered = topic.lower()
    if "llm" in lowered or "foundation" in lowered:
        return PERSONA_HINTS["LLM / Foundation Models"]
    if "agent" in lowered or "tool" in lowered:
        return PERSONA_HINTS["Agents / Tool Use / GUI"]
    if "safety" in lowered or "alignment" in lowered or "reliability" in lowered:
        return PERSONA_HINTS["AI Safety / Alignment / Reliability"]
    if "efficient" in lowered or "systems" in lowered or "hardware" in lowered:
        return PERSONA_HINTS["Efficient ML / Systems / Hardware"]
    if "robot" in lowered or "embodied" in lowered:
        return PERSONA_HINTS["Robotics / Embodied AI"]
    if "theory" in lowered or "optimization" in lowered:
        return PERSONA_HINTS["Theory / Optimization / Learning Foundations"]
    if "science" in lowered or "bio" in lowered or "medicine" in lowered:
        return PERSONA_HINTS["AI for Science / Bio / Medicine"]
    if "vision" in lowered or "multimodal" in lowered or "audio" in lowered:
        return PERSONA_HINTS["Vision / Multimodal / Audio"]
    return "适合想快速摸清这个方向今年趋势的人。"


def workshop_topics(title: str, abstract: str = "") -> list[str]:
    text = f"{title} {abstract}".lower()
    rules = [
        ("Agents", ["agent", "agentic", "planning", "tool", "coding"]),
        ("LLM / FM", ["language model", "foundation model", "llm", "multimodal", "scaling"]),
        ("AI4Science", ["biology", "physics", "math", "life science", "health", "molecule"]),
        ("Safety / Governance", ["safety", "governance", "trustworthy", "uncertainty", "failure"]),
        ("Theory", ["theory", "optimization", "probabilistic", "statistical", "dynamics"]),
        ("Systems / Efficiency", ["efficient", "scalable", "systems", "wireless", "sustainable"]),
        ("Vision / Audio", ["video", "audio", "vision", "frames"]),
        ("Graph / Data", ["graph", "structured data", "tabular"]),
        ("Society / Law", ["law", "culture", "human-ai", "creativity", "philosophy"]),
        ("RL", ["reinforcement", "rl", "world feedback"]),
    ]
    picked = []
    for label, needles in rules:
        if any(needle in text for needle in needles):
            picked.append(label)
        if len(picked) >= 3:
            break
    return picked or ["Workshop"]


def guide_day_key(date: str) -> str:
    if date in {"2026-07-10", "2026-07-11"}:
        return "2026-07-10_11"
    return date


def clean_session_title(title: str) -> str:
    return (title or "").strip()


def split_session_code(title: str) -> tuple[str, str]:
    clean = clean_session_title(title)
    parts = clean.split(" ", 2)
    if len(parts) == 3 and parts[0] in {"Oral", "Poster"} and any(ch.isdigit() for ch in parts[1]):
        return f"{parts[0]} {parts[1]}", parts[2].strip()
    return "", clean


def paper_score(row: dict[str, str]) -> int:
    return (
        (row.get("is_spotlight") == "yes") * 80
        + (row.get("is_oral") == "yes") * 60
        + (row.get("is_position") == "yes") * 40
        + (row.get("is_journal_track") == "yes") * 20
        + bool(row.get("code_or_project_url")) * 5
    )


def interest_stars_from_score(score: int) -> int:
    if score >= 22:
        return 5
    if score >= 16:
        return 4
    if score >= 11:
        return 3
    if score >= 6:
        return 2
    if score >= 2:
        return 1
    return 0


def personal_interest(*values: str) -> dict[str, object]:
    text = " ".join(str(value or "") for value in values).lower()
    score = 0
    reasons: list[str] = []

    def add(points: int, reason: str) -> None:
        nonlocal score
        score += points
        if reason not in reasons:
            reasons.append(reason)

    def has(pattern: str) -> bool:
        return bool(re.search(pattern, text))

    titleish = text[:260]
    has_video = has(r"\b(video|videos|video-language|long-video|frame|frames|clip|clips|visual)\b")
    has_anomaly = has(r"\b(anomaly|anomalies|anomalous|abnormal)\b")
    has_video_anomaly_phrase = has(r"\b(video anomaly|video anomalies|anomalous video|abnormal video|video anomaly detection|video anomaly understanding)\b")
    has_vl = has(r"\b(vision-language|vision language|visual language|video-language|vlm|mllm|lvlm|image-text|large vision-language model|large vision language model)\b")
    has_mm = has(r"\b(multimodal|multi-modal|cross-modal|audio-visual)\b")
    has_llm = has(r"\b(large language model|language model|foundation model|llm|gpt)\b")

    if has_video_anomaly_phrase:
        add(18, "Video anomaly")
    elif has(r"\banomaly detection\b"):
        add(3, "Anomaly")
    if has_video and has_anomaly:
        add(8, "Video anomaly")
    if has(r"\b(video understanding|long video|video reasoning|video generation|video quality|video-language)\b"):
        add(6, "Video")
    elif has_video and "time series" not in titleish:
        add(3, "Video")
    if has_vl:
        add(5, "VLM/MLLM")
    if has_mm:
        add(4, "Multimodal")
    if has_llm:
        add(3, "LLM/FM")
    if has_video and (has_vl or has_mm or has_llm):
        add(6, "Video MLLM")
    if has_mm and has_llm:
        add(4, "MLLM")
    if "multimodal / vision-language / video" in text:
        add(2, "Video/MM")
    if has(r"\b(vla|vision-language-action|visual reasoning|pixel grounding|visual grounding)\b"):
        add(3, "VLM/MLLM")
    if "time series" in titleish and not has_video_anomaly_phrase:
        score = max(0, score - 8)

    return {
        "interest_score": score,
        "interest_stars": interest_stars_from_score(score),
        "interest_reasons": reasons[:3],
    }


def paper_interest(row: dict[str, str] | None) -> dict[str, object]:
    if not row:
        return personal_interest("")
    main = personal_interest(
        row.get("title", ""),
        row.get("abstract", ""),
        row.get("topic", ""),
        row.get("keywords", ""),
    )
    track = personal_interest(row.get("topic_tracks", ""))
    score = int(main["interest_score"]) + min(int(track["interest_score"]), 3)
    reasons: list[str] = []
    for meta in [main, track]:
        for reason in meta.get("interest_reasons", []):
            if reason not in reasons:
                reasons.append(str(reason))
    return {
        "interest_score": score,
        "interest_stars": interest_stars_from_score(score),
        "interest_reasons": reasons[:3],
    }


def aggregate_interest(rows: list[dict[str, str]], *fallback: str) -> dict[str, object]:
    metas = [paper_interest(row) for row in rows]
    fallback_meta = personal_interest(*fallback)
    best_score = max([int(fallback_meta["interest_score"])] + [int(meta["interest_score"]) for meta in metas])
    relevant_count = sum(1 for meta in metas if int(meta["interest_stars"]) >= 3)
    score = best_score + min(relevant_count, 2)
    if relevant_count >= 3 and best_score >= 10:
        score += 1
    reasons: list[str] = []
    for meta in sorted(metas + [fallback_meta], key=lambda item: int(item["interest_score"]), reverse=True):
        for reason in meta.get("interest_reasons", []):
            if reason not in reasons:
                reasons.append(str(reason))
    return {
        "interest_score": score,
        "interest_stars": interest_stars_from_score(score),
        "interest_reasons": reasons[:3],
    }


def paper_focus_score(row: dict[str, str]) -> int:
    meta = paper_interest(row)
    return (
        int(meta["interest_score"]) * 10
        + (row.get("is_oral") == "yes") * 4
        + (row.get("is_spotlight") == "yes") * 3
        + (row.get("is_position") == "yes") * 2
        + bool(row.get("code_or_project_url")) * 1
    )


def paper_focus_entry(row: dict[str, str]) -> dict[str, object]:
    meta = paper_interest(row)
    title = row.get("title", "")
    website_url = row.get("poster_url") or row.get("oral_url") or ""
    flags = []
    if row.get("is_oral") == "yes":
        flags.append("Oral-linked")
    if row.get("is_spotlight") == "yes":
        flags.append("Spotlight")
    if row.get("is_position") == "yes":
        flags.append("Position")
    if row.get("is_journal_track") == "yes":
        flags.append("Journal")
    return {
        "title": title,
        "date": row.get("poster_date_kst") or row.get("oral_date_kst", ""),
        "time": row.get("poster_time_kst") or row.get("oral_time_kst", ""),
        "session": row.get("poster_session") or row.get("oral_session", ""),
        "room": row.get("poster_room") or row.get("oral_room", ""),
        "position": row.get("poster_position", ""),
        "url": website_url,
        "website_url": website_url,
        "arxiv_url": PAPER_ARXIV_URLS.get(title, ""),
        "tracks": [topic for topic in (row.get("topic_tracks") or "").split(" | ") if topic][:3],
        "flags": flags,
        "focus_score": paper_focus_score(row),
        **meta,
    }


def poster_number(value: object) -> int:
    match = re.search(r"\d+", str(value or ""))
    return int(match.group(0)) if match else 999999


def focus_group_sort_key(row: dict[str, object]) -> tuple[str, str, int, str]:
    return (
        str(row.get("date") or "9999-99-99"),
        str(row.get("time") or "99:99"),
        poster_number(row.get("position")),
        str(row.get("title") or ""),
    )


def build_focus_groups(papers: list[dict[str, str]]) -> list[dict[str, object]]:
    papers_by_title = {row.get("title", ""): row for row in papers}
    groups = []
    for group_id, title, paper_titles in FOCUS_GROUP_TITLES:
        group_papers = [
            paper_focus_entry(papers_by_title[paper_title])
            for paper_title in paper_titles
            if paper_title in papers_by_title
        ]
        group_papers.sort(key=focus_group_sort_key)
        groups.append(
            {
                "id": group_id,
                "title": title,
                "papers": group_papers,
            }
        )
    return groups


def company_focus_rows() -> list[dict[str, str]]:
    rows = []
    for row in read_research_csv("icml2026_domestic_industry_events.csv"):
        if row.get("company_en") not in {
            "Kuaishou",
            "Alibaba",
            "Tencent",
            "ByteDance",
            "Huawei",
            "Xiaomi",
            "Meituan",
            "Shanghai AI Laboratory",
            "Jiangmen Venture",
            "ShanghaiTech University",
        }:
            continue
        bucket = "confirmed" if row.get("guide_bucket") == "timeline_confirmed" else "watch"
        if row.get("guide_bucket") == "not_found":
            bucket = "not_found"
        date_value = row.get("date_kst", "")
        is_exact_date = bool(re.match(r"^\d{4}-\d{2}-\d{2}$", date_value))
        display_date = date_value if is_exact_date else "2026-07-10_11"
        rows.append(
            {
                "company": f"{row.get('company_zh')} / {row.get('company_en')}",
                "title": row.get("event_title_zh") or row.get("event_title_en"),
                "date": display_date,
                "raw_date": date_value,
                "time": "-".join(part for part in [row.get("start_time_kst", ""), row.get("end_time_kst", "")] if part and part != "unknown"),
                "location": row.get("location_public", ""),
                "area": row.get("area_hint", ""),
                "url": (row.get("source_url") or "").split(" ; ", 1)[0],
                "source_type": row.get("source_type", ""),
                "confidence": row.get("confidence", ""),
                "status": row.get("status", ""),
                "note": row.get("notes_zh", ""),
                "bucket": bucket,
            }
        )

    rows.append(
        {
            "company": "Qwen / Alibaba Cloud Korea",
            "title": "Qwen Meetup Seoul #3 - Agent AI",
            "date": "2026-07-09",
            "raw_date": "2026-07-09",
            "time": "18:30-21:00",
            "location": "Team Sparta, Seoul",
            "area": "Seoul",
            "url": "https://luma.com/pd7uf8d8",
            "source_type": "direct_rsvp",
            "confidence": "high",
            "status": "public_rsvp",
            "note": "公开 Qwen / Alibaba Cloud Korea 活动页，标题不写 ICML，但发生在 ICML Seoul 周。",
            "bucket": "confirmed",
        }
    )

    rank = {
        "Kuaishou": 0,
        "Alibaba": 1,
        "Qwen": 2,
        "Tencent": 3,
        "ByteDance": 4,
        "Huawei": 5,
        "Xiaomi": 6,
        "Meituan": 7,
        "Shanghai AI Laboratory": 8,
        "Jiangmen Venture": 9,
        "ShanghaiTech University": 10,
    }

    def sort_key(row: dict[str, str]) -> tuple[int, str]:
        text = row.get("company", "")
        order = next((value for key, value in rank.items() if key in text), 99)
        return order, row.get("date", "")

    return sorted(rows, key=sort_key)


def build_focus() -> dict[str, object]:
    papers = read_csv("icml2026_papers_tagged.csv")
    return {
        "generated_at": "2026-07-03",
        "focus_groups": build_focus_groups(papers),
    }


def paper_flags(row: dict[str, str]) -> str:
    flags = []
    if row.get("is_oral") == "yes":
        flags.append("oral-linked")
    if row.get("is_spotlight") == "yes":
        flags.append("spotlight")
    if row.get("is_position") == "yes":
        flags.append("position")
    if row.get("is_journal_track") == "yes":
        flags.append("journal")
    return ", ".join(flags)


def paper_example(paper: dict[str, str]) -> dict[str, object]:
    return {
        "position": paper.get("poster_position", ""),
        "title": paper.get("title", ""),
        "flags": paper_flags(paper),
        "url": paper.get("poster_url", ""),
        **paper_interest(paper),
    }


def count_fact(value: str, label: str) -> str:
    count = int_value(value)
    return f"{count} {label}" if count else ""


def readable_ticket(value: str) -> str:
    value = (value or "").strip()
    if not value:
        return "RSVP"
    lowered = value.lower()
    if "instock" in lowered:
        return "Open"
    if "limited" in lowered:
        return "Limited"
    if "soldout" in lowered:
        return "Sold out"
    return value.replace("https://schema.org/", "").replace("http://schema.org/", "")


def poster_route_score(row: dict[str, str]) -> float:
    return (
        int_value(row.get("spotlight")) * 8
        + int_value(row.get("oral")) * 5
        + int_value(row.get("position")) * 3
        + int_value(row.get("journal_track")) * 2
        + min(int_value(row.get("papers")), 80) / 10
    )


def topic_family(topic: str) -> str:
    value = topic.lower()
    for key in ["llm", "agent", "safety", "efficient", "systems", "robot", "theory", "optimization", "science", "vision", "multimodal"]:
        if key in value:
            return key
    return topic.split("/")[0].strip().lower()


def pick_diverse(rows: list[dict], limit: int, family_key) -> list[dict]:
    picked = []
    seen = set()
    for row in rows:
        family = family_key(row)
        if family in seen and len(picked) < limit - 1:
            continue
        picked.append(row)
        seen.add(family)
        if len(picked) >= limit:
            break
    for row in rows:
        if row not in picked:
            picked.append(row)
        if len(picked) >= limit:
            break
    return picked[:limit]


def read_csv(name: str) -> list[dict[str, str]]:
    path = PROCESSED / name
    with path.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def read_research_csv(name: str) -> list[dict[str, str]]:
    path = RESEARCH / name
    if not path.exists():
        return []
    with path.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def side_events_with_verified() -> list[dict[str, str]]:
    rows = read_csv("icml2026_side_events.csv")
    seen = {(row.get("date_2026", ""), row.get("title", "").strip().lower(), row.get("rsvp_url", "")) for row in rows}
    for row in VERIFIED_SIDE_EVENTS:
        key = (row["date_2026"], row["title"].strip().lower(), row["rsvp_url"])
        if key not in seen:
            rows.append(row.copy())
            seen.add(key)
    return rows


def visible_side_region(row: dict[str, str]) -> str:
    title = row.get("title", "")
    location = row.get("location_name", "")
    region = row.get("address_region", "")
    if "Google DeepMind" in title:
        return "Gangnam Finance Center"
    if region and any("\uac00" <= char <= "\ud7a3" for char in region):
        return location or "Seoul"
    return region


def side_event_summary(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    counts = Counter(row.get("event_kind", "Other") or "Other" for row in rows)
    return [{"event_kind": kind, "count": str(count)} for kind, count in sorted(counts.items())]


def write_json(name: str, value: object) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")


def write_guide_plans(plans_by_day: dict[str, list[dict[str, object]]]) -> None:
    shutil.rmtree(OUT / "guide_plans", ignore_errors=True)
    for date, plans in plans_by_day.items():
        write_json(f"guide_plans/{date}.json", plans)


def write_star_papers(star_papers: dict[str, object]) -> None:
    shutil.rmtree(OUT / "star_papers", ignore_errors=True)
    rows_by_day: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in star_papers.get("papers", []):
        rows_by_day[str(row.get("date", ""))].append(row)
    for date, rows in rows_by_day.items():
        write_json(f"star_papers/{date}.json", {"papers": rows})


def maps_search_url(query: str) -> str:
    return "https://www.google.com/maps/search/?api=1&" + urlencode({"query": query})


def maps_directions_url(origin: str, destination: str, travelmode: str = "transit") -> str:
    return "https://www.google.com/maps/dir/?api=1&" + urlencode(
        {"origin": origin, "destination": destination, "travelmode": travelmode}
    )


def airport_route_steps() -> list[dict[str, object]]:
    return [
        {
            "name": "ICN T1 -> COEX · AREX + Line 9",
            "badge": "Subway",
            "badge_kind": "ok",
            "duration": "live timing",
            "fare": "",
            "summary": "Airport Railroad to Gimpo, then Line 9 to the COEX side.",
            "steps": [
                {"kind": "rail", "line": "AREX", "text": "Take Airport Railroad from Incheon Airport toward Gimpo Airport."},
                {"kind": "rail", "line": "Line 9", "text": "Transfer at Gimpo Airport to Subway Line 9 toward Bongeunsa."},
                {"kind": "walk", "line": "Exit 7", "text": "Walk from Bongeunsa Station Exit 7 through ASEM Plaza to COEX."},
            ],
            "google_maps_directions_url": maps_directions_url("Incheon Airport Terminal 1, 272 Gonghang-ro, Yeongjong-gu, Incheon", COEX_QUERY, "transit"),
            "source_url": SEOUL_AIRPORT_SOURCE,
        },
    ]


def travel_hotel() -> dict[str, str]:
    return {
        "name_zh": "普罗威斯塔酒店",
        "name_en": "Provista Hotel",
        "area": "Seocho",
        "address_zh": PROVISTA_ADDRESS,
        "address_en": PROVISTA_ADDRESS,
        "commute_hint": "Nearest practical route: Seoul Nat'l Univ. of Education Station -> Line 2 -> Samseong Station -> COEX.",
        "maps_url": maps_search_url(PROVISTA_QUERY),
        "directions_to_coex_url": maps_directions_url(PROVISTA_QUERY, COEX_QUERY, "transit"),
        "source_url": PROVISTA_SOURCE,
    }


def int_value(value: str) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def short_text(value: str, limit: int) -> str:
    value = " ".join((value or "").split())
    if len(value) <= limit:
        return value
    return value[: limit - 1].rstrip() + "…"


def normalize_time(value: str) -> str:
    value = (value or "").strip().lower()
    if not value:
        return ""
    ampm = ""
    if value.endswith("am") or value.endswith("pm"):
        ampm = value[-2:]
        value = value[:-2].strip()
    parts = value.split(":", 1)
    try:
        hour = int(parts[0])
        minute = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 0
    except ValueError:
        return ""
    if ampm == "pm" and hour < 12:
        hour += 12
    if ampm == "am" and hour == 12:
        hour = 0
    return f"{hour:02d}:{minute:02d}"


def normalize_conference_time(value: str) -> str:
    normalized = normalize_time(value)
    if not normalized:
        return ""
    hour, minute = normalized.split(":", 1)
    hour_int = int(hour)
    if 1 <= hour_int <= 7:
        hour_int += 12
    return f"{hour_int:02d}:{minute}"


def normalize_side_event_time(value: str, end_value: str, event_kind: str, title: str) -> str:
    raw = (value or "").strip().lower()
    normalized = normalize_time(raw)
    if not normalized:
        return ""
    context = " ".join([end_value or "", event_kind or "", title or ""]).lower()
    if ("am" not in raw and "pm" not in raw) and (
        "pm" in context
        or "evening" in context
        or "dinner" in context
        or "happy" in context
        or "social" in context
        or "after" in context
        or "night" in context
        or "party" in context
    ):
        hour, minute = normalized.split(":", 1)
        hour_int = int(hour)
        if 1 <= hour_int <= 11:
            return f"{hour_int + 12:02d}:{minute}"
    return normalized


def parse_side_event_clock(value: str) -> tuple[int, int, str] | None:
    text = " ".join((value or "").split())
    if not text:
        return None
    if "," in text:
        text = text.rsplit(",", 1)[1]
    matches = list(re.finditer(r"\b(\d{1,2})(?::(\d{2}))?\s*(am|pm)?\b", text, flags=re.I))
    if not matches:
        return None
    match = matches[-1]
    return int(match.group(1)), int(match.group(2) or "0"), (match.group(3) or "").lower()


def to_24h_clock(hour: int, minute: int, ampm: str, fallback_hour: int | None = None) -> str:
    hour_24 = hour
    if ampm == "pm" and hour_24 < 12:
        hour_24 += 12
    elif ampm == "am" and hour_24 == 12:
        hour_24 = 0
    elif not ampm and fallback_hour is not None:
        hour_24 = fallback_hour
    return f"{hour_24:02d}:{minute:02d}"


def format_side_event_time_range(start_value: str, end_value: str, date_value: str, event_kind: str = "", title: str = "") -> str:
    start_clock = parse_side_event_clock(start_value)
    if not start_clock:
        return ""
    start_hour, start_minute, start_ampm = start_clock
    normalized_start = normalize_side_event_time(start_value, end_value, event_kind, title)
    normalized_start_hour = int(normalized_start.split(":", 1)[0]) if normalized_start else None
    start_label = to_24h_clock(start_hour, start_minute, start_ampm, normalized_start_hour)

    end_clock = parse_side_event_clock(end_value)
    if not end_clock:
        return start_label
    end_hour, end_minute, end_ampm = end_clock
    if not end_ampm:
        start_hour_24 = int(start_label.split(":", 1)[0])
        if start_hour_24 >= 12 and end_hour < start_hour:
            end_ampm = "am"
        elif start_hour_24 >= 12:
            end_ampm = "pm"
        else:
            end_ampm = start_ampm
    return f"{start_label}-{to_24h_clock(end_hour, end_minute, end_ampm)}"


def side_event_time_label(row: dict[str, str]) -> str:
    return format_side_event_time_range(
        row.get("start_time", ""),
        row.get("end_time", ""),
        row.get("date_2026", ""),
        row.get("event_kind", ""),
        row.get("title", ""),
    )


def compact_side_event_time(raw_time: str, date_value: str) -> str:
    raw_time = " ".join((raw_time or "").split())
    if not raw_time:
        return ""
    if "onward" in raw_time.lower():
        return raw_time
    if re.match(r"^\d{1,2}:\d{2}-\d{1,2}:\d{2}(?: \(\+[^)]+\))?$", raw_time):
        return raw_time
    if " - " in raw_time:
        return raw_time
    start, end = (raw_time.split(" ", 1) + [""])[:2]
    return format_side_event_time_range(start, end, date_value) or raw_time


def side_event_time_for_row(row: dict[str, str]) -> str:
    return side_event_time_label(row) or compact_side_event_time(
        " ".join(part for part in [row.get("start_time", ""), row.get("end_time", "")] if part),
        row.get("date_2026", ""),
    )


def side_event_priority(row: dict[str, str]) -> int:
    text = " ".join([row.get("title", ""), row.get("organizer_guess", ""), row.get("organizer_verified", ""), row.get("event_kind", "")]).lower()
    score = 0
    for needle in ["qwen", "alibaba", "kuaishou", "快手", "k-star", "openai", "google", "deepmind", "aws", "jane street", "hugging face", "vessl", "upstage", "furiosa"]:
        if needle in text:
            score += 35
    if "dinner" in text or "social" in text or "meetup" in text or "happy hour" in text:
        score += 18
    if row.get("detail_start") or row.get("location_name") or row.get("address_region"):
        score += 10
    if "manual_verified" in row.get("confidence", "") or "detail_page" in row.get("confidence", ""):
        score += 12
    return score


def side_event_candidate(row: dict[str, str]) -> dict[str, object]:
    time_label = side_event_time_for_row(row)
    organizer = row.get("organizer_guess") or row.get("organizer_verified") or row.get("event_kind")
    location = row.get("location_name") or row.get("address_region") or "Location after RSVP"
    if location == "Seoul, South Korea":
        location = ""
    ticket = readable_ticket(row.get("ticket_availability", ""))
    facts = [part for part in [time_label, row.get("event_kind"), ticket] if part]
    topics = [part for part in [organizer, row.get("platform")] if part][:2]
    title = row.get("title", "")
    if title.startswith("Let’s Talk Robots & AI"):
        title = "Let’s Talk Robots & AI"
    return {
        "verdict": "RSVP",
        "type": "side_event",
        "title": title,
        "where": location,
        "see": row.get("event_kind", ""),
        "topics": topics,
        "facts": facts,
        "fit": "",
        "why": row.get("notes", ""),
        "route": row.get("address_region") or row.get("location_name") or "RSVP page",
        "url": row.get("rsvp_url", ""),
        "source_url": row.get("source_url", ""),
        "map_url": "",
        "examples": [
            {
                "time": time_label,
                "title": organizer,
                "location": location,
            }
        ],
        "score": side_event_priority(row),
    }


def company_event_candidate(row: dict[str, str]) -> dict[str, object]:
    title = row.get("title", "")
    date = row.get("date", "")
    time = row.get("time") or "time TBD"
    location = row.get("location") or row.get("area") or "Location TBD"
    bucket = row.get("bucket", "watch")
    status_label = {
        "confirmed": "Confirmed",
        "watch": "线索 / Lead",
        "not_found": "No public source",
    }.get(bucket, "Lead")
    return {
        "verdict": status_label,
        "type": "company_event",
        "title": title,
        "where": location,
        "see": " · ".join(part for part in [date, time, row.get("company", "")] if part and part != "unknown"),
        "topics": [part for part in [row.get("company", ""), status_label] if part][:2],
        "facts": [part for part in [time if time != "time TBD" else "", row.get("confidence", ""), row.get("source_type", "")] if part][:3],
        "fit": "",
        "why": row.get("note", ""),
        "route": row.get("area", ""),
        "url": row.get("url", ""),
        "source_url": row.get("url", ""),
        "map_url": "",
        "examples": [],
        "score": 100 if bucket == "confirmed" else 62 if bucket == "watch" else 20,
    }


def is_company_side_event(row: dict[str, str]) -> bool:
    text = " ".join(
        [
            row.get("title", ""),
            row.get("organizer_guess", ""),
            row.get("organizer_verified", ""),
            row.get("notes", ""),
        ]
    ).lower()
    return any(
        needle in text
        for needle in [
            "kuaishou",
            "快手",
            "k-star",
            "qwen meetup seoul #3",
            "alibaba cloud korea",
        ]
    )


def key_by_date(rows: list[dict[str, str]], date_key: str = "date") -> dict[str, list[dict[str, str]]]:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[row.get(date_key, "")].append(row)
    return dict(sorted(grouped.items()))


def build_manifest() -> dict[str, object]:
    papers = read_csv("icml2026_papers_tagged.csv")
    sessions = read_csv("icml2026_sessions.csv")
    side_events = side_events_with_verified()
    opportunities = read_csv("icml2026_onsite_opportunities.csv")
    workshops = read_csv("icml2026_workshops.csv")

    days = ["2026-07-06", "2026-07-07", "2026-07-08", "2026-07-09", "2026-07-10", "2026-07-11"]
    nav_days = ["2026-07-06", "2026-07-07", "2026-07-08", "2026-07-09", "2026-07-10_11"]
    topic_counts = Counter()
    for row in papers:
        for topic in (row.get("topic_tracks") or "").split(" | "):
            if topic:
                topic_counts[topic] += 1

    return {
        "generated_at": "2026-07-02",
        "conference": {
            "name_zh": "ICML 2026 逛会指南",
            "name_en": "ICML 2026 Field Guide",
            "venue_zh": "首尔 COEX 会展中心",
            "venue_en": "COEX Convention & Exhibition Center, Seoul",
            "timezone": "Asia/Seoul",
            "dates": days,
            "nav_dates": nav_days,
        },
        "counts": {
            "papers": len(papers),
            "onsite_papers": sum(row.get("attention_bucket") == "现场可逛" for row in papers),
            "extra_attention": sum(row.get("attention_bucket") != "现场可逛" for row in papers),
            "orals": sum(row.get("is_oral") == "yes" for row in papers),
            "spotlights": sum(row.get("is_spotlight") == "yes" for row in papers),
            "sessions": len(sessions),
            "workshops": len(workshops),
            "side_events": len(side_events),
            "opportunities": len(opportunities),
        },
        "topic_counts": topic_counts.most_common(),
    }


def build_today() -> dict[str, object]:
    practical = read_csv("icml2026_practical_info.csv")
    checklist = read_csv("icml2026_pretrip_checklist.csv")
    sessions = read_csv("icml2026_sessions.csv")
    side_events = side_events_with_verified()
    opportunities = read_csv("icml2026_onsite_opportunities.csv")

    must_know_categories = {
        "official_schedule",
        "badge_access",
        "onsite_services",
        "conference_tools",
        "weather",
        "sponsors_expo",
    }
    must_know = [
        {
            "category": row["category"],
            "title_zh": row["item_zh"],
            "title_en": row["item_en"],
            "time": row["date_or_time_kst"],
            "location_zh": row["location_zh"],
            "location_en": row["location_en"],
            "action_zh": row["action_zh"],
            "action_en": row["action_en"],
            "needs_recheck": row["needs_recheck"],
            "source_url": row["source_url"],
        }
        for row in practical
        if row.get("guide_priority") == "must_include" and row.get("category") in must_know_categories
    ]

    schedule_by_day = {}
    for date, rows in key_by_date(sessions).items():
        ordered = sorted(rows, key=lambda item: (item["start_time"], item["title"]))
        schedule_by_day[date] = [
            {
                "time": f"{row['start_time']}-{row['end_time']}",
                "type": row["event_type"],
                "title": row["title"],
                "room": row["room"],
                "url": row["session_url"],
            }
            for row in ordered
        ]

    event_by_day = {}
    for date, rows in key_by_date(side_events, "date_2026").items():
        event_by_day[date] = [
            {
                "time": side_event_time_for_row(row),
                "title": row["title"],
                "kind": row["event_kind"],
                "region": row["address_region"],
                "url": row["rsvp_url"],
                "confidence": row["confidence"],
                "ticket": row["ticket_availability"],
            }
            for row in rows
        ]

    timeline_by_day: dict[str, list[dict[str, str]]] = defaultdict(list)
    timeline_by_day["2026-07-06"].extend(
        [
            {
                "sort_time": "08:00",
                "time": "All day",
                "kind": "official_session",
                "title": "Expo / Tutorial Day",
                "subtitle_zh": "熟悉 COEX、看 Expo talks / demos / workshops，并准备主会路线。",
                "subtitle_en": "Use the day for COEX orientation, Expo talks/demos/workshops, and main-conference planning.",
                "url": "https://icml.cc/virtual/2026/events/2026-Expo",
                "status": "official",
                "action_label": "Open ICML",
            }
        ]
    )
    for row in sessions:
        timeline_by_day[row["date"]].append(
            {
                "sort_time": row["start_time"],
                "time": f"{row['start_time']}-{row['end_time']}",
                "kind": "official_session",
                "title": row["title"],
                "subtitle_zh": f"{row['event_type']} · {row['room']}",
                "subtitle_en": f"{row['event_type']} · {row['room']}",
                "url": row["session_url"],
                "status": "official",
                "action_label": "Open ICML",
            }
        )

    for row in side_events:
        if not row.get("date_2026"):
            continue
        timeline_by_day[row["date_2026"]].append(
            {
                "sort_time": normalize_side_event_time(row["start_time"], row["end_time"], row["event_kind"], row["title"]) or "23:59",
                "time": side_event_time_for_row(row),
                "kind": "side_event",
                "title": row["title"],
                "subtitle_zh": f"{row['event_kind']} · {row['address_region'] or 'RSVP 后确认地点'}",
                "subtitle_en": f"{row['event_kind']} · {row['address_region'] or 'Location after RSVP'}",
                "url": row["rsvp_url"],
                "status": "recheck",
                "action_label": "RSVP",
            }
        )

    sorted_timeline = {
        date: sorted(rows, key=lambda item: (item["sort_time"], item["kind"], item["title"]))
        for date, rows in sorted(timeline_by_day.items())
    }

    return {
        "checklist": [
            {
                "phase": row["phase"],
                "task_zh": row["task_zh"],
                "task_en": row["task_en"],
                "why_zh": row["why_zh"],
                "why_en": row["why_en"],
                "source_url": row["source_url"],
                "priority": row["priority"],
            }
            for row in checklist
        ],
        "must_know": must_know,
        "schedule_by_day": schedule_by_day,
        "side_events_by_day": event_by_day,
        "timeline_by_day": sorted_timeline,
        "top_opportunities": [
            row for row in opportunities if row.get("priority") in {"P0", "P1"}
        ][:12],
    }


def build_guide_plans() -> dict[str, list[dict[str, object]]]:
    sessions = read_csv("icml2026_sessions.csv")
    scheduled_items = read_csv("icml2026_scheduled_items.csv")
    papers = read_csv("icml2026_papers_tagged.csv")
    topic_summary = read_csv("icml2026_topic_session_summary.csv")
    side_events = side_events_with_verified()
    workshops = read_csv("icml2026_workshops.csv")

    papers_by_title = {row["title"].strip().lower(): row for row in papers if row.get("title")}
    papers_by_session_topic: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in papers:
        for topic in (row.get("topic_tracks") or "").split(" | "):
            if topic:
                papers_by_session_topic[(row.get("poster_session_id", ""), topic)].append(row)
    for rows in papers_by_session_topic.values():
        rows.sort(key=paper_score, reverse=True)

    items_by_session: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in scheduled_items:
        items_by_session[row["session_id"]].append(row)

    oral_groups: dict[tuple[str, str, str], list[dict[str, str]]] = defaultdict(list)
    for row in sessions:
        if row.get("event_type") == "Oral Session":
            start = normalize_conference_time(row["start_time"])
            end = normalize_conference_time(row["end_time"])
            oral_groups[(row["date"], start, end)].append(row)

    poster_groups: dict[tuple[str, str, str, str, str], list[dict[str, str]]] = defaultdict(list)
    for row in topic_summary:
        if not row.get("date") or not row.get("session_id"):
            continue
        start = normalize_conference_time(row["session_start_time"])
        end = normalize_conference_time(row["session_end_time"])
        poster_groups[(row["date"], start, end, row["session_title"], row["session_id"])].append(row)

    plans_by_day: dict[str, list[dict[str, object]]] = defaultdict(list)
    official_social_candidates = [
        {
            "verdict": "Maybe",
            "type": "official_social",
            "title": title,
            "where": "",
            "see": "Official ICML social",
            "topics": ["Official Social", "Networking"],
            "facts": ["19:00-21:00"],
            "fit": "如果晚上不想赌外部 RSVP，可以直接选官方 social。",
            "why": "官方 ICML social，不是 Luma side event。",
            "route": "ASEM 在 2F；Room 300 / Room E 在 3F，晚间不要把它们当成同一个区域。",
            "url": url,
            "map_url": FLOOR_MAP_URL,
            "examples": [],
            "score": 86,
        }
        for title, url in [
            ("AI Co-scientists in the Research Loop: Share, Compare, Critique", "https://icml.cc/virtual/2026/social/80670"),
            ("The ICML Chess Club: Blitz, Bullet, and Over-the-Board Networking", "https://icml.cc/virtual/2026/social/80671"),
            ("AI for Games", "https://icml.cc/virtual/2026/social/80673"),
            ("India @ ICML: Numbers, Stories & What's Next", "https://icml.cc/virtual/2026/social/80672"),
        ]
    ]
    plans_by_day["2026-07-06"].append(
        {
            "date": "2026-07-06",
            "sort_time": "09:00",
            "time": "09:00-17:00",
            "title": "Venue activities",
            "kind": "official_slot",
            "summary": "Official daytime picks: tutorials, nearby demos, and RAI mentoring.",
            "candidates": [
                {
                    "verdict": "Go",
                    "type": "tutorial",
                    "title": "Morning tutorials: pick one research block",
                    "where": "Auditorium, Hall B2, Hall D1",
                    "see": "Jul 6 09:00-11:30 · Tutorials",
                    "topics": ["Tutorial", "Privacy / Governance", "Diffusion", "Theorem Proving"],
                    "facts": ["09:00-11:30", "Auditorium / Hall B2 / Hall D1"],
                    "fit": "如果你不想第一天只逛展，上午 tutorial 是最稳的官方研究内容。",
                    "why": "Unlearning、diffusion/flow matching、Lean+ML 都比随机 demo 更像主会前热身。",
                    "route": "先确认房间：Auditorium、Hall B2、Hall D1 分散在不同区域，别临开场再换。",
                    "url": "https://icml.cc/virtual/2026/events/tutorial",
                    "map_url": FLOOR_MAP_URL,
                    "examples": [
                        {
                            "time": "09:00-11:30",
                            "title": "Unlearning Data at Scale",
                            "url": "https://icml.cc/virtual/2026/75372",
                        },
                        {
                            "time": "09:00-11:30",
                            "title": "Diffusion and Flow-Matching: From Memorization to Generalization & Beyond",
                            "url": "https://icml.cc/virtual/2026/75374",
                        },
                        {
                            "time": "09:00-11:30",
                            "title": "Proving Theorems with Lean and Machine Learning",
                            "url": "https://icml.cc/virtual/2026/75365",
                        },
                    ],
                    "score": 126,
                },
                {
                    "verdict": "Maybe",
                    "type": "expo",
                    "title": "Grand Ballroom Foyer demos",
                    "where": "Grand Ballroom Foyer",
                    "see": "Jul 6 12:30-14:30 · Xiaomi GUI Agent + Alibaba e-commerce demo",
                    "topics": ["GUI Agent", "Device AI", "E-commerce"],
                    "facts": ["12:30-14:30", "Grand Ballroom Foyer"],
                    "fit": "适合看手机 GUI agent、端侧 AI、电商推荐和购物 agent 的人。",
                    "why": "同一时段同一地点，合并成一站；如果刚好在 1F North / Grand Ballroom 附近，顺手扫最划算。",
                    "route": room_hint("GRAND BALLROOM"),
                    "url": "https://icml.cc/virtual/2026/events/2026-Expo",
                    "map_url": FLOOR_MAP_URL,
                    "examples": [
                        {
                            "time": "12:30-14:30",
                            "title": "Xiaomi GUI Agent",
                            "url": "https://icml.cc/virtual/2026/75720",
                        },
                        {
                            "time": "12:30-14:30",
                            "title": "AI for International E-Commerce",
                            "url": "https://icml.cc/virtual/2026/75719",
                        },
                    ],
                    "score": 112,
                },
                {
                    "verdict": "Go",
                    "type": "tutorial",
                    "title": "Afternoon tutorials: LLM reasoning / calibration",
                    "where": "Hall C, Auditorium, Hall B2",
                    "see": "Jul 6 13:30-16:00 · Tutorials",
                    "topics": ["Tutorial", "LLM", "Reasoning", "Calibration", "Alignment"],
                    "facts": ["13:30-16:00", "Hall C / Auditorium / Hall B2"],
                    "fit": "适合做 LLM post-training、test-time reasoning、可靠性和 alignment 的人。",
                    "why": "Adaptive reasoning 和 calibration/alignment 都比大部分 sponsor demo 更贴近主会研究线。",
                    "route": "Hall C 在 3F；Auditorium 和 Hall B2 不在同一个点位，提前选定一个。",
                    "url": "https://icml.cc/virtual/2026/events/tutorial",
                    "map_url": FLOOR_MAP_URL,
                    "examples": [
                        {
                            "time": "13:30-16:00",
                            "title": "Adaptive Reasoning in LLMs: From Post-Training to Test-Time Learning",
                            "url": "https://icml.cc/virtual/2026/75366",
                        },
                        {
                            "time": "13:30-16:00",
                            "title": "Calibration: From Predictions to Decisions, Collaboration, and Alignment",
                            "url": "https://icml.cc/virtual/2026/75369",
                        },
                        {
                            "time": "13:30-16:00",
                            "title": "Evaluating and Training LLMs for Math Copilots and Theorem Proving",
                            "url": "https://icml.cc/virtual/2026/75367",
                        },
                    ],
                    "score": 124,
                },
                {
                    "verdict": "Go",
                    "type": "mentorship",
                    "title": "RAI Mentoring Circle",
                    "where": "ASEM Ballroom 201-203",
                    "see": "Jul 6 13:00-17:00 · Responsible AI mentoring",
                    "topics": ["Responsible AI", "Mentoring", "Networking"],
                    "facts": ["13:00-17:00", "ASEM Ballroom 201-203"],
                    "fit": "适合 early-career、想找 responsible AI / safety 社群入口的人。",
                    "why": "这是官方 mentoring，不是 sponsor 展台；如果目标是认识人，比盲逛更有效。",
                    "route": room_hint("ASEM BALLROOM 201-203"),
                    "url": "https://icml.cc/virtual/2026/mentorship/80259",
                    "map_url": FLOOR_MAP_URL,
                    "score": 116,
                },
            ],
        }
    )
    plans_by_day["2026-07-06"].append(
        {
            "date": "2026-07-06",
            "sort_time": "07:30",
            "time": "First arrival",
            "title": "第一天先把会场摸清楚",
            "kind": "onsite_slot",
            "summary": "到 COEX 后先解决会场锚点：Hall A poster、oral 房间、Grand Ballroom/ASEM。",
            "candidates": [
                {
                    "verdict": "Badge",
                    "type": "onsite_tip",
                    "title": "Pick up badge at Hall B Foyer",
                    "where": "Hall B Foyer, East Gate",
                    "see": "Registration Desk: Jul 6 07:00-18:00.",
                    "topics": ["Badge", "Registration"],
                    "facts": ["07:00-18:00", "Hall B Foyer", "East Gate"],
                    "fit": "",
                    "why": "",
                    "route": "Registration Desk 在 Hall B Foyer，可从 East Gate 进入；Help Desk / Lost and Found 也在这个锚点。",
                    "url": "https://icml.cc/virtual/2026/registration-desk/77230",
                    "map_url": FLOOR_MAP_URL,
                    "examples": [],
                    "score": 130,
                },
                {
                    "verdict": "Bag",
                    "type": "onsite_tip",
                    "title": "Luggage and coat check",
                    "where": "2F inside the Plaetz",
                    "see": "Jul 6 07:30-19:30 · 2F inside the Plaetz.",
                    "topics": ["Luggage", "Coat check"],
                    "facts": ["07:30-19:30", "2F Plaetz"],
                    "fit": "",
                    "why": "",
                    "route": "带箱子或退房后先去 2F Plaetz 寄存，再回 Hall B Foyer / Hall A / tutorial 房间。",
                    "url": "https://icml.cc/Conferences/2026/AtTheConference",
                    "map_url": FLOOR_MAP_URL,
                    "examples": [],
                    "score": 112,
                },
                {
                    "verdict": "Walk",
                    "type": "onsite_tip",
                    "title": "走一遍 Hall A / C / D / E / Grand Ballroom",
                    "where": "Hall A; Hall C/D/Room E; Grand Ballroom; ASEM",
                    "see": "Hall A 是 poster；C/D/E 多在 3F；Grand Ballroom 在 1F North；ASEM 在 2F。",
                    "topics": ["Hall A", "3F rooms"],
                    "facts": ["Map", "Route"],
                    "fit": "",
                    "why": "",
                    "route": "Hall A 是 poster 主场；C/D/E 多在 3F；ASEM 在 2F；Grand Ballroom 在 1F North。",
                    "url": FLOOR_MAP_URL,
                    "map_url": FLOOR_MAP_URL,
                    "examples": [],
                    "score": 90,
                },
                {
                    "verdict": "Expo",
                    "type": "onsite_tip",
                    "title": "看 Grand Ballroom Foyer 的公司 demo",
                    "where": "Grand Ballroom Foyer",
                    "see": "小米 GUI Agent、Alibaba e-commerce 等 demo 在第一天中午。",
                    "topics": ["Xiaomi", "Alibaba", "Expo"],
                    "facts": ["Grand Ballroom Foyer", "12:30-14:30"],
                    "fit": "",
                    "why": "",
                    "route": room_hint("GRAND BALLROOM"),
                    "url": "https://icml.cc/virtual/2026/events/2026-Expo",
                    "map_url": FLOOR_MAP_URL,
                    "examples": [],
                    "score": 70,
                },
            ],
        }
    )

    workshops_by_date: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in workshops:
        workshops_by_date[row["date"]].append(row)
    for date, rows in sorted(workshops_by_date.items()):
        rows.sort(
            key=lambda item: (
                -int(personal_interest(item["title"], item["abstract"]).get("interest_stars", 0)),
                item["room"],
                item["title"],
            )
        )
        label = "Jul 10" if date == "2026-07-10" else "Jul 11"
        workshop_candidates = []
        for row in rows:
            interest = personal_interest(row["title"], row["abstract"])
            workshop_candidates.append(
                {
                    "verdict": "Workshop",
                    "type": "workshop",
                    "title": row["title"],
                    "where": row["room"],
                    "see": f"{row['time_label']} · {row['room']}",
                    "topics": workshop_topics(row["title"], row["abstract"]),
                    "facts": [row["time_label"], row["room"], "9h"],
                    "fit": "",
                    "why": "",
                    "route": room_hint(row["room"]),
                    "url": row["url"],
                    "map_url": FLOOR_MAP_URL,
                    "examples": [],
                    "score": 0,
                    **interest,
                }
            )
        plans_by_day["2026-07-10_11"].append(
            {
                "date": "2026-07-10_11",
                "sort_time": f"{date} 08:00",
                "time": f"{label} · 08:00-17:00",
                "title": f"{label} · Workshops",
                "kind": "workshop_slot",
                "summary": f"{label} 有 {len(rows)} 个 workshop，全部 08:00-17:00；按主题和房间横向选。",
                "candidates": workshop_candidates,
            }
        )

    for (date, start, end), rows in oral_groups.items():
        candidates = []
        for row in rows:
            session_code, session_title = split_session_code(row["title"])
            items = items_by_session.get(row["session_id"], [])
            matched = [papers_by_title.get(item.get("title", "").strip().lower()) for item in items]
            matched = [paper for paper in matched if paper]
            topic_counts = Counter()
            for paper in matched:
                for topic in (paper.get("topic_tracks") or "").split(" | "):
                    if topic:
                        topic_counts[topic] += 1
            score = (
                len(matched) * 10
                + sum(p.get("is_spotlight") == "yes" for p in matched) * 6
                + sum(p.get("is_position") == "yes" for p in matched) * 4
                + sum(p.get("is_journal_track") == "yes" for p in matched) * 3
                + sum(bool(p.get("code_or_project_url")) for p in matched)
                + len(topic_counts)
            )
            top_topics = [topic for topic, _ in topic_counts.most_common(4)]
            interest = aggregate_interest(matched, session_title, row["title"])
            candidates.append(
                {
                    "verdict": "Go",
                    "type": "oral",
                    "code": session_code,
                    "title": session_title,
                    "where": row["room"],
                    "see": f"{len(items)} oral talks",
                    "topics": top_topics,
                    "facts": [f"{len(items)} oral talks"],
                    "fit": persona_for(top_topics[0] if top_topics else row["title"]),
                    "why": "并行 oral 里信息密度较高；想听成体系短讲时，比随机扫 poster 更有效。",
                    "route": room_hint(row["room"]),
                    "url": row["session_url"],
                    "map_url": FLOOR_MAP_URL,
                    "examples": [
                        {
                            "time": normalize_conference_time(item.get("item_time", "")) or item.get("item_time", ""),
                            "title": item.get("title", ""),
                            "url": item.get("item_url", "") or row["session_url"],
                            **paper_interest(papers_by_title.get(item.get("title", "").strip().lower())),
                        }
                        for item in items
                    ],
                    "score": score,
                    **interest,
                }
            )
        candidates.sort(key=lambda item: (-int(item.get("interest_stars", 0)), -int(item.get("interest_score", 0)), -int(item["score"])))
        picked = candidates[:7]
        plans_by_day[date].append(
            {
                "date": date,
                "sort_time": start,
                "time": f"{start}-{end}",
                "title": f"{start}-{end} · Oral choices",
                "kind": "oral_slot",
                "summary": "7 个 oral 并行，别全看；按主题选一个房间扎进去。",
                "candidates": picked,
            }
        )

    for (date, start, end, session_title, session_id), rows in poster_groups.items():
        all_session_papers = sorted(
            [
                paper
                for (paper_session_id, _topic), topic_papers in papers_by_session_topic.items()
                if paper_session_id == session_id
                for paper in topic_papers
            ],
            key=lambda paper: (
                -int(paper_interest(paper).get("interest_score", 0)),
                -paper_focus_score(paper),
                paper.get("poster_position", ""),
            ),
        )
        unique_session_papers = []
        seen_titles_for_focus = set()
        for paper in all_session_papers:
            title_key = paper.get("title", "").strip().lower()
            if title_key in seen_titles_for_focus:
                continue
            seen_titles_for_focus.add(title_key)
            if int(paper_interest(paper).get("interest_score", 0)) >= 11:
                unique_session_papers.append(paper)
            if len(unique_session_papers) >= 6:
                break

        def topic_best_interest(row: dict[str, str]) -> tuple[int, int, float]:
            topic_papers = papers_by_session_topic.get((session_id, row["topic_track"]), [])
            best_interest = max([int(paper_interest(paper).get("interest_score", 0)) for paper in topic_papers] or [0])
            return best_interest, int(personal_interest(row["topic_track"]).get("interest_stars", 0)), poster_route_score(row)

        ranked = sorted(rows, key=lambda row: (-topic_best_interest(row)[0], -topic_best_interest(row)[1], -topic_best_interest(row)[2]))
        picked_topics = pick_diverse(ranked, 3, lambda row: topic_family(row["topic_track"]))
        candidates = []
        used_titles: set[str] = set()
        if unique_session_papers:
            used_titles.update(paper.get("title", "").strip().lower() for paper in unique_session_papers)
            focus_interest = aggregate_interest(unique_session_papers[:6], "personal focus", session_title)
            candidates.append(
                {
                    "verdict": "Go",
                    "type": "poster_route",
                    "title": session_title,
                    "where": "HALL A",
                    "see": f"{len(unique_session_papers)} priority posters",
                    "topics": ["Video / MLLM", "Personal"],
                    "facts": [f"{len(unique_session_papers)} picks", "deduped"],
                    "fit": "",
                    "why": "",
                    "route": "同一时间段先按这些 poster number 找，不要在多个 topic route 里反复看同一篇。",
                    "url": next((paper.get("poster_url", "") for paper in unique_session_papers if paper.get("poster_url")), ""),
                    "map_url": FLOOR_MAP_URL,
                    "examples": [paper_example(paper) for paper in unique_session_papers[:6]],
                    "score": max([paper_focus_score(paper) for paper in unique_session_papers] or [0]),
                    **focus_interest,
                }
            )
        for row in picked_topics:
            topic_papers = papers_by_session_topic.get((session_id, row["topic_track"]), [])
            topic_papers = sorted(
                topic_papers,
                key=lambda paper: (
                    -int(paper_interest(paper).get("interest_score", 0)),
                    -int(paper_interest(paper).get("interest_stars", 0)),
                    -paper_focus_score(paper),
                    -paper_score(paper),
                ),
            )
            topic_papers = [paper for paper in topic_papers if paper.get("title", "").strip().lower() not in used_titles]
            if not topic_papers:
                continue
            top_papers = topic_papers[:2]
            top_titles = [paper["title"] for paper in top_papers]
            example_papers = topic_papers[:4]
            used_titles.update(paper.get("title", "").strip().lower() for paper in example_papers)
            interest = aggregate_interest(topic_papers[:4], row["topic_track"], session_title)
            candidates.append(
                {
                    "verdict": "Go",
                    "type": "poster_route",
                    "title": f"{row['topic_track']} 路线 · {session_title}",
                    "where": row["room"],
                    "see": f"{row['papers']} posters",
                    "topics": [row["topic_track"]],
                    "facts": [
                        fact
                        for fact in [
                            count_fact(row["papers"], "posters"),
                            count_fact(row["spotlight"], "spotlight"),
                            count_fact(row["oral"], "oral-linked"),
                            count_fact(row["position"], "position"),
                        ]
                        if fact
                    ],
                    "fit": persona_for(row["topic_track"]),
                    "why": f"这个时间段该方向密度高；可优先找 {'、'.join(top_titles) if top_titles else 'spotlight / oral-linked poster'} 深聊。",
                    "route": "去 Hall A 后按 poster number 扫；先挑 3-5 个摊位，不要从入口开始顺序逛。",
                    "url": row["session_url"],
                    "map_url": FLOOR_MAP_URL,
                    "examples": [
                        paper_example(paper)
                        for paper in example_papers
                    ],
                    "score": poster_route_score(row),
                    **interest,
                }
            )
        candidates.sort(key=lambda item: (-int(item.get("interest_stars", 0)), -int(item.get("interest_score", 0)), -float(item["score"])))
        plans_by_day[date].append(
            {
                "date": date,
                "sort_time": start,
                "time": f"{start}-{end}",
                "title": f"{start}-{end} · Poster routes",
                "kind": "poster_slot",
                "summary": "Hall A 只适合按主题扫；下面是这个 block 里最值得优先看的方向。",
                "candidates": candidates[:8],
            }
        )

    evening_groups: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
    raw_times_by_evening_group: dict[tuple[str, str], list[str]] = defaultdict(list)
    company_title_keys = {
        row.get("title", "").strip().lower()
        for row in company_focus_rows()
        if row.get("date") != "2026-07-10_11"
    }
    for row in side_events:
        date = row.get("date_2026")
        if not date:
            continue
        if date == "2026-07-06" and row.get("title", "").strip().lower() in {"ai for games — icml social", "india@icml 2026"}:
            continue
        if row.get("title", "").strip().lower() in company_title_keys or is_company_side_event(row):
            continue
        start = normalize_side_event_time(row["start_time"], row["end_time"], row["event_kind"], row["title"]) or "23:59"
        if int(start.split(":", 1)[0]) < 17:
            continue
        key = (guide_day_key(date), f"{date} {start}")
        raw_times_by_evening_group[key].append(side_event_time_for_row(row))
        evening_groups[key].append(side_event_candidate(row))
    official_social_key = ("2026-07-06", "2026-07-06 19:00")
    for candidate in official_social_candidates:
        raw_times_by_evening_group[official_social_key].append("19:00-21:00")
        evening_groups[official_social_key].append(candidate)

    for (date, start), candidates in evening_groups.items():
        times = [time for time in raw_times_by_evening_group[(date, start)] if time]
        event_date, sort_start = start.split(" ", 1) if " " in start else (date, start)
        time_label = times[0] if len(set(times)) == 1 else f"{sort_start} onward"
        time_label = compact_side_event_time(time_label, event_date)
        candidates.sort(key=lambda item: (-int(item["score"]), str(item["where"]), str(item["title"])))
        plans_by_day[date].append(
            {
                "date": date,
                "sort_time": start,
                "time": time_label,
                "title": f"{start} · Evening options",
                "kind": "evening_slot",
                "summary": "同一时段的 dinner / meetup 横向选；出发前先打开 RSVP 确认地点。",
                "candidates": candidates[:10],
            }
        )

    company_rows = company_focus_rows()
    company_by_date: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in company_rows:
        date = row.get("date", "")
        if not (re.match(r"^\d{4}-\d{2}-\d{2}$", date) or date == "2026-07-10_11"):
            continue
        if row.get("bucket") == "not_found":
            if date != "2026-07-10_11":
                continue
        company_by_date[date].append(row)

    for date, rows in sorted(company_by_date.items()):
        candidates = [company_event_candidate(row) for row in rows]
        if not candidates:
            continue
        candidates.sort(key=lambda item: (-int(item.get("score", 0)), str(item.get("title", ""))))
        plans_by_day[guide_day_key(date)].append(
            {
                "date": guide_day_key(date),
                "sort_time": f"{date if date != '2026-07-10_11' else '2026-07-10'} 18:00:01",
                "time": "Company leads" if date != "2026-07-10_11" else "Extra company watch",
                "title": "Domestic company dinners / meetups",
                "kind": "company_slot",
                "summary": "已核实活动和媒体/微信线索分开看；未公开 RSVP 的不要直接导航。",
                "candidates": candidates[:8],
            }
        )

    for rows in plans_by_day.values():
        rows.sort(key=lambda item: item["sort_time"])
    return dict(sorted(plans_by_day.items()))


def build_papers() -> dict[str, object]:
    papers = read_csv("icml2026_papers_tagged.csv")
    topic_summary = read_csv("icml2026_topic_session_summary.csv")
    extra_summary = read_csv("icml2026_extra_attention_topic_summary.csv")

    paper_rows = []
    for row in papers:
        paper_rows.append(
            {
                "id": row["poster_id"],
                "title": row["title"],
                "authors": short_text(row["authors"], 180),
                "topic": row["topic"],
                "tracks": row["topic_tracks"],
                "bucket": row["attention_bucket"],
                "date": row["poster_date_kst"],
                "time": row["poster_time_kst"],
                "session": row["poster_session"],
                "room": row["poster_room"],
                "position": row["poster_position"],
                "oral": row["is_oral"] == "yes",
                "spotlight": row["is_spotlight"] == "yes",
                "position_paper": row["is_position"] == "yes",
                "journal": row["is_journal_track"] == "yes",
                "poster_url": row["poster_url"],
                "openreview_url": row["openreview_url"],
            }
        )

    routes_by_topic: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in topic_summary:
        routes_by_topic[row["topic_track"]].append(
            {
                "date": row["date"],
                "time": f"{row['session_start_time']}-{row['session_end_time']}",
                "session": row["session_title"],
                "session_id": row["session_id"],
                "room": row["room"],
                "url": row["session_url"],
                "papers": int_value(row["papers"]),
                "oral": int_value(row["oral"]),
                "spotlight": int_value(row["spotlight"]),
                "position": int_value(row["position"]),
                "journal": int_value(row["journal_track"]),
            }
        )

    return {
        "papers": paper_rows,
        "topic_routes": dict(sorted(routes_by_topic.items())),
        "extra_summary": extra_summary,
    }


STAR_AUTHOR_ALIASES = [
    ("Kaiming He", 120, ["Kaiming He", "He Kaiming", "何恺明", "何凯明"]),
    ("Huazhe Xu", 120, ["Huazhe Xu", "Xu Huazhe", "许华哲"]),
    ("Michael I. Jordan", 119, ["Michael Jordan", "Michael I. Jordan"]),
    ("Yann LeCun", 118, ["Yann LeCun", "杨立昆"]),
    ("Yoshua Bengio", 118, ["Yoshua Bengio", "约书亚·本吉奥", "约书亚·本希奥"]),
    ("Li Fei-Fei", 116, ["Li Fei-Fei", "Fei-Fei Li", "李飞飞", "李飛飛"]),
    ("Sanjeev Arora", 115, ["Sanjeev Arora"]),
    ("Zico Kolter", 115, ["Zico Kolter", "J. Zico Kolter"]),
    ("Sepp Hochreiter", 114, ["Sepp Hochreiter"]),
    ("Dawn Song", 96, ["Dawn Song", "宋晓冬", "宋曉冬"]),
    ("Sergey Levine", 94, ["Sergey Levine"]),
    ("Chelsea Finn", 93, ["Chelsea Finn"]),
    ("Sham Kakade", 93, ["Sham Kakade"]),
    ("Pieter Abbeel", 92, ["Pieter Abbeel"]),
    ("Jitendra Malik", 91, ["Jitendra Malik"]),
    ("Percy Liang", 90, ["Percy Liang"]),
    ("Mihaela van der Schaar", 90, ["Mihaela van der Schaar"]),
    ("Bo Li", 89, ["Bo Li"]),
    ("Yejin Choi", 89, ["Yejin Choi"]),
    ("Graham Neubig", 88, ["Graham Neubig"]),
    ("Huazheng Wang", 88, ["Huazheng Wang"]),
    ("Zhiyuan Liu", 88, ["Zhiyuan Liu", "刘知远"]),
    ("Jun Zhu", 88, ["Jun Zhu", "朱军"]),
    ("Jie Tang", 87, ["Jie Tang", "唐杰"]),
    ("Luke Zettlemoyer", 87, ["Luke Zettlemoyer"]),
    ("Christopher Manning", 87, ["Christopher Manning"]),
    ("Stefano Ermon", 86, ["Stefano Ermon"]),
    ("Jure Leskovec", 86, ["Jure Leskovec"]),
    ("Max Welling", 86, ["Max Welling"]),
    ("Ion Stoica", 76, ["Ion Stoica"]),
    ("Matei Zaharia", 76, ["Matei Zaharia"]),
    ("Alec Radford", 75, ["Alec Radford"]),
    ("Trevor Darrell", 74, ["Trevor Darrell"]),
    ("Antonio Torralba", 74, ["Antonio Torralba"]),
    ("Rob Fergus", 73, ["Rob Fergus"]),
    ("Dieter Fox", 72, ["Dieter Fox"]),
    ("Russ Tedrake", 72, ["Russ Tedrake"]),
    ("Saining Xie", 71, ["Saining Xie"]),
    ("Zhuang Liu", 70, ["Zhuang Liu", "Liu Zhuang", "刘壮"]),
    ("Jim Fan", 70, ["Jim Fan"]),
    ("Jacob Steinhardt", 70, ["Jacob Steinhardt"]),
    ("David Sontag", 70, ["David Sontag"]),
    ("Anca Dragan", 69, ["Anca Dragan"]),
    ("Dorsa Sadigh", 69, ["Dorsa Sadigh"]),
    ("Ken Goldberg", 69, ["Ken Goldberg"]),
    ("Yuke Zhu", 69, ["Yuke Zhu"]),
    ("Moritz Hardt", 68, ["Moritz Hardt"]),
    ("Tatsunori Hashimoto", 68, ["Tatsunori Hashimoto"]),
    ("Ludwig Schmidt", 68, ["Ludwig Schmidt"]),
    ("Marzyeh Ghassemi", 68, ["Marzyeh Ghassemi"]),
    ("Aditi Raghunathan", 68, ["Aditi Raghunathan"]),
    ("Joseph E Gonzalez", 68, ["Joseph E Gonzalez", "Joseph E. Gonzalez"]),
]


def normalize_author_name(value: str) -> str:
    import unicodedata

    normalized = unicodedata.normalize("NFKD", value)
    return " ".join("".join(char if char.isalnum() else " " for char in normalized if not unicodedata.combining(char)).split()).lower()


def star_author_weight_for_authors(authors: str) -> int:
    names = {normalize_author_name(author) for author in str(authors or "").split(" | ") if author.strip()}
    if not names:
        return 0
    best = 0
    for _, weight, aliases in STAR_AUTHOR_ALIASES:
        if any(normalize_author_name(alias) in names for alias in aliases):
            best = max(best, weight)
    return best


def build_star_papers() -> dict[str, object]:
    paper_rows = []
    for row in read_csv("icml2026_papers_tagged.csv"):
        star_weight = star_author_weight_for_authors(row.get("authors", ""))
        if not star_weight or row.get("attention_bucket") != "现场可逛":
            continue
        paper_rows.append(
            {
                "id": row["poster_id"],
                "title": row["title"],
                "authors": short_text(row["authors"], 180),
                "bucket": row["attention_bucket"],
                "date": row["poster_date_kst"],
                "time": row["poster_time_kst"],
                "session": row["poster_session"],
                "room": row["poster_room"],
                "position": row["poster_position"],
                "oral": row["is_oral"] == "yes",
                "spotlight": row["is_spotlight"] == "yes",
                "poster_url": row["poster_url"],
                "openreview_url": row["openreview_url"],
                "star_weight": star_weight,
            }
        )
    paper_rows.sort(key=lambda row: (row["date"], row["time"], -int(row["star_weight"]), row["position"]))
    return {"papers": paper_rows}


def build_schedule() -> dict[str, object]:
    sessions = read_csv("icml2026_sessions.csv")
    scheduled_items = read_csv("icml2026_scheduled_items.csv")
    event_cards = read_csv("icml2026_event_cards.csv")
    orals = read_csv("icml2026_oral_metadata.csv")
    workshops = read_csv("icml2026_workshops.csv")

    items_by_session: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in scheduled_items:
        items_by_session[row["session_id"]].append(
            {
                "time": row["item_time"],
                "title": row["title"],
                "url": row["item_url"],
            }
        )

    session_rows = []
    for row in sessions:
        session_rows.append(
            {
                "date": row["date"],
                "day": row["day_label"],
                "time": f"{row['start_time']}-{row['end_time']}",
                "start": row["start_time"],
                "end": row["end_time"],
                "type": row["event_type"],
                "title": row["title"],
                "id": row["session_id"],
                "url": row["session_url"],
                "room": row["room"],
                "items": items_by_session.get(row["session_id"], [])[:8],
                "item_count": len(items_by_session.get(row["session_id"], [])),
            }
        )
    for row in workshops:
        session_rows.append(
            {
                "date": row["date"],
                "day": "Fri-Sat",
                "time": row["time_label"],
                "start": row["start_time"],
                "end": row["end_time"],
                "type": "Workshop",
                "title": row["title"],
                "id": row["workshop_id"],
                "url": row["url"],
                "room": row["room"],
                "items": [],
                "item_count": 0,
            }
        )

    featured = [
        {
            "type": row["event_type"],
            "title": row["title"],
            "authors": short_text(row["authors"], 160),
            "time": row["time"],
            "room": row["room"],
            "abstract": short_text(row["abstract"], 260),
            "url": row["item_url"],
        }
        for row in event_cards[:80]
    ]
    oral_rows = [
        {
            "title": row["title"],
            "authors": short_text(row["authors"], 160),
            "time": row["time"],
            "room": row["room"],
            "url": row["oral_url"],
        }
        for row in orals
    ]
    return {"sessions": session_rows, "featured": featured, "orals": oral_rows}


def build_events() -> dict[str, object]:
    side_events = side_events_with_verified()
    opportunities = read_csv("icml2026_onsite_opportunities.csv")
    summary = side_event_summary(side_events)

    side_rows = [
        {
            "date": row["date_2026"],
            "label": row["date_label"],
            "time": side_event_time_for_row(row),
            "sort_time": normalize_side_event_time(row["start_time"], row["end_time"], row["event_kind"], row["title"]) or "23:59",
            "title": row["title"],
            "organizer": row["organizer_guess"] or row["organizer_verified"],
            "kind": row["event_kind"],
            "platform": row["platform"],
            "location": row["location_name"],
            "region": visible_side_region(row),
            "url": row["rsvp_url"],
            "source_url": row["source_url"],
            "ticket": row["ticket_availability"],
            "confidence": row["confidence"],
            "notes": row["notes"],
            "priority": side_event_priority(row),
        }
        for row in side_events
    ]
    side_rows.sort(key=lambda row: (row["date"], row["sort_time"], -int(row["priority"]), row["title"]))

    return {
        "opportunities": opportunities,
        "side_events": side_rows,
        "side_summary": summary,
        "unconfirmed_watch": UNCONFIRMED_COMPANY_WATCH,
    }


def build_essentials() -> dict[str, object]:
    return {
        "local": read_csv("icml2026_local_essentials.csv"),
        "practical": read_csv("icml2026_practical_info.csv"),
        "transport": read_csv("icml2026_transport.csv"),
        "routes": read_csv("icml2026_route_links.csv"),
        "nearby": read_csv("icml2026_nearby_picks.csv"),
        "backlog": read_csv("icml2026_collection_backlog.csv"),
    }


def build_travel() -> dict[str, object]:
    groups = []
    for group in PERSONAL_ROUTE_GROUPS:
        spots = [
            {
                "name_zh": spot[0],
                "name_en": spot[1],
                "kind": spot[2],
                "note": spot[3],
                "query": spot[4],
                "source_url": spot[5] if len(spot) > 5 else "",
                "maps_url": maps_search_url(spot[4]),
                "directions_url": maps_directions_url(COEX_QUERY, spot[4], "transit"),
            }
            for spot in group["spots"]
        ]
        groups.append(
            {
                "id": group["id"],
                "title_zh": group["title_zh"],
                "title_en": group["title_en"],
                "when": group["when"],
                "route_hint": group["route_hint"],
                "destination_query": group["destination_query"],
                "directions_url": maps_directions_url(COEX_QUERY, group["destination_query"], "transit"),
                "spots": spots,
            }
        )
    return {
        "map_html": "./maps/icml2026_seoul_maplibre.html",
        "origin": COEX_QUERY,
        "groups": groups,
        "routes": read_csv("icml2026_route_links.csv"),
        "essentials": read_csv("icml2026_local_essentials.csv"),
        "airport_route_steps": airport_route_steps(),
        "hotel": travel_hotel(),
    }


def build_search_index() -> list[dict[str, str]]:
    index: list[dict[str, str]] = []

    for row in read_csv("icml2026_papers_tagged.csv"):
        index.append(
            {
                "type": "paper",
                "title": row["title"],
                "subtitle": " · ".join(part for part in [row["poster_date_kst"], row["poster_time_kst"], row["poster_session"], row["topic_tracks"]] if part),
                "url": row["poster_url"] or row["openreview_url"],
                "keywords": " ".join([row["authors"], row["topic"], row["topic_tracks"], row["attention_bucket"]]),
            }
        )

    for row in read_csv("icml2026_sessions.csv"):
        index.append(
            {
                "type": "session",
                "title": row["title"],
                "subtitle": " · ".join([row["date"], f"{row['start_time']}-{row['end_time']}", row["room"]]),
                "url": row["session_url"],
                "keywords": " ".join([row["event_type"], row["room"]]),
            }
        )

    for row in read_csv("icml2026_workshops.csv"):
        index.append(
            {
                "type": "workshop",
                "title": row["title"],
                "subtitle": " · ".join([row["date"], row["time_label"], row["room"]]),
                "url": row["url"],
                "keywords": " ".join([row["organizers"], row["abstract"], row["room"]]),
            }
        )

    for row in side_events_with_verified():
        index.append(
            {
                "type": "side_event",
                "title": row["title"],
                "subtitle": " · ".join(part for part in [row["date_2026"], side_event_time_for_row(row), row["event_kind"], row["address_region"]] if part),
                "url": row["rsvp_url"],
                "keywords": " ".join([row["organizer_guess"], row["event_kind"], row["platform"], row["notes"]]),
            }
        )

    for row in read_csv("icml2026_local_essentials.csv"):
        index.append(
            {
                "type": "place",
                "title": f"{row['name_zh']} / {row['name_en']}",
                "subtitle": " · ".join(part for part in [row["category"], row["hours_or_timing"], row["location_en"]] if part),
                "url": row["source_url"],
                "keywords": " ".join([row["why_zh"], row["why_en"], row["guide_use_zh"], row["guide_use_en"], row["korean_note"]]),
            }
        )

    for group in PERSONAL_ROUTE_GROUPS:
        index.append(
            {
                "type": "travel",
                "title": f"{group['title_zh']} / {group['title_en']}",
                "subtitle": " · ".join([group["when"], group["route_hint"]]),
                "url": "./travel.html",
                "keywords": " ".join([spot[0] + " " + spot[1] + " " + spot[2] for spot in group["spots"]]),
            }
        )

    return index


def copy_map_assets() -> None:
    MAP_OUT.mkdir(parents=True, exist_ok=True)
    for name in [
        "coex_map.svg",
        "coex_map_modern.html",
        "icml2026_seoul_maplibre.html",
        "icml2026_seoul_schematic.svg",
        "icml2026_seoul_schematic.png",
    ]:
        src = MAPS / name
        if src.exists():
            shutil.copy2(src, MAP_OUT / name)


def main() -> None:
    DOCS.mkdir(parents=True, exist_ok=True)
    write_json("manifest.json", build_manifest())
    write_json("focus.json", build_focus())
    write_guide_plans(build_guide_plans())
    write_star_papers(build_star_papers())
    write_json("papers.json", build_papers())
    write_json("schedule.json", build_schedule())
    write_json("events.json", build_events())
    write_json("essentials.json", build_essentials())
    write_json("travel.json", build_travel())
    write_json("search.json", build_search_index())
    copy_map_assets()
    print(f"Wrote web data to {OUT.relative_to(ROOT)}")
    print(f"Copied map assets to {MAP_OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
