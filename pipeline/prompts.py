"""Prompt templates for pipeline steps."""

import json
from pipeline.models import KnowledgeBase


def curator_prompt(kb_text: str) -> str:
    """Prompt for Knowledge Curator (Step 1)."""
    return f"""You are a sports science knowledge curator. Extract rules, principles, and loading schemes from the knowledge base below.

KNOWLEDGE BASE:
{kb_text}

Output valid JSON with this exact structure:
{{
  "meta": {{"last_updated": "2026-06-29", "source": "knowledge-base"}},
  "rules": [
    {{"id": "string", "rule": "string", "source": "string", "category": "string", "priority": "critical|high"}}
  ],
  "principles": [
    {{"id": "string", "name": "string", "summary": "string", "source": "string"}}
  ],
  "loading_schemes": {{
    "strength": {{"range": [70, 85], "unit": "%1RM", "reps": "1-5"}}
  }}
}}

Be concise. Extract only rules that are clearly stated in the knowledge base."""


def strategist_prompt(kb: KnowledgeBase, program_name: str, weeks: int) -> str:
    """Prompt for Program Strategist (Step 2)."""
    rules_text = "\n".join([f"- {r['rule']} ({r['source']})" for r in kb["rules"][:3]])

    return f"""You are a periodization expert. Design a {weeks}-week macroplan for "{program_name}".

RULES (do not violate):
{rules_text}

PRINCIPLES:
- Week 1: General prep (movement baseline, mobility focus)
- Week 2-3: Strength/hypertrophy build (heavier loads, compound focus)
- Week 4: Deload (light intensity, recovery focus) [only if weeks==4]

Output Markdown with clear week-by-week themes, loading progression, and focus areas.

---

# {program_name.title()} {weeks}-Week Macroplan

[Write week-by-week breakdown here]"""


def planner_prompt(macro_plan: str, week_number: int, kb: KnowledgeBase) -> str:
    """Prompt for Weekly Planner (Step 3)."""
    rules_preview = "\n".join([f"- {r['rule']}" for r in kb["rules"][:2]])

    return f"""You are a program designer. Convert this week's theme into 5 session objectives.

MACROPLAN (this week's section):
{macro_plan}

RULES:
{rules_preview}

Output Markdown with 5 sessions (W{week_number}D1-D5), each with:
- Primary lift + loading
- Secondary lift + loading
- Metcon format
- Notes

---

# Week {week_number} Objectives

## Session Distribution
[List 5 sessions with clear objectives]"""


def composer_prompt(
    week_objective: str,
    week_num: int,
    day_num: int,
    kb: KnowledgeBase,
    movement_library: dict,
    prev_session: dict = None
) -> str:
    """Prompt for Session Composer (Step 4)."""
    rules_preview = json.dumps(kb["rules"][:2], indent=2)
    movements_preview = json.dumps(movement_library.get("categories", {}).get("compounds", [])[:3], indent=2)

    prev_context = ""
    if prev_session:
        prev_context = f"\nPREVIOUS SESSION (for progression context):\n{json.dumps(prev_session, indent=2)[:500]}"

    return f"""You are a CrossFit programming expert. Generate a complete 60-minute session as valid JSON.

WEEK OBJECTIVE:
{week_objective[:500]}

RULES (MUST OBEY):
{rules_preview}

MOVEMENT LIBRARY (use only these names):
{movements_preview}

SESSION SCHEMA:
{{
  "id": "w{week_num}d{day_num}",
  "week": {week_num},
  "day": {day_num},
  "is_rest_day": false,
  "title": "Session Title",
  "focus": "Focus area",
  "blocks": [
    {{"type": "warmup_static", "duration_seconds": 300, "content": [...]}},
    {{"type": "warmup_active", "duration_seconds": 300, "content": [...]}},
    {{"type": "strength", "duration_seconds": 1200, "content": [...]}},
    {{"type": "metcon", "timer_config": {{"type": "amrap", "duration_seconds": 600}}, "content": [...]}},
    {{"type": "cooldown", "duration_seconds": 300, "content": [...]}}
  ],
  "rationale": {{
    "session_why": {{"text": "...", "source": "...", "url_or_ref": "..."}},
    "movement_why": {{"text": "...", "source": "...", "url_or_ref": "..."}},
    "loading_why": {{"text": "...", "source": "...", "url_or_ref": "..."}}
  }},
  "equipment": ["barbell", "dumbbell", "kettlebell"]
}}

TOTAL SESSION TIME: 60 minutes max. Be specific with weights, reps, and timing.{prev_context}

Output only valid JSON."""


def validator_prompt(
    week_summary: dict,
    prev_week_summary: dict = None,
    kb: KnowledgeBase = None
) -> str:
    """Prompt for Validator (Step 6)."""
    rules_to_check = json.dumps(kb["rules"] if kb else [], indent=2)
    prev_data = f"\nPREVIOUS WEEK SUMMARY:\n{json.dumps(prev_week_summary, indent=2)[:300]}" if prev_week_summary else ""

    return f"""You are a training program validator. Check this week's metrics against all rules.

CURRENT WEEK SUMMARY:
{json.dumps(week_summary, indent=2)}

RULES TO CHECK:
{rules_to_check}{prev_data}

VALIDATION SCHEMA:
{{
  "week": {week_summary.get('week', 1)},
  "validation_timestamp": "ISO8601",
  "valid": true/false,
  "issues": [
    {{
      "rule_id": "rule-id",
      "severity": "critical|high|warning",
      "message": "Detailed finding",
      "action": "regenerate|monitor|pass"
    }}
  ],
  "retry_count": 0,
  "max_retries": 3
}}

Check:
1. Volume progression (no >15% week-over-week increase)
2. Push:pull ratio (≥1:1)
3. Pattern repetition (no excessive repeats)
4. Recovery spacing (heavy sessions not back-to-back)
5. Energy system balance
6. Weekly theme alignment

Output only valid JSON."""


def summarizer_instructions() -> str:
    """Instructions for Summarizer (Step 5 - pure Python, not a prompt)."""
    return """
    SUMMARIZER RESPONSIBILITIES (Pure Python - no API call):

    1. Load all 5 daily session JSONs for the week
    2. Extract metrics:
       - Total reps per movement
       - Total tonnage (weight × reps)
       - Push vs pull movement count
       - Frequency of each movement
       - Intensity distribution (%1RM ranges used)
       - Energy system distribution
    3. Identify patterns:
       - Repeated movements (flagged if >2x)
       - Recovery days
       - Peak intensity days
    4. Generate WeekSummary JSON with all metrics
    5. Write to artifacts/[program]/week-N-summary.json
    """
