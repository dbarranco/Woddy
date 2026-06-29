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


def validate_program(program: dict, rules: dict) -> list[str]:
    """Basic validation of generated program against hard rules. Returns list of violations."""
    violations = []
    sessions = program.get("program", {}).get("sessions", [])

    for s in sessions:
        if s.get("is_rest_day"):
            continue
        dur = s.get("duration_minutes", 0)
        if dur > rules["session"]["full_session_max_minutes"]:
            violations.append(f"Session {s['id']}: duration {dur} exceeds 60 min")

        rationale = s.get("rationale", {})
        for key in ["session_why", "movement_why", "loading_why"]:
            if not rationale.get(key, {}).get("text"):
                violations.append(f"Session {s['id']}: missing rationale.{key}.text")
            source = rationale.get(key, {}).get("source", "")
            allowed = rules["rationale"]["allowed_sources"]
            if source and not any(a.lower() in source.lower() or source.lower() in a.lower() for a in allowed):
                violations.append(f"Session {s['id']}: rationale.{key}.source '{source}' not in allowed sources")

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
        violations = validate_program(data, rules)
        if violations:
            print(f"⚠️  {len(violations)} validation issues:")
            for v in violations:
                print(f"   - {v}")
        else:
            print("✅ Validation passed")

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

