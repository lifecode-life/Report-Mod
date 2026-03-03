from __future__ import annotations

from typing import Dict, Iterable, List, Set


def apply_filters(
    grouped_conditions: Dict[str, List[str]],
    excluded_categories: Iterable[str],
    excluded_conditions: Iterable[str],
) -> Dict[str, List[str]]:
    excluded_categories_set: Set[str] = {c.strip().lower() for c in excluded_categories}
    excluded_conditions_set: Set[str] = {c.strip().lower() for c in excluded_conditions}

    filtered: Dict[str, List[str]] = {}
    for category, conditions in grouped_conditions.items():
        if category.strip().lower() in excluded_categories_set:
            continue

        kept_conditions = [
            condition
            for condition in conditions
            if condition.strip().lower() not in excluded_conditions_set
        ]
        if kept_conditions:
            filtered[category] = kept_conditions
    return filtered
