# Spanish Translation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement full Spanish language support with auto-detect browser language, manual picker, and dual-variant data serving.

**Architecture:** Create `docs/i18n/es.json` for UI strings + movement names, update HTML with `data-i18n` attributes, implement language detection and switching in app.js, extend generator with `--language` flag, and generate Spanish programs/WODs to `docs/data-es/`.

**Tech Stack:** Vanilla JavaScript (no framework), static JSON files, Python generation script, localStorage for persistence.

## Global Constraints

- Zero runtime API calls (static data only)
- Browser language auto-detection via `navigator.language`
- Spanish locale code: `es` (not regional variants like `es-MX`)
- All UI strings stored in `docs/i18n/es.json`
- All movement/exercise names sourced from `data/movement-library.json`
- Acronyms (AMRAP, EMOM, etc.) kept in English in both languages
- Sports science citations preserved as-is; rationale text translated
- Spanish programs/WODs generated to `docs/data-es/` (mirror structure of `docs/data/`)
- Full locale support ready for future language expansion (e.g., `es-MX` variants, French, Portuguese)

---

## File Structure

**New Files:**
- `docs/i18n/es.json` — Spanish UI strings + movement names (human-maintained)
- `docs/i18n/en.json` — English UI strings (optional reference, mirrors existing HTML)
- `docs/data-es/programs/` — Spanish program variants (generated)
- `docs/data-es/wods/` — Spanish WOD variants (generated)

**Modified Files:**
- `docs/index.html` — Add `data-i18n` attributes to UI text nodes, add language picker to header
- `docs/assets/js/app.js` — Add i18n initialization, language detection, language switching, data path logic
- `scripts/generate.py` — Add `--language` flag, language-aware output paths, Spanish prompt logic
- `generate-all.sh` — Add Spanish generation commands

---

## Tasks

### Task 1: Create `docs/i18n/es.json` with all UI strings

**Files:**
- Create: `docs/i18n/es.json`

**Interfaces:**
- Consumes: Existing HTML button/label text, acronym expansions from app.js
- Produces: Keyed object with all UI strings for use in `app.js` via `i18n.strings[key]`

This is the translation source file. Extract every static UI string from `docs/index.html` and `docs/assets/js/app.js`, key it semantically, and provide Spanish translations.

- [ ] **Step 1: Extract all UI strings from index.html**

Review `docs/index.html` and list every user-visible text node (buttons, labels, headings, descriptions). Example strings to capture:
- "Loading Woddy..."
- "Woddy"
- "Science-backed CrossFit programming"
- "Start Program"
- "Structured 2-4 week training cycle with progressive loading"
- "Daily WOD"
- "Drop-in workout, no commitment"
- "← Back"
- "Choose a Program"
- "Program Duration"
- "How many weeks do you want to commit?"
- "2 Weeks", "3 Weeks", "4 Weeks"
- "Training Frequency"
- "How many days per week can you train?"
- "3 Days/Week", "4 Days/Week", "5 Days/Week"
- "Continue"
- "Program"
- "0/0 trainings"
- "↻ Reset"
- "Training"
- "Today's Workout"
- "Equipment Needed"
- "Select a program or WOD to get started"
- "🔬 Why This Session?"
- "Start Session"
- "Select a Category"
- "Full Body"
- "Upper Body"
- "Lower Body"
- "Cardio"
- "Strength"
- "Active Warmup"
- "Round 3/8"
- "PLAY"
- "PAUSE"
- "RESET"
- "← PREV BLOCK"
- "NEXT BLOCK →"
- "FINISH"
- "← Change Category"
- "Next: Strength block"
- "Loading WOD..."

- [ ] **Step 2: Extract all acronym expansions from app.js**

From `docs/assets/js/app.js`, lines 38-50, extract acronyms:
- `CARs` → `Controlled Articular Rotations`
- `ROM` → `Range of Motion`
- `CNS` → `Central Nervous System`
- `AMRAP` → `As Many Rounds As Possible`
- `EMOM` → `Every Minute On the Minute`
- `RPE` → `Rate of Perceived Exertion`
- `C2B` → `Chest to Bar`
- `1RM` → `One-Rep Max`
- `RFD` → `Rate of Force Development`
- `RIR` → `Reps In Reserve`

**Note:** These stay in English (standard in Spanish fitness communities).

- [ ] **Step 3: Extract all 68 movement names from data/movement-library.json**

Read `data/movement-library.json` and extract every movement name. These need Spanish translations. Example movements:
- Back Squat
- Bench Press
- Deadlift
- Pull-Up
- Push-Up
- Dumbbell
- Kettlebell
- etc.

(There are 68 total. The spec lists a subset; extract all 68.)

- [ ] **Step 4: Create docs/i18n/es.json with semantic keys**

Create a JSON file with structure:

```json
{
  "app.loading": "Cargando Woddy...",
  "app.title": "Woddy",
  "app.subtitle": "Programación de CrossFit respaldada por ciencia",
  "onboarding.startProgram": "Comenzar Programa",
  "onboarding.startProgramDesc": "Ciclo de entrenamiento estructurado de 2-4 semanas con carga progresiva",
  "onboarding.dailyWod": "WOD Diario",
  "onboarding.dailyWodDesc": "Entrenamiento drop-in, sin compromiso",
  "nav.back": "← Atrás",
  "programs.chooseProgram": "Elegir un Programa",
  "programs.duration": "Duración del Programa",
  "programs.durationQuestion": "¿Cuántas semanas deseas comprometerte?",
  "programs.frequency": "Frecuencia de Entrenamiento",
  "programs.frequencyQuestion": "¿Cuántos días por semana puedes entrenar?",
  "programs.weeks.2": "2 Semanas",
  "programs.weeks.3": "3 Semanas",
  "programs.weeks.4": "4 Semanas",
  "programs.frequency.3": "3 Días/Semana",
  "programs.frequency.4": "4 Días/Semana",
  "programs.frequency.5": "5 Días/Semana",
  "programs.reset": "↻ Reiniciar",
  "programs.trainings": "entrenamientos",
  "btn.continue": "Continuar",
  "btn.start": "Comenzar Sesión",
  "btn.finish": "TERMINAR",
  "btn.play": "REPRODUCIR",
  "btn.pause": "PAUSA",
  "btn.reset": "REINICIAR",
  "btn.prevBlock": "← BLOQUE ANTERIOR",
  "btn.nextBlock": "SIGUIENTE BLOQUE →",
  "btn.changeCategory": "← Cambiar Categoría",
  "btn.nextWod": "Siguiente WOD",
  "equipment.title": "Equipo Necesario",
  "session.title": "Entrenamiento de Hoy",
  "session.details": "Detalles del Entrenamiento",
  "rationale.title": "🔬 ¿Por Qué Esta Sesión?",
  "placeholder.selectProgram": "Selecciona un programa o WOD para comenzar",
  "timer.block": "Bloque Activo",
  "timer.roundInfo": "Ronda",
  "timer.nextBlock": "Siguiente:",
  "wod.selectCategory": "Seleccionar Categoría",
  "wod.fullBody": "Cuerpo Completo",
  "wod.upperBody": "Tren Superior",
  "wod.lowerBody": "Tren Inferior",
  "wod.strength": "Fuerza",
  "wod.cardio": "Cardio",
  "wod.loading": "Cargando WOD...",
  "acronyms.AMRAP": "As Many Rounds As Possible",
  "acronyms.EMOM": "Every Minute On the Minute",
  "acronyms.RPE": "Rate of Perceived Exertion",
  "acronyms.C2B": "Chest to Bar",
  "acronyms.1RM": "One-Rep Max",
  "acronyms.RFD": "Rate of Force Development",
  "acronyms.RIR": "Reps In Reserve",
  "acronyms.CARs": "Controlled Articular Rotations",
  "acronyms.ROM": "Range of Motion",
  "acronyms.CNS": "Central Nervous System",
  "movements.backSquat": "Sentadilla Trasera",
  "movements.benchPress": "Press de Banca",
  "movements.deadlift": "Levantamiento de Tierra",
  "movements.pullUp": "Dominada",
  "movements.pushUp": "Flexión",
  "movements.dumbbell": "Mancuerna",
  "movements.kettlebell": "Kettlebell",
  "movements.barbell": "Barra",
  "movements.plates": "Discos",
  "movements.rack": "Rack de Pesas",
  "movements.pullUpBar": "Barra de Dominadas",
  "movements.rowingMachine": "Remadora",
  "movements.jumpRope": "Cuerda para Saltar",
  "movements.boxJump": "Salto a la Caja",
  "movements.burpee": "Burpee",
  "movements.wallBall": "Lanzamiento al Muro",
  "movements.kettlebellSwing": "Swing de Kettlebell",
  "movements.doubleUnder": "Doble Salto",
  "movements.muscleUp": "Muscle Up",
  "movements.handstandWalk": "Caminata en Posición Invertida",
  "movements.medBallClean": "Clean de Balón Medicinal",
  "movements.inchworm": "Inchworm",
  "movements.hipCircles": "Círculos de Cadera",
  "movements.catCow": "Cat-Cow",
  "movements.hipFlexorStretch": "Estiramiento de Flexores de Cadera",
  "movements.worldsGreatestStretch": "Estiramiento Más Genial del Mundo",
  "movements.airSquat": "Sentadilla Aérea",
  "movements.goodMorning": "Good Morning",
  "movements.bandedPullApart": "Abducción con Banda"
}
```

Include all 68 movements (extract from `data/movement-library.json`). Use camelCase keys like `movements.movementName`.

- [ ] **Step 5: Validate completeness**

Ensure every key from step 1 has an entry. Check that:
- All UI buttons/labels have entries
- All 68 movements are present
- All 10 acronyms are present
- No placeholders or "TBD" entries

- [ ] **Step 6: Commit**

```bash
git add docs/i18n/es.json
git commit -m "i18n: add Spanish translation strings (UI + movements)"
```

---

### Task 2: Add `data-i18n` attributes to HTML and create language picker

**Files:**
- Modify: `docs/index.html`

**Interfaces:**
- Consumes: `i18n.strings` object from app.js (populated in Task 4)
- Produces: HTML elements with `data-i18n` attributes; language picker dropdown in header

Update all static UI text nodes to use `data-i18n` attributes so app.js can swap them based on language. Add language picker to the header.

- [ ] **Step 1: Add `data-i18n` attributes to onboarding section**

Modify `docs/index.html`, lines 60-73 (onboarding):

```html
<h1 data-i18n="app.title">Woddy</h1>
<p data-i18n="app.subtitle">Science-backed CrossFit programming</p>

<div class="onboarding-options">
  <button id="btn-start-program" class="option-card">
    <h3 data-i18n="onboarding.startProgram">Start Program</h3>
    <p data-i18n="onboarding.startProgramDesc">Structured 2-4 week training cycle with progressive loading</p>
  </button>

  <button id="btn-random-wod-start" class="option-card">
    <h3 data-i18n="onboarding.dailyWod">Daily WOD</h3>
    <p data-i18n="onboarding.dailyWodDesc">Drop-in workout, no commitment</p>
  </button>
</div>
```

- [ ] **Step 2: Add `data-i18n` to header and navigation**

Modify lines 78-97 (header):

```html
<header id="app-header" class="app-header hidden">
  <button id="btn-back" class="btn-back hidden" data-i18n="nav.back">← Back</button>
  <div class="header-center">
    <svg class="logo logo-header" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 240 120">
      <!-- SVG code unchanged -->
    </svg>
    <h1 data-i18n="app.title">Woddy</h1>
  </div>
  <select id="language-picker" aria-label="Select language">
    <option value="en">English</option>
    <option value="es">Español</option>
  </select>
</header>
```

Place the language picker after the logo, aligned right via CSS (to be added in later styling task).

- [ ] **Step 3: Add `data-i18n` to program selection view**

Modify lines 100-107 (program selection):

```html
<section id="view-programs" class="view hidden">
  <div class="programs-container">
    <h2 data-i18n="programs.chooseProgram">Choose a Program</h2>
    <div class="programs-list" id="programs-list">
      <!-- Populated by JavaScript -->
    </div>
  </div>
</section>
```

- [ ] **Step 4: Add `data-i18n` to program configuration view**

Modify lines 110-139 (program config):

```html
<section id="view-program-config" class="view hidden">
  <div class="programs-container">
    <button id="btn-back-from-config" class="btn-nav" style="margin-bottom: 32px;" data-i18n="nav.back">← Back</button>
    <h2 id="config-program-name">Program Name</h2>

    <div class="config-section">
      <h3 data-i18n="programs.duration">Program Duration</h3>
      <p class="config-subtitle" data-i18n="programs.durationQuestion">How many weeks do you want to commit?</p>
      <div class="duration-options" id="duration-options">
        <button class="duration-btn" data-weeks="2" data-i18n="programs.weeks.2">2 Weeks</button>
        <button class="duration-btn" data-weeks="3" data-i18n="programs.weeks.3">3 Weeks</button>
        <button class="duration-btn" data-weeks="4" data-i18n="programs.weeks.4">4 Weeks</button>
      </div>
    </div>

    <div class="config-section">
      <h3 data-i18n="programs.frequency">Training Frequency</h3>
      <p class="config-subtitle" data-i18n="programs.frequencyQuestion">How many days per week can you train?</p>
      <div class="frequency-options" id="frequency-options">
        <button class="frequency-btn" data-freq="3" data-i18n="programs.frequency.3">3 Days/Week</button>
        <button class="frequency-btn" data-freq="4" data-i18n="programs.frequency.4">4 Days/Week</button>
        <button class="frequency-btn" data-freq="5" data-i18n="programs.frequency.5">5 Days/Week</button>
      </div>
    </div>

    <div class="config-actions">
      <button id="btn-continue-config" class="btn-primary btn-large" disabled data-i18n="btn.continue">Continue</button>
    </div>
  </div>
</section>
```

- [ ] **Step 5: Add `data-i18n` to trainings list view**

Modify lines 142-155 (trainings list):

```html
<section id="view-trainings" class="view hidden">
  <div class="trainings-header">
    <div class="trainings-header-top">
      <h2 id="program-title">Program</h2>
      <button id="btn-reset-program" class="btn-reset" title="Reset program and start over" data-i18n="programs.reset">↻ Reset</button>
    </div>
    <div class="progress-info">
      <span id="trainings-completed">0/0 trainings</span>
    </div>
  </div>
  <div class="trainings-list" id="trainings-list">
    <!-- Populated by JavaScript -->
  </div>
</section>
```

- [ ] **Step 6: Add `data-i18n` to program details view**

Modify lines 157-211 (program view, session):

```html
<section id="view-program" class="view hidden">
  <!-- Program Progress -->
  <div class="program-progress">
    <button id="btn-back-to-trainings" class="btn-nav" data-i18n="nav.back">← Back</button>
    <h2 id="program-name">Training</h2>
    <div class="progress-info">
      <span id="session-meta" class="session-meta">Training</span>
    </div>
  </div>
  <div class="session-card">
    <div class="session-header">
      <h2 id="session-title" data-i18n="session.title">Today's Workout</h2>
      <span id="session-details" class="session-meta" data-i18n="session.details">Training Details</span>
    </div>

    <!-- Equipment List -->
    <div id="equipment-section" class="equipment-section collapsed">
      <button class="section-toggle" data-target="equipment-list">
        <span data-i18n="equipment.title">Equipment Needed</span>
        <span class="toggle-icon">▼</span>
      </button>
      <ul id="equipment-list" class="equipment-list hidden">
        <li>Barbell</li>
        <li>Plates</li>
        <li>Pull-up bar</li>
      </ul>
    </div>

    <!-- Workout Blocks -->
    <div id="workout-blocks" class="workout-blocks">
      <!-- Blocks will be populated by JavaScript -->
      <div class="block-placeholder">
        <p data-i18n="placeholder.selectProgram">Select a program or WOD to get started</p>
      </div>
    </div>

    <!-- Rationale (Collapsed by default) -->
    <div id="rationale-section" class="rationale-section collapsed">
      <button class="section-toggle" data-target="rationale-content">
        <span data-i18n="rationale.title">🔬 Why This Session?</span>
        <span class="toggle-icon">▼</span>
      </button>
      <div id="rationale-content" class="rationale-content hidden">
        <!-- Populated by JavaScript -->
      </div>
    </div>

    <!-- Start Button -->
    <div class="session-actions">
      <button id="btn-start-session" class="btn-primary btn-large" data-i18n="btn.start">Start Session</button>
    </div>
  </div>
</section>
```

- [ ] **Step 7: Add `data-i18n` to WOD view**

Modify lines 214-235 (WOD mode):

```html
<section id="view-wod" class="view hidden">
  <!-- Category Selection (shown when no WOD loaded) -->
  <div id="wod-category-selector" class="wod-category-selector">
    <h2 data-i18n="wod.selectCategory">Select a Category</h2>
    <div class="wod-filters">
      <button class="filter-btn" data-category="full-body" data-i18n="wod.fullBody">Full Body</button>
      <button class="filter-btn" data-category="upper-body" data-i18n="wod.upperBody">Upper Body</button>
      <button class="filter-btn" data-category="lower-body" data-i18n="wod.lowerBody">Lower Body</button>
      <button class="filter-btn" data-category="cardio" data-i18n="wod.cardio">Cardio</button>
      <button class="filter-btn" data-category="strength" data-i18n="wod.strength">Strength</button>
    </div>
  </div>

  <!-- WOD Display (shown when WOD loaded) -->
  <div id="wod-display" class="session-card hidden">
    <div class="wod-header-controls">
      <button id="btn-change-category" class="btn-back-category" data-i18n="btn.changeCategory">← Change Category</button>
    </div>
    <p class="empty-state" data-i18n="wod.loading">Loading WOD...</p>
  </div>
</section>
```

- [ ] **Step 8: Add `data-i18n` to timer overlay**

Modify lines 237-286 (timer):

```html
<div id="timer-overlay" class="timer-overlay hidden">
  <div class="timer-container">
    <!-- Block Header -->
    <div class="timer-header">
      <h3 id="timer-block-name" data-i18n="timer.block">Active Warmup</h3>
      <span id="timer-round-info" data-i18n="timer.roundInfo">Round 3/8</span>
    </div>

    <!-- Main Clock -->
    <div id="timer-clock" class="timer-clock">
      <span id="timer-display">00:00</span>
    </div>

    <!-- Progress Bar -->
    <div class="timer-progress-container">
      <div id="timer-progress-bar" class="timer-progress-bar"></div>
    </div>

    <!-- Block Content -->
    <div id="timer-movements" class="timer-movements">
      <p>Inchworm × 5</p>
      <p>Hip circles × 10 each</p>
      <p>Banded pull-apart × 15</p>
    </div>

    <!-- Next Block Preview -->
    <div id="timer-next" class="timer-next">
      <span data-i18n="timer.nextBlock">Next:</span>
      <span id="timer-next-name"> Strength block</span>
    </div>

    <!-- Timer Controls -->
    <div class="timer-controls">
      <button id="btn-play" class="btn-timer" data-i18n="btn.play">PLAY</button>
      <button id="btn-pause" class="btn-timer" data-i18n="btn.pause">PAUSE</button>
      <button id="btn-reset" class="btn-timer" data-i18n="btn.reset">RESET</button>
    </div>

    <!-- Block Navigation -->
    <div class="timer-nav">
      <button id="btn-prev-block" class="btn-nav-block" data-i18n="btn.prevBlock">← PREV BLOCK</button>
      <button id="btn-next-block" class="btn-nav-block" data-i18n="btn.nextBlock">NEXT BLOCK →</button>
    </div>

    <!-- Finish Session Button -->
    <div class="timer-actions">
      <button id="btn-stop" class="btn-secondary" data-i18n="btn.finish">FINISH</button>
    </div>
  </div>
</div>
```

- [ ] **Step 9: Update loading state**

Modify line 37 (loading):

```html
<p data-i18n="app.loading">Loading Woddy...</p>
```

- [ ] **Step 10: Validate all `data-i18n` attributes match es.json keys**

Search `docs/index.html` for all `data-i18n` attributes and confirm each key exists in `docs/i18n/es.json` from Task 1. Check:
- No typos in attribute values
- All values follow the key format (e.g., `app.title`, `btn.start`)
- No keys are missing from es.json

- [ ] **Step 11: Commit**

```bash
git add docs/index.html
git commit -m "markup: add data-i18n attributes for language switching"
```

---

### Task 3: Implement i18n system in app.js (initialization, detection, switching)

**Files:**
- Modify: `docs/assets/js/app.js`

**Interfaces:**
- Consumes: `docs/i18n/es.json` (loaded via fetch), localStorage for language persistence
- Produces:
  - `i18n` global object with properties: `language` (string), `strings` (object)
  - Functions: `detectBrowserLanguage()`, `initI18n()`, `applyTranslations()`, `setupLanguagePicker()`, `getDataPath(type, filename)` → returns path string

Add i18n infrastructure to support language detection, string loading, and language switching.

- [ ] **Step 1: Add i18n state object after acronym expansions**

In `docs/assets/js/app.js`, after line 50 (after `acronymExpansions`), add:

```javascript
//=== Internationalization ===
const i18n = {
  language: localStorage.getItem('language') || 'en',
  strings: {},
};

function detectBrowserLanguage() {
  const browserLang = navigator.language.split('-')[0]; // 'es', 'en', etc.
  return ['es', 'en'].includes(browserLang) ? browserLang : 'en';
}

async function loadTranslations(language) {
  try {
    const response = await fetch(`./i18n/${language}.json`);
    if (!response.ok) throw new Error(`Failed to load ${language}.json`);
    i18n.strings = await response.json();
  } catch (e) {
    console.error('Failed to load translations:', e);
    i18n.language = 'en'; // Fallback
    if (language !== 'en') {
      return loadTranslations('en'); // Retry with English
    }
  }
}

function applyTranslations() {
  document.querySelectorAll('[data-i18n]').forEach(el => {
    const key = el.getAttribute('data-i18n');
    if (i18n.strings[key]) {
      el.textContent = i18n.strings[key];
    } else {
      console.warn(`Missing translation key: ${key}`);
      el.textContent = key; // Fallback to key itself
    }
  });
}

function getDataPath(type, filename) {
  const dir = i18n.language === 'es' ? 'data-es' : 'data';
  return `./${dir}/${type}/${filename}.json`;
}

function setupLanguagePicker() {
  const picker = document.getElementById('language-picker');
  if (!picker) {
    console.warn('Language picker element not found');
    return;
  }

  picker.value = i18n.language;
  picker.addEventListener('change', async (e) => {
    i18n.language = e.target.value;
    localStorage.setItem('language', i18n.language);

    // Reload translations and reapply
    await loadTranslations(i18n.language);
    applyTranslations();

    // Optionally reload data if a program/WOD is currently loaded
    // This is handled in the data loader functions
    console.log(`Language switched to: ${i18n.language}`);
  });
}
```

- [ ] **Step 2: Update initialization in DOMContentLoaded**

Find the `DOMContentLoaded` event listener (starts at line 70), and modify the setup sequence to initialize i18n first:

```javascript
document.addEventListener('DOMContentLoaded', async () => {
  console.log('🚀 App initializing...');

  try {
    console.log('  Initializing i18n...');
    // On first load, detect browser language if not set
    if (!localStorage.getItem('language')) {
      i18n.language = detectBrowserLanguage();
      localStorage.setItem('language', i18n.language);
    }
    await loadTranslations(i18n.language);
    applyTranslations();

    console.log('  Loading progress...');
    loadProgress();

    console.log('  Setting up onboarding...');
    setupOnboarding();

    console.log('  Setting up navigation...');
    setupNavigation();

    console.log('  Setting up program flow...');
    setupProgramFlow();

    console.log('  Setting up collapsibles...');
    setupCollapsibles();

    console.log('  Setting up session start...');
    setupSessionStart();

    console.log('  Setting up WOD mode...');
    setupWodMode();

    console.log('  Setting up language picker...');
    setupLanguagePicker();

    console.log('✅ All setup complete');

    document.getElementById('loading').classList.add('hidden');
    document.getElementById('main-container').classList.remove('hidden');

    // Check if there's a saved program and load it
    // ... rest of initialization
```

- [ ] **Step 3: Update data loading functions to use getDataPath()**

Find the `loadProgram()` function (should be in the program flow section). Update it to use language-aware paths:

```javascript
async function loadProgram(programId) {
  try {
    const path = getDataPath('programs', programId);
    console.log(`Loading program from: ${path}`);
    const response = await fetch(path);
    if (!response.ok) throw new Error(`Failed to load ${programId}`);

    const data = await response.json();
    state.currentProgram = data;
    renderProgram(data);
  } catch (e) {
    console.error('Error loading program:', e);
    showError('Failed to load program');
  }
}
```

Find `loadWod()` or equivalent WOD loading function:

```javascript
async function loadWod(category) {
  try {
    const filename = `wods-${category}`;
    const path = getDataPath('wods', filename);
    console.log(`Loading WOD from: ${path}`);
    const response = await fetch(path);
    if (!response.ok) throw new Error(`Failed to load WOD: ${category}`);

    const data = await response.json();
    // WOD rendering logic
    renderWod(data, category);
  } catch (e) {
    console.error('Error loading WOD:', e);
    showError('Failed to load WOD');
  }
}
```

- [ ] **Step 4: Test language switching manually**

Do NOT commit yet. Manually test:
1. Open `docs/index.html` in browser
2. Check that English loads by default (or Spanish if browser locale is `es`)
3. Check that `i18n.strings` has content (open DevTools console and type `i18n.strings`)
4. Change language picker from English to Español
5. Verify all `data-i18n` text updates on screen
6. Refresh page; verify language persists in localStorage

Expected behavior:
- Language persists across page reloads
- All UI text translates correctly
- No console errors

- [ ] **Step 5: Commit**

```bash
git add docs/assets/js/app.js
git commit -m "feat: add i18n system with language detection and switching"
```

---

### Task 4: Update generator script to support `--language` flag

**Files:**
- Modify: `scripts/generate.py`

**Interfaces:**
- Consumes: `--language` CLI argument (default: `en`)
- Produces: JSON output to `output/` (English) or `output-es/` (Spanish); ready to copy to `docs/data/` or `docs/data-es/`

Add language support to the generation pipeline so Spanish variants can be generated.

- [ ] **Step 1: Read generate.py and understand current flow**

Open `scripts/generate.py` and identify:
- The main() function entry point
- The argument parser (argparse or similar)
- How the prompt is constructed
- Where the output path is determined
- The call_claude() function

Understand the current structure before modifying.

- [ ] **Step 2: Add --language argument to CLI parser**

Find the argument parser section (likely uses argparse). Add:

```python
parser.add_argument('--language',
                    choices=['en', 'es'],
                    default='en',
                    help='Language for generation (en: English, es: Spanish)')
```

- [ ] **Step 3: Modify output directory logic**

Find where the output directory is set (likely early in main()). Update to account for language:

```python
# After parsing language argument
language = args.language
if language == 'es':
    output_dir = 'output-es'
else:
    output_dir = 'output'

os.makedirs(output_dir, exist_ok=True)
```

- [ ] **Step 4: Modify the system prompt for Spanish generation**

Find where the system prompt is constructed for Claude (the knowledge base + hard rules prompt). It should look something like:

```python
def call_claude(prompt):
    system_prompt = [
        {
            "type": "text",
            "text": f"You are an expert CrossFit coach...\n\n{knowledge_base_content}\n\n{hard_rules_content}",
            "cache_control": {"type": "ephemeral"}
        }
    ]
    # ... rest of API call
```

Modify the system prompt to include language instruction:

```python
def call_claude(prompt, language='en'):
    language_instruction = ""
    if language == 'es':
        language_instruction = "\n\nIMPORTANT: All output must be in Spanish. Write naturally in Spanish, not translated. Movement names, descriptions, and rationales should all be in proper Spanish. Keep acronyms (AMRAP, EMOM, RPE, etc.) in English."

    system_prompt = [
        {
            "type": "text",
            "text": f"You are an expert CrossFit coach...\n\n{knowledge_base_content}\n\n{hard_rules_content}{language_instruction}",
            "cache_control": {"type": "ephemeral"}
        }
    ]
    # ... rest of API call
```

Update all calls to `call_claude()` to pass the language:

```python
# In main(), instead of:
data = call_claude(prompt)

# Use:
data = call_claude(prompt, language=args.language)
```

- [ ] **Step 5: Update output file paths**

Find where JSON is written to disk (likely `json.dump(data, open(...))`). Update:

```python
# Before: output_path = f'output/back-in-shape-2w.json'
# After:
output_path = os.path.join(output_dir, f'back-in-shape-2w.json')

# Before: md_path = f'output/back-in-shape-2w.md'
# After:
md_path = os.path.join(output_dir, f'back-in-shape-2w.md')
```

- [ ] **Step 6: Test Spanish generation**

Run a test generation for Spanish:

```bash
source venv/bin/activate
export ANTHROPIC_API_KEY="sk-ant-api03-..."
python3 scripts/generate.py --type wod --count 1 --category cardio --language es
```

Expected output:
- Creates `output-es/` directory if it doesn't exist
- Generates `output-es/wods-cardio.json` with Spanish content
- No errors in stderr

Verify the JSON contains Spanish text (sample a movement name or rationale).

- [ ] **Step 7: Commit**

```bash
git add scripts/generate.py
git commit -m "feat: add --language flag to generator for Spanish output"
```

---

### Task 5: Create `docs/data-es/` directory structure and generate Spanish content

**Files:**
- Create: `docs/data-es/programs/` (directory)
- Create: `docs/data-es/wods/` (directory)
- Create: Spanish program and WOD JSON files

**Interfaces:**
- Consumes: Modified `generate.py` from Task 4, `docs/i18n/es.json` from Task 1
- Produces: Spanish JSON files in `docs/data-es/programs/` and `docs/data-es/wods/`, ready to serve to frontend

Generate all Spanish variants and organize them.

- [ ] **Step 1: Create directory structure**

```bash
mkdir -p docs/data-es/programs
mkdir -p docs/data-es/wods
```

- [ ] **Step 2: Generate Spanish 2-week program**

```bash
source venv/bin/activate
export ANTHROPIC_API_KEY="sk-ant-api03-..."
python3 scripts/generate.py --type program --name back-in-shape --weeks 2 --language es
```

Expected: Creates `output-es/back-in-shape-2w.json` with Spanish content.

- [ ] **Step 3: Generate all Spanish WODs (5 categories)**

```bash
python3 scripts/generate.py --type wod --count 5 --category full-body --language es
python3 scripts/generate.py --type wod --count 5 --category upper-body --language es
python3 scripts/generate.py --type wod --count 5 --category lower-body --language es
python3 scripts/generate.py --type wod --count 5 --category strength --language es
python3 scripts/generate.py --type wod --count 5 --category cardio --language es
```

Expected: Creates `output-es/wods-*.json` files for each category.

- [ ] **Step 4: Copy generated files to docs/data-es/**

```bash
cp output-es/back-in-shape-2w.json docs/data-es/programs/
cp output-es/wods-*.json docs/data-es/wods/
```

- [ ] **Step 5: Verify structure**

```bash
ls -R docs/data-es/
```

Expected output:
```
docs/data-es/:
programs  wods

docs/data-es/programs:
back-in-shape-2w.json

docs/data-es/wods:
wods-cardio.json
wods-full-body.json
wods-lower-body.json
wods-strength.json
wods-upper-body.json
```

- [ ] **Step 6: Spot-check Spanish content**

Open one file (e.g., `docs/data-es/wods/wods-cardio.json`) and verify:
- Session titles are in Spanish (not English)
- Movement names are in Spanish
- Rationale text is in Spanish
- Acronyms (AMRAP, EMOM) are in English
- JSON is valid (no syntax errors)

Example expected format:
```json
{
  "wods": [
    {
      "id": "cardio-1",
      "title": "Ronda Rápida de Cardio",
      "description": "Un AMRAP de 12 minutos con movimientos de cardio intensos",
      ...
    }
  ]
}
```

- [ ] **Step 7: Commit**

```bash
git add docs/data-es/
git commit -m "data: add Spanish program and WOD variants"
```

---

### Task 6: Update generate-all.sh to include Spanish generation

**Files:**
- Modify: `generate-all.sh`

**Interfaces:**
- Consumes: Modified `generate.py` with `--language` flag
- Produces: Shell script that generates both English and Spanish variants in one run

Simplify future generation by automating Spanish variants.

- [ ] **Step 1: View current generate-all.sh**

Open `generate-all.sh` and understand the current structure.

- [ ] **Step 2: Add Spanish generation commands**

After the English generation section, add:

```bash
echo ""
echo "🌍 SPANISH VARIANTS (1 program + 5 WOD categories)"
echo ""

echo "Generating Spanish program..."
python3 scripts/generate.py --type program --name back-in-shape --weeks 2 --language es
cp output-es/back-in-shape-2w.json docs/data-es/programs/
echo "✅ 2-week Spanish program generated"
echo ""

echo "Generating Spanish WODs..."
python3 scripts/generate.py --type wod --count 5 --category full-body --language es
cp output-es/wods-full-body.json docs/data-es/wods/
echo "✅ Full-body Spanish WODs generated"

python3 scripts/generate.py --type wod --count 5 --category upper-body --language es
cp output-es/wods-upper-body.json docs/data-es/wods/
echo "✅ Upper-body Spanish WODs generated"

python3 scripts/generate.py --type wod --count 5 --category lower-body --language es
cp output-es/wods-lower-body.json docs/data-es/wods/
echo "✅ Lower-body Spanish WODs generated"

python3 scripts/generate.py --type wod --count 5 --category strength --language es
cp output-es/wods-strength.json docs/data-es/wods/
echo "✅ Strength Spanish WODs generated"

python3 scripts/generate.py --type wod --count 5 --category cardio --language es
cp output-es/wods-cardio.json docs/data-es/wods/
echo "✅ Cardio Spanish WODs generated"
echo ""
```

Add this before the final "All generations complete" message.

- [ ] **Step 2: Update final summary**

Update the final output to show both languages:

```bash
echo "=============================="
echo "🎉 All generations complete!"
echo ""
echo "📊 English files:"
ls -lh docs/data/programs/*.json docs/data/wods/*.json | awk '{print "  " $9 " (" $5 ")"}'
echo ""
echo "📊 Spanish files:"
ls -lh docs/data-es/programs/*.json docs/data-es/wods/*.json 2>/dev/null | awk '{print "  " $9 " (" $5 ")"}' || echo "  (Spanish files not yet generated)"
```

- [ ] **Step 3: Commit**

```bash
git add generate-all.sh
git commit -m "build: update generate-all.sh to include Spanish variants"
```

---

### Task 7: Add basic CSS for language picker styling

**Files:**
- Modify: `docs/assets/css/app.css`

**Interfaces:**
- Consumes: Language picker `<select>` element in HTML from Task 2
- Produces: Styled language picker that fits in the header

Add minimal CSS to style the language picker in the header.

- [ ] **Step 1: Find header styling in app.css**

Open `docs/assets/css/app.css` and find the `.app-header` class. It should exist around the header section.

- [ ] **Step 2: Add language picker styles**

After the `.app-header` class definition, add:

```css
/* Language Picker */
#language-picker {
  position: absolute;
  right: 20px;
  top: 50%;
  transform: translateY(-50%);
  padding: 8px 12px;
  background-color: #1a1a1a;
  color: #c9b89d;
  border: 1px solid #c9b89d;
  border-radius: 4px;
  font-family: inherit;
  font-size: 14px;
  cursor: pointer;
}

#language-picker:hover {
  background-color: #2a2a2a;
}

#language-picker:focus {
  outline: 2px solid #c9b89d;
  outline-offset: 2px;
}

#language-picker option {
  background-color: #1a1a1a;
  color: #c9b89d;
}
```

- [ ] **Step 2: Make header position relative**

Ensure the `.app-header` has `position: relative` so absolute positioning of the picker works:

```css
.app-header {
  position: relative;
  /* ... existing styles ... */
}
```

- [ ] **Step 3: Test styling**

Do NOT commit. Open browser and check:
1. Language picker appears in header, aligned right
2. Picker is visible and clickable
3. Colors match the app theme (dark background, tan text)
4. Hover and focus states work

- [ ] **Step 4: Commit**

```bash
git add docs/assets/css/app.css
git commit -m "style: add language picker styling to header"
```

---

### Task 8: Final integration test and validation

**Files:**
- None modified (testing only)

**Interfaces:**
- Consumes: All previous tasks' outputs
- Produces: Validation checklist confirming full Spanish support works end-to-end

Test the complete Spanish translation flow without code changes.

- [ ] **Step 1: Full flow test — English to Spanish**

1. Open `docs/index.html` in browser (or live server)
2. Check that app loads in English (default)
3. Verify onboarding screen shows English text:
   - "Woddy" (app title)
   - "Science-backed CrossFit programming"
   - "Start Program"
   - "Daily WOD"
4. Click language picker, select "Español"
5. Verify all UI text changes to Spanish:
   - "Woddy" → "Woddy" (unchanged, as expected)
   - "Science-backed CrossFit programming" → "Programación de CrossFit respaldada por ciencia"
   - "Start Program" → "Comenzar Programa"
   - "Daily WOD" → "WOD Diario"
6. Refresh page (Cmd+R / Ctrl+R)
7. Verify language persists (still in Spanish)
8. Check browser DevTools → Application → LocalStorage, confirm `language: es` is set

- [ ] **Step 2: Program flow in Spanish**

1. Still in Spanish, click "Comenzar Programa"
2. Verify "Elegir un Programa" heading in Spanish
3. Select a program (e.g., "Back in Shape")
4. Verify configuration page shows Spanish:
   - "Duración del Programa"
   - "¿Cuántas semanas deseas comprometerte?"
   - "Frecuencia de Entrenamiento"
   - "¿Cuántos días por semana puedes entrenar?"
   - "Continuar" button
5. Select duration and frequency, click "Continuar"
6. Verify program loads with Spanish content:
   - Session titles in Spanish
   - Movement names in Spanish
   - Equipment list in Spanish

- [ ] **Step 3: WOD flow in Spanish**

1. Go back to onboarding (Cmd+R or Back button)
2. Still in Spanish, click "WOD Diario"
3. Verify "Seleccionar Categoría" heading
4. Verify category buttons:
   - "Cuerpo Completo"
   - "Tren Superior"
   - "Tren Inferior"
   - "Fuerza"
   - "Cardio"
5. Click a category (e.g., "Cardio")
6. Verify WOD loads with Spanish content
7. Click "Comenzar Sesión"
8. Verify timer overlay shows Spanish:
   - Button labels: "REPRODUCIR", "PAUSA", "REINICIAR", "TERMINAR"
   - Block info: "Ronda", "Siguiente:"

- [ ] **Step 4: Language switch persistence test**

1. Change language to English via picker
2. Navigate to a program, select options, start a session
3. Change language to Spanish
4. Navigate back — verify language was retained and all content is Spanish
5. Refresh page — verify Spanish persists

- [ ] **Step 5: Console validation**

Open DevTools console and run:

```javascript
// Check i18n state
console.log(i18n.language);  // Should output: 'es' or 'en'
console.log(Object.keys(i18n.strings).length);  // Should be ~130+ keys
console.log(i18n.strings['app.title']);  // Should output: 'Woddy' (same in both)
console.log(i18n.strings['onboarding.startProgram']);  // Should output: 'Comenzar Programa'
```

Expected output:
```
es
138
Woddy
Comenzar Programa
```

- [ ] **Step 6: Data path validation**

In console, run:

```javascript
// Test data path logic
console.log(getDataPath('programs', 'back-in-shape-2w'));
// If language is 'es', should output: ./data-es/programs/back-in-shape-2w.json
// If language is 'en', should output: ./data/programs/back-in-shape-2w.json
```

- [ ] **Step 7: Spot-check generated Spanish files**

Manually open a few Spanish JSON files and verify:
- `docs/data-es/programs/back-in-shape-2w.json`:
  - Session titles in Spanish
  - Movement names in Spanish
  - Rationale text in Spanish
- `docs/data-es/wods/wods-cardio.json`:
  - WOD titles in Spanish
  - Movement descriptions in Spanish
  - No untranslated English sections

- [ ] **Step 8: Check for console errors**

Open DevTools console in both English and Spanish modes. Verify:
- No JavaScript errors
- No 404s for missing i18n files
- No warnings about missing `data-i18n` keys

Expected: Clean console with only `✅ SW registered` and `✅ All setup complete` messages.

- [ ] **Step 9: Mobile responsiveness check**

Test on mobile (DevTools device emulation or physical device):
1. Load app in Spanish
2. Verify language picker is accessible and clickable
3. Verify text is readable (no layout shifts)
4. Verify timer overlay works in Spanish

- [ ] **Step 10: Document validation checklist**

No code changes. Just verify all requirements from the spec are met:
- [ ] Auto-detect browser language (Spanish speakers default to es)
- [ ] Language picker in header (English/Español)
- [ ] All UI strings translated via `docs/i18n/es.json`
- [ ] All movement names translated
- [ ] Dual data variants: `docs/data/` (English) + `docs/data-es/` (Spanish)
- [ ] Language choice persisted in localStorage
- [ ] Data path logic uses correct language-aware paths
- [ ] Spanish programs and WODs generated and in place
- [ ] No runtime API calls (all static)
- [ ] Acronyms in English in both languages
- [ ] Sports science citations preserved

- [ ] **Step 11: Final confirmation**

If all checks pass, you're done. Document any issues found and create GitHub issues if needed. No commit required for this task (it's testing only).

---

## Spec Coverage Check

✅ **Directory Structure** — Task 5 creates `docs/data-es/` with programs and WODs
✅ **UI Strings (`docs/i18n/es.json`)** — Task 1 creates and Task 2 integrates via `data-i18n` attributes
✅ **Movement Names** — Task 1 includes all 68 movements in `es.json`
✅ **Generated Content** — Tasks 4 & 5 add `--language` flag and generate Spanish variants
✅ **Runtime Switching** — Task 3 implements language detection, picker, and data path switching
✅ **Header Picker** — Task 2 adds picker, Task 7 styles it
✅ **localStorage Persistence** — Task 3 implements `localStorage.getItem/setItem` for language
✅ **Fallback & Error Handling** — Task 3 includes fallback to English on missing translations
✅ **Performance** — No new performance concerns (static JSON)
✅ **Future Expansion** — Architecture supports additional languages without changes
✅ **Generator Updates** — Task 4 modifies `generate.py`, Task 6 updates `generate-all.sh`
✅ **Testing** — Task 8 validates end-to-end flows

---

## Execution Options

Plan is complete and saved to `docs/superpowers/plans/2026-06-28-spanish-translation-implementation.md`.

**Two execution options:**

1. **Subagent-Driven (recommended)** — I dispatch a fresh subagent per task, review work between tasks, faster iteration and isolation
2. **Inline Execution** — Execute tasks sequentially in this session with checkpoints for review

Which approach would you prefer?
