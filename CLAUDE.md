# Woddy 🏋️

AI-powered CrossFit programming app. Static PWA hosted on GitHub Pages. All content is pre-generated offline via Claude API and committed as static JSON. Zero runtime API calls.

---

## What This Project Is

A Progressive Web App that delivers science-backed CrossFit programs and daily WODs. Two modes:
- **Program mode** — structured 2/3/4-week programs with progressive loading
- **WOD mode** — rotating pool of daily workouts with category filters

Every workout includes full session structure, equipment list, and scientific rationale with real citations.

---

## Repository Structure

```
woddy/
├── CLAUDE.md                   ← you are here
├── DESIGN.md                   ← full product design document
├── setup-woddy.sh              ← one-shot project setup script
│
├── knowledge-base/             ← curated sports science documents (source of truth)
│   ├── 01-energy-systems.md
│   ├── 02-crossfit-methodology.md
│   ├── 03-periodization.md
│   ├── 04-recovery.md
│   └── 05-gymnastics.md
│
├── data/                       ← structured data the generator uses
│   ├── movement-library.json   ← 68 movements across 6 categories
│   └── hard-rules.json         ← hard constraints (time caps, loading %, weekly limits)
│
├── scripts/
│   └── generate.py             ← main generation script (calls Claude API)
│
├── output/                     ← generated JSON + markdown (gitignored during dev)
│   ├── *.json                  ← program and WOD data
│   └── *.md                    ← human-readable previews
│
├── docs/                       ← GitHub Pages root (the actual app)
│   ├── index.html
│   ├── manifest.json
│   ├── sw.js
│   ├── assets/
│   │   ├── css/
│   │   ├── js/
│   │   └── icons/
│   └── data/                   ← committed generated JSON served to users
│       ├── programs/
│       └── wods/
│
└── .github/
    └── workflows/
        └── generate.yml        ← scheduled GitHub Actions regeneration
```

---

## Architecture — Read This First

**The browser does nothing.** It fetches static JSON and renders it. No API calls at runtime.

```
[Local / GitHub Actions]          [GitHub Pages]
generate.py                  →    docs/data/*.json
  reads knowledge-base/           served statically
  reads data/                     to any browser
  calls Claude API                worldwide
  validates output
  writes JSON + markdown
```

**API key** lives in your local environment (`ANTHROPIC_API_KEY`) or as a GitHub Actions repository secret. It is never in the codebase.

---

## Running the Generator

```bash
cd woddy/scripts
pip install anthropic
export ANTHROPIC_API_KEY=your_key_here

# Generate a 3-week program
python generate.py --type program --name back-in-shape --weeks 3

# Generate WOD pool
python generate.py --type wod --count 7 --category full-body
python generate.py --type wod --count 7 --category upper-body
python generate.py --type wod --count 7 --category lower-body
python generate.py --type wod --count 7 --category strength
python generate.py --type wod --count 7 --category cardio

# Output lands in woddy/output/
```

---

## The Knowledge Pyramid

The AI assembles — it never invents. Content must come from this hierarchy:

```
AI GENERATION        ← assembles only, never invents
      ↑ constrained by
HARD RULES           ← data/hard-rules.json (time caps, % tables, weekly limits)
      ↑ derived from
CURATED SOURCES      ← knowledge-base/*.md (real books, real papers)
      ↑ validated by
PRIMARY SCIENCE      ← energy systems, motor learning, biomechanics
```

**If a concept is not in the knowledge base, the generator must not use it.**

---

## Session Structure (Non-Negotiable)

Every full session = exactly 60 minutes:

| Block | Duration | Notes |
|---|---|---|
| Static warmup | 5 min | Stretching, mobility, joint prep |
| Active warmup | 5 min | Movement-specific activation |
| Strength / Skill | 20–25 min | Main work, placed first for CNS freshness |
| Metcon | 10–20 min | AMRAP/EMOM/For Time, max 20 min cap |
| Cooldown / Mobility | 5–10 min | Static stretch, foam roll |

Skill cycles (gymnastics) = 30 minutes max. No metcon block.

---

## Hard Constraints Summary

- Full session ≤ 60 min | Skill session ≤ 30 min
- Metcon time cap ≤ 20 min
- No Olympic lifting on consecutive days
- No two high-CNS sessions back to back
- Push:pull ratio ≥ 1:1 per week
- Minimum 1 aerobic session per week
- Week 4 of a 4-week program = mandatory deload
- Every rationale must cite from `hard-rules.json → allowed_sources`
- No fabricated citations — ever

---

## Data Schema — Key Types

### Session block `timer_config`
```json
{
  "type": "amrap | emom | for_time",
  "duration_seconds": 720,
  "interval_seconds": null
}
```
The UI uses this to pre-configure the clock. No user setup required.

### Rationale block
```json
{
  "session_why": { "text": "...", "source": "...", "url_or_ref": "..." },
  "movement_why": { "text": "...", "source": "...", "url_or_ref": "..." },
  "loading_why":  { "text": "...", "source": "...", "url_or_ref": "..." }
}
```
All three fields required. Source must be in `allowed_sources`.

---

## UI — Key Behaviours

- **Single "Start Session" button** → launches pre-configured timer sequence
- **Timer and workout content on the same screen** — user never navigates away
- **Clock auto-advances** through blocks, beeps at transitions
- **Final 10 seconds**: clock turns red, rapid beeps
- **Wake Lock API** — screen stays on during active timer
- **Equipment list** shown before session starts
- **Rationale block** collapsed by default, expandable
- **Dark mode** by default (gym lighting)

---

## PWA Requirements

- `manifest.json` with `display: standalone`
- Service worker with offline caching
- `apple-mobile-web-app-capable` meta tag (iOS)
- `apple-touch-icon` assets (iOS home screen)
- Wake Lock API for timer screen

---

## Development Slices (in order)

1. **PWA shell** — installable blank app on iOS + Android
2. **Timer** — standalone CrossFit clock, usable immediately
3. **Knowledge base + generator** ✅ done
4. **Program viewer** — display pre-generated program, track progress
5. **WOD mode + random WOD** — pool rotation + category filters
6. **Program selection** — pick program, duration, input 1RMs
7. **GitHub Actions pipeline** — scheduled auto-regeneration

---

## What NOT to Do

- Do not add runtime API calls to the frontend
- Do not put the API key in any file or the codebase
- Do not fabricate citations or invent loading percentages
- Do not generate sessions longer than 60 minutes
- Do not use Chippers or Hero WODs as regular sessions
- Do not schedule Olympic lifting on consecutive days
- Do not skip the rationale block — it is the differentiator

---

## Allowed Citation Sources

From `hard-rules.json`. Only these may appear in rationale blocks:

- Glassman 2002 - CrossFit Journal
- Haff & Triplett - NSCA Essentials 4th ed
- Bompa & Haff - Periodization 5th ed
- Zatsiorsky & Kraemer - Science and Practice of Strength Training
- Schoenfeld - Science and Development of Muscle Hypertrophy
- Wilson et al 2012 - Concurrent Training Meta-Analysis
- Robbins 2005 - Post-Activation Potentiation
- Sommer - Building the Gymnastic Body
- CrossFit Level 2 Training Guide
- CrossFit Gymnastics Specialty Course
- Gastin 2001 - Energy System Interaction
- Behm et al 2016 - Acute Effects of Muscle Stretching
- Kreher & Schwartz 2012 - Overtraining Syndrome
