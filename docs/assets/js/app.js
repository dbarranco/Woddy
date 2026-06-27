// WODie - Sport-Technical CrossFit PWA

//=== State ===
const state = {
  // Programs
  availablePrograms: [],
  currentProgramId: null,
  currentProgram: null,

  // Trainings
  currentTrainingIndex: 0,
  completedTrainings: [],

  // Timer
  timerActive: false,
  timerRunning: false,
  timerSeconds: 0,
  timerInterval: null,
  wakeLock: null,

  // WODs
  wodPools: {}, // {category: {wods: [...]}}
  currentWod: null,
  currentCategory: null
};

//=== Service Worker ===
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('./sw.js')
    .then(reg => console.log('✅ SW registered'))
    .catch(err => console.error('❌ SW failed:', err));
}

//=== Init ===
document.addEventListener('DOMContentLoaded', async () => {
  loadProgress();
  setupOnboarding();
  setupNavigation();
  setupProgramFlow();
  setupCollapsibles();
  setupSessionStart();
  setupWodMode();

  document.getElementById('loading').classList.add('hidden');
  document.getElementById('main-container').classList.remove('hidden');
});

//=== Onboarding ===
function setupOnboarding() {
  document.getElementById('btn-start-program').addEventListener('click', () => {
    document.getElementById('view-onboarding').classList.add('hidden');
    document.getElementById('app-header').classList.remove('hidden');
    showProgramsSelection();
  });

  document.getElementById('btn-random-wod-start').addEventListener('click', () => {
    document.getElementById('view-onboarding').classList.add('hidden');
    document.getElementById('app-header').classList.remove('hidden');
    document.getElementById('view-wod').classList.remove('hidden');
  });
}

//=== Program Flow ===
function setupProgramFlow() {
  // Load available programs (for now, just back-in-shape in different durations)
  state.availablePrograms = [
    { id: 'back-in-shape-2w', name: 'Back in Shape', description: '2-week progressive return to training program', weeks: 2 },
    { id: 'back-in-shape-3w', name: 'Back in Shape', description: '3-week progressive return to training program', weeks: 3 },
    { id: 'back-in-shape-4w', name: 'Back in Shape', description: '4-week progressive return to training program', weeks: 4 }
  ];

  // Setup back buttons
  document.getElementById('btn-back-to-programs').addEventListener('click', showProgramsSelection);
  document.getElementById('btn-back-to-trainings').addEventListener('click', showTrainingsList);
}

function showProgramsSelection() {
  // Hide all other views
  document.querySelectorAll('.view').forEach(v => v.classList.add('hidden'));
  document.getElementById('view-programs').classList.remove('hidden');

  // Render programs
  const programsList = document.getElementById('programs-list');
  programsList.innerHTML = state.availablePrograms.map(prog => `
    <div class="program-card" data-program-id="${prog.id}">
      <h3>${prog.name} ${prog.weeks}w</h3>
      <p>${prog.description}</p>
    </div>
  `).join('');

  // Add click handlers
  programsList.querySelectorAll('.program-card').forEach(card => {
    card.addEventListener('click', () => {
      const programId = card.getAttribute('data-program-id');
      loadProgramAndShowTrainings(programId);
    });
  });
}

async function loadProgramAndShowTrainings(programId) {
  try {
    const response = await fetch(`./data/programs/${programId}.json`);
    const data = await response.json();
    state.currentProgramId = programId;
    state.currentProgram = data.program;
    state.currentTrainingIndex = 0;

    showTrainingsList();
    console.log('✅ Program loaded:', programId);
  } catch (error) {
    console.error('❌ Failed to load program:', error);
  }
}

function showTrainingsList() {
  if (!state.currentProgram) return;

  // Hide all other views
  document.querySelectorAll('.view').forEach(v => v.classList.add('hidden'));
  document.getElementById('view-trainings').classList.remove('hidden');

  // Update header
  document.getElementById('program-title').textContent = state.currentProgram.name;

  // Filter out rest days and get trainings only
  const trainings = state.currentProgram.sessions.filter(s => !s.is_rest_day);
  const completed = state.completedTrainings.filter(id => trainings.map(t => t.id).includes(id)).length;
  document.getElementById('trainings-completed').textContent = `${completed}/${trainings.length} trainings`;

  // Render trainings list
  const trainingsList = document.getElementById('trainings-list');
  trainingsList.innerHTML = trainings.map((training, index) => {
    const isCompleted = state.completedTrainings.includes(training.id);
    return `
      <div class="training-item ${isCompleted ? 'completed' : ''}" data-training-index="${index}">
        <div>
          <h4>${training.title}</h4>
          <p>Training ${index + 1}</p>
        </div>
      </div>
    `;
  }).join('');

  // Add click handlers
  trainingsList.querySelectorAll('.training-item').forEach((item, index) => {
    item.addEventListener('click', () => {
      loadAndShowTraining(index);
    });
  });
}

function loadAndShowTraining(trainingIndex) {
  const trainings = state.currentProgram.sessions.filter(s => !s.is_rest_day);
  const training = trainings[trainingIndex];

  // Find the actual index in the sessions array
  const actualIndex = state.currentProgram.sessions.indexOf(training);
  state.currentTrainingIndex = actualIndex;

  // Hide all other views
  document.querySelectorAll('.view').forEach(v => v.classList.add('hidden'));
  document.getElementById('view-program').classList.remove('hidden');

  loadSession(actualIndex);
}

function loadSession(index) {
  const session = state.currentProgram.sessions[index];
  state.currentSessionIndex = index;

  document.getElementById('session-title').textContent = session.title;
  document.getElementById('session-meta').textContent = `Week ${session.week}, Day ${session.day}`;

  renderEquipment(session.equipment);
  renderWorkoutBlocks(session.blocks);
  renderRationale(session.rationale, 'rationale-content');
}

//=== Progress Tracking ===
function loadProgress() {
  const saved = localStorage.getItem('wodie_progress');
  if (saved) {
    state.completedTrainings = JSON.parse(saved);
  }
}

function saveProgress() {
  localStorage.setItem('wodie_progress', JSON.stringify(state.completedTrainings));
}

function markSessionComplete() {
  // Only mark as complete if in program mode
  if (!state.currentProgram) {
    return;
  }

  const trainingId = state.currentProgram.sessions[state.currentSessionIndex].id;
  if (!state.completedTrainings.includes(trainingId)) {
    state.completedTrainings.push(trainingId);
    saveProgress();

    // Refresh the trainings list to show completed status
    if (state.currentProgram) {
      showTrainingsList();
    }
  }
}

function renderWeekGrid() {
  // Week grid removed - using navigation buttons instead
  // This function is kept for compatibility but doesn't do much now
}

//=== Rendering ===
function renderEquipment(equipment) {
  const list = document.getElementById('equipment-list');
  list.innerHTML = equipment.map(item => `<li>${item}</li>`).join('');
}

function renderWorkoutBlocks(blocks) {
  const container = document.getElementById('workout-blocks');
  let html = '';

  if (blocks.static_warmup) {
    html += renderBlock('Static Warmup', blocks.static_warmup.duration_minutes, blocks.static_warmup.movements);
  }

  if (blocks.active_warmup) {
    html += renderBlock('Active Warmup', blocks.active_warmup.duration_minutes, blocks.active_warmup.movements);
  }

  if (blocks.strength) {
    html += renderStrengthBlock(blocks.strength);
  }

  if (blocks.metcon) {
    html += renderMetconBlock(blocks.metcon);
  }

  if (blocks.cooldown) {
    html += renderBlock('Cooldown', blocks.cooldown.duration_minutes, blocks.cooldown.movements);
  }

  container.innerHTML = html;
}

function renderBlock(title, duration, movements) {
  return `
    <div class="workout-block">
      <h3 class="block-title">${title} <span class="block-duration">${duration} min</span></h3>
      <ul class="movement-list">
        ${movements.map(m => `
          <li>
            <strong>${m.name}</strong> — ${m.reps_or_duration}
            ${m.notes ? `<br><em>${m.notes}</em>` : ''}
          </li>
        `).join('')}
      </ul>
    </div>
  `;
}

function renderStrengthBlock(strength) {
  return `
    <div class="workout-block">
      <h3 class="block-title">${strength.label} <span class="block-duration">${strength.duration_minutes} min</span></h3>
      <ul class="movement-list">
        ${strength.movements.map(m => `
          <li>
            <strong>${m.name}</strong> — ${m.sets ? `${m.sets}×${m.reps}` : m.reps} @ ${m.load}
            ${m.rest_seconds ? `<br><em>Rest: ${m.rest_seconds}s</em>` : m.rest ? `<br><em>Rest: ${m.rest}</em>` : ''}
            ${m.notes ? `<br><em>${m.notes}</em>` : ''}
            ${m.scaling ? `<br><small>Scale: ${m.scaling}</small>` : ''}
          </li>
        `).join('')}
      </ul>
    </div>
  `;
}

function renderMetconBlock(metcon) {
  return `
    <div class="workout-block metcon">
      <h3 class="block-title">Metcon ${metcon.rounds_or_duration ? `— ${metcon.rounds_or_duration}` : ''} <span class="block-duration">${metcon.duration_minutes} min</span></h3>
      <p class="metcon-format"><strong>${metcon.format}</strong> | Time cap: ${metcon.time_cap_minutes} min</p>
      <ul class="movement-list">
        ${metcon.movements.map(m => `
          <li>
            ${m.reps || m.reps_or_duration || ''} <strong>${m.name}</strong> ${m.load ? `@ ${m.load}` : ''}
            ${m.scaling ? `<br><small>Scale: ${m.scaling}</small>` : ''}
          </li>
        `).join('')}
      </ul>
      ${metcon.target_score ? `<p class="metcon-target">Target: ${metcon.target_score}</p>` : ''}
    </div>
  `;
}

function renderRationale(rationale, containerId = null) {
  const html = `
    <div class="rationale-item">
      <h4>Session Design</h4>
      <p>${rationale.session_why.text}</p>
      <cite>— ${rationale.session_why.source}</cite>
    </div>
    <div class="rationale-item">
      <h4>Movement Selection</h4>
      <p>${rationale.movement_why.text}</p>
      <cite>— ${rationale.movement_why.source}</cite>
    </div>
    <div class="rationale-item">
      <h4>Loading Rationale</h4>
      <p>${rationale.loading_why.text}</p>
      <cite>— ${rationale.loading_why.source}</cite>
    </div>
  `;

  if (containerId) {
    const container = document.getElementById(containerId);
    if (container) container.innerHTML = html;
  }

  return html;
}

//=== Navigation ===
function setupNavigation() {
  // Back button navigation is handled by specific view setup functions
  // No global navigation setup needed
}

function showView(view) {
  document.querySelectorAll('.view').forEach(v => v.classList.add('hidden'));
  document.getElementById(`view-${view}`).classList.remove('hidden');
}

//=== Collapsibles ===
function setupCollapsibles() {
  document.querySelectorAll('.section-toggle').forEach(toggle => {
    toggle.addEventListener('click', function() {
      const targetId = this.getAttribute('data-target');
      const target = document.getElementById(targetId);
      const isExpanded = this.getAttribute('aria-expanded') === 'true';

      this.setAttribute('aria-expanded', !isExpanded);
      target.classList.toggle('hidden');
    });
  });
}

//=== Session Start ===
function setupSessionStart() {
  document.getElementById('btn-start-session').addEventListener('click', startSession);
  document.getElementById('btn-stop').addEventListener('click', stopSession);
  document.getElementById('btn-play').addEventListener('click', playTimer);
  document.getElementById('btn-pause').addEventListener('click', pauseTimer);
  document.getElementById('btn-reset').addEventListener('click', resetTimer);
}


async function startSession() {
  try {
    if ('wakeLock' in navigator) {
      state.wakeLock = await navigator.wakeLock.request('screen');
    }
  } catch (err) {
    console.warn('Wake Lock failed:', err);
  }

  document.getElementById('timer-overlay').classList.remove('hidden');
  state.timerActive = true;
  runTimer();
}

function stopSession() {
  if (state.wakeLock) {
    state.wakeLock.release();
    state.wakeLock = null;
  }

  document.getElementById('timer-overlay').classList.add('hidden');
  state.timerActive = false;

  // Mark session complete
  markSessionComplete();
}

function runTimer() {
  // Get blocks from either program or WOD mode
  const blocks = state.currentProgram
    ? state.currentProgram.sessions[state.currentSessionIndex].blocks
    : state.currentWod?.blocks;

  if (!blocks) {
    console.error('No blocks found for timer');
    return;
  }

  // Find first non-warmup block or use static warmup
  const blockToShow = blocks.active_warmup || blocks.strength || blocks.metcon || blocks.static_warmup || blocks.cooldown;
  const blockName = blocks.active_warmup ? 'Active Warmup' : blocks.strength ? 'Strength' : blocks.metcon ? 'Metcon' : blocks.static_warmup ? 'Static Warmup' : 'Cooldown';
  const duration = blockToShow.duration_minutes || 5;

  // Determine round info
  let roundInfo = `${duration} minutes`;

  // For warmups and cooldowns, show as "X rounds" if duration allows
  if ((blockName === 'Active Warmup' || blockName === 'Static Warmup' || blockName === 'Cooldown') && blockToShow.movements && blockToShow.movements.length > 0) {
    // Simple round calculation: assume ~1min per movement
    const numRounds = Math.max(1, Math.floor(duration / Math.max(1, blockToShow.movements.length * 0.5)));
    if (numRounds > 1) {
      roundInfo = `${numRounds} rounds x ${Math.ceil(duration / numRounds)} min`;
    } else {
      roundInfo = `1 round x ${duration} min`;
    }
  } else if (blockName === 'Metcon' && blockToShow.rounds_or_duration) {
    roundInfo = blockToShow.rounds_or_duration;
  }

  document.getElementById('timer-block-name').textContent = blockName;
  document.getElementById('timer-round-info').textContent = roundInfo;

  if (blockToShow.movements) {
    document.getElementById('timer-movements').innerHTML = blockToShow.movements
      .map(m => `<p>${m.name}${m.reps_or_duration ? ` — ${m.reps_or_duration}` : m.reps ? ` — ${m.reps} reps x ${m.sets || 1} sets` : ''}</p>`)
      .join('');
  }

  state.timerSeconds = duration * 60;
  state.timerRunning = false;
  updateTimerDisplay();
}

function updateTimerDisplay() {
  const display = document.getElementById('timer-display');
  const mins = Math.floor(state.timerSeconds / 60);
  const secs = state.timerSeconds % 60;
  display.textContent = `${mins}:${secs.toString().padStart(2, '0')}`;

  // Update color based on remaining time
  display.classList.remove('warning', 'critical');
  if (state.timerSeconds <= 10 && state.timerSeconds > 0) {
    display.classList.add('critical');
  } else if (state.timerSeconds <= 20) {
    display.classList.add('warning');
  }
}

function playTimer() {
  if (state.timerRunning) return; // Already running
  state.timerRunning = true;

  state.timerInterval = setInterval(() => {
    if (!state.timerActive || !state.timerRunning || state.timerSeconds <= 0) {
      pauseTimer();
      return;
    }

    state.timerSeconds--;
    updateTimerDisplay();

    // Update progress bar - calculate total from all blocks
    const blocks = state.currentProgram
      ? state.currentProgram.sessions[state.currentSessionIndex].blocks
      : state.currentWod?.blocks;

    if (blocks) {
      const blockToShow = blocks.active_warmup || blocks.strength || blocks.metcon || blocks.static_warmup || blocks.cooldown;
      const total = (blockToShow.duration_minutes || 5) * 60;
      const pct = ((total - state.timerSeconds) / total) * 100;
      document.getElementById('timer-progress-bar').style.width = `${Math.min(pct, 100)}%`;
    }

    // Beep at 10 seconds
    if (state.timerSeconds === 10) {
      playBeep();
    }
  }, 1000);
}

function pauseTimer() {
  state.timerRunning = false;
  if (state.timerInterval) {
    clearInterval(state.timerInterval);
    state.timerInterval = null;
  }
}

function resetTimer() {
  pauseTimer();
  const blocks = state.currentProgram
    ? state.currentProgram.sessions[state.currentSessionIndex].blocks
    : state.currentWod?.blocks;

  if (blocks) {
    const blockToShow = blocks.active_warmup || blocks.strength || blocks.metcon || blocks.static_warmup || blocks.cooldown;
    state.timerSeconds = (blockToShow.duration_minutes || 5) * 60;
    updateTimerDisplay();
    document.getElementById('timer-progress-bar').style.width = '0%';
  }
}

function playBeep() {
  try {
    const audioContext = new (window.AudioContext || window.webkitAudioContext)();
    const oscillator = audioContext.createOscillator();
    const gainNode = audioContext.createGain();

    oscillator.connect(gainNode);
    gainNode.connect(audioContext.destination);

    oscillator.frequency.value = 800;
    oscillator.type = 'sine';

    gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
    gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.1);

    oscillator.start(audioContext.currentTime);
    oscillator.stop(audioContext.currentTime + 0.1);
  } catch (e) {
    console.warn('Beep not available:', e);
  }
}

//=== WOD Mode ===
function setupWodMode() {
  // Random WOD button
  document.getElementById('btn-random-wod').addEventListener('click', () => {
    const category = state.currentCategory || 'full-body';
    loadRandomWod(category);
  });

  // Category filter buttons
  document.querySelectorAll('.filter-btn').forEach(btn => {
    btn.addEventListener('click', function() {
      // Update active state
      document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
      this.classList.add('active');

      const category = this.getAttribute('data-category');
      state.currentCategory = category;
      loadRandomWod(category);
    });
  });
}

async function loadWodPool(category) {
  if (state.wodPools[category]) {
    return state.wodPools[category];
  }

  try {
    const response = await fetch(`./data/wods/wods-${category}.json`);
    const data = await response.json();
    state.wodPools[category] = data;
    return data;
  } catch (error) {
    console.error(`Failed to load ${category} WODs:`, error);
    return null;
  }
}

async function loadRandomWod(category) {
  const pool = await loadWodPool(category);
  if (!pool || !pool.wods || pool.wods.length === 0) {
    document.getElementById('wod-display').innerHTML =
      '<p class="empty-state">No WODs available for this category yet</p>';
    return;
  }

  // Pick random WOD
  const randomIndex = Math.floor(Math.random() * pool.wods.length);
  const wod = pool.wods[randomIndex];
  state.currentWod = wod;

  // Render it
  renderWod(wod);
}

function renderWod(wod) {
  const container = document.getElementById('wod-display');

  let html = `
    <div class="session-header">
      <h2>${wod.title}</h2>
      <span class="session-meta">${wod.duration_minutes} min • ${wod.category.join(', ')}</span>
    </div>

    <!-- Equipment List -->
    <div class="equipment-section">
      <button class="section-toggle" data-target="wod-equipment-list">
        <span>Equipment Needed</span>
        <span class="toggle-icon">▼</span>
      </button>
      <ul id="wod-equipment-list" class="equipment-list hidden">
        ${wod.equipment.map(item => `<li>${item}</li>`).join('')}
      </ul>
    </div>

    <!-- Workout Blocks -->
    <div class="workout-blocks">
  `;

  const blocks = wod.blocks;

  if (blocks.static_warmup) {
    html += renderBlock('Static Warmup', blocks.static_warmup.duration_minutes, blocks.static_warmup.movements);
  }

  if (blocks.active_warmup) {
    html += renderBlock('Active Warmup', blocks.active_warmup.duration_minutes, blocks.active_warmup.movements);
  }

  if (blocks.strength) {
    html += renderStrengthBlock(blocks.strength);
  }

  if (blocks.metcon) {
    html += renderMetconBlock(blocks.metcon);
  }

  if (blocks.cooldown) {
    html += renderBlock('Cooldown', blocks.cooldown.duration_minutes, blocks.cooldown.movements);
  }

  html += `</div>`;

  // Rationale
  if (wod.rationale) {
    html += `
      <div class="rationale-section">
        <button class="section-toggle" data-target="wod-rationale-content">
          <span>🔬 Why This Session?</span>
          <span class="toggle-icon">▼</span>
        </button>
        <div id="wod-rationale-content" class="rationale-content hidden">
    `;

    html += renderRationale(wod.rationale);
    html += `</div></div>`;
  }

  // Start button
  html += `
    <div class="session-actions">
      <button id="btn-start-wod" class="btn-primary btn-large">Start Session</button>
    </div>
  `;

  container.innerHTML = html;

  // Re-setup collapsibles for new content
  setupCollapsibles();

  // Setup start button
  document.getElementById('btn-start-wod').addEventListener('click', startSession);
}

window.woodieState = state;
