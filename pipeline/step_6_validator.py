"""Step 6: Validator - Check week meets all constraints."""

import os
import json
from datetime import datetime
from anthropic import Anthropic
from pipeline.models import ValidationResult, ValidationIssue
from pipeline.utils import load_artifact, write_artifact


def run_validator(
    program_name: str,
    week_number: int,
    kb = None,
    model: str = "claude-3-5-haiku-20241022"
) -> ValidationResult:
    """Validate week against all rules."""

    # Load summaries
    week_summary = load_artifact(program_name, f"week-{week_number}-summary.json")
    prev_week_summary = None
    if week_number > 1:
        try:
            prev_week_summary = load_artifact(program_name, f"week-{week_number - 1}-summary.json")
        except:
            pass

    if kb is None:
        kb = load_artifact(program_name, "knowledge-base.json")

    # Perform validations
    issues: list[ValidationIssue] = []

    # Check 1: Volume progression
    if prev_week_summary:
        prev_reps = prev_week_summary["total_volume"]["reps"]
        curr_reps = week_summary["total_volume"]["reps"]
        pct_increase = ((curr_reps - prev_reps) / prev_reps) * 100 if prev_reps > 0 else 0

        if pct_increase > 15:
            issues.append({
                "rule_id": "volume-progression",
                "severity": "critical",
                "message": f"Volume increased {pct_increase:.1f}% (>15% limit)",
                "action": "regenerate"
            })
        elif pct_increase > 12:
            issues.append({
                "rule_id": "volume-progression",
                "severity": "warning",
                "message": f"Volume increased {pct_increase:.1f}% (approaching limit)",
                "action": "monitor"
            })

    # Check 2: Push:pull ratio
    ratio = week_summary["push_pull_ratio"]
    if ratio < 1.0:
        issues.append({
            "rule_id": "push-pull-ratio",
            "severity": "high",
            "message": f"Push:pull ratio is {ratio:.2f} (<1:1 target)",
            "action": "regenerate"
        })

    # Check 3: Pattern concerns
    if week_summary["pattern_concerns"]:
        issues.append({
            "rule_id": "movement-repetition",
            "severity": "warning",
            "message": f"Movement patterns: {'; '.join(week_summary['pattern_concerns'])}",
            "action": "monitor"
        })

    # Create validation result
    valid = not any(i["action"] == "regenerate" for i in issues)
    timestamp = datetime.isoformat(datetime.now())

    result: ValidationResult = {
        "week": week_number,
        "validation_timestamp": timestamp,
        "valid": valid,
        "issues": issues,
        "retry_count": 0,
        "max_retries": 3
    }

    write_artifact(program_name, f"week-{week_number}-validation.json", result)
    status = "✅ PASS" if valid else "⚠️  FAIL"
    print(f"{status} Week {week_number} validation: {len(issues)} issues found")

    return result
