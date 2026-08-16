"""Association rule mining (apriori) over review-level aspect/sentiment/rating items.

Implemented from scratch with itertools since the item universe per review is
small (aspects + sentiment label + rating bucket), avoiding an extra
dependency (e.g. mlxtend) for a problem this size.
"""
from __future__ import annotations

import csv
import json
from collections import defaultdict
from itertools import combinations
from pathlib import Path
from typing import Any, Iterable

ASSOCIATION_METHOD = "apriori_v1"


def _rating_bucket(rating: Any) -> str | None:
    if rating is None:
        return None
    try:
        value = float(rating)
    except (TypeError, ValueError):
        return None
    if value <= 2:
        return "rating_low"
    if value == 3:
        return "rating_mid"
    return "rating_high"


def build_transactions(
    nlp_records: Iterable[dict[str, Any]], aspect_rows: Iterable[dict[str, Any]]
) -> list[set[str]]:
    """Build one item-set transaction per review from sentiment, rating, and aspects."""
    aspects_by_review: dict[Any, set[str]] = defaultdict(set)
    for row in aspect_rows:
        aspects_by_review[row.get("review_id")].add(f"aspect:{row['aspect']}")

    transactions = []
    for record in nlp_records:
        items: set[str] = set(aspects_by_review.get(record.get("review_id"), set()))
        sentiment = record.get("sentiment_label")
        if sentiment:
            items.add(f"sentiment:{sentiment}")
        bucket = _rating_bucket(record.get("rating"))
        if bucket:
            items.add(bucket)
        if items:
            transactions.append(items)
    return transactions


def _frequent_itemsets(
    transactions: list[set[str]], min_support: float, max_len: int
) -> dict[frozenset[str], float]:
    n = len(transactions)
    item_counts: dict[frozenset[str], int] = defaultdict(int)
    for transaction in transactions:
        for item in transaction:
            item_counts[frozenset([item])] += 1
    frequent = {
        itemset: count / n for itemset, count in item_counts.items() if count / n >= min_support
    }

    current_level = list(frequent.keys())
    length = 1
    while current_level and length < max_len:
        length += 1
        candidates: set[frozenset[str]] = set()
        for a, b in combinations(current_level, 2):
            union = a | b
            if len(union) == length:
                candidates.add(union)
        next_level = []
        for candidate in candidates:
            count = sum(1 for transaction in transactions if candidate <= transaction)
            support = count / n
            if support >= min_support:
                frequent[candidate] = support
                next_level.append(candidate)
        current_level = next_level
    return frequent


def mine_association_rules(
    nlp_records: Iterable[dict[str, Any]],
    aspect_rows: Iterable[dict[str, Any]],
    min_support: float = 0.01,
    min_confidence: float = 0.3,
    max_len: int = 3,
) -> dict[str, Any]:
    """Mine association rules with support/confidence/lift over review item-sets.

    Raises ValueError if there are no transactions to mine.
    """
    transactions = build_transactions(nlp_records, aspect_rows)
    if not transactions:
        raise ValueError("No transactions available to mine association rules")

    itemsets = _frequent_itemsets(transactions, min_support, max_len)

    rules = []
    for itemset, support in itemsets.items():
        if len(itemset) < 2:
            continue
        for consequent_size in range(1, len(itemset)):
            for consequent in combinations(sorted(itemset), consequent_size):
                consequent_set = frozenset(consequent)
                antecedent_set = itemset - consequent_set
                antecedent_support = itemsets.get(antecedent_set)
                consequent_support = itemsets.get(consequent_set)
                if not antecedent_support or not consequent_support:
                    continue
                confidence = support / antecedent_support
                if confidence < min_confidence:
                    continue
                lift = confidence / consequent_support
                rules.append(
                    {
                        "antecedent": sorted(antecedent_set),
                        "consequent": sorted(consequent_set),
                        "support": round(support, 6),
                        "confidence": round(confidence, 6),
                        "lift": round(lift, 6),
                    }
                )
    rules.sort(key=lambda rule: rule["lift"], reverse=True)

    return {
        "method": ASSOCIATION_METHOD,
        "status": "derived_unvalidated",
        "params": {
            "transaction_count": len(transactions),
            "min_support": min_support,
            "min_confidence": min_confidence,
            "max_len": max_len,
        },
        "frequent_itemset_count": len(itemsets),
        "rule_count": len(rules),
        "rules": rules,
    }


def write_association_artifacts(result: dict[str, Any], output_dir: str | Path) -> None:
    """Write association-rule mining results as JSON and a flat CSV for quick review."""
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    (output / "association_rules.json").write_text(json.dumps(result, indent=2), encoding="utf-8")

    rules = result["rules"]
    csv_path = output / "association_rules.csv"
    if not rules:
        csv_path.write_text("\n", encoding="utf-8")
        return
    with csv_path.open("w", encoding="utf-8", newline="") as file_handle:
        writer = csv.DictWriter(
            file_handle, fieldnames=["antecedent", "consequent", "support", "confidence", "lift"]
        )
        writer.writeheader()
        for rule in rules:
            writer.writerow(
                {
                    "antecedent": ",".join(rule["antecedent"]),
                    "consequent": ",".join(rule["consequent"]),
                    "support": rule["support"],
                    "confidence": rule["confidence"],
                    "lift": rule["lift"],
                }
            )
