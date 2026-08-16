"""Deterministic CRM issue ranking and action-tip generation."""
from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Iterable

CRM_METHOD = "evidence_ranked_crm_v1"


def build_crm_cases(
    aspect_rows: Iterable[dict[str, Any]],
    alert_rows: Iterable[dict[str, Any]],
    min_mentions: int = 3,
) -> dict[str, Any]:
    """Create compact, evidence-linked CRM cases without an LLM."""
    aspects: dict[tuple[str, str], dict[str, Any]] = {}
    for row in aspect_rows:
        branch_id = str(row.get("branch_id") or "<missing>")
        aspect = str(row.get("aspect") or "unknown")
        bucket = aspects.setdefault(
            (branch_id, aspect),
            {"branch_id": branch_id, "aspect": aspect, "mention_count": 0, "score_sum": 0.0},
        )
        bucket["mention_count"] += 1
        bucket["score_sum"] += float(row.get("aspect_sentiment_score") or 0.0)

    alerts_by_branch: dict[str, list[dict[str, Any]]] = {}
    for row in alert_rows:
        if str(row.get("is_anomaly", "")).lower() != "true":
            continue
        alerts_by_branch.setdefault(str(row.get("branch_id")), []).append(row)

    cases = []
    for (branch_id, aspect), bucket in aspects.items():
        if bucket["mention_count"] < min_mentions:
            continue
        average_score = bucket["score_sum"] / bucket["mention_count"]
        branch_alerts = alerts_by_branch.get(branch_id, [])
        high_alerts = [row for row in branch_alerts if row.get("alert_severity") == "high"]
        priority_score = bucket["mention_count"] * max(0.0, -average_score)
        priority_score += len(branch_alerts) * 2 + len(high_alerts) * 3
        priority = "high" if priority_score >= 10 else "medium" if priority_score >= 4 else "low"
        action = _action_for_aspect(aspect)
        cases.append(
            {
                "case_id": f"{branch_id}:{aspect}",
                "branch_id": branch_id,
                "issue": aspect,
                "priority": priority,
                "priority_score": round(priority_score, 4),
                "mention_count": bucket["mention_count"],
                "average_sentiment_score": round(average_score, 4),
                "supporting_alert_count": len(branch_alerts),
                "recommended_action": action,
                "suggested_owner": "Branch manager",
                "status": "open",
                "evidence_type": "derived",
                "review_cycle": "Review weekly against rating and negative-ratio trend",
            }
        )
    cases.sort(key=lambda row: (-row["priority_score"], row["branch_id"], row["issue"]))
    return {
        "method": CRM_METHOD,
        "status": "derived_actionable",
        "params": {"min_mentions": min_mentions},
        "case_count": len(cases),
        "cases": cases,
    }


def write_crm_artifacts(result: dict[str, Any], output_dir: str | Path) -> None:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    (output / "crm_cases.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    rows = result.get("cases", [])
    if not rows:
        (output / "crm_cases.csv").write_text("\n", encoding="utf-8")
        return
    with (output / "crm_cases.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def _action_for_aspect(aspect: str) -> str:
    actions = {
        "service": "Review peak-hour staffing, greeting consistency, and table follow-up.",
        "food": "Review preparation consistency and sample recent negative food feedback.",
        "price": "Audit value perception, portion consistency, and menu communication.",
        "ambiance": "Inspect cleanliness, seating comfort, noise, and dining-area checks.",
        "wait_time": "Measure order-to-table time and add a peak-period escalation check.",
    }
    return actions.get(aspect, f"Investigate recurring {aspect} feedback and assign a branch owner.")