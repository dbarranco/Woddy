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

        # Flowchart 2: Loading → Progression Scheme
        # Week-based loading intensity and rep scheme rules
        self.loading_rules = {
            1: {
                "intensity_min": 70,
                "intensity_max": 75,
                "rep_schemes": ["5x5", "4x5"],
            },
            2: {
                "intensity_min": 75,
                "intensity_max": 80,
                "rep_schemes": ["4x4", "4x3"],
            },
            3: {
                "intensity_min": 80,
                "intensity_max": 85,
                "rep_schemes": ["4x3", "5x2"],
            },
            4: {
                "intensity_min": 60,
                "intensity_max": 65,
                "rep_schemes": ["3x5", "3x3"],
            },
        }

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

    def _extract_intensity_percentage(self, load_string: str) -> Optional[float]:
        """Extract percentage from load string like '75% 1RM' or 'RPE 7'.

        Returns: float (0-100) for percentage, or None if unparseable
        """
        if not load_string:
            return None

        load_lower = load_string.lower()

        # Handle "X% 1RM" format
        if "%" in load_string:
            try:
                return float(load_string.split("%")[0].strip())
            except (ValueError, IndexError):
                return None

        # RPE and RIR handled separately — skip for now (outside KB scope)
        return None

    def _extract_rep_scheme(self, movement: Dict) -> Optional[str]:
        """Extract rep scheme from movement.

        Looks for 'sets x reps' pattern in 'sets' and 'reps' fields.
        Returns: 'SxR' format (e.g., '5x5', '4x3') or None
        """
        sets = movement.get("sets")
        reps = movement.get("reps")

        if sets is None or reps is None:
            return None

        # Handle reps as string or int
        reps_str = str(reps).strip()

        # Simple case: single rep count
        if reps_str.isdigit():
            return f"{sets}x{reps_str}"

        # Range case: '3-5' — use minimum for scheme matching
        if "-" in reps_str:
            min_rep = reps_str.split("-")[0].strip()
            if min_rep.isdigit():
                return f"{sets}x{min_rep}"

        return None

    def _check_loading_intensity_alignment(
        self, session: Dict, week: int
    ) -> Tuple[bool, List[Tuple[str, bool, str]]]:
        """Validate Flowchart 2: Program week → loading intensity.

        Returns: (passed: bool, checks: List[(check_name, passed, reason)])
        """
        checks = []
        passed = True

        # Get strength block
        strength = session.get("blocks", {}).get("strength", {})
        if not strength:
            checks.append(("strength_block_exists", False, "No strength block found"))
            return (passed, checks)

        movements = strength.get("movements", [])
        if not movements:
            checks.append(
                ("strength_movements_exist", False, "No movements in strength block")
            )
            return (passed, checks)

        # Get week-specific loading rules
        week_rules = self.loading_rules.get(week)
        if not week_rules:
            checks.append(("week_valid", False, f"Week {week} not in loading rules"))
            passed = False
            return (passed, checks)

        intensity_min = week_rules["intensity_min"]
        intensity_max = week_rules["intensity_max"]
        allowed_schemes = week_rules["rep_schemes"]

        # Check first movement's intensity (proxy for session intensity)
        first_move = movements[0]
        intensity = self._extract_intensity_percentage(first_move.get("load", ""))

        if intensity is not None:
            intensity_ok = intensity_min <= intensity <= intensity_max
            checks.append(
                (
                    f"intensity_week_{week}",
                    intensity_ok,
                    f"Intensity {intensity}% {'is' if intensity_ok else 'is not'} in range {intensity_min}-{intensity_max}% for week {week}",
                )
            )
            if not intensity_ok:
                passed = False
        else:
            checks.append(
                (
                    f"intensity_week_{week}",
                    False,
                    f"Could not extract intensity percentage from load string '{first_move.get('load', '')}'",
                )
            )
            passed = False

        # Check rep scheme
        rep_scheme = self._extract_rep_scheme(first_move)
        if rep_scheme:
            scheme_ok = rep_scheme in allowed_schemes
            checks.append(
                (
                    f"rep_scheme_week_{week}",
                    scheme_ok,
                    f"Rep scheme {rep_scheme} {'is' if scheme_ok else 'is not'} in allowed list {allowed_schemes} for week {week}",
                )
            )
            if not scheme_ok:
                passed = False
        else:
            checks.append(
                (
                    f"rep_scheme_week_{week}",
                    False,
                    "Could not extract rep scheme from sets/reps fields",
                )
            )
            # Don't fail on this if it's optional

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
        """Validate a program against KB decision flowcharts."""
        passed = True
        checks = []

        # Extract sessions from program structure
        program_data = program.get("program", {})
        program_id = program_data.get("id", program.get("id", "unknown"))
        sessions = program_data.get("sessions", [])

        if not sessions:
            checks.append(("sessions_exist", False, "No sessions found in program"))
            return ValidationResult(passed=False, wod_id=program_id, checks=checks)

        # Validate each session
        for session in sessions:
            session_id = session.get("id", "unknown")
            week = session.get("week")

            if week is None:
                checks.append(
                    (f"session_{session_id}_week_defined", False, "Session has no week number")
                )
                passed = False
                continue

            # Flowchart 2: Loading intensity alignment
            fc2_passed, fc2_checks = self._check_loading_intensity_alignment(
                session, week
            )
            if not fc2_passed:
                passed = False

            # Format checks with session context
            for check_name, check_passed, reason in fc2_checks:
                qualified_name = f"session_{session_id}_{check_name}"
                checks.append((qualified_name, check_passed, reason))

        return ValidationResult(passed=passed, wod_id=program_id, checks=checks)


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
