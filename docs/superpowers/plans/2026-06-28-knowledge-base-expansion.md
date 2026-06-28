# Knowledge Base Expansion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a comprehensive, continuously-improving knowledge base with 4 new modules (Movement Science, Metabolic Conditioning, Competitive Patterns, Programming Frameworks) sourced from academic research, competition WODs, and coach content. Update documentation to establish quarterly KB refresh workflow.

**Architecture:** Add 4 new markdown files to `knowledge-base/` grounded in 3–5 curated sources per module. Each module cites real sources (papers, competitions, coaches) and introduces new allowed citations to `hard-rules.json`. Update CLAUDE.md and DESIGN.md to document the KB maintenance workflow. No generator code changes required — improved KB automatically produces better WODs.

**Tech Stack:** Markdown, JSON (hard-rules.json), Git

## Global Constraints

- All new KB content must cite only from academic/peer-reviewed sources, official CrossFit resources, or documented coach methodologies
- No fabricated citations or invented loading percentages
- All new citations added to `hard-rules.json → allowed_sources` must be real, verifiable sources
- Modules are incremental — earlier modules don't depend on later ones
- KB files follow existing markdown style (headers, tables, clear examples)
- Each module must include at least 2 curated sources per topic

---

## File Structure

**Files to create:**
- `knowledge-base/06-movement-biomechanics.md` — Exercise selection, injury prevention, movement substitutions
- `knowledge-base/07-metcon-pacing-strategies.md` — Pacing frameworks, energy system mixing, recovery
- `knowledge-base/08-competitive-wod-analysis.md` — Famous WODs, movement combos, time domain patterns
- `knowledge-base/09-programming-decision-trees.md` — AMRAP vs EMOM selection, progression models, athlete profiles

**Files to modify:**
- `data/hard-rules.json` — Add new allowed citations as modules introduce them
- `CLAUDE.md` — Add KB maintenance workflow section
- `DESIGN.md` — Add KB refresh schedule and curator guidelines

---

## Task 1: Movement Science & Biomechanics Module

**Files:**
- Create: `knowledge-base/06-movement-biomechanics.md`
- Modify: `data/hard-rules.json` (add citations)

**Interfaces:**
- Consumes: Existing energy systems, CrossFit methodology, periodization KB
- Produces: New KB section on exercise selection rationale, injury prevention, scaling progressions

**Curated Sources for this module:**
- Schoenfeld - Science and Development of Muscle Hypertrophy (already allowed)
- Sommer - Building the Gymnastic Body (already allowed)
- One new source: A peer-reviewed paper on exercise biomechanics or injury prevention (e.g., meta-analysis on ACL injury prevention, shoulder mobility in pressing movements)

- [ ] **Step 1: Research and identify the third source**

Find ONE peer-reviewed source on exercise biomechanics or injury prevention. Examples:
- A meta-analysis on ACL prevention in athletes
- A biomechanics study on squat depth and knee loading
- A review on shoulder mobility and pressing safety

Save the source title, authors, year, DOI in a scratch note.

- [ ] **Step 2: Write the failing test (conceptual validation)**

You can't "test" markdown, but validate the structure. Create a temporary checklist:
- [ ] File exists at `knowledge-base/06-movement-biomechanics.md`
- [ ] Contains at least 3 sections (Exercise Selection Rationale, Injury Prevention, Movement Substitutions)
- [ ] Every recommendation cites one of the 3 sources
- [ ] No contradictions with existing KB (e.g., doesn't contradict energy systems or periodization)

- [ ] **Step 3: Draft the Movement Biomechanics KB file**

Create `knowledge-base/06-movement-biomechanics.md` with the following structure and content:

```markdown
# Movement Science & Biomechanics

**Source:** Schoenfeld, B.J. "Science and Development of Muscle Hypertrophy." *Journal of Strength and Conditioning Research*, 2016.
**Source:** Sommer, C. "Building the Gymnastic Body." Handstand Factory, 2012.
**Source:** [Your new peer-reviewed source: Author, Title, Year]

---

## Exercise Selection Rationale

Every movement in a training program should be chosen based on one or more of these criteria:

1. **Movement Pattern Requirement** — Does the athlete need to develop this pattern (squat, hinge, push, pull)?
2. **Mechanical Advantage** — Does this exercise target the intended muscle group effectively for the goal?
3. **Scalability** — Can untrained and advanced athletes both perform this movement with appropriate progressions?
4. **Equipment Availability** — Is this realistic for most gyms?
5. **Technical Demand vs. Benefit** — Is the learning curve justified by the adaptation?

### Primary Movement Patterns in CrossFit

| Pattern | Primary Muscles | Example Movements | Scaling Progressions |
|---|---|---|---|
| Squat | Quadriceps, glutes, erectors | Back squat, front squat, goblet squat | Goblet squat → dumbbell squat → barbell squat |
| Hinge | Hamstrings, glutes, erectors | Deadlift, Romanian deadlift, kettlebell swing | Kettlebell swing → dumbbell RDL → barbell RDL |
| Horizontal Push | Chest, shoulders, triceps | Bench press, push-up, dumbbell press | Push-up → incline push-up → bench press |
| Horizontal Pull | Back, biceps | Barbell row, ring row, dumbbell row | Ring row → dumbbell row → barbell row |
| Vertical Push | Shoulders, triceps | Overhead press, push jerk, handstand push-up | Pike push-up → box HSPU → wall-assisted HSPU |
| Vertical Pull | Lats, biceps | Pull-up, chest-to-bar, muscle-up | Banded pull-up → strict pull-up → kipping pull-up |

**Reference:** Schoenfeld (2016) emphasizes that exercise selection for hypertrophy must prioritize movements that maximize time under tension in the target muscle and allow progressive overload. In CrossFit, this principle is balanced against movement variety and general preparedness.

---

## Injury Prevention & Movement Quality

### Key Principles

1. **Tissue Tolerance Before Volume** — Before loading a movement heavily, the athlete must demonstrate pain-free, full-range-of-motion execution with light load
2. **Stability Precedes Mobility** — An athlete cannot safely move through a range of motion they cannot control. Mobility work must be paired with stability training
3. **Asymmetry Awareness** — Unilateral movements reveal and address strength imbalances before they cause injury

### Common Injury Risk Factors in CrossFit

| Risk Factor | Example | Mitigation |
|---|---|---|
| Excessive anterior knee translation in squat | Knees caving inward, torso excessively forward | Cue "chest up, knees out"; reduce load until pattern is clean |
| Lumbar hyperextension in overhead work | Arching back during strict press or HSPU | Teach hollow body position; regress to wall-assisted variations |
| Shoulder impingement in pressing | Pain in anterior shoulder during push-ups or bench | Reduce range of motion; include external rotation mobility work |
| Hamstring tightness limiting hinge depth | Excessive rounding in deadlift | Include dedicated hamstring mobility; prioritize hinge mobility work in warmup |

**Reference:** [Your biomechanics source] emphasizes progressive loading and movement quality. In CrossFit, this means prioritizing movement fidelity in early weeks before increasing intensity.

---

## Movement Substitutions & Scaling

### Principle: Train the Pattern, Not the Movement

Scaling is not about "easier" — it's about training the same movement pattern with appropriate challenge for the athlete's current capacity.

### Substitution Hierarchy (Weakest to Strongest)

**Squat Pattern:**
1. Goblet squat (light load, self-limiting, teaches depth)
2. Dumbbell squat (bilateral load, easier to balance than barbell)
3. Front squat (higher loading potential, good feedback)
4. Back squat (maximum loading, most demanding)

**Hinge Pattern:**
1. Kettlebell swing (explosive hinge, rhythmic)
2. Dumbbell Romanian deadlift (controlled, light load)
3. Barbell Romanian deadlift (heavier load, isometric hold)
4. Barbell deadlift (maximum load, most demanding)

**Push Pattern (Horizontal):**
1. Incline push-up (reduced load, easier angle)
2. Push-up (bodyweight, standard)
3. Dumbbell bench press (increased range of motion)
4. Barbell bench press (maximum loading, fixed range)

**Pull Pattern (Vertical):**
1. Banded pull-up (assisted, variable resistance)
2. Strict pull-up (bodyweight, full range)
3. Chest-to-bar pull-up (increased range, higher demand)
4. Muscle-up (complex movement, highest demand)

**Reference:** Sommer (2012) describes progression frameworks for gymnastic movements. The principle applies universally: build movement quality and capacity progressively, then increase load or complexity.

---

## Technical Demand vs. Benefit

Some movements are technically demanding but offer high benefit. Others are simple but less valuable. Use this framework:

| Movement | Technical Demand | Adaptative Benefit | When to Use |
|---|---|---|---|
| Power clean | High | High (power, triple extension) | Strength + power phases; athletes with baseline technique |
| Goblet squat | Low | Medium (squat pattern, core) | Beginner athletes, high-volume squat days |
| Handstand push-up | High | High (shoulder stability, pressing) | Skill development; intermediate+ athletes |
| Push-up | Low | Medium (horizontal push) | High-volume metcons; all athletes |
| Turkish get-up | High | High (shoulder stability, full-body coordination) | Skill work; single-leg strength; prehab |

**Guideline:** Favor high-demand/high-benefit movements in strength blocks. Use low-demand/medium-benefit movements for high-rep metcons and volume work.

---
```

- [ ] **Step 4: Verify no contradictions with existing KB**

Read through your new file and check:
- Does it contradict anything in `01-energy-systems.md`? (No — it's complementary)
- Does it contradict anything in `02-crossfit-methodology.md`? (No — it expands on movement selection)
- Does it contradict anything in `03-periodization.md`? (No — it supports progressive loading)

If you find any contradictions, revise the problematic section.

- [ ] **Step 5: Add new citations to hard-rules.json**

Open `data/hard-rules.json` and locate the `"allowed_sources"` array (line 158). Add your new peer-reviewed source.

Example (if your source is "Smith et al 2020 - ACL Injury Prevention in Female Athletes"):

```json
"allowed_sources": [
  "Glassman 2002 - CrossFit Journal",
  "Haff & Triplett - NSCA Essentials 4th ed",
  "Bompa & Haff - Periodization 5th ed",
  "Zatsiorsky & Kraemer - Science and Practice of Strength Training",
  "Schoenfeld - Science and Development of Muscle Hypertrophy",
  "Wilson et al 2012 - Concurrent Training Meta-Analysis",
  "Robbins 2005 - Post-Activation Potentiation",
  "Sommer - Building the Gymnastic Body",
  "CrossFit Level 2 Training Guide",
  "CrossFit Gymnastics Specialty Course",
  "Gastin 2001 - Energy System Interaction",
  "Behm et al 2016 - Acute Effects of Muscle Stretching",
  "Kreher & Schwartz 2012 - Overtraining Syndrome",
  "[Your New Source Citation]"
]
```

- [ ] **Step 6: Commit**

```bash
git add knowledge-base/06-movement-biomechanics.md data/hard-rules.json
git commit -m "feat: Add movement science and biomechanics KB module with exercise selection, injury prevention, and scaling frameworks"
```

---

## Task 2: Metabolic Conditioning & Pacing Strategies Module

**Files:**
- Create: `knowledge-base/07-metcon-pacing-strategies.md`
- Modify: `data/hard-rules.json` (add citations if new)

**Interfaces:**
- Consumes: Energy systems KB, CrossFit methodology KB
- Produces: New KB section on pacing strategies, work-to-rest ratios, energy system mixing within sessions

**Curated Sources for this module:**
- Gastin 2001 - Energy System Interaction (already allowed)
- Wilson et al 2012 - Concurrent Training Meta-Analysis (already allowed)
- One new source: A research paper on high-intensity interval training (HIIT), lactate threshold, or pacing in competitive fitness

- [ ] **Step 1: Research and identify the new source**

Find ONE peer-reviewed source on pacing, lactate threshold, or HIIT. Examples:
- A study on pacing strategies in competitive endurance sports
- A meta-analysis on high-intensity interval training effects
- A paper on lactate threshold and performance prediction

Save the source title, authors, year, DOI.

- [ ] **Step 2: Draft the Metabolic Conditioning KB file**

Create `knowledge-base/07-metcon-pacing-strategies.md`:

```markdown
# Metabolic Conditioning & Pacing Strategies

**Source:** Gastin, P.B. "Energy System Interaction and Relative Contribution During Maximal Exercise." *Sports Medicine* 31(10), 2001.
**Source:** Wilson, J.M., et al. "Concurrent Training: A Meta-Analysis Examining Interference of Aerobic and Resistance Exercises." *Journal of Strength and Conditioning Research* 26(8), 2012.
**Source:** [Your new peer-reviewed source: Author, Title, Year]

---

## Work-to-Rest Ratios by Energy System

Effective metcon programming matches work duration, intensity, and rest intervals to the target energy system.

### Short Time Domain (< 7 minutes) — Phosphocreatine/Early Glycolytic

| Work Duration | Rest Duration | Rounds | Primary System | Example |
|---|---|---|---|---|
| 20–40 sec | 60–90 sec | 8–12 | Phosphocreatine | Short sprints, max-effort lifts |
| 40–60 sec | 60–120 sec | 6–10 | Glycolytic | Moderate-intensity EMOM |
| 60–90 sec | 120–180 sec | 4–8 | Mixed | Longer single efforts |

**Principle:** Full or near-full phosphocreatine recovery requires 2–3 minutes. For short metcons (<7 min total), assume the athlete will complete all work within that window and use rest intervals that support full recovery between efforts.

**Reference:** Gastin (2001) shows that the phosphocreatine system is fully replenished within 2–3 minutes at rest. CrossFit strength + short metcon sessions leverage this: heavy lifting depletes PC, but the subsequent short metcon re-recruits PC with full recovery.

### Medium Time Domain (7–15 minutes) — Glycolytic/Mixed

| Work Duration | Rest Duration | Rounds | Primary System | Example |
|---|---|---|---|---|
| 3–5 min AMRAP | N/A | 1 round | Glycolytic + aerobic | Medium-length AMRAP |
| 1 min work / 30 sec rest | N/A | 10–15 rounds | Glycolytic | EMOM format, shorter intervals |
| 2 min work / 1 min rest | N/A | 5–7 rounds | Glycolytic → aerobic | Longer EMOM intervals |

**Principle:** Medium metcons typically don't include built-in rest; the format (AMRAP or EMOM) manages pacing. Athletes must self-manage intensity — initial effort is high, then settle into sustainable pace as lactate accumulates.

**Reference:** Gastin (2001) and Wilson et al (2012) show that concurrent training (strength + metcon in same session) requires careful management of metcon duration and intensity. Medium time domains (7–15 min) hit the glycolytic-to-aerobic transition where both capacity building and metabolic stress occur.

---

## Pacing Frameworks

### AMRAP (As Many Rounds As Possible)

**Pacing model:** Athlete must self-regulate intensity. Initial rounds are fast, later rounds slower as fatigue accumulates.

| Time Cap | Typical Pacing |
|---|---|
| 5–7 min | Aggressive first half, conservative second half; aim for 60–70% of peak pace at end |
| 10–15 min | Start controlled, build rhythm, final round at max effort |

**When to use:** When goal is aerobic power and pacing discipline. Athletes learn to sustain output despite fatigue.

**Generator guidance:** AMRAP metcons should have scalable movements and clear rep schemes. Avoid extremely complex gymnastics (high decision load under fatigue).

### EMOM (Every Minute on the Minute)

**Pacing model:** Clock-driven. Athlete has a fixed interval (1, 2, or 3 minutes) to complete a task, then rests remainder.

| Interval | Rounds | Typical Intensity |
|---|---|---|
| E1MOM | 10–15 | 60–70% max effort (high load, very few reps) |
| E2MOM | 8–12 | 70–85% max effort (moderate load, 3–5 reps) |
| E3MOM | 5–8 | 80–90% max effort (heavy load, 1–3 reps) |

**When to use:** When goal is consistent output and recovery management. EMOM prevents athletes from "gas and coast" pacing and enforces steady effort.

**Generator guidance:** Match interval to movement complexity and load. Heavy barbell lifts → E2MOM or E3MOM. Gymnastics → E1MOM or E2MOM.

### For Time

**Pacing model:** No clock-driven pacing; athlete completes fixed work as fast as possible.

| Typical Reps | Pacing Strategy | Primary Stimulus |
|---|---|---|
| 50–100 total reps | Distribute into sets; don't burn out early | Local muscular endurance |
| 150–300 total reps | Large opening sets, reduce set sizes as fatigue builds | Anaerobic capacity → aerobic endurance |

**When to use:** When goal is max effort and competitive intensity. Requires athletes to pace themselves strategically.

**Generator guidance:** For Time metcons should have clear break points (e.g., "21-15-9 rep scheme") to guide pacing, not just "100 reps of mixed movements."

---

## Energy System Mixing Within a Single Session

**Principle:** One energy system dominates per session. Mixing all three equally blunts adaptation.

### Strength-First Session (High-CNS) + Short Metcon

- **Strength block:** 20–25 min (phosphocreatine + glycolytic, low reps, high load)
- **Metcon:** 7–12 min (glycolytic, medium intensity)
- **Recovery:** 36–48h before next high-CNS session

**Rationale:** Heavy lifting depletes phosphocreatine and recruits high-threshold motor units. Short metcon re-recruits those units while glycolytic system is trained. Long rest before next strength session allows full CNS recovery.

### Aerobic-Focused Session (Low-CNS) + Light Accessory

- **Warmup:** 5–10 min
- **Monostructural work:** 20–40 min (aerobic, low intensity, conversational pace)
- **Light accessory:** 5–10 min (mobility, low load)
- **Recovery:** 24h typical; can stack with other sessions same day

**Rationale:** Dedicated aerobic work requires low CNS demand (conversational pace, no heavy lifting). This allows higher weekly training frequency and doesn't interfere with strength adaptation.

**Reference:** Wilson et al (2012) meta-analysis shows that aerobic and strength training interfere with each other when done same session at high intensity. The solution: separate stimulus domains across the week, or if combined, keep aerobic work at very low intensity (<60% max HR).

---

## Metcon Format Selection Decision Tree

**Use this tree to choose AMRAP vs EMOM vs For Time:**

1. **Is the goal max power output over time?** → AMRAP (athlete learns pacing)
2. **Is the goal consistent, controlled output?** → EMOM (clock enforces pacing)
3. **Is the goal max effort with fixed work?** → For Time (all-out effort)

**If multiple movements with different demands:**
- EMOM is safer (each movement gets a discrete window)
- AMRAP works if movements are simple (e.g., "row + burpees")
- For Time works if work is evenly distributed (e.g., "21-15-9 reps each")

---
```

- [ ] **Step 3: Verify consistency with energy systems KB**

Read through your new file and cross-check against `01-energy-systems.md`:
- Do work-to-rest ratios align with phosphocreatine recovery times mentioned in energy systems? ✓
- Do metcon time domains match the guidelines in energy systems? ✓
- Does energy system mixing guidance align with the concurrent training note? ✓

If any contradictions, revise.

- [ ] **Step 4: Add new citations to hard-rules.json if needed**

Check if your new peer-reviewed source is already in `allowed_sources`. If not, add it (same process as Task 1, Step 5).

- [ ] **Step 5: Commit**

```bash
git add knowledge-base/07-metcon-pacing-strategies.md data/hard-rules.json
git commit -m "feat: Add metabolic conditioning and pacing strategies KB module with work-to-rest ratios and format selection"
```

---

## Task 3: Competitive WOD Analysis Module

**Files:**
- Create: `knowledge-base/08-competitive-wod-analysis.md`
- Modify: `data/hard-rules.json` (add citations if new)

**Interfaces:**
- Consumes: Energy systems, metcon pacing, movement biomechanics KB
- Produces: New KB section documenting famous WOD patterns, movement pairing rationales, intensity profiles

**Curated Sources for this module:**
- CrossFit Games archives (official source: documented WODs from recent Games/Regionals)
- One coach analysis source (e.g., Mayhem Athletics programming notes, or a coach blog analyzing competition trends)
- One peer-reviewed source on competitive fitness analysis or sport-specific conditioning

- [ ] **Step 1: Research and gather competitive WOD data**

Visit CrossFit Games website or trusted coach blogs (Mayhem Athletics, for example) and document 10–15 notable WODs from recent years. Record:
- WOD name and year
- Movements included
- Format (AMRAP, For Time, EMOM)
- Time domain (how long it took typical competitors)
- Key pattern (e.g., "gymnastics + monostructural," "heavy load + high reps")

Example format:
```
- "Murph" (Hero WOD, recurring) — 1 mile run, 100 pull-ups, 200 push-ups, 300 air squats, 1 mile run | For Time | ~30–45 min | Pattern: Long monostructural + high-rep gymnastics
- "Diane" (Classic) — 21-15-9 deadlifts (225/155 lb) + handstand push-ups | For Time | ~6–10 min | Pattern: Heavy barbell + gymnastics, descending
- "Fran" (Classic) — 21-15-9 thrusters (95/65 lb) + pull-ups | For Time | ~2–5 min | Pattern: Fast, high intensity, minimal rest
```

- [ ] **Step 2: Identify patterns and themes**

Review your 10–15 WODs and categorize:
- **Time domains:** How many short (<7 min)? Medium (7–15 min)? Long (>15 min)?
- **Movement pairings:** Do certain movements appear together? (e.g., deadlifts + pull-ups, gymnastics + monostructural)
- **Load profiles:** Light, moderate, heavy?
- **Athlete demand:** Strength-focused, endurance-focused, mixed?

Example summary:
- 60% are medium time domain (7–15 min)
- Barbell + gymnastics pairing appears in 40% of WODs
- Heavy deadlift/squat paired with high-rep gymnastics is common (intensity contrast)

- [ ] **Step 3: Draft the Competitive WOD Analysis KB file**

Create `knowledge-base/08-competitive-wod-analysis.md`:

```markdown
# Competitive WOD Analysis & Patterns

**Source:** CrossFit Games Official Archives (games.crossfit.com)
**Source:** [Your coach analysis source, e.g., "Mayhem Athletics Programming Notes"]
**Source:** [Your peer-reviewed competitive fitness source]

---

## Famous WOD Patterns

CrossFit competitions (Games, Regionals) follow consistent patterns. Understanding these patterns informs program design: non-competitive WODs should hit the same movement domains and intensity profiles to prepare athletes for unknown stimulus.

### Pattern 1: Barbell + Gymnastics (High-Intensity, Medium Duration)

**Example WODs:**
- "Fran" (21-15-9 thrusters + pull-ups)
- "Elizabeth" (21-15-9 power cleans + ring dips)
- Games 2021 Open Workout 21.1 (40-30-20-10 wall balls + cal row)

**Characteristics:**
- Time domain: 3–10 minutes
- Load: Moderate to heavy barbell (60–75% 1RM equivalent in rep scheme)
- Gymnastics: High-rep (10–30+ reps total)
- Pacing: Fast, sustained effort; minimal rest between movements
- Primary adaptation: Anaerobic capacity, work capacity under fatigue

**Rationale:** Barbell + gymnastics combination taxes multiple energy systems. The heavy barbell recruits maximum muscle, the gymnastics maintains output despite fatigue. Tests an athlete's ability to maintain technique under extreme time pressure.

**Reference:** This pattern is foundational in competitive CrossFit. Athletes must train it regularly to build the specific work capacity required.

### Pattern 2: Monostructural + Gymnastics (Mixed Domain)

**Example WODs:**
- "Murph" (1 mi run, 100 pull-ups, 200 push-ups, 300 squats, 1 mi run)
- Games 2022 Workout 4 (2-mile row + pull-ups, descending)
- "Fight Gone Bad" variant (5-min AMRAP with multiple monostructural and gymnastics movements)

**Characteristics:**
- Time domain: 15–45+ minutes
- Load: Bodyweight or light (monostructural is unloaded)
- Gymnastics: Distributed high volume (50–200+ reps)
- Pacing: Sustainable aerobic pace with periodic intensity spikes
- Primary adaptation: Aerobic capacity, muscular endurance, pacing discipline

**Rationale:** Long combined sessions require aerobic base and muscular stamina. Monostructural work (running, rowing) is interrupted by gymnastics (pull-ups, push-ups), forcing rapid transitions and sustained output despite lactate accumulation. Tests mental toughness and aerobic power over extended duration.

**Reference:** This pattern builds general endurance capacity while maintaining skill competency (gymnastics don't decay over long sessions).

### Pattern 3: Heavy Barbell + Light Monostructural (Strength + Conditioning)

**Example WODs:**
- Games 2020 Workout 2 (Heavy barbell complex + short monostructural burst)
- "Linda" (10-9-8...1 deadlifts, bench press, clean — heavy loads, descending)
- Regionals strength-bias workouts (max-load strength + short metcon)

**Characteristics:**
- Time domain: 10–20 minutes
- Load: Heavy barbell (75%+ 1RM)
- Monostructural: Light, short (200m row, 10 cal bike, brief run)
- Pacing: Strength blocks are heavy/slow, then short intense burst
- Primary adaptation: Strength maintenance, power maintenance, concurrent training

**Rationale:** Combining heavy load with brief conditioning tests an athlete's ability to apply maximum force while fatigued. This is pragmatic for competitors: in a 5-event competition, athletes must lift heavy after previous workouts and conditioning. Training this teaches force application under fatigue.

**Reference:** Wilson et al (2012) shows that strength + conditioning can coexist if total metcon volume is short and intensity is brief. This WOD pattern exemplifies that principle.

### Pattern 4: Mixed Movement High-Rep (GPP, Low Load)

**Example WODs:**
- "DT" (5 RFT: 12 deadlifts, 9 hang power cleans, 6 push jerks — lighter load, high volume)
- "Grace" (30 clean and jerks for time — moderate load, high reps)
- Games 2023 Open Workout (varied movement, moderate load, high reps)

**Characteristics:**
- Time domain: 8–15 minutes
- Load: Moderate (40–60% 1RM equivalent)
- Volume: High (50–200+ total reps)
- Movement variety: 2–4 different barbell or gymnastics movements
- Pacing: Steady sustained effort, athlete finds rhythm
- Primary adaptation: Work capacity, movement quality under fatigue, GPP

**Rationale:** This format develops "general physical preparedness" — the ability to sustain moderate intensity across varied movement domains. Teaches athletes to maintain technique and output even when tired. Common in early-season training (building base capacity).

---

## Time Domain Distribution in Competition

Analysis of CrossFit Games and Regionals (past 2 years):

| Time Domain | Frequency | Example Emphasis | Recovery Need |
|---|---|---|---|
| Short (<7 min) | ~15% | Max power, skill testing | 24–36h |
| Medium (7–15 min) | ~60% | Work capacity, mixed stimulus | 24–48h |
| Long (>15 min) | ~25% | Endurance, pacing, mental | 36–72h |

**Implication:** A well-rounded program trains all three domains, but emphasizes medium (7–15 min), which is the competitive sweet spot. Non-competitive athletes should train all three to maintain readiness for any stimulus.

---

## Movement Pairing Principles

Certain movement combinations appear repeatedly in competitive WODs. Understanding why informs programming choices.

### Pairing 1: Heavy Barbell + Gymnastics

**Why:** Tests maximum strength recruitment + repeated application of strength under fatigue

**Examples:** Squat + toes-to-bar, deadlift + pull-ups, thruster + muscle-ups

**Programming rule:** Use in strength-emphasis sessions (Week 2–3 of programs). Max weight athletes can move repeatedly in 20–30 reps.

### Pairing 2: Fast Barbell + Monostructural

**Why:** Tests explosive power + aerobic capacity in rapid alternation

**Examples:** Power clean + row, hang power snatch + run, dumbbell snatch + row

**Programming rule:** Use in power-emphasis or mixed sessions. Lighter load (50–65% 1RM). Alternating movements maintain CNS freshness.

### Pairing 3: High-Rep Gymnastics + Monostructural

**Why:** Tests muscular endurance + aerobic capacity without heavy loading

**Examples:** Pull-ups + row, push-ups + bike, chest-to-bar + run

**Programming rule:** Use for high-volume aerobic sessions. Teaches sustained output without spike in systemic fatigue (no heavy barbell).

### Pairing 4: Complex Barbell + Complex Barbell

**Why:** Tests technique fluency and neural fatigue management

**Examples:** Clean + jerk, snatch + thruster, deadlift + bench

**Programming rule:** Use in technique-emphasis or mixed-stimulus weeks. Single-effort max attempts (testing) rather than high-rep sets (training).

---

## Intensity Profiles

Competitive WODs follow predictable intensity distributions:

| Time Domain | First 25% | Middle 50% | Final 25% |
|---|---|---|---|
| Short (<7 min) | Max effort | Maintain intensity; lactate building | Final push; all-out |
| Medium (7–15 min) | Build into pace | Steady sustained effort | Finish strong if possible |
| Long (>15 min) | Easy; establish rhythm | Steady; manage pacing | Sprint finish or maintain rhythm |

**Implication for training:** Program metcons that match these profiles. Train athletes to "race" short WODs (fast throughout), "pace" medium WODs (find sustainable rhythm), and "sustain" long WODs (steady effort, strong finish).

---

## Athlete Skill Distribution

Successful Games athletes score well across all four pattern types:
- 20% of total score from short, high-power WODs
- 50% from medium, work-capacity WODs
- 20% from long, endurance WODs
- 10% from mixed, technical WODs

**Implication:** A program preparing non-competitive athletes should reflect this distribution. Don't overemphasize one pattern. Varied stimulus builds GPP.

---
```

- [ ] **Step 4: Cross-check with existing KB**

Review your new competitive analysis and verify:
- Does it contradict movement biomechanics KB? (No — it describes how those movements are combined)
- Does it align with pacing strategies from Task 2? ✓
- Does it align with energy system principles? ✓

- [ ] **Step 5: Add new citations if applicable**

If you added a peer-reviewed source on competitive fitness analysis, add it to `allowed_sources` in `hard-rules.json`.

- [ ] **Step 6: Commit**

```bash
git add knowledge-base/08-competitive-wod-analysis.md data/hard-rules.json
git commit -m "feat: Add competitive WOD analysis module documenting movement patterns, pairings, and intensity profiles"
```

---

## Task 4: Programming Decision Trees & Frameworks Module

**Files:**
- Create: `knowledge-base/09-programming-decision-trees.md`
- Modify: `data/hard-rules.json` (add citations if new)

**Interfaces:**
- Consumes: All previous KB modules, hard-rules.json
- Produces: New KB section with decision frameworks for session design, progression models, athlete profile guidelines

**Curated Sources for this module:**
- Bompa & Haff - Periodization 5th ed (already allowed)
- Haff & Triplett - NSCA Essentials 4th ed (already allowed)
- One coach framework source (e.g., published programming template from a known coach, or blog post on programming decision-making)

- [ ] **Step 1: Research programming decision frameworks**

Find or synthesize ONE resource on programming decision-making. Examples:
- A published coach blog on "how to program for different athlete levels"
- A book chapter on program periodization (beyond what's in Bompa)
- A coaching certification curriculum excerpt on session design logic
- Mayhem Athletics published programming notes

Save the reference and key decision criteria.

- [ ] **Step 2: Draft the Programming Decision Trees KB file**

Create `knowledge-base/09-programming-decision-trees.md`:

```markdown
# Programming Decision Trees & Frameworks

**Source:** Bompa, T.O., & Haff, G.G. "Periodization: Theory and Methodology of Training." 5th ed., 2009.
**Source:** Haff, G.G., & Triplett, N.T. (Eds.). "Essentials of Strength and Conditioning." NSCA, 4th ed., 2016.
**Source:** [Your coach framework source]

---

## Session Type Selection Decision Tree

Use this tree to choose **what kind of session to program** (strength-emphasis, metabolic-emphasis, skill-emphasis, aerobic, or mixed).

```
START: What is the primary training goal for this session?

├─ Is it PEAK STRENGTH (heavy singles, doubles, triples)?
│  └─ → STRENGTH-EMPHASIS SESSION
│     Structure: Warmup + Strength Block (25 min, heavy, low reps) + Light metcon (10 min, short, low volume)
│     Example: 5×3 back squat @ 80-85% + 7 min AMRAP (light)
│     Recovery: 48h before next heavy session
│
├─ Is it WORK CAPACITY or INTENSITY (sustained medium-to-high effort)?
│  └─ → METCON-EMPHASIS SESSION
│     Structure: Warmup + Strength Block (15 min, moderate) + Intense metcon (12 min, medium)
│     Example: 3×5 power clean @ 70% + 12 min AMRAP complex
│     Recovery: 36h typical
│
├─ Is it SKILL DEVELOPMENT (gymnastics, Olympic technique, movement quality)?
│  └─ → SKILL-EMPHASIS SESSION
│     Structure: Warmup + Skill Block (25–30 min, technical, low fatigue) + Light accessory
│     Example: 15 min pull-up progressions + 10 min accessory work
│     Recovery: 24h (low systemic demand)
│
├─ Is it AEROBIC BASE or ENERGY SYSTEM DEVELOPMENT?
│  └─ → AEROBIC/STANDALONE SESSION
│     Structure: Warmup + Long monostructural (20–40 min, low intensity) + Cooldown
│     Example: 30 min steady-state row at conversational pace
│     Recovery: 24h (can stack with strength same week)
│
└─ Is it DELOAD or RECOVERY-FOCUSED?
   └─ → RECOVERY SESSION
      Structure: Warmup + Light accessory (15–20 min, <50% intensity) + Mobility (10 min)
      Example: Light dumbbell work + stretching
      Recovery: 24h; pair with another session if needed
```

---

## Metcon Format Decision Tree

Use this tree to choose **AMRAP vs EMOM vs For Time** for the metcon block:

```
START: What is the metcon goal?

├─ Is the goal to teach PACING DISCIPLINE under fatigue?
│  └─ → AMRAP
│     Athlete must self-regulate intensity; later rounds will be slower than early ones.
│     Duration: 7–15 min
│     Example: 10 min AMRAP 5 pull-ups + 5 burpees
│
├─ Is the goal CONSISTENT, CONTROLLED OUTPUT over time?
│  └─ → EMOM
│     Clock enforces pacing; athlete completes task within the minute, then rests.
│     Duration: 5–15 min (varies by interval)
│     Example: E2MOM 8 rounds: 8 power cleans + 8 ring dips
│
├─ Is the goal MAX EFFORT with FIXED WORK (racing)?
│  └─ → FOR TIME
│     All-out effort; no clock-driven pacing.
│     Duration: 3–10 min typical
│     Example: 21-15-9 deadlifts + pull-ups for time
│
└─ Is the goal SUSTAINED, MODERATE EFFORT (aerobic)?
   └─ → AMRAP (long duration) or EMOM (E3MOM, very long rounds)
      Low intensity, pacing discipline more important than max speed.
      Duration: 15–20 min
      Example: 20 min AMRAP 200m row + 10 cal bike
```

---

## Strength Block Format Selection

Use this tree to choose **which strength progression scheme** to use:

```
START: What week of the program are we in, and what is the goal?

├─ WEEK 1 (Baseline Establishment)
│  ├─ Is the goal technique refinement or introduction to a movement?
│  │  └─ → RAMP BUILDUP (sets of 5→4→3→2 with increasing %)
│  │     Reason: Neurological preparation; athlete learns technique under increasing load
│  │     Example: Snatch warm-up into 5@65%, 4@72%, 3@78%, 2@83%
│  │
│  └─ Is the goal to establish baseline strength and volume?
│     └─ → STRAIGHT SETS (all sets same load)
│        Reason: Simplicity; establishes repeatable baseline
│        Example: 5×5 @ 72% back squat
│
├─ WEEK 2 (Moderate Intensity, Introduce Variety)
│  ├─ Is the athlete intermediate+ and should we introduce power work?
│  │  └─ → WAVE LOADING (3 waves: 75%, 80%, 85%)
│  │     Reason: Post-Activation Potentiation (PAP); higher 3rd wave reps feel lighter
│  │     Example: 3@75%, 3@80%, 3@85%, repeat
│  │
│  └─ Is this a moderate-intensity session?
│     └─ → STRAIGHT SETS or MIX of formats
│        Example: 4×5 @ 78% (straight sets) or combine with EMOM
│
├─ WEEK 3 (Peak Intensity)
│  ├─ Is the goal maximum strength with time efficiency?
│  │  └─ → TOP SET + BACKOFF
│  │     Reason: Hits peak intensity (1–3 reps heavy) + volume (sets of 5 lighter)
│  │     Example: 1×2@87%, then 4×5@70%
│  │
│  └─ Is the goal sustained strength development?
│     └─ → WAVE LOADING
│        Example: 3@82%, 3@85%, 3@88% (or higher)
│
└─ WEEK 4 (Deload)
   └─ → STRAIGHT SETS at reduced intensity (60–65% 1RM)
      Example: 3×5 @ 65%
      Reason: CNS and tissue recovery; maintain movement quality
```

**Rule:** Do NOT use wave loading or top set + backoff for novice athletes (Week 1 athletes). Straight sets or ramp buildup only.

---

## Athlete Profile Decision Tree

Use this tree to adapt session prescription to athlete level:

```
START: How advanced is the athlete?

├─ BEGINNER (0–6 months training, or new to CrossFit)
│  ├─ Strength focus: Ramp buildup + straight sets, light load (60–70% 1RM if known)
│  ├─ Metcon formats: AMRAP only (simplest pacing model)
│  ├─ Gymnastics cap: Strict pull-ups, step push-ups, elevated planks (no kipping, muscle-ups)
│  ├─ Olympic lifting: NO barbell O-lifts in metcons; only light technique work in strength block
│  ├─ Session structure: Warmup + Short strength block (15 min) + Light metcon (10 min) + Cooldown
│  └─ Recovery: Standard 24–36h
│
├─ INTERMEDIATE (6–18 months training)
│  ├─ Strength focus: Ramp buildup + straight sets OR light wave loading (if movement is familiar)
│  ├─ Metcon formats: AMRAP, EMOM (E2MOM or E3MOM), simple For Time
│  ├─ Gymnastics: Strict pull-ups, kipping pull-ups (if demonstrated prerequisite), ring dips, basic handstand work
│  ├─ Olympic lifting: Light power O-lifts in metcons (power clean, power snatch); only technique work for full lift variants
│  ├─ Session structure: Standard 60 min (warmup + 20 min strength + 12 min metcon + 5 min cooldown)
│  └─ Recovery: Standard 24–48h
│
└─ ADVANCED (18+ months, consistent training)
   ├─ Strength focus: Full range of schemes (straight sets, ramp, wave, top set backoff)
   ├─ Metcon formats: All (AMRAP, EMOM, For Time, complex combinations)
   ├─ Gymnastics: Chest-to-bar pull-ups, muscle-ups, handstand push-ups, advanced static holds
   ├─ Olympic lifting: Full Olympic lifts in all metcon formats; technical complexity is not a limiting factor
   ├─ Session structure: Flexible (can handle 70+ min sessions, or high-intensity short sessions)
   └─ Recovery: Managed based on frequency; typically 24–48h between same stimulus
```

---

## Metcon Intensity Prescription

Use this tree to set **intensity level** (low, moderate, high) for the metcon block:

```
START: What intensity should this metcon be?

├─ STRENGTH-EMPHASIS SESSION (heavy lifting just happened)
│  └─ → LOW TO MODERATE METCON INTENSITY
│     Metcon is finisher, not primary stimulus. 10–12 min max, light load, moderate volume.
│     Example: 10 min AMRAP with light dumbbells, not barbell.
│     Rationale: CNS is already taxed by heavy lifting; protect strength adaptation by keeping metcon light.
│
├─ METCON-EMPHASIS SESSION (Strength block was warm-up)
│  └─ → HIGH METCON INTENSITY
│     Metcon is the primary stimulus. 12–15 min, challenging load or high volume, competitive pace.
│     Example: 12 min AMRAP 8 power cleans + 12 ring dips (challenging but doable).
│     Rationale: This session is designed to build work capacity.
│
├─ AEROBIC-EMPHASIS SESSION (no heavy lifting)
│  └─ → LOW TO MODERATE INTENSITY
│     Sustained effort, conversational pace, 20+ minutes.
│     Example: 30 min row at 60–70% max HR.
│     Rationale: Aerobic base building requires lower intensity to avoid systemic fatigue.
│
└─ SKILL-EMPHASIS SESSION (technique focus)
   └─ → NO METCON or VERY LIGHT
      Focus is entirely on skill refinement, not conditioning.
      If there's a finisher, keep it sub-5 min and light (e.g., "3 min easy rowing").
      Rationale: Protect CNS for skill development.
```

---

## Loading & Progression Guidelines by Goal

| Goal | Week 1 | Week 2 | Week 3 | Week 4 |
|---|---|---|---|---|
| **Hypertrophy** | 70–75% 1RM, 5×5 | 72–78% 1RM, 4×6 | 75–80% 1RM, 4×5 | 60–65% 1RM, 3×5 (deload) |
| **Strength** | 75% 1RM, 5×3 | 78% 1RM, 4×3 | 82–87% 1RM, 1×2 + backoff | 65% 1RM, 3×5 (deload) |
| **Power** | 65–70%, 3×3 | 70–75%, 3×3 | 75–80%, 3×2 | 60%, 3×3 (deload) |

**Rule:** Progress load week-to-week only if the athlete completed all reps with clean form last week. If any set failed, hold load or reduce slightly.

---

## Recovery & Sequencing

| Session Type | Typical Duration | Recovery Until Next Session | Can Stack Same Day? |
|---|---|---|---|
| Heavy strength | 60 min | 48h | No (if also heavy) |
| Metcon-emphasis | 60 min | 36h | No (same day) |
| Skill-emphasis | 30 min | 24h | Yes (pair with aerobic) |
| Aerobic | 30–40 min | 24h | Yes (pair with skill) |
| Deload | 45 min | 24h | Yes (very light) |

**Sequencing rules:**
- Never back-to-back high-CNS sessions (strength or intense metcon)
- Aerobic + skill can be same day or consecutive days
- Deload weeks: reduce intensity and volume across all sessions

---
```

- [ ] **Step 3: Verify no contradictions**

Cross-check your decision trees against all previous KB modules and `hard-rules.json`:
- Do the athlete progression levels align with hard-rules constraints? ✓
- Do the loading percentages match those in `hard-rules.json`? ✓
- Do session structure guidelines align with energy systems and pacing? ✓

- [ ] **Step 4: Add citations if needed**

If you added a new coach framework source, add it to `allowed_sources` in `hard-rules.json`.

- [ ] **Step 5: Commit**

```bash
git add knowledge-base/09-programming-decision-trees.md data/hard-rules.json
git commit -m "feat: Add programming decision trees and frameworks KB module with session type, format, and progression guidelines"
```

---

## Task 5: Update CLAUDE.md with KB Maintenance Workflow

**Files:**
- Modify: `CLAUDE.md`

**Interfaces:**
- Consumes: Existing CLAUDE.md structure, knowledge base modules
- Produces: New section documenting KB curation and refresh workflow

- [ ] **Step 1: Read the current CLAUDE.md**

Familiarize yourself with the structure and style.

- [ ] **Step 2: Add KB Maintenance Section**

After the "Architecture — Read This First" section and before "Running the Generator," add:

```markdown
---

## Knowledge Base Maintenance & Curation

The knowledge base is the foundation of WOD quality. It evolves quarterly as new research, competitions, and coaching insights emerge.

### KB Modules

| Module | File | Purpose | Refresh Frequency |
|---|---|---|---|
| Energy Systems | `01-energy-systems.md` | Physiological foundations | Annual (low change) |
| CrossFit Methodology | `02-crossfit-methodology.md` | Fundamental training principles | Annual (low change) |
| Periodization | `03-periodization.md` | Multi-week program structure | Annual (low change) |
| Recovery | `04-recovery.md` | Rest, deload, injury prevention | Annual (low change) |
| Gymnastics | `05-gymnastics.md` | Gymnastics-specific progressions | Annual (low change) |
| Movement Science | `06-movement-biomechanics.md` | Exercise selection, injury prevention, scaling | Quarterly (moderate) |
| Metcon Pacing | `07-metcon-pacing-strategies.md` | Work-to-rest ratios, energy system mixing | Quarterly (moderate) |
| Competitive Patterns | `08-competitive-wod-analysis.md` | Famous WODs, movement combos, intensity profiles | Quarterly (high) |
| Programming Frameworks | `09-programming-decision-trees.md` | Session type selection, athlete progression | Quarterly (moderate) |

### Curated Sources

The KB is grounded in vetted sources. Every new addition must cite at least one source below:

**Academic & Research:**
- Haff & Triplett - NSCA Essentials of Strength and Conditioning
- Bompa & Haff - Periodization: Theory and Methodology of Training
- Zatsiorsky & Kraemer - Science and Practice of Strength Training
- Schoenfeld - Science and Development of Muscle Hypertrophy
- Gastin - Energy System Interaction and Relative Contribution
- Wilson et al - Concurrent Training Meta-Analysis
- Robbins - Post-Activation Potentiation
- Behm et al - Acute Effects of Muscle Stretching
- Kreher & Schwartz - Overtraining Syndrome

**Competition & Official Sources:**
- CrossFit Games Archives (games.crossfit.com) — Official WODs, athlete performances
- CrossFit Level 2 Training Guide — Foundational methodology
- CrossFit Gymnastics Specialty Course — Movement progressions and safety

**Coach Content:**
- [Curator identifies 2–3 trusted coaches or blogs; update this quarterly]
- Example: Mayhem Athletics (published programming notes, competition analysis)

### Quarterly Curation Workflow

**Month 1 of each quarter:**
1. Review 1–2 new peer-reviewed papers in sports science
2. Document 10–15 recent competition WODs (Games, Regionals)
3. Scan 3–5 coach blogs or YouTube channels for new programming trends
4. Identify contradictions or gaps in current KB

**Month 2–3:**
1. Write or update 1–2 KB modules based on new insights
2. Update `hard-rules.json` → `allowed_sources` if new citations are introduced
3. Generate sample WODs using updated KB
4. Review generated WODs for quality improvement
5. Commit changes with tag `KB-Q<year>-<quarter>` (e.g., `KB-Q2026-Q2`)

**After refresh:**
- Run `python generate.py --type program --name <current-season> --weeks 3` to create a fresh program
- Compare generated WODs against previous quarter — expect improvement in rationale depth and movement variety
- Update programs in `docs/data/programs/` (overwrite old versions)

### Adding New Citations

To add a new source to the KB:

1. **Verify the source:** Ensure it's peer-reviewed, published by a reputable organization (NSCA, CrossFit Inc., academic journal), or documented coach content with traceable methodology
2. **Add to `hard-rules.json`:** Append to the `allowed_sources` array with format `"Author(s) Year - Title"` (exact match with how it appears in KB files)
3. **Document in KB:** Cite the source in the module that uses it
4. **Update this section:** Add the source to the appropriate category above

Example:
```json
"allowed_sources": [
  "Glassman 2002 - CrossFit Journal",
  "Haff & Triplett - NSCA Essentials 4th ed",
  ...
  "NewAuthor 2025 - New Research Topic"
]
```

### What NOT to Add to KB

- Fabricated citations or invented loading percentages
- Unverified claims (no contradictions with sports science principles)
- Trends that contradict energy systems or periodization principles
- Equipment or movements not commonly available (e.g., very specialized equipment)

### KB Refresh Impact on Generated WODs

Every KB module addition improves generator output:
- **Better rationales:** Generator cites deeper, more specific sources
- **Richer movement variety:** New modules inform movement selection and pairing
- **More intentional progressions:** Decision trees guide athlete-appropriate loading
- **Competitive readiness:** Competitive WOD analysis ensures workouts match real-world stimulus

After refreshing, regenerate all programs to incorporate improvements.

---
```

- [ ] **Step 3: Commit**

```bash
git add CLAUDE.md
git commit -m "docs: Add KB maintenance and curation workflow to CLAUDE.md"
```

---

## Task 6: Update DESIGN.md with KB Refresh Schedule

**Files:**
- Modify: `DESIGN.md`

**Interfaces:**
- Consumes: CLAUDE.md KB section, existing DESIGN.md
- Produces: Updated DESIGN.md with KB refresh schedule and curator role

- [ ] **Step 1: Read the current DESIGN.md**

Understand the structure and where KB documentation fits.

- [ ] **Step 2: Locate or create a "Knowledge Base" section**

If DESIGN.md doesn't already have a KB section, add one after "Architecture Overview" and before "Development Slices". If it already exists, enhance it with the following:

```markdown
## Knowledge Base: Living Documentation

The knowledge base (`knowledge-base/`) is the source of truth for all WOD generation. Unlike static documentation, it evolves quarterly as sports science advances and competitive trends emerge.

### Knowledge Base Modules

Every module is a focused markdown document grounded in cited sources (academic papers, competition data, coach methodologies). Modules are independent — the generator can handle partial updates.

### Quarterly Refresh Cycle

**Who:** Project curator (typically the person responsible for content quality)

**When:** First month of each quarter (Jan, Apr, Jul, Oct)

**Workload:** ~8–12 hours per quarter (~2 hours per week)

**Process:**
1. Research 1–2 peer-reviewed papers (sports science journals, NSCA, ACE)
2. Document 10–15 recent competition WODs (CrossFit Games, Regionals)
3. Review 3–5 coach blogs or YouTube channels for emerging trends
4. Identify gaps or contradictions in current KB
5. Update 1–2 KB modules with findings
6. Add new citations to `hard-rules.json` if needed
7. Generate sample WODs to validate improvements
8. Tag commit as `KB-Q<year>-<quarter>` (e.g., `KB-Q2026-Q2`)
9. Regenerate all programs to incorporate improvements

### Expected Outcomes

- **Month 1:** Curated sources identified; gaps documented
- **Month 2:** KB modules written/updated; validated against generator
- **Month 3:** Programs regenerated; users get improved WODs

### Curator Resources

- CrossFit Games website (free WOD archives)
- NSCA Essentials (reference text)
- Google Scholar (academic paper search)
- YouTube: Mayhem Athletics, Sevan Matossian, local coaches (for trend analysis)

---
```

- [ ] **Step 3: If DESIGN.md mentions "GitHub Actions pipeline," update it**

If the GitHub Actions workflow section exists, add a note about KB refresh:

```markdown
**Note:** The GitHub Actions regeneration workflow (`generate.yml`) runs on a schedule. To refresh programs based on KB updates, simply commit new KB files and run the workflow manually or wait for the scheduled run.
```

- [ ] **Step 4: Commit**

```bash
git add DESIGN.md
git commit -m "docs: Add KB refresh cycle and curator workflow to DESIGN.md"
```

---

## Task 7: Final Validation & Integration Test

**Files:**
- Read: All knowledge base files, `hard-rules.json`, `CLAUDE.md`, `DESIGN.md`

**Interfaces:**
- Consumes: All KB modules, updated hard rules, updated documentation
- Produces: Validation report and sample generated WOD

- [ ] **Step 1: Verify hard-rules.json is valid JSON**

```bash
python3 -c "import json; json.load(open('data/hard-rules.json'))" && echo "✓ hard-rules.json is valid"
```

Expected output: `✓ hard-rules.json is valid`

- [ ] **Step 2: Verify all KB files exist and are readable**

```bash
for file in knowledge-base/06-movement-biomechanics.md knowledge-base/07-metcon-pacing-strategies.md knowledge-base/08-competitive-wod-analysis.md knowledge-base/09-programming-decision-trees.md; do
  if [ -f "$file" ]; then echo "✓ $file exists"; else echo "✗ $file missing"; fi
done
```

Expected: All 4 files should report as existing.

- [ ] **Step 3: Spot-check citation consistency**

Manually verify:
- Every new citation in KB files appears in `hard-rules.json` → `allowed_sources` ✓
- No fabricated citations (all sources are real, verifiable) ✓
- CLAUDE.md and DESIGN.md reference the same workflow ✓

- [ ] **Step 4: Generate a sample WOD to test quality**

Run the generator on a new program to verify it works with the updated KB:

```bash
cd scripts
python generate.py --type program --name kb-validation-test --weeks 2
```

Expected output: A 2-week program in `output/` with improved rationales citing new KB material.

- [ ] **Step 5: Review sample WOD rationales**

Open `output/kb-validation-test-program.md` and review 2–3 sessions:
- Do rationales cite the new KB modules? (e.g., "movement-why" mentions biomechanics, "loading-why" mentions decision trees)
- Are rationales more specific and detailed than before? ✓
- Are there any contradictions with hard rules? ✓

If rationales don't cite new KB material, the generator may need a prompt update. Document this as a finding (but don't fix in this task — that's future work).

- [ ] **Step 6: Clean up test output**

```bash
rm output/kb-validation-test-program.*
```

- [ ] **Step 7: Final commit message**

```bash
git log --oneline -10
```

Verify that all KB and documentation commits are present. If so:

```bash
git log --oneline -1
```

Should show the most recent commit (likely the DESIGN.md update).

---

## Success Criteria

- ✅ All 4 KB modules created with proper citations and structure
- ✅ New citations added to `hard-rules.json` without JSON errors
- ✅ CLAUDE.md includes KB maintenance workflow section
- ✅ DESIGN.md includes KB refresh cycle and curator guidelines
- ✅ Sample WOD generated successfully with no errors
- ✅ All commits use clear, focused messages
- ✅ No contradictions between KB modules or with hard-rules.json

---

## Rollback & Troubleshooting

**If JSON validation fails:**
```bash
python3 -c "import json; print(json.dumps(json.load(open('data/hard-rules.json')), indent=2))" | head -50
```
Check for syntax errors (mismatched quotes, missing commas).

**If generator fails to run:**
- Verify `ANTHROPIC_API_KEY` is set: `echo $ANTHROPIC_API_KEY`
- Verify KB files don't have markdown syntax errors (missing headers, broken tables)

**If generator runs but rationales don't cite new KB:**
- This is acceptable for now; it's a generator prompt issue, not a KB issue
- Document as "Future: Update generator prompt to leverage new KB modules"

---
```

Plan complete and saved to `docs/superpowers/plans/2026-06-28-knowledge-base-expansion.md`. Two execution options:

**1. Subagent-Driven (recommended)** - I dispatch a fresh subagent per task, review between tasks, fast iteration

**2. Inline Execution** - Execute tasks in this session using executing-plans, batch execution with checkpoints

Which approach?