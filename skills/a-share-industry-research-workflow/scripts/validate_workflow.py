from __future__ import annotations

import json
import sys
from pathlib import Path


ALLOWED_STATUSES = {"pending", "in_progress", "completed", "partial", "failed", "skipped"}
REQUIRED_STAGES = {"screening", "filing_reviews", "peer_ranking"}


def fail(message: str) -> None:
    raise SystemExit(f"Workflow validation failed: {message}")


def load_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        fail(f"missing file: {path}")
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"cannot read JSON {path}: {exc}")
    if not isinstance(value, dict):
        fail(f"JSON root must be an object: {path}")
    return value


def resolve_relative(root: Path, value: object, field: str) -> Path:
    if not isinstance(value, str) or not value.strip():
        fail(f"{field} must be a non-empty relative path")
    relative = Path(value)
    if relative.is_absolute() or ".." in relative.parts:
        fail(f"{field} must stay inside the run directory: {value}")
    return root / relative


def require_file(root: Path, value: object, field: str, *, json_file: bool = False) -> Path:
    path = resolve_relative(root, value, field)
    if not path.is_file():
        fail(f"{field} does not exist: {path}")
    if json_file:
        load_json(path)
    elif path.stat().st_size == 0:
        fail(f"{field} is empty: {path}")
    return path


def validate_status(item: dict, field: str) -> str:
    status = item.get("status")
    if status not in ALLOWED_STATUSES:
        fail(f"{field}.status must be one of {sorted(ALLOWED_STATUSES)}")
    return status


def validate(root: Path) -> None:
    manifest = load_json(root / "workflow_manifest.json")
    if manifest.get("schema_version") != "1.0":
        fail("schema_version must be 1.0")
    for field in ("topic", "as_of_date"):
        if not isinstance(manifest.get(field), str) or not manifest[field].strip():
            fail(f"{field} must be a non-empty string")

    parameters = manifest.get("parameters")
    if not isinstance(parameters, dict):
        fail("parameters must be an object")
    minimum = parameters.get("ranking_min_companies", 3)
    if not isinstance(minimum, int) or minimum < 3:
        fail("ranking_min_companies must be an integer of at least 3")

    stages = manifest.get("stages")
    if not isinstance(stages, dict) or not REQUIRED_STAGES.issubset(stages):
        fail(f"stages must contain {sorted(REQUIRED_STAGES)}")
    if any(not isinstance(stages[name], dict) for name in REQUIRED_STAGES):
        fail("each stage must be an object")

    screening = stages["screening"]
    if validate_status(screening, "stages.screening") == "completed":
        universe_path = require_file(
            root, screening.get("universe_path"), "stages.screening.universe_path", json_file=True
        )
        universe = load_json(universe_path)
        if not isinstance(universe.get("companies"), list) or not universe["companies"]:
            fail("completed screening universe must contain a non-empty companies array")
        require_file(root, screening.get("report_path"), "stages.screening.report_path")

    reviews = stages["filing_reviews"]
    review_status = validate_status(reviews, "stages.filing_reviews")
    companies = reviews.get("selected_companies")
    if not isinstance(companies, list):
        fail("stages.filing_reviews.selected_companies must be an array")
    completed_reviews = 0
    for index, company in enumerate(companies):
        field = f"stages.filing_reviews.selected_companies[{index}]"
        if not isinstance(company, dict):
            fail(f"{field} must be an object")
        for key in ("security_code", "company_name"):
            if not isinstance(company.get(key), str) or not company[key].strip():
                fail(f"{field}.{key} must be a non-empty string")
        if validate_status(company, field) == "completed":
            completed_reviews += 1
            require_file(root, company.get("report_data_path"), f"{field}.report_data_path", json_file=True)
            require_file(root, company.get("report_path"), f"{field}.report_path")
    if review_status == "completed" and not companies:
        fail("completed filing_reviews must select at least one company")
    if review_status == "completed" and completed_reviews != len(companies):
        fail("completed filing_reviews cannot contain unfinished companies")

    ranking = stages["peer_ranking"]
    ranking_status = validate_status(ranking, "stages.peer_ranking")
    if ranking_status == "completed":
        if completed_reviews < minimum:
            fail(f"completed peer_ranking requires at least {minimum} completed filing reviews")
        require_file(root, ranking.get("peer_data_path"), "stages.peer_ranking.peer_data_path", json_file=True)
        require_file(root, ranking.get("ranking_data_path"), "stages.peer_ranking.ranking_data_path", json_file=True)
        require_file(root, ranking.get("report_data_path"), "stages.peer_ranking.report_data_path", json_file=True)
        require_file(root, ranking.get("markdown_path"), "stages.peer_ranking.markdown_path")
        require_file(root, ranking.get("report_path"), "stages.peer_ranking.report_path")

    if not isinstance(manifest.get("limitations", []), list):
        fail("limitations must be an array")
    print(
        "Workflow validation passed: "
        f"screening={screening['status']}, filing_reviews={review_status} "
        f"({completed_reviews}/{len(companies)} completed), peer_ranking={ranking_status}."
    )


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python validate_workflow.py <workflow-run-directory>")
    root = Path(sys.argv[1]).resolve()
    if not root.is_dir():
        fail(f"run directory does not exist: {root}")
    validate(root)


if __name__ == "__main__":
    main()
