from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Tuple



CATEGORY_HINTS = {
    "cardio": "Cardiovascular",
    "heart": "Cardiovascular",
    "metabolic": "Metabolic",
    "nutrition": "Nutrition",
    "vitamin": "Nutrition",
    "horm": "Hormonal",
    "sleep": "Sleep",
    "mental": "Mental Health",
    "cognitive": "Cognitive",
    "immune": "Immune",
    "inflamm": "Inflammation",
    "fitness": "Fitness",
    "detox": "Detoxification",
}

CONDITION_PATTERNS = [
    re.compile(r"^\s*(?:[-•*]|\d+[\.)])\s*([A-Za-z][A-Za-z0-9 ,/'&()\-]{2,})\s*$"),
    re.compile(r"^\s*([A-Za-z][A-Za-z0-9 ,/'&()\-]{2,})\s*[:|]\s*(?:Low|Medium|High|Elevated|Normal|Risk|Impact)", re.IGNORECASE),
]

CATEGORY_PATTERNS = [
    re.compile(r"^\s*(?:Category|Domain|System)\s*[:\-]\s*([A-Za-z][A-Za-z &/\-]{2,})\s*$", re.IGNORECASE),
    re.compile(r"^\s*([A-Z][A-Z &/\-]{3,})\s*$"),
]


@dataclass
class ExtractionResult:
    grouped_conditions: Dict[str, List[str]]
    raw_text: str
    uncertain: bool = False
    warnings: List[str] = field(default_factory=list)


def _normalize_condition(text: str) -> str:
    cleaned = re.sub(r"\s+", " ", text).strip(" -•*\t")
    return cleaned.strip()


def _is_likely_noise(text: str) -> bool:
    lower = text.lower().strip()
    if not lower:
        return True
    if len(lower) < 3:
        return True
    if lower.startswith(("page ", "copyright", "confidential", "www.")):
        return True
    if re.fullmatch(r"[0-9\s\-_.]+", lower):
        return True
    return False


def infer_category_from_condition(condition: str) -> str:
    lower = condition.lower()
    for hint, category in CATEGORY_HINTS.items():
        if hint in lower:
            return category
    return "General"


def extract_conditions_from_text(raw_text: str) -> ExtractionResult:
    grouped: Dict[str, List[str]] = {}
    current_category = "General"
    seen: set[Tuple[str, str]] = set()
    warnings: List[str] = []

    lines = [line.strip() for line in raw_text.splitlines()]
    for line in lines:
        if _is_likely_noise(line):
            continue

        cat_match = next((p.match(line) for p in CATEGORY_PATTERNS if p.match(line)), None)
        if cat_match:
            cat_candidate = cat_match.group(1).title().strip()
            # avoid turning condition-looking uppercase into categories
            if len(cat_candidate.split()) <= 6 and not any(ch.isdigit() for ch in cat_candidate):
                current_category = cat_candidate
                grouped.setdefault(current_category, [])
                continue

        cond_match = next((p.match(line) for p in CONDITION_PATTERNS if p.match(line)), None)
        if cond_match:
            condition = _normalize_condition(cond_match.group(1))
            if len(condition) > 2 and len(condition) < 120:
                category = current_category if current_category != "General" else infer_category_from_condition(condition)
                key = (category, condition.lower())
                if key not in seen:
                    grouped.setdefault(category, []).append(condition)
                    seen.add(key)
                continue

    if not grouped:
        warnings.append("No clear conditions detected from PDF text.")
    elif sum(len(v) for v in grouped.values()) < 5:
        warnings.append("Low number of detected conditions; extraction may be incomplete.")

    uncertain = bool(warnings)
    return ExtractionResult(grouped_conditions=grouped, raw_text=raw_text, uncertain=uncertain, warnings=warnings)


def extract_conditions_from_pdf_bytes(pdf_bytes: bytes) -> ExtractionResult:
    import pdfplumber

    text_chunks: List[str] = []
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        for page in pdf.pages:
            text_chunks.append(page.extract_text() or "")

    raw_text = "\n".join(text_chunks)
    return extract_conditions_from_text(raw_text)


# Local import to keep module import cheap for tests that only use text extraction.
import io  # noqa: E402
