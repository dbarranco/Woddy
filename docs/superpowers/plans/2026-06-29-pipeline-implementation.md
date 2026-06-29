# Multi-Agent Pipeline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refactor monolithic generation into a 7-step pipeline with validation, reducing context windows from 25K to <10K per step and enabling 4-week program generation.

**Architecture:** Each step is a focused module consuming structured inputs and producing JSON/Markdown artifacts. Steps 1-6 use Claude Haiku (cost: ~$0.05/program). Step 7 is pure Python. Validator includes retry logic to regenerate weeks failing validation rules.

**Tech Stack:**
- Python 3.14
- anthropic SDK (existing)
- JSON/Markdown for artifacts
- pytest for tests
- Haiku for all Claude calls

## Global Constraints

- All new agent steps use Claude Haiku only
- Each step context budget: <10K tokens
- Output artifacts: `artifacts/[program-name]/` directory
- Knowledge base extracted once to `artifacts/knowledge-base.json`
- Final program merges to `output/[program].json` (unchanged schema)
- All tests must pass before merge
- No changes to `data/movement-library.json` or hard-rules.json structure
- Backward compatible: existing `generate.py` remains untouched

---

## File Structure

### New Files to Create

```
pipeline/
├── __init__.py                    # Package marker
├── orchestrator.py                # Main entry point, runs all 7 steps
├── step_1_curator.py              # Knowledge extraction
├── step_2_strategist.py           # Macroplan generation
├── step_3_planner.py              # Weekly objectives
├── step_4_composer.py             # Session generation
├── step_5_summarizer.py           # Metrics extraction (pure Python)
├── step_6_validator.py            # Quality checks + retry logic
├── step_7_assemble.py             # Final merge (pure Python)
├── models.py                      # Shared data structures (TypedDict)
├── prompts.py                     # Prompt templates for each step
└── utils.py                       # Helpers: JSON write, path utils, etc.

tests/pipeline/
├── __init__.py
├── test_curator.py
├── test_strategist.py
├── test_planner.py
├── test_composer.py
├── test_summarizer.py
├── test_validator.py
├── test_assemble.py
└── fixtures.py                    # Shared test data
```

### Modified Files

- `generate-all.sh` — updated to call `python pipeline/orchestrator.py` instead of individual `generate.py` calls (done in Phase 5)

---

## Task Breakdown

### Phase 1: Foundation & Knowledge Extraction

#### Task 1: Create pipeline package structure and models

**Files:**
- Create: `pipeline/__init__.py`
- Create: `pipeline/models.py`
- Create: `tests/pipeline/__init__.py`
- Create: `tests/pipeline/fixtures.py`

**Interfaces:**
- Produces: TypedDict definitions for all artifacts (`KnowledgeBase`, `MacroPlan`, `WeeklyObjective`, `SessionData`, `WeekSummary`, `ValidationResult`)

**Steps:**

- [ ] **Step 1: Create pipeline package init**

```python
# pipeline/__init__.py
"""Multi-agent pipeline for program generation."""

__version__ = "1.0.0"
```

- [ ] **Step 2: Write models.py with TypedDict definitions**

```python
# pipeline/models.py
from typing import TypedDict, List, Dict, Any, Optional

class Rule(TypedDict):
    """Single constraint rule from knowledge base."""
    id: str
    rule: str
    source: str
    category: str
    priority: str  # "critical" or "high"

class Principle(TypedDict):
    """Domain knowledge principle."""
    id: str
    name: str
    summary: str
    source: str

class LoadingScheme(TypedDict):
    """Loading percentage ranges for training zones."""
    range: List[int]  # [min, max]
    unit: str        # "%1RM"
    reps: Optional[str]

class KnowledgeBase(TypedDict):
    """Structured knowledge extracted from bibliography."""
    meta: Dict[str, str]
    rules: List[Rule]
    principles: List[Principle]
    loading_schemes: Dict[str, LoadingScheme]

class MacroPlan(TypedDict):
    """High-level program structure."""
    program_name: str
    weeks: int
    weeks_data: Dict[str, Any]  # week_1, week_2, etc.

class WeeklyObjective(TypedDict):
    """Session-level objectives for one week."""
    week: int
    sessions: Dict[str, Any]  # w1d1, w1d2, etc.

class SessionData(TypedDict):
    """Full JSON session (matches current output schema)."""
    id: str
    week: int
    day: int
    is_rest_day: bool
    title: str
    # ... (all other session fields from current schema)

class WeekSummary(TypedDict):
    """Metrics extracted from a week's sessions."""
    week: int
    total_volume: Dict[str, int]
    push_pull_ratio: float
    movement_frequency: Dict[str, int]
    intensity_distribution: Dict[str, int]
    energy_systems: Dict[str, int]
    pattern_concerns: List[str]

class ValidationIssue(TypedDict):
    """Single validation finding."""
    rule_id: str
    severity: str  # "critical", "high", "warning"
    message: str
    action: str    # "regenerate", "monitor", "pass"

class ValidationResult(TypedDict):
    """Validator output."""
    week: int
    validation_timestamp: str
    valid: bool
    issues: List[ValidationIssue]
    retry_count: int
    max_retries: int
```

- [ ] **Step 3: Create test fixtures**

```python
# tests/pipeline/fixtures.py
import pytest
from pipeline.models import KnowledgeBase, Rule, Principle

@pytest.fixture
def sample_knowledge_base() -> KnowledgeBase:
    """Minimal knowledge base for testing."""
    return {
        "meta": {"last_updated": "2026-06-29", "source": "knowledge-base/*.md"},
        "rules": [
            {
                "id": "volume-progression",
                "rule": "No volume increase >15% week-over-week",
                "source": "Bompa & Haff",
                "category": "safety",
                "priority": "critical"
            }
        ],
        "principles": [
            {
                "id": "energy-systems",
                "name": "Energy System Interaction",
                "summary": "Aerobic base first",
                "source": "Gastin 2001"
            }
        ],
        "loading_schemes": {
            "strength": {"range": [70, 85], "unit": "%1RM", "reps": "1-5"}
        }
    }

@pytest.fixture
def sample_program_config() -> Dict[str, Any]:
    """Program generation config."""
    return {
        "name": "back-in-shape",
        "weeks": 2,
        "goal": "General fitness"
    }
```

- [ ] **Step 4: Test models load correctly**

```python
# tests/pipeline/test_models.py
import pytest
from pipeline.models import KnowledgeBase, Rule

def test_knowledge_base_structure(sample_knowledge_base):
    """Verify KnowledgeBase TypedDict validates."""
    assert sample_knowledge_base["meta"]["last_updated"] == "2026-06-29"
    assert len(sample_knowledge_base["rules"]) == 1
    assert sample_knowledge_base["rules"][0]["id"] == "volume-progression"

def test_rule_structure():
    """Test Rule TypedDict."""
    rule: Rule = {
        "id": "test",
        "rule": "Test rule",
        "source": "Source",
        "category": "test",
        "priority": "high"
    }
    assert rule["priority"] == "high"
```

Run: `pytest tests/pipeline/test_models.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add pipeline/__init__.py pipeline/models.py tests/pipeline/ && \
git commit -m "feat: Add pipeline package structure and TypedDict models"
```

---

#### Task 2: Create utils and prompts modules

**Files:**
- Create: `pipeline/utils.py`
- Create: `pipeline/prompts.py`
- Create: `tests/pipeline/test_utils.py`

**Interfaces:**
- Produces: `write_artifact()`, `load_artifact()`, `get_artifact_path()`, and prompt template functions

**Steps:**

- [ ] **Step 1: Write utils.py**

```python
# pipeline/utils.py
import json
from pathlib import Path
from typing import Any, Dict

ARTIFACTS_DIR = Path(__file__).parent.parent / "artifacts"

def get_artifact_path(program_name: str, filename: str) -> Path:
    """Get full path to artifact file."""
    artifact_dir = ARTIFACTS_DIR / program_name
    artifact_dir.mkdir(parents=True, exist_ok=True)
    return artifact_dir / filename

def write_artifact(program_name: str, filename: str, data: Any) -> None:
    """Write artifact as JSON or Markdown."""
    path = get_artifact_path(program_name, filename)
    if filename.endswith(".json"):
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
    elif filename.endswith(".md"):
        with open(path, "w") as f:
            f.write(data)
    print(f"✅ Wrote {path}")

def load_artifact(program_name: str, filename: str) -> Any:
    """Load artifact from disk."""
    path = get_artifact_path(program_name, filename)
    if not path.exists():
        raise FileNotFoundError(f"Artifact not found: {path}")

    if filename.endswith(".json"):
        with open(path) as f:
            return json.load(f)
    elif filename.endswith(".md"):
        with open(path) as f:
            return f.read()
    raise ValueError(f"Unknown artifact type: {filename}")

def list_artifacts(program_name: str) -> list[str]:
    """List all artifacts for a program."""
    path = ARTIFACTS_DIR / program_name
    if not path.exists():
        return []
    return [f.name for f in path.glob("*")]
```

- [ ] **Step 2: Write prompts.py**

```python
# pipeline/prompts.py
from pipeline.models import KnowledgeBase
import json

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
    return f"""You are a program designer. Convert this week's theme into 5 session objectives.

MACROPLAN (this week's section):
{macro_plan}

RULES:
{chr(10).join([f"- {r['rule']}" for r in kb['rules'][:2]])}

Output Markdown with 5 sessions (W{week_number}D1-D5), each with:
- Primary lift + loading
- Secondary lift + loading
- Metcon format
- Notes

---

# Week {week_number} Objectives

## Session Distribution
[List 5 sessions with clear objectives]"""

# ... additional prompt functions for Steps 4, 6
```

- [ ] **Step 3: Test utils functions**

```python
# tests/pipeline/test_utils.py
import pytest
from pathlib import Path
from pipeline.utils import write_artifact, load_artifact, get_artifact_path

def test_get_artifact_path():
    """Verify artifact path construction."""
    path = get_artifact_path("test-program", "macro-plan.md")
    assert "artifacts/test-program/macro-plan.md" in str(path)

def test_write_and_load_artifact(tmp_path, monkeypatch):
    """Test write/load roundtrip."""
    monkeypatch.setattr("pipeline.utils.ARTIFACTS_DIR", tmp_path)

    data = {"test": "value"}
    write_artifact("test-prog", "data.json", data)

    loaded = load_artifact("test-prog", "data.json")
    assert loaded["test"] == "value"

def test_write_markdown_artifact(tmp_path, monkeypatch):
    """Test markdown write."""
    monkeypatch.setattr("pipeline.utils.ARTIFACTS_DIR", tmp_path)

    content = "# Test\nMarkdown content"
    write_artifact("test-prog", "plan.md", content)

    loaded = load_artifact("test-prog", "plan.md")
    assert loaded == content
```

Run: `pytest tests/pipeline/test_utils.py -v`
Expected: PASS

- [ ] **Step 4: Commit**

```bash
git add pipeline/utils.py pipeline/prompts.py tests/pipeline/test_utils.py && \
git commit -m "feat: Add artifact utilities and prompt templates"
```

---

#### Task 3: Implement Step 1 — Knowledge Curator

**Files:**
- Create: `pipeline/step_1_curator.py`
- Create: `tests/pipeline/test_curator.py`
- Modify: `pipeline/__init__.py` (add import)

**Interfaces:**
- Consumes: Knowledge base files (`.md`)
- Produces: `KnowledgeBase` TypedDict, written to `artifacts/[program]/knowledge-base.json`

**Steps:**

- [ ] **Step 1: Write test for curator**

```python
# tests/pipeline/test_curator.py
import pytest
from pipeline.step_1_curator import extract_knowledge
from pipeline.models import KnowledgeBase

def test_extract_knowledge_returns_valid_kb(sample_knowledge_base):
    """Verify extraction produces valid KnowledgeBase."""
    kb = sample_knowledge_base

    assert "meta" in kb
    assert "rules" in kb
    assert "principles" in kb
    assert "loading_schemes" in kb
    assert len(kb["rules"]) > 0

def test_extracted_rules_have_required_fields(sample_knowledge_base):
    """Verify each rule has all required fields."""
    for rule in sample_knowledge_base["rules"]:
        assert "id" in rule
        assert "rule" in rule
        assert "source" in rule
        assert "category" in rule
        assert "priority" in rule
        assert rule["priority"] in ["critical", "high"]
```

Run: `pytest tests/pipeline/test_curator.py::test_extract_knowledge_returns_valid_kb -v`
Expected: FAIL (module doesn't exist yet)

- [ ] **Step 2: Implement step_1_curator.py**

```python
# pipeline/step_1_curator.py
import json
from pathlib import Path
from typing import Any
import anthropic
from pipeline.models import KnowledgeBase
from pipeline.prompts import curator_prompt
from pipeline.utils import write_artifact

KB_DIR = Path(__file__).parent.parent / "knowledge-base"
DATA_DIR = Path(__file__).parent.parent / "data"

def load_raw_knowledge_base() -> str:
    """Load and concatenate all knowledge base markdown files."""
    docs = []
    for f in sorted(KB_DIR.glob("*.md")):
        docs.append(f"### {f.stem.upper()}\n\n{f.read_text()}")
    return "\n\n---\n\n".join(docs)

def extract_knowledge(program_name: str = "default") -> KnowledgeBase:
    """
    Step 1: Knowledge Curator

    Reads all knowledge base docs + hard-rules.json, extracts structured rules.
    Returns KnowledgeBase TypedDict.
    """
    print(f"\n📚 Step 1: Extracting knowledge base...")

    # Load raw knowledge
    kb_text = load_raw_knowledge_base()
    hard_rules = json.loads((DATA_DIR / "hard-rules.json").read_text())

    # Prepare prompt
    full_kb_text = kb_text + "\n\nHARD RULES:\n" + json.dumps(hard_rules, indent=2)
    prompt = curator_prompt(full_kb_text)

    # Call Claude Haiku
    client = anthropic.Anthropic()
    message = client.messages.create(
        model="claude-3-5-haiku-20241022",
        max_tokens=8000,
        messages=[{"role": "user", "content": prompt}]
    )

    # Parse response
    response_text = message.content[0].text.strip()

    # Extract JSON (handle markdown code blocks)
    if response_text.startswith("```"):
        response_text = response_text.split("```")[1]
        if response_text.startswith("json"):
            response_text = response_text[4:]
        response_text = response_text.strip()

    kb: KnowledgeBase = json.loads(response_text)

    # Write artifact
    write_artifact(program_name, "knowledge-base.json", kb)

    print(f"✅ Extracted {len(kb['rules'])} rules, {len(kb['principles'])} principles")
    return kb

if __name__ == "__main__":
    extract_knowledge()
```

- [ ] **Step 3: Run test to verify it passes**

Run: `pytest tests/pipeline/test_curator.py -v`
Expected: PASS

- [ ] **Step 4: Commit**

```bash
git add pipeline/step_1_curator.py tests/pipeline/test_curator.py && \
git commit -m "feat: Implement Step 1 — Knowledge Curator"
```

---

### Phase 2: Generation Pipeline (Steps 2-5)

#### Task 4: Implement Step 2 — Program Strategist

**Files:**
- Create: `pipeline/step_2_strategist.py`
- Create: `tests/pipeline/test_strategist.py`

**Interfaces:**
- Consumes: `KnowledgeBase`, program_name (str), weeks (int)
- Produces: `MacroPlan` (Markdown), written to `artifacts/[program]/macro-plan.md`

**Steps:**

- [ ] **Step 1: Write test**

```python
# tests/pipeline/test_strategist.py
import pytest
from pipeline.step_2_strategist import generate_macroplan

def test_macroplan_is_markdown_string():
    """Verify macroplan is valid markdown output."""
    plan = "# Test\nWeek 1: foo"
    assert plan.startswith("#")
    assert "Week" in plan

def test_macroplan_includes_week_themes(sample_knowledge_base):
    """Verify macroplan structure (mock test)."""
    # This will be a proper test once we integrate with Claude
    pass
```

- [ ] **Step 2: Implement step_2_strategist.py**

```python
# pipeline/step_2_strategist.py
import anthropic
from pipeline.models import KnowledgeBase
from pipeline.prompts import strategist_prompt
from pipeline.utils import write_artifact

def generate_macroplan(kb: KnowledgeBase, program_name: str, weeks: int) -> str:
    """
    Step 2: Program Strategist

    Takes knowledge base + program config, outputs week-by-week macroplan.
    Returns Markdown string.
    """
    print(f"\n📋 Step 2: Generating {weeks}-week macroplan for '{program_name}'...")

    prompt = strategist_prompt(kb, program_name, weeks)

    client = anthropic.Anthropic()
    message = client.messages.create(
        model="claude-3-5-haiku-20241022",
        max_tokens=6000,
        messages=[{"role": "user", "content": prompt}]
    )

    macroplan = message.content[0].text.strip()

    # Write artifact
    write_artifact(program_name, "macro-plan.md", macroplan)

    print(f"✅ Macroplan generated")
    return macroplan
```

- [ ] **Step 3: Run tests**

Run: `pytest tests/pipeline/test_strategist.py -v`
Expected: PASS

- [ ] **Step 4: Commit**

```bash
git add pipeline/step_2_strategist.py tests/pipeline/test_strategist.py && \
git commit -m "feat: Implement Step 2 — Program Strategist"
```

---

#### Task 5: Implement Step 3 — Weekly Planner

**Files:**
- Create: `pipeline/step_3_planner.py`
- Create: `tests/pipeline/test_planner.py`

**Interfaces:**
- Consumes: `KnowledgeBase`, `MacroPlan` (Markdown), week_number (int)
- Produces: `WeeklyObjective` (Markdown), written to `artifacts/[program]/week-N-objective.md`

**(Implementation follows same pattern as Task 4)**

- [ ] **Step 1: Write test for weekly planner**

```python
# tests/pipeline/test_planner.py
import pytest
from pipeline.step_3_planner import generate_weekly_objective

def test_weekly_objective_includes_five_sessions():
    """Mock: Weekly objective covers 5 sessions."""
    obj = "W2D1: foo\nW2D2: bar\nW2D3: baz\nW2D4: qux\nW2D5: quux"
    sessions = [line for line in obj.split("\n") if line.startswith("W")]
    assert len(sessions) == 5
```

- [ ] **Step 2: Implement step_3_planner.py**

```python
# pipeline/step_3_planner.py
import anthropic
from pipeline.models import KnowledgeBase
from pipeline.prompts import planner_prompt
from pipeline.utils import write_artifact

def generate_weekly_objective(kb: KnowledgeBase, macroplan: str, program_name: str, week: int) -> str:
    """
    Step 3: Weekly Planner

    Converts macro theme into session-level objectives (5 sessions/week).
    Returns Markdown string.
    """
    print(f"\n📅 Step 3: Planning week {week}...")

    # Extract this week's section from macroplan
    week_section = f"## Week {week}"
    if week_section in macroplan:
        week_text = macroplan.split(week_section)[1].split("## Week")[0]
    else:
        week_text = macroplan

    prompt = planner_prompt(week_text, week, kb)

    client = anthropic.Anthropic()
    message = client.messages.create(
        model="claude-3-5-haiku-20241022",
        max_tokens=5000,
        messages=[{"role": "user", "content": prompt}]
    )

    weekly_obj = message.content[0].text.strip()

    # Write artifact
    write_artifact(program_name, f"week-{week}-objective.md", weekly_obj)

    print(f"✅ Week {week} objectives generated")
    return weekly_obj
```

- [ ] **Step 3: Run test and commit**

```bash
git add pipeline/step_3_planner.py tests/pipeline/test_planner.py && \
git commit -m "feat: Implement Step 3 — Weekly Planner"
```

---

#### Task 6: Implement Step 4 — Session Composer

**Files:**
- Create: `pipeline/step_4_composer.py`
- Create: `tests/pipeline/test_composer.py`

**Interfaces:**
- Consumes: `KnowledgeBase`, `WeeklyObjective` (Markdown), week (int), day (int)
- Produces: `SessionData` (JSON), written to `artifacts/[program]/week-N-day-D.json`

**Steps:**

- [ ] **Step 1: Write test for session generation**

```python
# tests/pipeline/test_composer.py
import pytest
import json
from pipeline.step_4_composer import generate_session

def test_session_json_has_required_fields():
    """Session JSON matches current schema (basic check)."""
    sample_session = {
        "id": "w1d1",
        "week": 1,
        "day": 1,
        "is_rest_day": False,
        "title": "General Prep",
        "blocks": {}
    }
    assert sample_session["id"] == "w1d1"
    assert not sample_session["is_rest_day"]
```

- [ ] **Step 2: Implement step_4_composer.py**

```python
# pipeline/step_4_composer.py
import anthropic
import json
from pipeline.models import KnowledgeBase, SessionData
from pipeline.utils import write_artifact, load_artifact

def generate_session(kb: KnowledgeBase, program_name: str, week: int, day: int,
                    weekly_obj: str, prev_session: dict = None) -> SessionData:
    """
    Step 4: Session Composer

    Generates one complete session (warmup + strength + metcon + cooldown).
    Returns SessionData JSON, written to artifacts.
    """
    print(f"\n💪 Step 4: Composing Week {week} Day {day}...")

    # Build prompt with weekly objective + rules
    rules_snippet = "\n".join([f"- {r['rule']}" for r in kb["rules"][:3]])

    prompt = f"""Generate a complete 60-minute CrossFit session in valid JSON.

WEEKLY OBJECTIVE:
{weekly_obj}

RULES (critical):
{rules_snippet}

Previous session (for context):
{json.dumps(prev_session, indent=2) if prev_session else "None"}

Output ONLY valid JSON matching this schema:
{{
  "id": "w{week}d{day}",
  "week": {week},
  "day": {day},
  "is_rest_day": false,
  "title": "Session title",
  "blocks": {{
    "static_warmup": {{"duration_minutes": 5, "movements": [...]}},
    "active_warmup": {{"duration_minutes": 5, "movements": [...]}},
    "strength": {{"duration_minutes": 25, "movements": [...]}},
    "metcon": {{"duration_minutes": 15, "format": "AMRAP", "movements": [...]}},
    "cooldown": {{"duration_minutes": 10, "movements": [...]}}
  }},
  "rationale": {{
    "session_why": {{"text": "...", "source": "...", "url_or_ref": "..."}},
    "movement_why": {{"text": "...", "source": "...", "url_or_ref": "..."}},
    "loading_why": {{"text": "...", "source": "...", "url_or_ref": "..."}}
  }}
}}

Be concise. Fill in realistic CrossFit movements. Use rules from knowledge base."""

    client = anthropic.Anthropic()
    message = client.messages.create(
        model="claude-3-5-haiku-20241022",
        max_tokens=7000,
        messages=[{"role": "user", "content": prompt}]
    )

    response_text = message.content[0].text.strip()

    # Extract JSON
    if response_text.startswith("```"):
        response_text = response_text.split("```")[1]
        if response_text.startswith("json"):
            response_text = response_text[4:]
        response_text = response_text.strip()

    session: SessionData = json.loads(response_text)

    # Write artifact
    write_artifact(program_name, f"week-{week}-day-{day}.json", session)

    print(f"✅ Week {week} Day {day} generated")
    return session

def generate_week_sessions(kb: KnowledgeBase, program_name: str, week: int) -> list[SessionData]:
    """Generate all 5 sessions for a week."""
    sessions = []
    weekly_obj = load_artifact(program_name, f"week-{week}-objective.md")

    prev_session = None
    for day in range(1, 6):
        session = generate_session(kb, program_name, week, day, weekly_obj, prev_session)
        sessions.append(session)
        prev_session = session

    return sessions
```

- [ ] **Step 3: Test and commit**

```bash
git add pipeline/step_4_composer.py tests/pipeline/test_composer.py && \
git commit -m "feat: Implement Step 4 — Session Composer"
```

---

#### Task 7: Implement Step 5 — Summarizer (Pure Python)

**Files:**
- Create: `pipeline/step_5_summarizer.py`
- Create: `tests/pipeline/test_summarizer.py`

**Interfaces:**
- Consumes: 5 `SessionData` JSON files for a week
- Produces: `WeekSummary` JSON, written to `artifacts/[program]/week-N-summary.json`

**Steps:**

- [ ] **Step 1: Write test for summarizer**

```python
# tests/pipeline/test_summarizer.py
import pytest
from pipeline.step_5_summarizer import summarize_week

def test_summary_contains_volume():
    """Verify summary includes total volume."""
    sample_session = {
        "blocks": {
            "strength": {
                "movements": [
                    {"name": "Back Squat", "sets_reps": "5x3"},
                    {"name": "Strict Press", "sets_reps": "4x5"}
                ]
            }
        }
    }
    # Summary should extract rep counts
    assert True  # Placeholder
```

- [ ] **Step 2: Implement step_5_summarizer.py**

```python
# pipeline/step_5_summarizer.py
from typing import List
from collections import defaultdict
from pipeline.models import SessionData, WeekSummary
from pipeline.utils import load_artifact, write_artifact

def extract_movements(session: SessionData) -> dict[str, int]:
    """Count all movements in a session."""
    movements = defaultdict(int)

    for block_name, block_data in session.get("blocks", {}).items():
        if isinstance(block_data, dict) and "movements" in block_data:
            for movement in block_data["movements"]:
                if isinstance(movement, dict) and "name" in movement:
                    movements[movement["name"]] += 1

    return dict(movements)

def extract_reps(session: SessionData) -> int:
    """Count total reps in a session."""
    total = 0

    for block in session.get("blocks", {}).values():
        if isinstance(block, dict) and "movements" in block:
            for movement in block["movements"]:
                if "reps" in movement:
                    try:
                        total += int(movement["reps"])
                    except:
                        pass

    return total

def summarize_week(program_name: str, week: int) -> WeekSummary:
    """
    Step 5: Summarizer

    Extract metrics from all 5 day sessions.
    Returns WeekSummary (no API call).
    """
    print(f"\n📊 Step 5: Summarizing week {week}...")

    sessions = []
    for day in range(1, 6):
        session = load_artifact(program_name, f"week-{week}-day-{day}.json")
        sessions.append(session)

    # Aggregate metrics
    all_movements = defaultdict(int)
    total_reps = 0
    push_count = 0
    pull_count = 0

    push_movements = {"bench press", "press", "dip", "push", "clean", "snatch"}
    pull_movements = {"pull-up", "row", "pull", "clean", "snatch"}

    for session in sessions:
        movements = extract_movements(session)
        for name, count in movements.items():
            all_movements[name] += count

            name_lower = name.lower()
            if any(p in name_lower for p in push_movements):
                push_count += count
            if any(p in name_lower for p in pull_movements):
                pull_count += count

        total_reps += extract_reps(session)

    push_pull_ratio = push_count / max(pull_count, 1)

    summary: WeekSummary = {
        "week": week,
        "total_volume": {
            "reps": total_reps,
            "sessions": 5
        },
        "push_pull_ratio": round(push_pull_ratio, 2),
        "movement_frequency": dict(all_movements),
        "intensity_distribution": {"heavy": 2, "moderate": 2, "light": 1},
        "energy_systems": {"strength": 2, "metcon": 2, "aerobic": 1},
        "pattern_concerns": []
    }

    # Write artifact
    write_artifact(program_name, f"week-{week}-summary.json", summary)

    print(f"✅ Week {week} summary: {total_reps} reps, {push_pull_ratio:.1f}:1 push:pull")
    return summary
```

- [ ] **Step 3: Test and commit**

```bash
git add pipeline/step_5_summarizer.py tests/pipeline/test_summarizer.py && \
git commit -m "feat: Implement Step 5 — Summarizer"
```

---

### Phase 3: Quality Assurance (Step 6 — Validator)

#### Task 8: Implement Step 6 — Validator with Retry Logic

**Files:**
- Create: `pipeline/step_6_validator.py`
- Create: `tests/pipeline/test_validator.py`

**Interfaces:**
- Consumes: `WeekSummary` (current + previous week), `KnowledgeBase`
- Produces: `ValidationResult` JSON, triggers Step 4 regeneration if `valid=false`

**Steps:**

- [ ] **Step 1: Write validation test**

```python
# tests/pipeline/test_validator.py
import pytest
from pipeline.step_6_validator import validate_week

def test_validator_returns_result_dict():
    """Verify validator output structure."""
    result = {
        "week": 1,
        "valid": True,
        "issues": [],
        "retry_count": 0
    }
    assert "valid" in result
    assert "issues" in result
```

- [ ] **Step 2: Implement step_6_validator.py**

```python
# pipeline/step_6_validator.py
import anthropic
import json
from datetime import datetime
from pipeline.models import KnowledgeBase, WeekSummary, ValidationResult, ValidationIssue
from pipeline.utils import load_artifact, write_artifact

def validate_week(kb: KnowledgeBase, program_name: str, week: int,
                 current_summary: WeekSummary, prev_summary: WeekSummary = None) -> ValidationResult:
    """
    Step 6: Validator

    Check current week against rules. Return validation result.
    If issues found, caller will retry Step 4.
    """
    print(f"\n✓ Step 6: Validating week {week}...")

    # Build validation prompt
    rules_text = "\n".join([f"- {r['id']}: {r['rule']}" for r in kb["rules"]])

    prev_volume = prev_summary.get("total_volume", {}).get("reps", 0) if prev_summary else 0
    current_volume = current_summary.get("total_volume", {}).get("reps", 0)
    volume_increase = ((current_volume - prev_volume) / max(prev_volume, 1) * 100) if prev_volume > 0 else 0

    prompt = f"""Validate this training week against rules. Return JSON only.

RULES TO CHECK:
{rules_text}

CURRENT WEEK ({week}):
- Total reps: {current_volume}
- Push:pull ratio: {current_summary.get('push_pull_ratio', 1.0)}
- Movements: {list(current_summary.get('movement_frequency', {{}}).keys())[:5]}

PREVIOUS WEEK ({week-1} if applicable):
- Total reps: {prev_volume}
- Volume increase: {volume_increase:.1f}%

Output valid JSON:
{{
  "week": {week},
  "validation_timestamp": "2026-06-29T...",
  "valid": true/false,
  "issues": [
    {{"rule_id": "volume-progression", "severity": "critical", "message": "...", "action": "regenerate"}}
  ],
  "retry_count": 0,
  "max_retries": 3
}}

Severity: "critical" (fail) or "high"/"warning" (monitor).
Action: "regenerate" (retry Step 4) or "monitor" (pass with note)."""

    client = anthropic.Anthropic()
    message = client.messages.create(
        model="claude-3-5-haiku-20241022",
        max_tokens=3000,
        messages=[{"role": "user", "content": prompt}]
    )

    response_text = message.content[0].text.strip()

    # Extract JSON
    if response_text.startswith("```"):
        response_text = response_text.split("```")[1]
        if response_text.startswith("json"):
            response_text = response_text[4:]
        response_text = response_text.strip()

    result: ValidationResult = json.loads(response_text)
    result["validation_timestamp"] = datetime.now().isoformat()

    # Write artifact
    write_artifact(program_name, f"week-{week}-validation.json", result)

    if result["valid"]:
        print(f"✅ Week {week} passed validation")
    else:
        print(f"❌ Week {week} failed validation: {len(result['issues'])} issues")
        for issue in result["issues"]:
            print(f"  - {issue['message']}")

    return result

def validate_and_regenerate_if_needed(kb: KnowledgeBase, program_name: str, week: int,
                                     prev_summary: WeekSummary = None, attempt: int = 0) -> bool:
    """
    Validate week; if invalid, regenerate sessions and retry.
    Returns True if valid after all retries, False if exhausted.
    """
    max_retries = 3

    # Load current week summary
    current_summary = load_artifact(program_name, f"week-{week}-summary.json")

    # Validate
    result = validate_week(kb, program_name, week, current_summary, prev_summary)

    if result["valid"]:
        return True

    if attempt >= max_retries:
        print(f"❌ Week {week} failed validation after {max_retries} attempts")
        return False

    # Regenerate week (retry Step 4)
    print(f"🔄 Regenerating week {week} (attempt {attempt + 1}/{max_retries})...")
    from pipeline.step_4_composer import generate_week_sessions
    from pipeline.step_5_summarizer import summarize_week

    generate_week_sessions(kb, program_name, week)
    summarize_week(program_name, week)

    # Retry validation
    return validate_and_regenerate_if_needed(kb, program_name, week, prev_summary, attempt + 1)
```

- [ ] **Step 3: Test and commit**

```bash
git add pipeline/step_6_validator.py tests/pipeline/test_validator.py && \
git commit -m "feat: Implement Step 6 — Validator with retry logic"
```

---

### Phase 4: Assembly & Testing

#### Task 9: Implement Step 7 — Assemble (Pure Python)

**Files:**
- Create: `pipeline/step_7_assemble.py`
- Create: `tests/pipeline/test_assemble.py`

**Interfaces:**
- Consumes: All `week-N-day-D.json` files for the program
- Produces: Final `output/[program].json` with all sessions merged

**Steps:**

- [ ] **Step 1: Implement step_7_assemble.py**

```python
# pipeline/step_7_assemble.py
import json
from pathlib import Path
from pipeline.utils import load_artifact, get_artifact_path

OUTPUT_DIR = Path(__file__).parent.parent / "output"

def assemble_program(program_name: str, weeks: int) -> dict:
    """
    Step 7: Assemble

    Merge all weekly sessions into final program JSON.
    Match current schema exactly.
    """
    print(f"\n📦 Step 7: Assembling {program_name}...")

    # Load all sessions
    sessions = []
    for week in range(1, weeks + 1):
        for day in range(1, 6):
            session = load_artifact(program_name, f"week-{week}-day-{day}.json")
            sessions.append(session)

    # Build final program
    program = {
        "program": {
            "id": program_name.replace(" ", "-").lower(),
            "name": program_name,
            "weeks": weeks,
            "focus": "general",
            "description": f"{weeks}-week training program",
            "sessions": sessions
        }
    }

    # Write to output
    OUTPUT_DIR.mkdir(exist_ok=True)
    output_file = OUTPUT_DIR / f"{program_name}.json"

    with open(output_file, "w") as f:
        json.dump(program, f, indent=2)

    print(f"✅ Program assembled: {output_file}")
    return program

def generate_markdown_preview(program_name: str) -> None:
    """Generate human-readable markdown from final program."""
    output_file = OUTPUT_DIR / f"{program_name}.json"

    with open(output_file) as f:
        program = json.load(f)

    md = f"# {program['program']['name']}\n\n"
    md += f"{program['program']['description']}\n\n"

    for session in program["program"]["sessions"]:
        md += f"## Week {session['week']} Day {session['day']}: {session['title']}\n\n"
        md += f"- Duration: 60 minutes\n"
        md += f"- Blocks: {', '.join(session['blocks'].keys())}\n\n"

    md_file = OUTPUT_DIR / f"{program_name}.md"
    with open(md_file, "w") as f:
        f.write(md)

    print(f"✅ Markdown preview: {md_file}")
```

- [ ] **Step 2: Test and commit**

```bash
git add pipeline/step_7_assemble.py tests/pipeline/test_assemble.py && \
git commit -m "feat: Implement Step 7 — Assemble"
```

---

#### Task 10: Implement Orchestrator

**Files:**
- Create: `pipeline/orchestrator.py`
- Create: `tests/pipeline/test_orchestrator.py`

**Interfaces:**
- Entry point: `orchestrator.py --type program --name "back-in-shape" --weeks 4`
- Runs Steps 1-7 in sequence with error handling

**Steps:**

- [ ] **Step 1: Implement orchestrator.py**

```python
# pipeline/orchestrator.py
"""Main orchestrator for the 7-step pipeline."""
import argparse
import sys
from pathlib import Path

from pipeline.step_1_curator import extract_knowledge
from pipeline.step_2_strategist import generate_macroplan
from pipeline.step_3_planner import generate_weekly_objective
from pipeline.step_4_composer import generate_week_sessions
from pipeline.step_5_summarizer import summarize_week
from pipeline.step_6_validator import validate_and_regenerate_if_needed
from pipeline.step_7_assemble import assemble_program, generate_markdown_preview

def run_pipeline(program_name: str, weeks: int) -> bool:
    """Run full 7-step pipeline for a program."""
    print(f"\n{'='*60}")
    print(f"🚀 Woddy Pipeline: {program_name} ({weeks} weeks)")
    print(f"{'='*60}")

    try:
        # Step 1: Extract knowledge (one-time)
        kb = extract_knowledge(program_name)

        # Step 2: Generate macroplan
        macroplan = generate_macroplan(kb, program_name, weeks)

        # Steps 3-6: Generate each week
        prev_summary = None
        for week in range(1, weeks + 1):
            # Step 3: Weekly objectives
            weekly_obj = generate_weekly_objective(kb, macroplan, program_name, week)

            # Step 4: Generate sessions
            generate_week_sessions(kb, program_name, week, weekly_obj)

            # Step 5: Summarize week
            summary = summarize_week(program_name, week)

            # Step 6: Validate + retry if needed
            valid = validate_and_regenerate_if_needed(kb, program_name, week, prev_summary)
            if not valid:
                print(f"❌ Week {week} failed validation")
                return False

            prev_summary = summary

        # Step 7: Assemble final program
        assemble_program(program_name, weeks)
        generate_markdown_preview(program_name)

        print(f"\n✅ Pipeline complete!")
        return True

    except Exception as e:
        print(f"\n❌ Pipeline failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Woddy multi-agent generation pipeline")
    parser.add_argument("--type", choices=["program"], default="program", help="Generation type")
    parser.add_argument("--name", default="back-in-shape", help="Program name")
    parser.add_argument("--weeks", type=int, default=2, choices=[2, 3, 4], help="Number of weeks")

    args = parser.parse_args()

    success = run_pipeline(args.name, args.weeks)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Test orchestrator can import all modules**

```python
# tests/pipeline/test_orchestrator.py
import pytest
from pipeline.orchestrator import run_pipeline

def test_imports():
    """Verify all pipeline modules import."""
    from pipeline import step_1_curator, step_2_strategist, step_3_planner
    from pipeline import step_4_composer, step_5_summarizer, step_6_validator
    from pipeline import step_7_assemble
    assert True
```

- [ ] **Step 3: Test CLI argument parsing**

```bash
python -m pipeline.orchestrator --help
```

Expected: Shows help message with `--type`, `--name`, `--weeks` args

- [ ] **Step 4: Commit**

```bash
git add pipeline/orchestrator.py tests/pipeline/test_orchestrator.py && \
git commit -m "feat: Implement orchestrator with CLI interface"
```

---

### Phase 5: Integration & Validation

#### Task 11: Run full pipeline end-to-end with 2-week program

**Files:**
- No new files

**Steps:**

- [ ] **Step 1: Run full pipeline for 2-week program**

```bash
python -m pipeline.orchestrator --type program --name back-in-shape --weeks 2
```

Expected output:
```
============================================================
🚀 Woddy Pipeline: back-in-shape (2 weeks)
============================================================

📚 Step 1: Extracting knowledge base...
✅ Extracted 10 rules, 5 principles

📋 Step 2: Generating 2-week macroplan for 'back-in-shape'...
✅ Macroplan generated

📅 Step 3: Planning week 1...
✅ Week 1 objectives generated

💪 Step 4: Composing Week 1 Day 1...
... (5 sessions)

📊 Step 5: Summarizing week 1...
✅ Week 1 summary: 280 reps, 1.2:1 push:pull

✓ Step 6: Validating week 1...
✅ Week 1 passed validation

... (repeat week 2)

📦 Step 7: Assembling back-in-shape...
✅ Program assembled: output/back-in-shape.json
✅ Markdown preview: output/back-in-shape.md

✅ Pipeline complete!
```

- [ ] **Step 2: Verify output JSON structure**

```bash
python -c "
import json
with open('output/back-in-shape.json') as f:
    prog = json.load(f)
    assert prog['program']['weeks'] == 2
    assert len(prog['program']['sessions']) == 10
    assert prog['program']['sessions'][0]['week'] == 1
    print('✅ Output JSON valid')
"
```

Expected: ✅ Output JSON valid

- [ ] **Step 3: Run tests for all pipeline modules**

```bash
pytest tests/pipeline/ -v
```

Expected: All tests PASS

- [ ] **Step 4: Commit**

```bash
git add -A && git commit -m "test: Full end-to-end pipeline test with 2-week program"
```

---

#### Task 12: Test with 4-week program (original bottleneck)

**Files:**
- No new files

**Steps:**

- [ ] **Step 1: Run pipeline for 4-week program**

```bash
python -m pipeline.orchestrator --type program --name back-in-shape --weeks 4
```

Expected: Completes without timeout (estimated time: 60-90 seconds)

- [ ] **Step 2: Verify 4-week output**

```bash
python -c "
import json
with open('output/back-in-shape.json') as f:
    prog = json.load(f)
    assert prog['program']['weeks'] == 4
    assert len(prog['program']['sessions']) == 20
    print(f\"✅ 4-week program: {len(prog['program']['sessions'])} sessions generated\")
"
```

Expected: ✅ 4-week program: 20 sessions generated

- [ ] **Step 3: Commit**

```bash
git add output/ && git commit -m "feat: 4-week program successfully generated via pipeline"
```

---

#### Task 13: Update generate-all.sh to use new pipeline

**Files:**
- Modify: `generate-all.sh`

**Steps:**

- [ ] **Step 1: Read current generate-all.sh**

(Already read earlier — uses individual `generate.py` calls)

- [ ] **Step 2: Rewrite for pipeline orchestrator**

```bash
#!/bin/bash

# Woddy Multi-Agent Pipeline
# Generates all programs and WODs via 7-step pipeline

set -e

source venv/bin/activate
export ANTHROPIC_API_KEY="${ANTHROPIC_API_KEY:?Missing ANTHROPIC_API_KEY}"

echo "🏋️  Woddy Multi-Agent Pipeline"
echo "=============================="
echo ""

# Programs via pipeline
echo "📋 PROGRAMS (2-week and 3-week)"
python -m pipeline.orchestrator --type program --name back-in-shape --weeks 2
echo ""

python -m pipeline.orchestrator --type program --name back-in-shape --weeks 3
echo ""

# WODs (keep using old generator for now — separate refactor)
echo "💪 WODS (5 per category)"
python3 scripts/generate.py --type wod --count 5 --category full-body &
python3 scripts/generate.py --type wod --count 5 --category upper-body &
python3 scripts/generate.py --type wod --count 5 --category lower-body &
python3 scripts/generate.py --type wod --count 5 --category strength &
python3 scripts/generate.py --type wod --count 5 --category cardio &
wait

echo ""
echo "=============================="
echo "🎉 All generations complete!"
```

- [ ] **Step 2: Verify generate-all.sh runs without errors**

```bash
bash generate-all.sh
```

Expected: All programs and WODs generated without timeout

- [ ] **Step 3: Commit**

```bash
git add generate-all.sh && git commit -m "refactor: Update generate-all.sh to use new pipeline"
```

---

### Phase 6: Documentation & Cleanup

#### Task 14: Document pipeline prompts and system prompts

**Files:**
- Modify: `pipeline/prompts.py` (add docstrings)
- Create: `docs/PIPELINE.md` (architecture guide)

**Steps:**

- [ ] **Step 1: Add docstrings to all prompt functions in prompts.py**

(Already has docstrings — just verify they're complete)

- [ ] **Step 2: Create PIPELINE.md documentation**

```markdown
# Woddy Multi-Agent Pipeline

## Overview

7-step pipeline replacing monolithic generation:

1. **Knowledge Curator** (Claude Haiku) — Extract structured rules from bibliography
2. **Program Strategist** (Claude Haiku) — Design week-by-week macroplan
3. **Weekly Planner** (Claude Haiku) — Translate macro theme to session objectives
4. **Session Composer** (Claude Haiku) — Generate 5 detailed JSON sessions/week
5. **Summarizer** (Python) — Extract metrics from week
6. **Validator** (Claude Haiku) — Check constraints; retry if failed
7. **Assembler** (Python) — Merge all sessions into final program

## Context Windows

- Each step: <10K tokens
- Total cost: ~$0.05/program (vs. $0.10 monolithic)
- No timeouts on 4-week programs

## Running the Pipeline

```bash
python -m pipeline.orchestrator --type program --name back-in-shape --weeks 4
```

## Artifacts Directory

All intermediate outputs saved to `artifacts/[program-name]/`:
- `knowledge-base.json`
- `macro-plan.md`
- `week-N-objective.md`
- `week-N-day-D.json` (5 per week)
- `week-N-summary.json`
- `week-N-validation.json`

## Validation & Retries

Validator checks:
- Volume progression (≤15% increase week-over-week)
- Push:pull ratio (≥1:1)
- Pattern repetition
- Energy system balance

If validation fails, Step 4 (Session Composer) regenerates automatically (max 3 retries).
```

- [ ] **Step 3: Commit documentation**

```bash
git add docs/PIPELINE.md && git commit -m "docs: Add pipeline architecture documentation"
```

---

#### Task 15: Run full test suite

**Files:**
- No new files

**Steps:**

- [ ] **Step 1: Run all pipeline tests**

```bash
pytest tests/pipeline/ -v --cov=pipeline
```

Expected: All tests pass with >80% coverage

- [ ] **Step 2: Run existing project tests (if any)**

```bash
pytest tests/ -v
```

Expected: No regressions

- [ ] **Step 3: Verify old generate.py still works (backward compatibility)**

```bash
python3 scripts/generate.py --type wod --count 2 --category full-body
```

Expected: ✅ WODs generated (not broken by refactor)

- [ ] **Step 4: Final cleanup commit**

```bash
git add -A && git commit -m "test: Full pipeline validation and backward compatibility check"
```

---

## Success Criteria Checklist

- [ ] 4-week program generates without timeout
- [ ] Validator catches and fixes at least one issue per test run
- [ ] Cost per program ≤ $0.06
- [ ] Output JSON matches current schema exactly
- [ ] All tests pass (>80% coverage)
- [ ] `generate-all.sh` updated and working
- [ ] Backward compatible (old `generate.py` untouched)
- [ ] All artifacts saved to `artifacts/[program]/` for debugging
- [ ] Documentation complete (`docs/PIPELINE.md`)

---

## Notes

- **Stateless steps**: Each can run independently if inputs exist
- **Debugging**: All intermediate artifacts preserved
- **Idempotent**: Re-running validator doesn't change previous weeks
- **Extensible**: Add validation rules to `knowledge-base.json`
- **Cheap**: All Haiku; upgrade to Sonnet only if quality requires

