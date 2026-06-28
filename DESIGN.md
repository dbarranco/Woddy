# Woddy — Design Document
**Version 1.0 | Status: Draft**

---

## 1. Product Vision

A Progressive Web App (PWA) that delivers science-backed CrossFit programming directly to your phone. The app provides two modes: a structured multi-week program with progressive overload, and a daily WOD for drop-in sessions. Every workout is grounded in sports science, explains its reasoning, and cites its sources.

**Core principles:**
- Every workout is backed by science, not generated arbitrarily
- The AI assembles from a curated knowledge base — it does not invent
- Sessions fit within a hard 60-minute cap (30 min for skill cycles)
- The app works offline, on iPhone and Android, installable from the browser

---

## 2. Target User

Someone who goes to the gym regularly but does not have a coach. They want structured, progressive training that makes sense — not random WODs with no continuity. They may know their 1RMs on major lifts or be willing to estimate them.

---

## 3. Features — V1 Scope

### 3.1 Two Coexisting Modes

#### Mode A — Structured Program
- User selects a program and a duration (2, 3, or 4 weeks)
- App generates a full program upfront and stores it in localStorage
- Home screen shows the current day of the program when active
- If the user skips a day, the program pauses and resumes next session — no recalculation
- WOD mode remains accessible as a secondary option while a program is active

#### Mode B — WOD of the Day
- Default state when no program is active
- Rotates through a pre-generated pool of workouts (minimum 4 weeks = ~28 WODs before repeating)
- User can randomize and filter by category
- Filters: Upper Body / Lower Body / Full Body / Cardio / Strength

### 3.2 Programs (V1)

| Program | Duration | Focus |
|---|---|---|
| Back in Shape | 2–4 weeks (user selects) | General fitness, return to training |
| Gymnastics Base | 4 weeks | Skill cycle, 30 min sessions |

Program generation requires user to optionally input 1RMs (Back Squat, Deadlift, Press, Clean). If not provided, the generator uses RPE-based guidance instead of percentages.

### 3.3 Session Structure

#### Full Session (60 min hard cap)
| Block | Duration | Content |
|---|---|---|
| Static warmup | 5 min | Stretching, mobility, joint prep |
| Active warmup | 5 min | Movement-specific activation, light barbell/gymnastics prep |
| Skill / Strength | 20–25 min | Main strength or skill work |
| Metcon | 15–20 min | Conditioning piece (AMRAP, EMOM, For Time) |
| Cooldown / Mobility | 5–10 min | Targeted stretching, recovery work |

**Metcon time domains allowed:** short (<7 min), medium (7–15 min). Long AMRAPs (20–30 min) and hero WODs are excluded from regular sessions. They can be offered as optional "extended session" variants flagged in the UI.

#### Skill Cycle Session (30 min hard cap)
| Block | Duration | Content |
|---|---|---|
| Warmup | 5 min | Specific to the skill being trained |
| Skill work | 20–25 min | Progressions, drills, volume sets |
| No metcon | — | Recovery is part of the adaptation |

### 3.4 Equipment — Bill of Materials

Every session displays the equipment needed before the workout begins. This is generated per-session from the movement list.

**Standard gym equipment referenced:**
- Barbell + plates
- Pull-up bar / rig
- Gymnastics rings
- Kettlebell(s)
- Dumbbell(s)
- Box (plyo box, 20"/24")
- Rowing machine / Assault bike / Ski erg
- Jump rope
- Resistance bands (for mobility and scaling)
- Foam roller / lacrosse ball (cooldown)

Each session lists only what is needed for that session, with scaling alternatives if equipment is unavailable.

### 3.5 Scientific Rationale Block

Every session includes a rationale section explaining:

1. **Session rationale** — why this session today in the context of the program (energy system targeted, placement in the weekly structure)
2. **Movement rationale** — why these movements are paired, what adaptation they drive
3. **Loading rationale** — why this rep scheme and percentage, what it targets physiologically

Each rationale cites a real source with a link or reference. No claim is made without a source. If no source exists in the knowledge base for a claim, the claim is not made.

**Example rationale output:**
```
WHY THIS SESSION
This session targets the phosphocreatine and glycolytic energy systems with
a short, high-power metcon following a moderate-volume strength piece.
Placing the strength block first preserves neural freshness for heavier loading.
→ Haff & Triplett, NSCA Essentials of Strength & Conditioning (4th ed.), Ch. 20

WHY THESE MOVEMENTS
The clean pull + hang clean pairing develops positional awareness through
partial range repetition before the full movement — a standard teaching
progression in Olympic weightlifting.
→ Zatsiorsky & Kraemer, Science and Practice of Strength Training (2006)

WHY THIS LOADING
75% 1RM for 4x3 targets neuromuscular efficiency and technique consolidation
without excessive metabolic fatigue, appropriate mid-cycle.
→ Schoenfeld, The Science and Development of Muscle Hypertrophy (2016)
```

### 3.6 Session Timer — Unified Session View

The timer is not a separate screen. The workout content and the clock occupy the **same screen simultaneously** so the user can read what to do while the clock runs. They never navigate away or lose their place.

**Screen layout during an active session:**
```
┌─────────────────────────────┐
│  ACTIVE WARMUP  •  Round 3/8│  ← block name + round progress
│                             │
│           0:24              │  ← large clock, screen center
│                             │
│  ▓▓▓▓▓▓▓▓▓░░░░░░░░░░░░░░░  │  ← round progress bar
│                             │
│  Inchworm × 5               │  ← movements for this block
│  Hip circles × 10 each      │
│  Banded pull-apart × 15     │
│                             │
│  Next: Strength block ───►  │  ← preview of next block
└─────────────────────────────┘
```

**The clock is pre-configured per block and per round structure.** Every session encodes its own timer instructions in JSON — the user configures nothing:

| Block type | Timer behaviour |
|---|---|
| Warmup — 8 rounds × 30 sec | EMOM: beeps every 30s, shows round N/8 |
| Strength — 4 sets, 2 min rest | Counts down rest period after each set |
| Metcon AMRAP — 12 min | Single countdown 12:00 → 0:00 |
| Metcon EMOM — 10 min | Beeps every 60s, shows round N/10 |
| Metcon For Time — cap 15 min | Count-up, stops on Done tap or at cap |
| Cooldown — 8 min | Single countdown, no rounds |

**Timer behaviour:**
- Auto-advances to next block at end of each block with audible beep + visual transition
- User can manually skip forward or back to any block
- Final 10 seconds: clock turns red, rapid beeps
- Screen stays awake (Wake Lock API)
- Works fully offline
- CrossFit competition clock aesthetic: large digits, dark background

**Entry point:** A single **"Start Session"** button at the top of the session view. One tap starts the first block. Everything else is automatic.

### 3.7 Random WOD

Available from the home screen and from within the WOD mode:
- Filter by: Upper Body / Lower Body / Full Body / Cardio / Strength
- Draws from the pre-generated WOD pool
- Shows equipment needed before confirming
- Does not repeat the same WOD within 7 days (tracked in localStorage)

---

## 4. Technical Architecture

### 4.1 Platform

Progressive Web App (PWA):
- Works on iOS (Safari) and Android (Chrome)
- Installable to home screen on both platforms
- Offline capable via service worker
- No app store required

**iOS-specific:** requires `apple-mobile-web-app-capable` and `apple-mobile-web-app-status-bar-style` meta tags, plus apple-touch-icon assets.

**Android-specific:** requires `manifest.json` with `display: standalone`.

### 4.2 Hosting

GitHub Pages — fully static. No backend server.

**Repository structure:**
```
/
├── index.html          ← app shell
├── manifest.json       ← PWA manifest
├── sw.js               ← service worker
├── assets/
│   ├── css/
│   ├── js/
│   └── icons/          ← PWA icons (iOS + Android sizes)
├── data/
│   ├── knowledge-base/ ← curated source documents (markdown)
│   ├── programs/       ← pre-generated program JSON files
│   └── wods/           ← pre-generated WOD pool JSON
└── scripts/
    └── generate.py     ← local generation script (not deployed)
```

### 4.3 Data Storage

All user state lives in **localStorage** on the device:
```json
{
  "activeProgram": { "id": "back-in-shape-3w", "currentDay": 6, "startDate": "2025-01-01" },
  "completedSessions": ["day-1", "day-2", "day-3", "day-5"],
  "skippedSessions": ["day-4"],
  "userProfile": { "backSquat1RM": 100, "deadlift1RM": 130, "press1RM": 65, "clean1RM": 80 },
  "wodHistory": ["wod-14", "wod-07", "wod-22"],
  "preferences": { "units": "kg", "sessionReminder": false }
}
```

No account, no sync, no server. Data lives on the device.

### 4.4 AI Generation — Fully Pre-computed

The GitHub Pages site is a **complete static dump**. The browser renders HTML and JSON — it performs zero computation, makes zero API calls, and has zero external dependencies at runtime. This means it works offline, scales to unlimited users for free, and requires no backend.

**All content is generated before deployment:**

```
[GitHub Actions — scheduled every 3–7 days]
generate.py
  ├── Load knowledge base, movement library, hard rules
  ├── Call Claude API (API key stored as GitHub repository secret)
  ├── Generate: full program JSON × all durations (2w, 3w, 4w)
  ├── Generate: WOD pool JSON (28–56 WODs, enough for 4–8 weeks)
  ├── Validate all output against schema
  ├── Write to /data/programs/ and /data/wods/
  └── git commit + push → GitHub Pages serves updated static files

[User's browser — runtime]
  Fetches static JSON. Renders workout. Runs timer.
  No API. No server. No dependencies.
```

**Refresh cadence:** GitHub Actions runs on a schedule (configurable — weekly is a good default). The maintainer can also trigger it manually at any time. The WOD pool is large enough that users will not see repeats between refresh cycles.

### 4.5 Data Schema

#### Program
```json
{
  "id": "back-in-shape-3w",
  "name": "Back in Shape",
  "weeks": 3,
  "focus": "general",
  "description": "A progressive return-to-training program...",
  "sessions": [ ]
}
```

#### Session
```json
{
  "id": "day-1",
  "week": 1,
  "day": 1,
  "title": "Squat + Short Metcon",
  "durationMinutes": 60,
  "equipment": ["barbell", "plates", "pull-up bar"],
  "blocks": {
    "staticWarmup": { "durationMinutes": 5, "content": [ ] },
    "activeWarmup": { "durationMinutes": 5, "content": [ ] },
    "strength": { "durationMinutes": 22, "content": [ ] },
    "metcon": { "durationMinutes": 15, "format": "AMRAP", "timeCap": 12, "content": [ ] },
    "cooldown": { "durationMinutes": 8, "content": [ ] }
  },
  "rationale": {
    "session": { "text": "...", "source": "...", "url": "..." },
    "movement": { "text": "...", "source": "...", "url": "..." },
    "loading": { "text": "...", "source": "...", "url": "..." }
  }
}
```

#### Movement (within a block)
```json
{
  "name": "Back Squat",
  "sets": 4,
  "reps": 5,
  "load": "75% 1RM",
  "restSeconds": 180,
  "notes": "Pause 2 seconds in the hole",
  "scaling": "Goblet squat with KB if barbell unavailable"
}
```

#### WOD
```json
{
  "id": "wod-14",
  "title": "Grace-style",
  "category": ["full-body", "strength"],
  "equipment": ["barbell", "plates"],
  "durationMinutes": 60,
  "blocks": { },
  "rationale": { }
}
```

---

## 5. Knowledge Base Structure

The knowledge base is the foundation the AI builds from. It is curated by humans, sourced from authoritative references, and the AI cannot override it.

### 5.1 Pyramid

```
         ┌─────────────────┐
         │  AI GENERATION  │  assembles only — never invents
         └────────┬────────┘
                  │ constrained by
         ┌────────▼────────┐
         │   HARD RULES    │  periodization logic, % tables,
         │  (JSON/code)    │  recovery constraints, time caps
         └────────┬────────┘
                  │ derived from
         ┌────────▼────────┐
         │ CURATED SOURCES │  real books, real papers
         │  (KB documents) │  written and verified by us
         └────────┬────────┘
                  │ validated by
         ┌────────▼────────┐
         │ PRIMARY SCIENCE │  energy systems, motor learning,
         │   (the base)    │  biomechanics — things that don't change
         └─────────────────┘
```

### 5.2 Source Tiers

**Tier 1 — Primary (non-negotiable foundations)**
- Glassman, "What is Fitness?" CrossFit Journal (2002) — GPP, 10 physical skills
- Haff & Triplett, *NSCA Essentials of Strength & Conditioning* (4th ed.) — periodization, % tables, energy systems
- Zatsiorsky & Kraemer, *Science and Practice of Strength Training* (2006) — loading parameters
- Bompa & Haff, *Periodization: Theory and Methodology of Training* (5th ed.) — block structure

**Tier 2 — Applied research**
- Schoenfeld, *The Science and Development of Muscle Hypertrophy* (2016) — rep ranges, volume
- Wilson et al. (2012), J Strength Cond Res — concurrent training interference
- Robbins (2005) — post-activation potentiation
- Seiler & Tønnessen (2009) — intensity distribution, polarized training

**Tier 3 — Practitioner methodology**
- CrossFit Level 2 Training Guide — WOD structure, coaching cues
- Sommer, *Building the Gymnastic Body* — gymnastics progressions
- PRVN / Mayhem programming structure (publicly documented)

### 5.3 Hard Rules (enforced in code, not prompt)

```
SESSION CONSTRAINTS
- Total session duration ≤ 60 min (skill cycles ≤ 30 min)
- Warmup = static (5 min) + active (5 min) — both always present
- Cooldown/mobility always present at end of full session
- Metcon time cap ≤ 20 min for regular sessions

WEEKLY STRUCTURE
- No Olympic lifting two consecutive days
- Max 2 heavy lower body days per week (≥80% 1RM)
- Min 1 pure aerobic session per week
- No two high-CNS-demand sessions back to back

LOADING (when 1RM provided)
- Week 1: 70–75% 1RM
- Week 2: 75–80% 1RM
- Week 3: 80–85% 1RM
- Week 4 (if applicable): Deload at 60–65% 1RM

MOVEMENT BALANCE (per week)
- Push/pull ratio ≥ 1:1
- Hinge and squat patterns both present
- At least one monostructural cardio piece
```

---

## 6. Generator Prompt Structure

The prompt has three mandatory sections:

**Section 1 — Identity and constraint**
The AI is a CrossFit strength and conditioning coach. It generates programs strictly from the knowledge base. It does not invent loading percentages, energy system claims, or scientific references. If a concept is not in the knowledge base, it is not used. All rationale must cite a source from the knowledge base.

**Section 2 — Knowledge context**
Full text of the relevant knowledge base documents, movement library, and hard rules, injected at prompt time.

**Section 3 — Output contract**
The AI returns only valid JSON matching the session schema. No prose, no markdown, no explanation outside the schema fields. If a required field cannot be filled from the knowledge base, it is set to null — never guessed.

---

## 7. UI / UX Principles

- Mobile-first, large tap targets
- Screen stays on during active timer (Wake Lock API)
- Dark mode by default (gym lighting)
- Equipment list visible before the session begins — no surprises
- Rationale block collapsed by default, expandable — doesn't clutter the workout view
- CrossFit-style timer: large digits, color shift in final 10 seconds, audible beep

---

## 8. Development Plan — Vertical Slices

Each slice is independently deployable and useful on its own.

### Slice 1 — PWA Shell (foundation)
**Goal:** Installable app on iOS and Android with navigation structure.
- `manifest.json`, service worker, offline support
- App shell with bottom navigation: Home / Programs / Timer
- iOS and Android install prompts
- localStorage initialization
- No content yet — just the working skeleton

**Deliverable:** Installable blank app on both platforms.

---

### Slice 2 — Timer
**Goal:** A fully working CrossFit timer, usable immediately.
- Count-up and countdown modes
- AMRAP timer (countdown)
- EMOM interval timer (beep every minute)
- Wake Lock API (screen stays on)
- Large display, dark background, color shift in last 10 seconds

**Deliverable:** Standalone timer that works in the gym today.

---

### Slice 3 — Knowledge Base + Generator
**Goal:** Build the knowledge base documents and the generation script.
- Write and source Tier 1 knowledge base documents
- Write movement library JSON
- Write hard rules JSON
- Write and test generator prompt
- Write `generate.py` script
- Validate output quality: does the program make sense? Are citations real?

**Deliverable:** A working generator that produces valid, science-backed program JSON from the command line.

---

### Slice 4 — Program Viewer
**Goal:** Display a pre-generated program in the app.
- Load "Back in Shape" program JSON
- Home screen shows current day when program is active
- Session view: static warmup → active warmup → strength → metcon → cooldown
- Equipment bill of materials before session
- Rationale block (collapsed/expandable)
- Mark session complete / skip
- LocalStorage tracks progress

**Deliverable:** A real workout program you can follow in the gym.

---

### Slice 5 — WOD Mode + Random WOD
**Goal:** Drop-in WOD experience.
- Pre-generated WOD pool (minimum 28 WODs)
- Home screen WOD when no program is active
- Random WOD button with category filters
- No-repeat logic (7-day window via localStorage)

**Deliverable:** Daily WOD with randomization, fully usable.

---

### Slice 6 — Program Selection + Gymnastics Skill Cycle
**Goal:** Let the user pick a program and duration, and access the Gymnastics Base skill cycle.
- Programs screen listing all available programs with descriptions and focus areas
- Duration selector (2 / 3 / 4 weeks) — selects the matching pre-generated JSON
- 1RM input form stored in localStorage — used to display personalised % guidance within the pre-generated program (the percentages adapt in the UI based on the user's numbers, no API call needed)
- Gymnastics Base skill cycle available as a separate program

**Deliverable:** Full program selection experience with personalised loading display.

---

### Slice 7 — GitHub Actions Pipeline (optional)
**Goal:** Automate WOD pool refresh.
- GitHub Actions workflow runs on schedule (weekly or monthly)
- Runs `generate.py` to refresh WOD pool
- Commits output to repo
- GitHub Pages serves updated content automatically

**Deliverable:** Self-updating WOD pool without manual intervention.

---

## 9. Out of Scope (V1)

- Adaptive programs (recalculation on missed sessions)
- User accounts or cross-device sync
- Social features
- Video demonstrations
- Nutrition guidance
- Long AMRAPs / hero WODs as regular sessions
- Snatch / Clean & Jerk skill cycles (V2)
- Strict strength skill cycle (V2)

---

## 10. Open Questions

1. **Units:** kg or lbs? Or user-selectable on first launch?
2. **Language:** English only for V1?
3. **App name:** To be decided.
4. **Refresh cadence:** Every 3 days, weekly, or on push? (Recommendation: weekly via GitHub Actions scheduled workflow)
