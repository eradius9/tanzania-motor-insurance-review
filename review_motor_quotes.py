"""Review annual comprehensive motor base-premium records using supplied quote terms.

No tariff is built in. Input files should be kept private. Python 3.10+ only.
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from decimal import Decimal, InvalidOperation
from pathlib import Path

FIELDS = [
    "record_id", "insurer", "quote_reference", "vehicle_use", "sum_insured_tzs",
    "rate_percent", "minimum_base_premium_tzs", "quoted_base_premium_tzs",
]
OUTPUT_FIELDS = FIELDS + [
    "rate_component_tzs", "expected_base_premium_tzs", "difference_tzs",
    "review_status", "questions",
]


def parse_number(value: str, label: str, questions: list[str], *, zero_ok=False):
    if not value:
        questions.append(f"Confirm {label}: no value supplied.")
        return None
    try:
        number = Decimal(value)
    except InvalidOperation:
        questions.append(f"Confirm {label}: use a plain number.")
        return None
    if not number.is_finite() or number < 0 or (number == 0 and not zero_ok):
        questions.append(f"Confirm {label}: the supplied value is invalid.")
        return None
    return number


def show(number):
    return "" if number is None else format(number, "f")


def review_rows(rows: list[dict[str, str]], tolerance=Decimal("0")):
    if not tolerance.is_finite() or tolerance < 0:
        raise ValueError("Tolerance must be a finite, nonnegative amount in TZS.")
    cleaned = [{field: str(row.get(field) or "").strip() for field in FIELDS} for row in rows]
    counts = Counter(row["record_id"] for row in cleaned if row["record_id"])
    results = []
    for row in cleaned:
        questions = []
        for field in ["record_id", "insurer", "quote_reference", "vehicle_use"]:
            if not row[field]:
                questions.append(f"Confirm {field.replace('_', ' ')}: missing reference or description.")
        if row["record_id"] and counts[row["record_id"]] > 1:
            questions.append("Repeated record ID: establish whether these are separate quotations or versions.")
        insured = parse_number(row["sum_insured_tzs"], "sum insured", questions)
        rate = parse_number(row["rate_percent"], "quoted rate percent", questions)
        minimum = parse_number(row["minimum_base_premium_tzs"], "applicable minimum base premium", questions, zero_ok=True)
        recorded = parse_number(row["quoted_base_premium_tzs"], "recorded base premium", questions)
        component = insured * rate / Decimal("100") if insured is not None and rate is not None else None
        expected = max(component, minimum) if component is not None and minimum is not None else None
        difference = recorded - expected if recorded is not None and expected is not None else None
        if difference is not None and abs(difference) > tolerance:
            questions.append("Base premium differs from the entered rate and minimum. Confirm the source figures or an adjustment.")
        results.append({**row,
                        "rate_component_tzs": show(component),
                        "expected_base_premium_tzs": show(expected),
                        "difference_tzs": show(difference),
                        "review_status": "Needs confirmation" if questions else "Arithmetic matches inputs",
                        "questions": " ".join(questions)})
    return results


def read_source(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        missing = set(FIELDS) - set(reader.fieldnames or [])
        if missing:
            raise ValueError("Required columns missing: " + ", ".join(sorted(missing)))
        rows = []
        for row_number, row in enumerate(reader, start=2):
            if None in row:
                raise ValueError(f"CSV row {row_number} contains extra fields. Check commas and quoting.")
            if any(str(row.get(field) or "").strip() for field in FIELDS):
                rows.append(row)
        return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("--output", type=Path, default=Path("review_output"))
    parser.add_argument("--tolerance", default="0", help="Explicit comparison tolerance in TZS; default is exact.")
    args = parser.parse_args()
    try:
        tolerance = Decimal(args.tolerance)
        rows = read_source(args.source)
        reviewed = review_rows(rows, tolerance)
    except (ValueError, InvalidOperation, OSError) as error:
        parser.error(str(error))
    args.output.mkdir(parents=True, exist_ok=True)
    with (args.output / "reviewed_quotes.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        writer.writerows(reviewed)
    matches = sum(row["review_status"] == "Arithmetic matches inputs" for row in reviewed)
    summary = {"run_status": "review_complete" if rows else "no_records",
               "records_received": len(rows), "arithmetic_matches_inputs": matches,
               "records_needing_confirmation": len(rows) - matches,
               "comparison_tolerance_tzs": show(tolerance),
               "scope": "Base-premium arithmetic using supplied quote terms. No tariff or cover approval."}
    (args.output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
