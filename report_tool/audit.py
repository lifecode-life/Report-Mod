from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


def sha256_bytes(data: bytes) -> str:
    h = hashlib.sha256()
    h.update(data)
    return h.hexdigest()


def write_audit_json(
    output_path: Path,
    original_filename: str,
    original_pdf_bytes: bytes,
    counselor_name: str,
    filter_profile_name: str,
    excluded_categories: Iterable[str],
    excluded_conditions: Iterable[str],
) -> None:
    payload = {
        "original_filename": original_filename,
        "sha256": sha256_bytes(original_pdf_bytes),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "counselor_name": counselor_name,
        "filter_profile_name": filter_profile_name,
        "excluded_categories": sorted(set(excluded_categories)),
        "excluded_conditions": sorted(set(excluded_conditions)),
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
