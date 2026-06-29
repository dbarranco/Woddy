# Multi-Agent Pipeline Architecture Redesign

**Date:** 2026-06-29
**Status:** Approved (awaiting implementation)
**Goal:** Replace monolithic single-prompt generation with a modular 7-step pipeline to reduce context windows, improve quality via validation, and lower costs.

---

## Problem Statement

Current architecture generates entire programs in a single API call, requiring ~25K tokens of context. This causes:
- Timeouts on 4-week programs (exceeded 10-minute non-streaming limit)
- High cost per generation (~$0.10 per program)
- No intermediate quality checks or validation
- Difficult to debug issues (can't isolate which week failed)
- Coupling of distinct concerns (knowledge, strategy, execution)

---

## Solution: Pipeline with Validation Loop

Replace single monolithic prompt with a **7-step pipeline** where:
1. Each step has a single, clear responsibility
2. Each step operates on <10K tokens (fits Haiku)
3. Artifacts are structured data (JSON/Markdown), not prose
4. A **validator** with retry logic ensures quality
5. One-time knowledge extraction amortizes costs

---

## Architecture Overview

### Step 1: Knowledge Extractor (One-time, triggers on bibliography change)

**Responsibility**: Convert prose knowledge base into structured rules.

**Input**:
- `knowledge-base/*.md` (all 5 documents)
- `data/hard-rules.json`

**Process**:
- Extract CrossFit methodology principles
- Extract energy system definitions
- Extract periodization rules
- Convert to JSON rule format (ID, rule text, source, priority)

**Output**: `artifacts/knowledge-base.json`

```json
{
  "meta": {
    "last_updated": "2026-06-29",
    "source": "knowledge-base/*.md + data/hard-rules.json"
  },
  "rules": [
    {
      "id": "volume-progression",
      "rule": "No volume increase >15% week-over-week",
      "source": "Bompa & Haff - Periodization 5th ed",
      "category": "safety",
      "priority": "critical"
    },
    {
      "id": "consecutive-oly",
      "rule": "No Olympic lifts on consecutive days",
      "source": "CrossFit Level 2 Training Guide",
      "category": "cns-fatigue",
      "priority": "critical"
    },
    {
      "id": "push-pull-ratio",
      "rule": "Push:pull ratio ≥ 1:1 per week",
      "source": "NSCA Essentials 4th ed",
      "category": "movement-balance",
      "priority": "high"
    },
    {
      "id": "no-consecutive-metcons",
      "rule": "No high-intensity metcons on consecutive days",
      "source": "CrossFit Methodology",
      "category": "recovery",
      "priority": "high"
    }
  ],
  "principles": [
    {
      "id": "energy-systems",
      "name": "Energy System Interaction",
      "summary": "Aerobic base first, then power/strength, then glycolytic work. Interference minimization: separate modalities by 6+ hours or days.",
      "source": "Gastin 2001"
    },
    {
      "id": "periodization",
      "name": "Linear Periodization (4-week macro)",
      "summary": "Week 1: General prep. Week 2-3: Strength/hypertrophy build. Week 4: Deload.",
      "source": "Bompa & Haff"
    }
  ],
  "loading_schemes": {
    "strength": { "range": [70, 85], "unit": "%1RM", "reps": "1-5" },
    "hypertrophy": { "range": [65, 75], "unit": "%1RM", "reps": "6-12" },
    "power": { "range": [75, 90], "unit": "%1RM", "reps": "1-5" },
    "endurance": { "range": [40, 60], "unit": "%1RM", "reps": "15+" }
  }
}
```

**Model**: Haiku
**Cost**: ~$0.01 (one-time, amortized)

---

### Step 2: Macroplan Generator

**Responsibility**: Design the overall training arc (week-by-week themes, loading progression).

**Input**:
- `artifacts/knowledge-base.json` (3K)
- Program name, duration (e.g., "back-in-shape", 4 weeks)
- `data/hard-rules.json` (constraints)

**Process**:
- Assign week themes based on periodization principle
- Plan loading progression (ramp → peak → deload)
- Identify weekly focus areas (movement emphasis, energy systems)

**Output**: `artifacts/[program-name]/macro-plan.md`

```markdown
# Back-in-Shape 4-Week Macroplan

## Week 1: General Preparation
- **Theme**: Movement baseline, work capacity foundation
- **Focus**: Full-body patterns, metabolic conditioning
- **Loading**: 60-65% 1RM
- **Energy Systems**: Aerobic + glycolytic mix
- **Notes**: Establish movement quality before intensity

## Week 2: Strength Building
- **Theme**: Maximum strength & power development
- **Focus**: Heavy compound lifts (squat, deadlift, press)
- **Loading**: 75-85% 1RM
- **Energy Systems**: CNS-intensive, lower metcon volume
- **Notes**: Limit Olympic lifts to Mon/Wed/Fri (no consecutive days)

## Week 3: Work Capacity
- **Theme**: Sustained effort under load
- **Focus**: Moderate loading with volume
- **Loading**: 70-75% 1RM
- **Energy Systems**: Balanced (aerobic + glycolytic)
- **Notes**: Increase metcon duration/volume

## Week 4: Deload
- **Theme**: Recovery & adaptation
- **Focus**: Light movement, skill work, mobility
- **Loading**: 50-60% 1RM (reduced volume)
- **Energy Systems**: Low-intensity steady state
- **Notes**: Prepare nervous system for next cycle
```

**Model**: Haiku
**Context**: ~3K
**Cost**: ~$0.0008

---

### Step 3: Weekly Objective Generator

**Responsibility**: Translate week theme into session-level objectives.

**Input**:
- `artifacts/[program]/macro-plan.md` (2K, this week's section)
- `artifacts/knowledge-base.json` (3K)
- Previous week's summary (if week > 1)

**Process**:
- Define 5 session types for the week
- Assign movement categories (compound vs accessory, push vs pull)
- Set intensity targets and energy system focus per session

**Output**: `artifacts/[program]/week-N-objective.md`

```markdown
# Week 2 Objectives: Strength Building

## Session Distribution
- **Mon (W2D1)**: Squat focus, max-strength CNS work
- **Tue (W2D2)**: Pressing focus, horizontal movement balance
- **Wed (W2D3)**: Deadlift focus, posterior chain emphasis
- **Thu (W2D4)**: Upper body pull, accessory volume
- **Fri (W2D5)**: Mixed modality, moderate intensity

## Movement Categories per Session

### W2D1: Squat Focus
- Primary: Back Squat (5×3 @ 75% 1RM)
- Secondary: Strict Press (4×5 @ 70% 1RM)
- Metcon: 12-min AMRAP, moderate intensity
- Notes: Heavy CNS work early; do not pair with Olympic lift

### W2D2: Pressing Focus
- Primary: Bench Press (5×5 @ 72% 1RM)
- Secondary: Pull-ups (3×8 bodyweight)
- Metcon: 15-min EMOM, moderate pace
- Notes: Maintain 1:1 push-pull ratio across week

### W2D3: Deadlift Focus
- Primary: Conventional Deadlift (3×2 @ 80% 1RM)
- Secondary: Rows (4×6 @ 70% 1RM)
- Metcon: 10-min For Time, high intensity
- Notes: Last heavy CNS session of week; ample recovery after

### W2D4: Upper Body Pull
- Primary: Gymnastics skill (muscle-ups, handstand)
- Secondary: Accessory (face pulls, band work)
- Metcon: 20-min AMRAP, aerobic focus
- Notes: Lighter CNS load; allows higher metcon volume

### W2D5: Mixed Modality
- Primary: Complex movement (thruster or clean)
- Secondary: Dumbbell work (hypertrophy)
- Metcon: 12-min AMRAP, mixed modal
- Notes: End-of-week fatigue; moderate intensity
```

**Model**: Haiku
**Context**: ~6K
**Cost**: ~$0.0008

---

### Step 4: Session Generator (Runs 5× per week)

**Responsibility**: Generate full detailed JSON for one session.

**Input**:
- `artifacts/[program]/week-N-objective.md` (this session's spec)
- `artifacts/knowledge-base.json` (3K)
- `data/movement-library.json` (movement names, categories)
- Previous session's JSON (for context/progression)

**Process**:
- Build warmup (5 min static + 5 min active)
- Assemble strength block (20-25 min)
- Design metcon (10-20 min)
- Add cooldown (5-10 min)
- Generate rationales from knowledge base
- Output valid JSON

**Output**: `artifacts/[program]/week-N-day-D.json` (current schema)

**Model**: Haiku
**Context**: ~7K
**Cost**: ~$0.002/session × 5 = $0.01/week

---

### Step 5: Summarizer (Python code, no API call)

**Responsibility**: Extract metrics and patterns from generated sessions.

**Input**:
- `artifacts/[program]/week-N-day-*.json` (all 5 sessions)

**Process** (pure Python):
- Count total reps per movement
- Calculate volume (tonnage) for week
- Track push vs pull movements
- Identify pattern repetition (which movements appear multiple times)
- Extract intensity distribution (% 1RM ranges used)
- Note energy system distribution

**Output**: `artifacts/[program]/week-N-summary.json`

```json
{
  "week": 2,
  "total_volume": {
    "reps": 280,
    "tonnage_lb": 45200,
    "sessions": 5
  },
  "push_pull_ratio": 1.05,
  "movement_frequency": {
    "back_squat": 2,
    "bench_press": 1,
    "deadlift": 1,
    "strict_press": 1,
    "pull_ups": 1,
    "rows": 1
  },
  "intensity_distribution": {
    "heavy_70_85": 8,
    "moderate_60_70": 12,
    "light_50_60": 5
  },
  "energy_systems": {
    "cns_intensive": 2,
    "glycolytic": 2,
    "aerobic": 1
  },
  "pattern_concerns": [
    "Squat appears twice; check spacing"
  ]
}
```

**Cost**: $0.00 (no API call)

---

### Step 6: Validator with Retry Logic

**Responsibility**: Verify week meets all constraints; trigger regeneration if needed.

**Input**:
- `artifacts/[program]/week-N-summary.json` (current week)
- `artifacts/[program]/week-(N-1)-summary.json` (previous week, if N > 1)
- `artifacts/knowledge-base.json` (rules)

**Process** (Claude Haiku):
- Check volume progression (≤15% increase from previous week)
- Check push-pull ratio (≥1:1)
- Check pattern repetition (no excessive repeat movements)
- Check recovery days (sufficient spacing for heavy sessions)
- Check energy system distribution (balanced)
- Verify week aligns with macro-plan theme

**Output**: `artifacts/[program]/week-N-validation.json`

```json
{
  "week": 2,
  "validation_timestamp": "2026-06-29T10:30:00Z",
  "valid": false,
  "issues": [
    {
      "rule_id": "push-pull-ratio",
      "severity": "high",
      "message": "Push:pull ratio is 0.8:1. Must be ≥1:1. Consider adding pull session or rebalancing.",
      "action": "regenerate"
    },
    {
      "rule_id": "volume-progression",
      "severity": "warning",
      "message": "Week 2 volume (280 reps) vs Week 1 (250 reps) = 12% increase. Within limit (15%) but at edge.",
      "action": "monitor"
    }
  ],
  "retry_count": 0,
  "max_retries": 3
}
```

**Logic**:
- If any `action: "regenerate"` → **retry Step 4** (re-generate all 5 sessions with feedback)
- If all `action: "monitor"` or no issues → **proceed to Step 7**
- If `retry_count` reaches `max_retries` (3) → fail and report to user

**Model**: Haiku
**Context**: ~5K
**Cost**: ~$0.0008/week

---

### Step 7: Assemble Final Program

**Responsibility**: Merge all validated weekly JSONs into final program.

**Input**:
- `artifacts/[program]/week-*/week-*-day-*.json` (all sessions, validated)
- Program metadata

**Process** (Python):
- Merge all day JSONs into `program.sessions` array
- Add program metadata (name, weeks, focus, description)
- Output to `output/[program].json`
- Generate markdown preview to `output/[program].md`

**Output**:
- `output/back-in-shape-4w.json` (final program, ~80K)
- `output/back-in-shape-4w.md` (human-readable)

**Cost**: $0.00 (pure Python)

---

## Folder Structure

```
woddy/
├── knowledge-base/          (existing, unchanged)
├── data/                    (existing, unchanged)
├── pipeline/                (NEW)
│   ├── orchestrator.py      (runs all 7 steps in sequence)
│   ├── step_1_curator.py    (Claude Haiku)
│   ├── step_2_strategist.py (Claude Haiku)
│   ├── step_3_planner.py    (Claude Haiku)
│   ├── step_4_composer.py   (Claude Haiku)
│   ├── step_5_summarizer.py (Pure Python)
│   ├── step_6_validator.py  (Claude Haiku)
│   └── step_7_assemble.py   (Pure Python)
├── artifacts/               (NEW)
│   └── [program-name]/
│       ├── knowledge-base.json           (Step 1 output)
│       ├── macro-plan.md                 (Step 2 output)
│       ├── week-1-objective.md           (Step 3 output)
│       ├── week-1-day-1.json             (Step 4 outputs)
│       ├── week-1-day-2.json
│       ├── ... (5 per week)
│       ├── week-1-summary.json           (Step 5 output)
│       ├── week-1-validation.json        (Step 6 output)
│       └── (repeat week-2, week-3, week-4)
├── output/                  (existing, final deliverables)
└── docs/
```

---

## Cost Analysis

| Step | Model | Input | Output | Cost/Run |
|------|-------|-------|--------|----------|
| 1: Extract | Haiku | 25K | 3K | $0.01 (one-time) |
| 2: Strategist | Haiku | 3K | 2K | $0.0008 |
| 3: Planner | Haiku | 6K | 1.5K | $0.0008 |
| 4: Composer | Haiku | 7K | 6K | $0.002 × 5 = $0.01 |
| 5: Summarizer | – | 30K | 1K | $0.00 |
| 6: Validator | Haiku | 5K | 0.5K | $0.0008 |
| 7: Assemble | – | 50K | 80K | $0.00 |
| **Per week** | – | – | – | **~$0.0124** |
| **Per 4-week program** | – | – | – | **~$0.05** |

**Compare to old approach**: ~$0.10+ per program → **50% cost reduction**

---

## Implementation Order

1. **Phase 1 — Pipeline Foundation**
   - Create `pipeline/` directory and orchestrator skeleton
   - Implement Step 1 (Knowledge Extractor)
   - Generate `artifacts/knowledge-base.json`

2. **Phase 2 — Generation Pipeline (Steps 2-5)**
   - Implement Step 2 (Macroplan Generator)
   - Implement Step 3 (Weekly Planner)
   - Implement Step 4 (Session Composer)
   - Implement Step 5 (Summarizer)

3. **Phase 3 — Quality Assurance (Step 6)**
   - Implement Step 6 (Validator)
   - Test retry logic

4. **Phase 4 — Assembly & Testing**
   - Implement Step 7 (Assemble)
   - Test full pipeline with 2-week and 4-week programs
   - Validate output matches current JSON schema

5. **Phase 5 — Optimization & Documentation**
   - Profile execution time per step
   - Document step prompts
   - Update `generate-all.sh` to use new pipeline

---

## Success Criteria

- ✅ 4-week program generates without timeout
- ✅ Validator catches and fixes at least one issue per program
- ✅ Cost per program ≤ $0.06
- ✅ Output JSON schema identical to current
- ✅ Human-readable artifacts in `artifacts/` for debugging
- ✅ All rules in `knowledge-base.json` used by at least one step

---

## Migration Path (No Breaking Changes)

- Current `generate.py` remains untouched during development
- New pipeline runs in `pipeline/orchestrator.py`
- Once validated, swap `generate-all.sh` to use new orchestrator
- Old monolithic generator kept as fallback reference

---

## Notes

- **Stateless steps**: Each step can run independently if inputs exist (supports parallelization in future)
- **Debugging**: All intermediate artifacts saved to `artifacts/` for inspection
- **Idempotent**: Re-running validator doesn't change previous weeks
- **Extensible**: Easy to add new validation rules (just add to `knowledge-base.json`)
- **Cheap**: All steps use Haiku; upgrade to Sonnet only if quality requires it

