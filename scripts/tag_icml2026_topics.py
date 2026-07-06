#!/usr/bin/env python3
"""Add lightweight multi-label topic tracks to ICML 2026 master paper table."""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
IN = ROOT / "data" / "processed" / "icml2026_papers_master.csv"
OUT_CSV = ROOT / "data" / "processed" / "icml2026_papers_tagged.csv"
OUT_JSON = ROOT / "data" / "processed" / "icml2026_papers_tagged.json"


TOPIC_KEYWORDS = {
    "LLM / Foundation Models": [
        "llm",
        "language model",
        "large language",
        "foundation model",
        "transformer",
        "pretraining",
        "post-training",
        "fine-tuning",
        "instruction",
        "lora",
        "peft",
        "moe",
        "long-context",
        "rag",
        "decoding",
        "model merging",
        "dataset selection",
    ],
    "Agents / Tool Use / GUI": [
        "agent",
        "agentic",
        "tool use",
        "tool-calling",
        "planner",
        "planning",
        "memory",
        "procedural memory",
        "gui",
        "web",
        "browser",
        "workflow",
        "self-evolution",
        "verification",
        "multi-agent",
    ],
    "AI Safety / Alignment / Reliability": [
        "safety",
        "alignment",
        "rlhf",
        "dpo",
        "preference",
        "reward model",
        "jailbreak",
        "red team",
        "robustness",
        "reliability",
        "hallucination",
        "backdoor",
        "adversarial",
        "calibration",
        "risk",
        "uncertainty",
        "guardrail",
    ],
    "Multimodal / Vision-Language / Video": [
        "multimodal",
        "multi-modal",
        "vision-language",
        "vlm",
        "mllm",
        "image",
        "video",
        "audio",
        "spatial",
        "visual reasoning",
        "tracking",
        "segmentation",
        "detection",
        "caption",
        "text-to-image",
        "diffusion",
        "3d",
        "gaussian splatting",
    ],
    "AI4Science / Bio / Molecules": [
        "ai for science",
        "protein",
        "genomic",
        "dna",
        "rna",
        "sequence",
        "molecule",
        "molecular",
        "chemistry",
        "drug",
        "material",
        "physics",
        "pde",
        "ode",
        "differential equation",
        "dynamical system",
        "climate",
        "eeg",
        "medical",
    ],
    "Robotics / Embodied AI": [
        "robot",
        "robotics",
        "embodied",
        "manipulation",
        "navigation",
        "locomotion",
        "control",
        "trajectory",
        "policy",
        "imitation",
        "vla",
        "vision-language-action",
        "world model",
        "sim-to-real",
        "dexterous",
    ],
    "Reinforcement Learning / Decision Making": [
        "reinforcement learning",
        "rl",
        "offline rl",
        "online rl",
        "mdp",
        "pomdp",
        "policy gradient",
        "q-learning",
        "actor-critic",
        "exploration",
        "reward shaping",
        "bandit",
        "markov game",
        "stackelberg",
        "multi-agent rl",
    ],
    "Theory / Optimization / Learning Foundations": [
        "theory",
        "bound",
        "convergence",
        "generalization",
        "sample complexity",
        "expressivity",
        "pac",
        "minimax",
        "optimization",
        "sgd",
        "non-convex",
        "convex",
        "sharpness",
        "langevin",
        "gradient",
        "privacy",
    ],
    "Efficient ML / Systems / Hardware": [
        "efficiency",
        "efficient",
        "scalable",
        "inference",
        "training",
        "compression",
        "quantization",
        "pruning",
        "sparsity",
        "low-rank",
        "distillation",
        "cache",
        "attention",
        "kernel",
        "hardware",
        "compiler",
        "memory",
    ],
    "Data / Evaluation / Benchmarks": [
        "benchmark",
        "evaluation",
        "eval",
        "dataset",
        "data curation",
        "data selection",
        "synthetic data",
        "annotation",
        "methodology",
        "metric",
        "leaderboard",
        "a/b testing",
        "diagnostic",
        "contamination",
        "reproducibility",
    ],
    "Causal / Probabilistic / Structured Data": [
        "causal",
        "causality",
        "bayesian",
        "probabilistic",
        "uncertainty",
        "sampling",
        "graph",
        "gnn",
        "federated",
        "tabular",
        "time series",
        "forecasting",
        "representation",
        "latent variable",
    ],
    "Responsible AI / Social Impact / Economics": [
        "fairness",
        "bias",
        "privacy",
        "copyright",
        "governance",
        "social impact",
        "misinformation",
        "ai-generated",
        "detection",
        "watermark",
        "mechanism design",
        "peer review",
        "market",
        "pricing",
        "game theory",
        "big tech",
    ],
}


def normalize(text: str) -> str:
    text = text.lower()
    text = text.replace("–", "-").replace("—", "-")
    text = re.sub(r"\s+", " ", text)
    return text


def keyword_hit(text: str, keyword: str) -> bool:
    keyword = normalize(keyword)
    if re.search(r"^[a-z0-9]+$", keyword):
        return re.search(rf"\b{re.escape(keyword)}\b", text) is not None
    return keyword in text


def tag_row(row: dict[str, str]) -> tuple[list[str], list[str]]:
    haystack = normalize(
        " ".join(
            [
                row.get("title", ""),
                row.get("abstract", ""),
                row.get("poster_session", ""),
                row.get("oral_session", ""),
                row.get("topic", ""),
                row.get("keywords", ""),
            ]
        )
    )
    topics: list[str] = []
    hits: list[str] = []
    for topic, keywords in TOPIC_KEYWORDS.items():
        matched = [kw for kw in keywords if keyword_hit(haystack, kw)]
        if matched:
            topics.append(topic)
            hits.extend(f"{topic}: {kw}" for kw in matched[:5])
    return topics, hits


def main() -> None:
    with IN.open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    for row in rows:
        topics, hits = tag_row(row)
        row["attention_bucket"] = (
            "现场可逛" if row.get("is_scheduled") == "yes" else "额外关注（未进入当前现场日程）"
        )
        row["topic_tracks"] = " | ".join(topics)
        row["topic_keyword_hits"] = " | ".join(hits)
        row["topic_count"] = str(len(topics))

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        fieldnames = list(rows[0].keys()) if rows else []
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    OUT_JSON.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"tagged_papers: {len(rows)}")
    print(f"topics: {len(TOPIC_KEYWORDS)}")


if __name__ == "__main__":
    main()
