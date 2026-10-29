#!/usr/bin/env python3
"""Rank normalized peer data without inventing missing values."""

from __future__ import annotations

import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path


DEFAULT_SCENARIOS = {
    "quality_first": {
        "business_quality": 25,
        "growth_quality": 12,
        "profitability": 18,
        "cash_quality": 18,
        "balance_sheet": 12,
        "capital_governance": 15,
        "valuation": 0,
    },
    "growth_first": {
        "business_quality": 18,
        "growth_quality": 27,
        "profitability": 15,
        "cash_quality": 12,
        "balance_sheet": 8,
        "capital_governance": 10,
        "valuation": 10,
    },
    "valuation_first": {
        "business_quality": 20,
        "growth_quality": 10,
        "profitability": 15,
        "cash_quality": 15,
        "balance_sheet": 10,
        "capital_governance": 10,
        "valuation": 20,
    },
}


def load_input(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    companies = data.get("companies")
    if not isinstance(companies, list) or len(companies) < 3:
        raise ValueError("peer_data.json must contain at least three companies")
    codes = [c.get("security_code") for c in companies]
    if any(not code for code in codes) or len(codes) != len(set(codes)):
        raise ValueError("Every company needs a unique security_code")
    return data


def numeric_score(company: dict, dimension: str) -> float | None:
    value = company.get("dimension_scores", {}).get(dimension)
    if value is None:
        return None
    if isinstance(value, dict):
        value = value.get("value")
    if not isinstance(value, (int, float)) or isinstance(value, bool) or not math.isfinite(value):
        raise ValueError(f"Invalid score for {company['security_code']}:{dimension}")
    if not 0 <= value <= 100:
        raise ValueError(f"Score outside 0-100 for {company['security_code']}:{dimension}")
    return float(value)


def relative_tier(position: int, count: int) -> str:
    if position == 1:
        return "strong"
    if position == count:
        return "weak"
    return "middle"


def rank_scenario(companies: list[dict], weights: dict[str, float], *, formal: bool) -> list[dict]:
    total_weight = sum(weights.values())
    results = []
    for company in companies:
        used_weight = 0.0
        weighted_sum = 0.0
        for dimension, weight in weights.items():
            if weight <= 0:
                continue
            score = numeric_score(company, dimension)
            if score is None:
                continue
            used_weight += weight
            weighted_sum += score * weight
        coverage = used_weight / total_weight if total_weight else 0.0
        evidence = company.get("evidence_quality", 0.0)
        if not isinstance(evidence, (int, float)) or not 0 <= evidence <= 1:
            raise ValueError(f"Invalid evidence_quality for {company['security_code']}")
        score = weighted_sum / used_weight if used_weight else None
        confidence = coverage * float(evidence)
        results.append({
            "security_code": company["security_code"],
            "short_name": company.get("short_name", company.get("company_name", "")),
            "score": round(score, 2) if formal and score is not None else None,
            "_calculated_score": score,
            "coverage_ratio": round(coverage, 4),
            "evidence_quality": round(float(evidence), 4),
            "confidence": round(confidence, 4),
            "rank": None,
            "directional_order": None,
            "relative_tier": None,
            "rank_status": ("ranked" if formal else "directional") if coverage >= 0.70 else "insufficient_coverage",
        })
    eligible = [r for r in results if r["rank_status"] != "insufficient_coverage" and r["_calculated_score"] is not None]
    eligible.sort(key=lambda r: (r["_calculated_score"], r["confidence"], r["security_code"]), reverse=True)
    for index, item in enumerate(eligible, start=1):
        if formal:
            item["rank"] = index
        else:
            item["directional_order"] = index
            item["relative_tier"] = relative_tier(index, len(eligible))
    for item in results:
        item.pop("_calculated_score", None)
    order_key = "rank" if formal else "directional_order"
    return sorted(results, key=lambda r: (r[order_key] is None, r[order_key] or 10**9, r["security_code"]))


def main() -> int:
    if len(sys.argv) not in (2, 3):
        print("Usage: rank_peers.py <peer_data.json> [ranking_data.json]", file=sys.stderr)
        return 2
    input_path = Path(sys.argv[1]).resolve()
    output_path = Path(sys.argv[2]).resolve() if len(sys.argv) == 3 else input_path.with_name("ranking_data.json")
    data = load_input(input_path)
    formal = len(data["companies"]) >= 5
    comparison_mode = "formal_ranking" if formal else "directional_comparison"
    requested_mode = data.get("comparison_mode")
    if requested_mode == "formal_ranking" and not formal:
        raise ValueError("formal_ranking requires at least five companies")
    scenarios = data.get("scenarios") or DEFAULT_SCENARIOS
    if not isinstance(scenarios, dict) or not scenarios:
        raise ValueError("scenarios must be a non-empty object")

    valuation_available = bool(data.get("price_date")) and all(
        numeric_score(company, "valuation") is not None for company in data["companies"]
    )
    output_scenarios = {}
    for name, weights in scenarios.items():
        if not isinstance(weights, dict) or not weights:
            raise ValueError(f"Invalid weights for scenario: {name}")
        effective = {key: float(value) for key, value in weights.items()}
        if name == "valuation_first" and not valuation_available:
            output_scenarios[name] = {
                "enabled": False,
                "reason": "A common price_date and valuation score for every company are required.",
                "weights": effective,
                "ranking": [],
            }
            continue
        if not valuation_available:
            effective["valuation"] = 0.0
        output_scenarios[name] = {
            "enabled": True,
            "weights": effective,
            "ranking": rank_scenario(data["companies"], effective, formal=formal),
        }

    result = {
        "schema_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "input": input_path.name,
        "comparison_mode": comparison_mode,
        "topic": data.get("topic"),
        "financial_period": data.get("financial_period"),
        "price_date": data.get("price_date"),
        "scenarios": output_scenarios,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
