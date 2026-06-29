#!/usr/bin/env python3
"""
KB Decision Flowcharts Validator

Validates that generated WODs follow the decision flowcharts documented in the knowledge base.
Ensures AI-generated content aligns with sports science principles.

Usage:
    python validate-kb-alignment.py --wod path/to/wod.json --verbose
    python validate-kb-alignment.py --program path/to/program.json --verbose
    python validate-kb-alignment.py --help
"""

import json
import argparse
import sys
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple


@dataclass
class ValidationResult:
    """Result of validating a WOD or program."""
    passed: bool
    wod_id: str
    checks: List[Tuple[str, bool, str]]

    def __str__(self) -> str:
        status = "PASS" if self.passed else "FAIL"
        lines = [f"[{status}] WOD {self.wod_id}"]
        for check_name, passed, reason in self.checks:
            symbol = "✓" if passed else "✗"
            lines.append(f"  {symbol} {check_name}: {reason}")
        return "\n".join(lines)


class KBValidator:
    """Validates WODs against KB decision flowcharts."""

    def __init__(self):
        """Initialize validator with hardcoded energy system rules."""
        # Flowchart 1: Energy System → Metcon Format mapping
        # Based on physiology: energy system determines optimal work/rest ratio
        self.energy_system_rules = {
            "phosphocreatine": {
                "description": "ATP-PC system (high power output, 0-8 seconds naturally)",
                "allowed_formats": ["EMOM", "E2MOM", "E3MOM"],
                "time_cap_min": 8,
                "time_cap_max": 12,
            },
            "glycolytic": {
                "description": "Anaerobic glycolysis (high intensity, 30 seconds to ~3 minutes)",
                "allowed_formats": ["AMRAP", "For Time"],
                "time_cap_min": 7,
                "time_cap_max": 15,
            },
            "oxidative": {
                "description": "Aerobic oxidation (base building, sustained effort)",
                "allowed_formats": ["AMRAP"],
                "time_cap_min": 15,
                "time_cap_max": 20,
            },
        }

        # Flowchart 2: Loading → Progression Scheme (placeholder for future)
        self.loading_rules = {}

    def _extract_energy_system_from_rationale(
        self, rationale: Dict
    ) -> Optional[str]:
        """Extract energy system target from session rationale.

        Looks for keywords in session_why.text:
        - 'phosphocreatine' or 'ATP-PC' or 'maximal effort'
        - 'glycolytic' or 'anaerobic' or 'high-intensity'
        - 'oxidative' or 'aerobic' or 'base work'

        Returns: 'phosphocreatine', 'glycolytic', 'oxidative', or None
        """
        if not rationale or "session_why" not in rationale:
            return None

        text = rationale["session_why"].get("text", "").lower()

        if any(
            kw in text
            for kw in [
                "phosphocreatine",
                "atp-pc",
                "maximal effort",
                "heavy single",
            ]
        ):
            return "phosphocreatine"
        elif any(
            kw in text
            for kw in ["glycolytic", "anaerobic", "high-intensity", "metcon intensity"]
        ):
            return "glycolytic"
        elif any(kw in text for kw in ["oxidative", "aerobic", "base", "long effort"]):
            return "oxidative"

        return None

    def _check_metcon_format_alignment(
        self, wod: Dict
    ) -> Tuple[bool, List[Tuple[str, bool, str]]]:
        """Validate Flowchart 1: Energy system → metcon format.

        Returns: (passed: bool, checks: List[(check_name, passed, reason)])
        """
        checks = []
        passed = True

        # Extract energy system goal from rationale
        rationale = wod.get("rationale", {})
        energy_system = self._extract_energy_system_from_rationale(rationale)

        if not energy_system:
            checks.append(
                (
                    "energy_system_stated",
                    False,
                    "Rationale does not state energy system target",
                )
            )
            passed = False
            return (passed, checks)

        # Get metcon block
        metcon = wod.get("blocks", {}).get("metcon", {})
        if not metcon:
            checks.append(("metcon_exists", False, "No metcon block found"))
            passed = False
            return (passed, checks)

        # Extract format and time cap
        format_chosen = metcon.get("format", "unknown")
        time_cap = metcon.get("time_cap_minutes", 0)

        # Get expected rules for this energy system
        rules = self.energy_system_rules.get(energy_system, {})
        allowed = rules.get("allowed_formats", [])
        cap_min = rules.get("time_cap_min", 0)
        cap_max = rules.get("time_cap_max", 100)

        # Check format matches energy system
        format_match = format_chosen in allowed
        checks.append(
            (
                f"format_for_{energy_system}",
                format_match,
                f"Format {format_chosen} {'is' if format_match else 'is not'} in allowed list {allowed} for {energy_system}",
            )
        )
        if not format_match:
            passed = False

        # Check time cap is in range
        cap_ok = cap_min <= time_cap <= cap_max
        checks.append(
            (
                f"time_cap_for_{energy_system}",
                cap_ok,
                f"Time cap {time_cap}min {'is' if cap_ok else 'is not'} in range {cap_min}-{cap_max}min for {energy_system}",
            )
        )
        if not cap_ok:
            passed = False

        return (passed, checks)

    def validate_wod(self, wod: Dict) -> ValidationResult:
        """Validate a single WOD against KB rules."""
        passed = True
        checks = []

        # Flowchart 1: Energy system → metcon format
        fc1_passed, fc1_checks = self._check_metcon_format_alignment(wod)
        checks.extend(fc1_checks)
        if not fc1_passed:
            passed = False

        return ValidationResult(passed=passed, wod_id=wod.get("id", "unknown"), checks=checks)

    def validate_program(self, program: Dict) -> ValidationResult:
        """Validate a program (placeholder for future flowcharts)."""
        # TODO: Implement flowchart validations for programs
        return ValidationResult(
            passed=True, wod_id=program.get("id", "unknown"), checks=[]
        )


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Validate generated WODs against KB decision flowcharts"
    )
    parser.add_argument(
        "--wod",
        type=str,
        help="Path to WOD JSON file to validate",
    )
    parser.add_argument(
        "--program",
        type=str,
        help="Path to program JSON file to validate",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show detailed check results",
    )

    args = parser.parse_args()

    if not args.wod and not args.program:
        parser.print_help()
        return 1

    validator = KBValidator()

    if args.wod:
        try:
            with open(args.wod, "r") as f:
                wod = json.load(f)
            result = validator.validate_wod(wod)
            print(result)
            return 0 if result.passed else 1
        except FileNotFoundError:
            print(f"Error: File not found: {args.wod}", file=sys.stderr)
            return 1
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in {args.wod}: {e}", file=sys.stderr)
            return 1

    if args.program:
        try:
            with open(args.program, "r") as f:
                program = json.load(f)
            result = validator.validate_program(program)
            print(result)
            return 0 if result.passed else 1
        except FileNotFoundError:
            print(f"Error: File not found: {args.program}", file=sys.stderr)
            return 1
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in {args.program}: {e}", file=sys.stderr)
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
