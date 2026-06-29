#!/usr/bin/env python3
"""
CrossFit Program Generator
Builds a full program from the knowledge base and hard rules,
calls the Claude API, validates output, and writes to markdown/JSON.

Usage:
    python generate.py --type program --name "back-in-shape" --weeks 3
    python generate.py --type wod --count 7 --category full-body
    python generate.py --type skill --name "gymnastics-base"
"""

import os
import json
import argparse
import subprocess
import sys
from pathlib import Path
import anthropic

# ── Paths ──────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).parent.parent
KB_DIR = ROOT / "knowledge-base"
DATA_DIR = ROOT / "data"
OUTPUT_DIR = ROOT / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

# ── Load knowledge base ────────────────────────────────────────────────────────

def load_knowledge_base() -> str:
    """Load and concatenate all knowledge base markdown files."""
    docs = []
    for f in sorted(KB_DIR.glob("*.md")):
        docs.append(f"### {f.stem.upper()}\n\n{f.read_text()}")
    return "\n\n---\n\n".join(docs)


def load_movement_library() -> dict:
    return json.loads((DATA_DIR / "movement-library.json").read_text())


def load_hard_rules() -> dict:
    return json.loads((DATA_DIR / "hard-rules.json").read_text())


# ── Prompt builders ────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are an expert CrossFit strength and conditioning coach with deep knowledge of sports science and periodization. You generate training programs strictly from the knowledge base and rules provided to you.

CRITICAL CONSTRAINTS — you must follow all of these:
1. You NEVER invent loading percentages, energy system claims, or scientific references.
2. Every rationale must cite a source that exists in the allowed_sources list in the hard rules.
3. You NEVER fabricate citations or authors.
4. If a concept is not in the knowledge base, you do not use it.
5. All session durations must respect the hard rules (full session ≤60 min, skill session ≤30 min).
6. Weekly structure must respect all frequency limits, sequencing rules, and movement balance rules.
7. Your output must be PERFECTLY VALID JSON matching the schema exactly. No prose, no markdown, no explanation outside the JSON fields.
8. If you cannot fill a required field from the knowledge base, set it to null — never guess.
9. CRITICAL: All strings in your JSON must be properly quoted with double quotes. Check for unterminated strings.
10. CRITICAL: All objects and arrays must have matching braces and brackets. Your JSON must be 100% syntactically valid.
11. If generating multiple items (like WODs), ensure the outer JSON structure is an object with a single top-level key ("program", "wods", etc).

KB FLOWCHART ALIGNMENT (from Knowledge Base Decision Flowcharts):
- FLOWCHART 1 (Energy System → Metcon Format): ALWAYS state the energy system target in session_why rationale. Match format to energy system:
  * Phosphocreatine (0-10s): Use EMOM/E2MOM/E3MOM format, time cap 8-12 min
  * Glycolytic (10s-2m): Use AMRAP/For Time/RFT format, time cap 7-15 min
  * Oxidative (>2m): Use AMRAP format, time cap 15-20 min
- FLOWCHART 2 (Week → Loading Intensity): Match intensity % and rep scheme to program week:
  * Week 1: 70-75% 1RM, rep schemes 5x5 or 4x5
  * Week 2: 75-80% 1RM, rep schemes 4x4 or 4x3
  * Week 3: 80-85% 1RM, rep schemes 4x3 or 5x2
  * Week 4: 60-65% 1RM (deload), rep schemes 3x5 or 3x3
- FLOWCHART 3 (Weekly Sequencing): Plan weekly sequence to minimize interference:
  * No Olympic lifting on consecutive days
  * No heavy lower body (>75% 1RM) on consecutive days
  * No high-CNS sessions back-to-back
  * Minimum 1 aerobic session per week

RATIONALE REQUIREMENTS:
- session_why: ALWAYS explicitly state which energy system you're training (phosphocreatine, glycolytic, or oxidative)
- movement_why: Explain the movement selection and how it supports the session goal
- loading_why: ALWAYS reference the specific week's loading progression and cite the appropriate KB source

You are assembling from a foundation of verified knowledge. You are not inventing."""


def build_program_prompt(name: str, weeks: int, kb: str, movements: dict, rules: dict) -> str:
    return f"""Generate a complete {weeks}-week CrossFit training program called "{name}".

KNOWLEDGE BASE:
{kb}

MOVEMENT LIBRARY:
{json.dumps(movements, indent=2)}

HARD RULES (you must not violate any of these):
{json.dumps(rules, indent=2)}

PROGRAM REQUIREMENTS:
- {weeks} weeks × 5 sessions per week = {weeks * 5} total sessions
- 2 rest days per week (do not generate sessions for rest days, mark them)
- Each session: 60 minutes total (5 static warmup + 5 active warmup + 20-25 strength + 10-20 metcon + 5-10 cooldown)
- Progressive loading across weeks per the loading rules
- {"Include a deload in week 4." if weeks == 4 else "No deload required for " + str(weeks) + "-week program."}
- Every session must have a rationale block with real citations from allowed_sources only

OUTPUT FORMAT — return this exact JSON structure, nothing else:
{{
  "program": {{
    "id": "string (kebab-case)",
    "name": "string",
    "weeks": {weeks},
    "focus": "string (e.g. general, strength, gymnastics)",
    "description": "string (2-3 sentences, natural language)",
    "sessions": [
      {{
        "id": "string (e.g. w1d1)",
        "week": 1,
        "day": 1,
        "is_rest_day": false,
        "title": "string",
        "duration_minutes": 60,
        "equipment": ["list of required equipment"],
        "blocks": {{
          "static_warmup": {{
            "duration_minutes": 5,
            "movements": [
              {{ "name": "string", "reps_or_duration": "string", "notes": "string or null" }}
            ]
          }},
          "active_warmup": {{
            "duration_minutes": 5,
            "movements": [
              {{ "name": "string", "reps_or_duration": "string", "notes": "string or null" }}
            ]
          }},
          "strength": {{
            "duration_minutes": 22,
            "label": "string (e.g. Strength — Back Squat)",
            "movements": [
              {{
                "name": "string",
                "sets": 4,
                "reps": "string (e.g. '5' or '3-5')",
                "load": "string (e.g. '75% 1RM' or 'RPE 7-8')",
                "rest_seconds": 180,
                "notes": "string or null",
                "scaling": "string"
              }}
            ]
          }},
          "metcon": {{
            "duration_minutes": 15,
            "format": "AMRAP | EMOM | For Time | RFT",
            "time_cap_minutes": 12,
            "rounds_or_duration": "string (e.g. '12 min AMRAP' or '5 rounds')",
            "movements": [
              {{
                "name": "string",
                "reps_or_duration": "string",
                "load": "string or null",
                "scaling": "string"
              }}
            ],
            "target_score": "string (e.g. '4+ rounds', 'sub 10 min') or null",
            "timer_config": {{
              "type": "amrap | emom | for_time",
              "duration_seconds": 720,
              "interval_seconds": null
            }}
          }},
          "cooldown": {{
            "duration_minutes": 8,
            "movements": [
              {{ "name": "string", "reps_or_duration": "string", "notes": "string or null" }}
            ]
          }}
        }},
        "rationale": {{
          "session_why": {{
            "text": "string (why this session today — energy system, placement in week)",
            "source": "string (exact source name from allowed_sources)",
            "url_or_ref": "string (e.g. 'Ch. 20' or PubMed ID or null)"
          }},
          "movement_why": {{
            "text": "string (why these movements together — pairing logic, adaptation target)",
            "source": "string",
            "url_or_ref": "string or null"
          }},
          "loading_why": {{
            "text": "string (why this rep scheme and percentage — physiological rationale)",
            "source": "string",
            "url_or_ref": "string or null"
          }}
        }}
      }}
    ]
  }}
}}"""


def build_wod_prompt(count: int, category: str, kb: str, movements: dict, rules: dict) -> str:
    return f"""Generate {count} CrossFit WODs for the category: "{category}".

KNOWLEDGE BASE:
{kb}

MOVEMENT LIBRARY (use only movements from this library):
{json.dumps(movements, indent=2)}

HARD RULES:
{json.dumps(rules, indent=2)}

REQUIREMENTS:
- Each WOD is a complete 60-minute session (static warmup 5 min + active warmup 5 min + strength 20-25 min + metcon 10-20 min + cooldown 5-10 min)
- No two WODs should repeat the same main movements
- Each WOD must have a rationale block with real citations
- Vary metcon formats across the set (mix AMRAP, EMOM, For Time)
- Category filter: "{category}" — all WODs should fit this category

CRITICAL RATIONALE REQUIREMENTS:
- session_why MUST explicitly name the energy system being targeted:
  * Write "phosphocreatine" or "ATP-PC system" for short, max-effort work
  * Write "glycolytic system" or "anaerobic glycolysis" for high-intensity 30s-2min work
  * Write "oxidative system" or "aerobic base" for sustained long-duration work
  * This is checked by validation: energy system MUST be mentioned in session_why.text
- loading_why MUST describe why the intensity % and rep scheme are chosen (even for WODs without strength blocks)
- movement_why MUST explain how movements support the energy system being trained

Return this JSON structure, nothing else:
{{
  "wods": [
    {{
      "id": "string (e.g. wod-001)",
      "title": "string",
      "category": ["{category}"],
      "equipment": ["list"],
      "duration_minutes": 60,
      "blocks": {{
        "static_warmup": {{ "duration_minutes": 5, "movements": [] }},
        "active_warmup": {{ "duration_minutes": 5, "movements": [] }},
        "strength": {{ "duration_minutes": 22, "label": "string", "movements": [] }},
        "metcon": {{
          "duration_minutes": 15,
          "format": "string",
          "time_cap_minutes": 12,
          "rounds_or_duration": "string",
          "movements": [],
          "target_score": "string or null",
          "timer_config": {{ "type": "string", "duration_seconds": 720, "interval_seconds": null }}
        }},
        "cooldown": {{ "duration_minutes": 8, "movements": [] }}
      }},
      "rationale": {{
        "session_why": {{ "text": "string", "source": "string", "url_or_ref": "string or null" }},
        "movement_why": {{ "text": "string", "source": "string", "url_or_ref": "string or null" }},
        "loading_why": {{ "text": "string", "source": "string", "url_or_ref": "string or null" }}
      }}
    }}
  ]
}}"""


# ── API call ───────────────────────────────────────────────────────────────────

def call_claude(prompt: str, retries: int = 2, model: str = None) -> dict:
    """Call Claude API (if key available) or CLI. Retries on JSON parse failure."""

    # Try to use API if ANTHROPIC_API_KEY is available
    if "ANTHROPIC_API_KEY" in os.environ:
        return call_claude_api(prompt, retries, model)
    else:
        print("⚠️  ANTHROPIC_API_KEY not set. Using claude CLI (if available).")
        return call_claude_cli(prompt, retries, model)


def call_claude_api(prompt: str, retries: int = 2, model: str = None) -> dict:
    """Call Anthropic API and parse JSON response. Uses streaming for large requests."""
    client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from env
    model_id = model or "claude-sonnet-4-5-20250929"  # Default to Sonnet 4.5

    for attempt in range(1, retries + 1):
        print(f"→ Calling Claude API ({model_id})... (attempt {attempt}/{retries})")

        # Use streaming for all requests (safer for potentially long operations)
        raw = ""
        with client.messages.stream(
            model=model_id,
            max_tokens=20000,
            system=[
                {
                    "type": "text",
                    "text": SYSTEM_PROMPT,
                },
                {
                    "type": "text",
                    "text": "KNOWLEDGE BASE AND HARD RULES BELOW — CACHED FOR EFFICIENCY",
                    "cache_control": {"type": "ephemeral"}
                }
            ],
            messages=[{"role": "user", "content": prompt}]
        ) as stream:
            for text in stream.text_stream:
                raw += text

        response = stream.get_final_message()
        raw = raw.strip()

        # Log cache performance
        usage = response.usage
        print(f"   Input tokens: {usage.input_tokens} | Cache write: {getattr(usage, 'cache_creation_input_tokens', 0)} | Cache read: {getattr(usage, 'cache_read_input_tokens', 0)}")

        # Strip markdown fences if present
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1]
            raw = raw.rsplit("```", 1)[0]

        try:
            result = json.loads(raw)
            print(f"   ✅ JSON parsed successfully")
            return result
        except json.JSONDecodeError as e:
            if attempt < retries:
                print(f"   ❌ JSON parse error (attempt {attempt}): {e}")
                print(f"   Retrying...")
                continue
            else:
                print(f"ERROR: Failed to parse JSON after {retries} attempts: {e}")
                print("Raw response saved to output/debug-last-response.txt")
                (OUTPUT_DIR / "debug-last-response.txt").write_text(raw)
                raise


def call_claude_cli(prompt: str, retries: int = 2, model: str = None) -> dict:
    """Call Claude CLI and parse JSON response. Only used if API key unavailable."""

    for attempt in range(1, retries + 1):
        print(f"→ Calling Claude CLI (--model {model or 'default'})... (attempt {attempt}/{retries})")

        # Build the full prompt with system instructions
        full_prompt = f"""{SYSTEM_PROMPT}

KNOWLEDGE BASE AND HARD RULES BELOW:
{prompt}

Important: Return ONLY the JSON, no additional text or summary."""

        try:
            # Call claude CLI with --print for non-interactive output
            cmd = ["claude", "--print"]
            if model:
                cmd.extend(["--model", model])
            cmd.append("-")

            result = subprocess.run(
                cmd,
                input=full_prompt,
                capture_output=True,
                text=True,
                timeout=600  # 10 minutes for CLI (higher token context = slower)
            )

            if result.returncode != 0:
                print(f"   ❌ Claude CLI error: {result.stderr}")
                if attempt < retries:
                    print(f"   Retrying...")
                    continue
                else:
                    raise RuntimeError(f"Claude CLI failed: {result.stderr}")

            raw = result.stdout.strip()

            # Strip markdown fences if present
            if raw.startswith("```"):
                raw = raw.split("\n", 1)[1]
                raw = raw.rsplit("```", 1)[0]

            try:
                parsed = json.loads(raw)
                print(f"   ✅ JSON parsed successfully")
                return parsed
            except json.JSONDecodeError as e:
                if attempt < retries:
                    print(f"   ❌ JSON parse error (attempt {attempt}): {e}")
                    print(f"   Retrying...")
                    continue
                else:
                    print(f"ERROR: Failed to parse JSON after {retries} attempts: {e}")
                    print("Raw response saved to output/debug-last-response.txt")
                    (OUTPUT_DIR / "debug-last-response.txt").write_text(raw)
                    raise
        except subprocess.TimeoutExpired:
            print(f"   ❌ Claude CLI timeout (attempt {attempt})")
            if attempt < retries:
                print(f"   Retrying...")
                continue
            else:
                raise RuntimeError("Claude CLI timed out after all retries")


# ── Validation ─────────────────────────────────────────────────────────────────

def validate_schema_structure(data: dict, content_type: str) -> list[str]:
    """Validate that the generated JSON matches the expected structure. Returns list of violations."""
    violations = []

    # Check for undefined values in the JSON structure
    json_str = json.dumps(data)
    if '"undefined"' in json_str or ':undefined' in json_str or 'undefined,' in json_str:
        violations.append("Generated content contains literal 'undefined' values - this indicates missing movement names or block content")
        return violations

    if content_type == "program":
        # Check top-level structure
        if "program" not in data:
            violations.append("Missing top-level 'program' key")
            return violations

        program = data["program"]
        if not isinstance(program.get("sessions"), list):
            violations.append("'program.sessions' must be a list")
            return violations

        if len(program.get("sessions", [])) == 0:
            violations.append("'program.sessions' must not be empty")
            return violations

        # Spot-check first session structure
        first_session = program["sessions"][0]
        required_fields = ["id", "title", "blocks", "rationale"]
        for field in required_fields:
            if field not in first_session:
                violations.append(f"Session missing required field: '{field}'")

        # Check blocks structure
        if "blocks" in first_session:
            blocks = first_session["blocks"]
            required_blocks = ["static_warmup", "active_warmup", "strength", "metcon", "cooldown"]
            for block in required_blocks:
                if block not in blocks:
                    violations.append(f"Session missing required block: '{block}'")
                elif not isinstance(blocks[block].get("movements"), list):
                    violations.append(f"Block '{block}.movements' must be a list")

        # Check rationale structure
        if "rationale" in first_session:
            rationale = first_session["rationale"]
            required_rationale = ["session_why", "movement_why", "loading_why"]
            for field in required_rationale:
                if field not in rationale:
                    violations.append(f"Rationale missing required field: '{field}'")
                elif not isinstance(rationale[field], dict) or "text" not in rationale[field]:
                    violations.append(f"Rationale.{field} must be an object with 'text' field")

    elif content_type == "wod":
        # Check top-level structure
        if "wods" not in data:
            violations.append("Missing top-level 'wods' key")
            return violations

        wods = data["wods"]
        if not isinstance(wods, list):
            violations.append("'wods' must be a list")
            return violations

        if len(wods) == 0:
            violations.append("'wods' must not be empty")
            return violations

    return violations


def validate_program(program: dict, rules: dict, movements: dict = None) -> list[str]:
    """Comprehensive validation of generated program against hard rules. Returns list of violations."""
    violations = []
    sessions = program.get("program", {}).get("sessions", [])

    if not sessions:
        violations.append("Program has no sessions")
        return violations

    # Build movement set for validation (if provided)
    valid_movements = set()
    if movements:
        for category in movements.get("categories", {}).values():
            valid_movements.update(m.get("name", "").lower() for m in category.get("movements", []))

    # Track metrics for weekly validation
    weekly_metrics = {}
    progression_schemes_used = set()

    for s in sessions:
        if s.get("is_rest_day"):
            continue

        session_id = s.get("id", "unknown")
        week = s.get("week", 1)

        # Initialize weekly tracking for this week
        if week not in weekly_metrics:
            weekly_metrics[week] = {
                "olympic_sessions": 0,
                "heavy_lower": 0,
                "heavy_upper": 0,
                "high_intensity_metcons": 0,
                "aerobic_sessions": 0,
                "metcon_formats": [],
                "prev_day_session": None
            }

        # ─── Session Duration Validation ───
        dur = s.get("duration_minutes", 0)
        if dur > rules["session"]["full_session_max_minutes"]:
            violations.append(f"Session {session_id}: duration {dur} exceeds {rules['session']['full_session_max_minutes']} min")

        # ─── Block Duration Validation ───
        blocks = s.get("blocks", {})
        block_durations = {}
        for block_name in ["static_warmup", "active_warmup", "strength", "metcon", "cooldown"]:
            block = blocks.get(block_name, {})
            block_dur = block.get("duration_minutes", 0)
            block_durations[block_name] = block_dur

            if block_name == "static_warmup" and block_dur != 5:
                violations.append(f"Session {session_id}: static_warmup duration {block_dur} should be 5 min")
            elif block_name == "active_warmup" and block_dur != 5:
                violations.append(f"Session {session_id}: active_warmup duration {block_dur} should be 5 min")
            elif block_name == "strength":
                expected_min, expected_max = rules["session"]["blocks"]["strength_block_minutes"]["min"], rules["session"]["blocks"]["strength_block_minutes"]["max"]
                if not (expected_min <= block_dur <= expected_max):
                    violations.append(f"Session {session_id}: strength duration {block_dur} outside {expected_min}-{expected_max} min range")
            elif block_name == "metcon":
                expected_min, expected_max = rules["session"]["blocks"]["metcon_minutes"]["min"], rules["session"]["blocks"]["metcon_minutes"]["max"]
                if not (expected_min <= block_dur <= expected_max):
                    violations.append(f"Session {session_id}: metcon duration {block_dur} outside {expected_min}-{expected_max} min range")
            elif block_name == "cooldown":
                expected_min, expected_max = rules["session"]["blocks"]["cooldown_minutes"]["min"], rules["session"]["blocks"]["cooldown_minutes"]["max"]
                if not (expected_min <= block_dur <= expected_max):
                    violations.append(f"Session {session_id}: cooldown duration {block_dur} outside {expected_min}-{expected_max} min range")

        # ─── Movement Name Validation ───
        if valid_movements:
            for block_name in ["static_warmup", "active_warmup", "strength", "metcon", "cooldown"]:
                block = blocks.get(block_name, {})
                for movement in block.get("movements", []):
                    mov_name = movement.get("name", "").lower().strip()
                    if mov_name and mov_name not in valid_movements:
                        violations.append(f"Session {session_id}: '{mov_name}' not found in movement library")

        # ─── Metcon Validation ───
        metcon = blocks.get("metcon", {})
        if metcon and isinstance(metcon, dict):
            metcon_format = metcon.get("format", "")
            if metcon_format:
                metcon_format = metcon_format.upper()
                if metcon_format not in rules["session"]["metcon"]["allowed_formats"]:
                    violations.append(f"Session {session_id}: metcon format '{metcon_format}' not in allowed formats {rules['session']['metcon']['allowed_formats']}")

                time_cap = metcon.get("time_cap_minutes", 0)
                if time_cap > rules["session"]["metcon"]["max_time_cap_minutes"]:
                    violations.append(f"Session {session_id}: metcon time cap {time_cap} exceeds {rules['session']['metcon']['max_time_cap_minutes']} min")

                # Track for weekly validation
                weekly_metrics[week]["metcon_formats"].append(metcon_format)
                if metcon_format in ["AMRAP", "FOR TIME"]:
                    weekly_metrics[week]["high_intensity_metcons"] += 1

        # ─── Equipment Validation ───
        equipment = s.get("equipment", [])
        for item in equipment:
            if item in rules["equipment_restrictions"]["forbidden_equipment"]:
                violations.append(f"Session {session_id}: forbidden equipment '{item}'")

        # ─── Rationale Validation ───
        rationale = s.get("rationale", {})
        for key in ["session_why", "movement_why", "loading_why"]:
            if not rationale.get(key, {}).get("text"):
                violations.append(f"Session {session_id}: missing rationale.{key}.text")

            source = rationale.get(key, {}).get("source", "")
            allowed = rules["rationale"]["allowed_sources"]
            # Check if source appears in allowed sources (case-insensitive, partial match)
            if source:
                source_found = False
                for allowed_src in allowed:
                    if source.lower() in allowed_src.lower() or allowed_src.lower() in source.lower():
                        source_found = True
                        break
                if not source_found:
                    violations.append(f"Session {session_id}: rationale.{key}.source '{source}' not in allowed sources")

        # ─── Progression Scheme Tracking ───
        if "strength" in blocks and blocks["strength"].get("movements"):
            # Simple heuristic: check loading pattern from first strength movement
            first_movement = blocks["strength"]["movements"][0]
            load = first_movement.get("load", "").lower()
            if "%" in load or "rpe" in load.lower():
                # Track scheme for variety validation later
                if "rpe" in load.lower():
                    scheme_type = "rpe-based"
                elif any(x in load for x in ["%"]):
                    scheme_type = "percentage-based"
                else:
                    scheme_type = "unknown"
                progression_schemes_used.add(scheme_type)

    # ─── Weekly Validation ───
    for week, metrics in weekly_metrics.items():
        if metrics["high_intensity_metcons"] > rules["weekly"]["frequency_limits"]["high_intensity_metcon_sessions_max"]:
            violations.append(f"Week {week}: {metrics['high_intensity_metcons']} high-intensity metcon sessions exceed max {rules['weekly']['frequency_limits']['high_intensity_metcon_sessions_max']}")

        if metrics["aerobic_sessions"] < rules["weekly"]["frequency_limits"]["aerobic_sessions_min"]:
            violations.append(f"Week {week}: {metrics['aerobic_sessions']} aerobic sessions below minimum {rules['weekly']['frequency_limits']['aerobic_sessions_min']}")

    # ─── Program Structure Validation ───
    program_weeks = program.get("program", {}).get("weeks", 0)
    if program_weeks == 4:
        # Check that week 4 exists and has deload indicator
        week_4_sessions = [s for s in sessions if s.get("week") == 4 and not s.get("is_rest_day")]
        if week_4_sessions:
            # Week 4 should have moderate intensity noted in rationale
            w4_intensities = [s.get("rationale", {}).get("session_why", {}).get("text", "").lower() for s in week_4_sessions]
            if not any("deload" in t or "recovery" in t for t in w4_intensities):
                violations.append(f"Week 4 (deload): sessions should emphasize recovery/reduced intensity")

    return violations


# ── Markdown renderer ──────────────────────────────────────────────────────────

def render_session_markdown(session: dict) -> str:
    """Render a single session as readable markdown."""
    if session.get("is_rest_day"):
        return f"## {session['id'].upper()} — Rest Day\n\nActive recovery. Walk, stretch, sleep well.\n"

    lines = []
    lines.append(f"## {session['id'].upper()} — {session.get('title', '')}")

    # Program sessions have week/day, WODs don't
    if 'week' in session and 'day' in session:
        lines.append(f"**Duration:** {session.get('duration_minutes', 60)} min | "
                     f"**Week {session['week']}, Day {session['day']}**\n")
    else:
        lines.append(f"**Duration:** {session.get('duration_minutes', 60)} min\n")

    equipment = session.get("equipment", [])
    if equipment:
        lines.append(f"### 🎒 Equipment Needed\n")
        for item in equipment:
            lines.append(f"- {item}")
        lines.append("")

    blocks = session.get("blocks", {})

    # Static warmup
    sw = blocks.get("static_warmup", {})
    if sw:
        lines.append(f"### 🧘 Static Warmup ({sw.get('duration_minutes', 5)} min)\n")
        for m in sw.get("movements", []):
            note = f" — *{m['notes']}*" if m.get("notes") else ""
            reps = m.get('reps_or_duration', m.get('reps', ''))
            lines.append(f"- {m['name']} — {reps}{note}")
        lines.append("")

    # Active warmup
    aw = blocks.get("active_warmup", {})
    if aw:
        lines.append(f"### 🏃 Active Warmup ({aw.get('duration_minutes', 5)} min)\n")
        for m in aw.get("movements", []):
            note = f" — *{m['notes']}*" if m.get("notes") else ""
            reps = m.get('reps_or_duration', m.get('reps', ''))
            lines.append(f"- {m['name']} — {reps}{note}")
        lines.append("")

    # Strength
    st = blocks.get("strength", {})
    if st:
        lines.append(f"### 💪 {st.get('label', 'Strength Block')} ({st.get('duration_minutes', 22)} min)\n")
        for m in st.get("movements", []):
            load = f" @ {m['load']}" if m.get("load") else ""
            rest = f" | Rest {m['rest_seconds']}s" if m.get("rest_seconds") else ""
            # Handle both 'rest' string and 'rest_seconds' fields
            if not rest and m.get("rest"):
                rest = f" | {m['rest']}"
            note = f"\n  > *{m['notes']}*" if m.get("notes") else ""
            scale = f"\n  > **Scale:** {m['scaling']}" if m.get("scaling") else ""
            # Strength movements can have either 'reps' or 'reps_or_duration'
            reps_info = m.get('reps', m.get('reps_or_duration', ''))
            # Handle both program strength (with 'sets') and other movement types
            sets_info = f"{m['sets']}×" if m.get('sets') else ""
            lines.append(f"- **{m['name']}** — {sets_info}{reps_info}{load}{rest}{note}{scale}")
        lines.append("")

    # Metcon
    mc = blocks.get("metcon", {})
    if mc:
        lines.append(f"### 🔥 Metcon — {mc.get('rounds_or_duration', '')} ({mc.get('duration_minutes', 15)} min)\n")
        lines.append(f"**Format:** {mc.get('format', '')} | **Time cap:** {mc.get('time_cap_minutes', '')} min\n")
        for m in mc.get("movements", []):
            load = f" @ {m['load']}" if m.get("load") else ""
            scale = f" *(Scale: {m['scaling']})*" if m.get("scaling") else ""
            # Metcon movements use "reps" field, warmup/cooldown use "reps_or_duration"
            reps = m.get('reps', m.get('reps_or_duration', ''))
            lines.append(f"- {reps} {m['name']}{load}{scale}")
        if mc.get("target_score"):
            lines.append(f"\n**Target:** {mc['target_score']}")
        lines.append("")

    # Cooldown
    cd = blocks.get("cooldown", {})
    if cd:
        lines.append(f"### 🧊 Cooldown & Mobility ({cd.get('duration_minutes', 8)} min)\n")
        for m in cd.get("movements", []):
            note = f" — *{m['notes']}*" if m.get("notes") else ""
            reps = m.get('reps_or_duration', m.get('reps', ''))
            lines.append(f"- {m['name']} — {reps}{note}")
        lines.append("")

    # Rationale
    rat = session.get("rationale", {})
    if rat:
        lines.append("### 🔬 Why This Session?\n")
        for key, label in [("session_why", "Session design"), ("movement_why", "Movement selection"), ("loading_why", "Loading rationale")]:
            r = rat.get(key, {})
            if r.get("text"):
                ref = f" *— {r['source']}*" if r.get("source") else ""
                lines.append(f"**{label}:** {r['text']}{ref}\n")
        lines.append("")

    lines.append("---\n")
    return "\n".join(lines)


def render_program_markdown(data: dict) -> str:
    """Render a full program as markdown."""
    prog = data.get("program", {})
    lines = []
    lines.append(f"# {prog.get('name', 'Program')}")
    lines.append(f"**{prog.get('weeks', '?')} weeks** | {prog.get('focus', '').title()} focus\n")
    lines.append(f"{prog.get('description', '')}\n")
    lines.append("---\n")

    for session in prog.get("sessions", []):
        lines.append(render_session_markdown(session))

    return "\n".join(lines)


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="CrossFit Program Generator")
    parser.add_argument("--type", choices=["program", "wod", "skill"], required=True)
    parser.add_argument("--name", type=str, default="back-in-shape")
    parser.add_argument("--weeks", type=int, choices=[2, 3, 4], default=3)
    parser.add_argument("--count", type=int, default=7, help="Number of WODs to generate")
    parser.add_argument("--category", type=str, default="full-body",
                        choices=["upper-body", "lower-body", "full-body", "cardio", "strength"])
    parser.add_argument("--model", type=str, default=None,
                        help="Claude model to use (e.g., 'opus' or full model ID). For API: uses full model ID. For CLI: passes to --model flag.")
    args = parser.parse_args()

    print("Loading knowledge base...")
    kb = load_knowledge_base()
    movements = load_movement_library()
    rules = load_hard_rules()
    print(f"  Knowledge base: {len(kb)} chars across {len(list(KB_DIR.glob('*.md')))} documents")
    print(f"  Movement library: {sum(len(c['movements']) for c in movements['categories'].values())} movements")

    if args.type == "program":
        print(f"\nGenerating {args.weeks}-week program: {args.name}")
        prompt = build_program_prompt(args.name, args.weeks, kb, movements, rules)
        data = call_claude(prompt, model=args.model)

        print("Validating structure...")
        schema_violations = validate_schema_structure(data, "program")
        if schema_violations:
            print(f"❌ Schema validation failed:")
            for v in schema_violations:
                print(f"   - {v}")
            raise ValueError(f"Generated JSON does not match expected schema")

        print("Validating against hard rules...")
        violations = validate_program(data, rules, movements)
        if violations:
            print(f"⚠️  {len(violations)} validation issues:")
            for v in violations:
                print(f"   - {v}")
        else:
            print("✅ Validation passed (0 warnings)")

        # Save JSON
        json_path = OUTPUT_DIR / f"{args.name}-{args.weeks}w.json"
        json_path.write_text(json.dumps(data, indent=2))
        print(f"\nJSON saved: {json_path}")

        # Save Markdown
        md_path = OUTPUT_DIR / f"{args.name}-{args.weeks}w.md"
        md_path.write_text(render_program_markdown(data))
        print(f"Markdown saved: {md_path}")

    elif args.type == "wod":
        print(f"\nGenerating {args.count} WODs — category: {args.category}")
        prompt = build_wod_prompt(args.count, args.category, kb, movements, rules)
        data = call_claude(prompt, model=args.model)

        print("Validating structure...")
        schema_violations = validate_schema_structure(data, "wod")
        if schema_violations:
            print(f"❌ Schema validation failed:")
            for v in schema_violations:
                print(f"   - {v}")
            raise ValueError(f"Generated JSON does not match expected schema")

        json_path = OUTPUT_DIR / f"wods-{args.category}.json"
        json_path.write_text(json.dumps(data, indent=2))
        print(f"JSON saved: {json_path}")

        # Render each WOD to markdown
        md_lines = [f"# WODs — {args.category.replace('-', ' ').title()}\n"]
        for wod in data.get("wods", []):
            md_lines.append(render_session_markdown(wod))
        md_path = OUTPUT_DIR / f"wods-{args.category}.md"
        md_path.write_text("\n".join(md_lines))
        print(f"Markdown saved: {md_path}")

    print("\nDone.")


if __name__ == "__main__":
    main()

