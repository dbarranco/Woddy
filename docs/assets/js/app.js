// Woddy - Sport-Technical CrossFit PWA

//=== State ===
const state = {
  // Programs
  availablePrograms: [],
  currentProgramId: null,
  currentProgram: null,

  // Program Configuration
  configProgramId: null,
  selectedDuration: null,
  selectedFrequency: localStorage.getItem('trainingFrequency') ? parseInt(localStorage.getItem('trainingFrequency')) : null,

  // Trainings
  currentTrainingIndex: 0,
  completedTrainings: [],

  // Timer
  timerActive: false,
  timerRunning: false,
  timerSeconds: 0,
  timerInterval: null,
  wakeLock: null,
  currentBlockIndex: 0,
  currentRound: 1,
  totalRounds: 1,
  roundDuration: 0,
  roundStartSeconds: 0,

  // WODs
  wodPools: {}, // {category: {wods: [...]}}
  currentWod: null,
  currentCategory: null,
  currentSessionIndex: 0
};

//=== Acronym Expansion ===
const acronymExpansions = {
  'CARs': 'Controlled Articular Rotations',
  'ROM': 'Range of Motion',
  'CNS': 'Central Nervous System',
  'AMRAP': 'As Many Rounds As Possible',
  'EMOM': 'Every Minute On the Minute',
  'RPE': 'Rate of Perceived Exertion',
  'C2B': 'Chest to Bar',
  '1RM': 'One-Rep Max',
  'RFD': 'Rate of Force Development',
  'RIR': 'Reps In Reserve'
};

function expandAcronyms(text) {
  if (!text) return text;
  let expanded = text;
  Object.entries(acronymExpansions).forEach(([acronym, expansion]) => {
    const regex = new RegExp(`\\b${acronym}\\b`, 'g');
    expanded = expanded.replace(regex, `${acronym} (${expansion})`);
  });
  return expanded;
}

//=== Service Worker ===
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('./sw.js')
    .then(reg => console.log('✅ SW registered'))
    .catch(err => console.error('❌ SW failed:', err));
}

//=== Init ===
document.addEventListener('DOMContentLoaded', async () => {
  console.log('🚀 App initializing...');

  try {
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

    console.log('✅ All setup complete');

    document.getElementById('loading').classList.add('hidden');
    document.getElementById('main-container').classList.remove('hidden');

    // Check if there's a saved program and load it
    const savedProgram = loadSavedProgram();
    if (savedProgram && state.selectedDuration && state.selectedFrequency) {
      console.log('📦 Loading saved program:', savedProgram);
      // Bypass onboarding and show the saved program
      document.getElementById('view-onboarding').classList.add('hidden');
      document.getElementById('app-header').classList.remove('hidden');
      await loadProgramAndShowTrainings('back-in-shape');
    }

    console.log('✅ App loaded successfully');
  } catch (error) {
    console.error('❌ Init error:', error);
    document.getElementById('loading').classList.add('hidden');
    document.getElementById('main-container').classList.remove('hidden');
  }
});

//=== Onboarding ===
function setupOnboarding() {
  const btnStartProgram = document.getElementById('btn-start-program');
  if (btnStartProgram) {
    btnStartProgram.addEventListener('click', () => {
      document.getElementById('view-onboarding').classList.add('hidden');
      document.getElementById('app-header').classList.remove('hidden');
      showProgramsSelection();
    });
  }

  const btnRandomWod = document.getElementById('btn-random-wod-start');
  if (btnRandomWod) {
    btnRandomWod.addEventListener('click', () => {
      document.getElementById('view-onboarding').classList.add('hidden');
      document.getElementById('app-header').classList.remove('hidden');
      document.getElementById('view-wod').classList.remove('hidden');
      // Reset WOD view to show category selector
      document.getElementById('wod-category-selector').classList.remove('hidden');
      document.getElementById('wod-display').classList.add('hidden');
    });
  }
}

//=== Program Flow ===
function setupProgramFlow() {
  // Load available programs - only one base program, duration selected by user
  state.availablePrograms = [
    { id: 'back-in-shape', name: 'Back in Shape', description: 'Progressive return to training program. Choose your duration and weekly frequency.', weeks: null }
  ];

  // Setup back buttons (only if they exist in DOM)
  const btnBackToTrainings = document.getElementById('btn-back-to-trainings');
  if (btnBackToTrainings) {
    btnBackToTrainings.addEventListener('click', showTrainingsList);
  }
}

function showProgramsSelection() {
  // Hide all other views
  document.querySelectorAll('.view').forEach(v => v.classList.add('hidden'));
  document.getElementById('view-programs').classList.remove('hidden');

  // Render programs
  const programsList = document.getElementById('programs-list');
  programsList.innerHTML = state.availablePrograms.map(prog => `
    <div class="program-card" data-program-id="${prog.id}">
      <h3>${prog.name}</h3>
      <p>${prog.description}</p>
    </div>
  `).join('');

  // Add click handlers
  programsList.querySelectorAll('.program-card').forEach(card => {
    card.addEventListener('click', () => {
      const programId = card.getAttribute('data-program-id');
      showProgramConfiguration(programId);
    });
  });
}

function showProgramConfiguration(programId) {
  // Find program details from available programs
  const program = state.availablePrograms.find(p => p.id === programId);
  if (!program) return;

  // Hide all other views
  document.querySelectorAll('.view').forEach(v => v.classList.add('hidden'));
  document.getElementById('view-program-config').classList.remove('hidden');

  // Update header
  document.getElementById('config-program-name').textContent = program.name;

  // Reset selections
  document.querySelectorAll('.duration-btn, .frequency-btn').forEach(btn => {
    btn.classList.remove('active');
  });

  // Store selected program ID
  state.configProgramId = programId;

  // Reset button state
  const continueBtn = document.getElementById('btn-continue-config');
  continueBtn.disabled = true;

  // Setup event listeners for duration and frequency buttons
  document.querySelectorAll('.duration-btn').forEach(btn => {
    btn.addEventListener('click', function() {
      document.querySelectorAll('.duration-btn').forEach(b => b.classList.remove('active'));
      this.classList.add('active');
      state.selectedDuration = parseInt(this.dataset.weeks);
      updateConfigContinueButton();
    });
  });

  document.querySelectorAll('.frequency-btn').forEach(btn => {
    btn.addEventListener('click', function() {
      document.querySelectorAll('.frequency-btn').forEach(b => b.classList.remove('active'));
      this.classList.add('active');
      state.selectedFrequency = parseInt(this.dataset.freq);
      updateConfigContinueButton();
    });
  });

  // Back button handler
  document.getElementById('btn-back-from-config').onclick = showProgramsSelection;

  // Continue button handler
  continueBtn.onclick = () => {
    if (state.selectedDuration && state.selectedFrequency) {
      // Store frequency preference
      localStorage.setItem('trainingFrequency', state.selectedFrequency);
      loadProgramAndShowTrainings(state.configProgramId);
    }
  };
}

function updateConfigContinueButton() {
  const continueBtn = document.getElementById('btn-continue-config');
  continueBtn.disabled = !(state.selectedDuration && state.selectedFrequency);
}

async function loadProgramAndShowTrainings(programId) {
  try {
    // Construct file name with selected duration
    const duration = state.selectedDuration;
    const fileName = `back-in-shape-${duration}w`;

    const response = await fetch(`./data/programs/${fileName}.json`);
    const data = await response.json();
    state.currentProgramId = programId;
    state.currentProgram = data.program;
    state.currentTrainingIndex = 0;

    // Save program selection to localStorage
    saveProgram();

    showTrainingsList();
    console.log('✅ Program loaded:', fileName);
  } catch (error) {
    console.error('❌ Failed to load program:', error);
  }
}

function showTrainingsList() {
  if (!state.currentProgram) return;

  // Hide all other views
  document.querySelectorAll('.view').forEach(v => v.classList.add('hidden'));
  document.getElementById('view-trainings').classList.remove('hidden');

  // Update header with program name, duration and frequency
  let titleText = state.currentProgram.name;
  if (state.selectedDuration) {
    titleText += ` • ${state.selectedDuration}w`;
  }
  if (state.selectedFrequency) {
    titleText += ` • ${state.selectedFrequency}d/week`;
  }
  document.getElementById('program-title').textContent = titleText;

  // Filter out rest days to get all training sessions
  let allTrainings = state.currentProgram.sessions.filter(s => !s.is_rest_day);

  // Further filter by selected frequency (show only selected number of trainings per week)
  if (state.selectedFrequency && state.selectedFrequency < 7) {
    const trainingsPerWeek = state.selectedFrequency;
    allTrainings = allTrainings.filter((training, index) => {
      // Calculate which day of the week this is
      const dayOfWeek = index % 7; // Assuming up to 7 days per week
      return dayOfWeek < trainingsPerWeek;
    });
  }

  const completed = state.completedTrainings.filter(id => allTrainings.map(t => t.id).includes(id)).length;
  document.getElementById('trainings-completed').textContent = `${completed}/${allTrainings.length} trainings`;

  // Render trainings list grouped by week
  const trainingsList = document.getElementById('trainings-list');

  // Group trainings by week
  let html = '';
  let currentWeek = null;

  allTrainings.forEach((training, index) => {
    const week = training.week;

    // Add week header if we're entering a new week
    if (week !== currentWeek) {
      if (currentWeek !== null) {
        html += '</div>'; // Close previous week group
      }
      html += `<div class="week-group"><h3 class="week-header">Week ${week}</h3>`;
      currentWeek = week;
    }

    const isCompleted = state.completedTrainings.includes(training.id);
    html += `
      <div class="training-item ${isCompleted ? 'completed' : ''}" data-training-id="${training.id}">
        <div>
          <h4>${training.title}</h4>
          <p>Day ${training.day}</p>
        </div>
      </div>
    `;
  });

  if (currentWeek !== null) {
    html += '</div>'; // Close last week group
  }

  trainingsList.innerHTML = html;

  // Add click handlers for trainings
  trainingsList.querySelectorAll('.training-item').forEach((item, index) => {
    item.addEventListener('click', () => {
      loadAndShowTraining(allTrainings[index].id);
    });
  });

  // Setup reset button
  const resetBtn = document.getElementById('btn-reset-program');
  if (resetBtn) {
    resetBtn.addEventListener('click', () => {
      if (confirm('Are you sure? This will reset your program progress.')) {
        resetProgram();
      }
    });
  }
}

function loadAndShowTraining(trainingId) {
  const training = state.currentProgram.sessions.find(s => s.id === trainingId);
  if (!training) return;

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
  const saved = localStorage.getItem('woddy_progress');
  if (saved) {
    state.completedTrainings = JSON.parse(saved);
  }
}

function saveProgress() {
  localStorage.setItem('woddy_progress', JSON.stringify(state.completedTrainings));
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

function saveProgram() {
  const programData = {
    programId: state.currentProgramId,
    duration: state.selectedDuration,
    frequency: state.selectedFrequency,
    timestamp: new Date().toISOString()
  };
  localStorage.setItem('woddy_program', JSON.stringify(programData));
}

function loadSavedProgram() {
  const saved = localStorage.getItem('woddy_program');
  if (saved) {
    const programData = JSON.parse(saved);
    state.currentProgramId = programData.programId;
    state.selectedDuration = programData.duration;
    state.selectedFrequency = programData.frequency;
    return programData;
  }
  return null;
}

function resetProgram() {
  localStorage.removeItem('woddy_program');
  state.currentProgram = null;
  state.currentProgramId = null;
  state.selectedDuration = null;
  state.selectedFrequency = null;
  state.completedTrainings = [];
  localStorage.removeItem('woddy_progress');
  showProgramsSelection();
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
            <strong>${expandAcronyms(m.name)}</strong> — ${m.reps_or_duration}
            ${m.notes ? `<br><em>${expandAcronyms(m.notes)}</em>` : ''}
          </li>
        `).join('')}
      </ul>
    </div>
  `;
}

function renderStrengthBlock(strength) {
  return `
    <div class="workout-block">
      <h3 class="block-title">${expandAcronyms(strength.label)} <span class="block-duration">${strength.duration_minutes} min</span></h3>
      <table class="strength-table">
        <thead>
          <tr>
            <th>Exercise</th>
            <th>Sets/Reps</th>
            <th>Load</th>
            <th>Rest</th>
            <th>Notes</th>
          </tr>
        </thead>
        <tbody>
          ${strength.movements.map(m => `
            <tr>
              <td class="exercise-name"><strong>${expandAcronyms(m.name)}</strong></td>
              <td class="sets-reps">${m.sets ? `${m.sets}×${m.reps}` : m.reps}</td>
              <td class="load">${expandAcronyms(m.load)}</td>
              <td class="rest">${m.rest_seconds ? `${m.rest_seconds}s` : m.rest ? m.rest : '—'}</td>
              <td class="notes">
                ${m.notes ? `<em>${expandAcronyms(m.notes)}</em>` : ''}
                ${m.scaling ? `${m.notes ? '<br>' : ''}<small>Scale: ${expandAcronyms(m.scaling)}</small>` : ''}
              </td>
            </tr>
          `).join('')}
        </tbody>
      </table>
    </div>
  `;
}

function renderMetconBlock(metcon) {
  return `
    <div class="workout-block metcon">
      <h3 class="block-title">Metcon ${metcon.rounds_or_duration ? `— ${expandAcronyms(metcon.rounds_or_duration)}` : ''} <span class="block-duration">${metcon.duration_minutes} min</span></h3>
      <p class="metcon-format"><strong>${expandAcronyms(metcon.format)}</strong> | Time cap: ${metcon.time_cap_minutes} min</p>
      <ul class="movement-list">
        ${metcon.movements.map(m => `
          <li>
            ${m.reps || m.reps_or_duration || ''} <strong>${expandAcronyms(m.name)}</strong> ${m.load ? `@ ${expandAcronyms(m.load)}` : ''}
            ${m.scaling ? `<br><small>Scale: ${expandAcronyms(m.scaling)}</small>` : ''}
          </li>
        `).join('')}
      </ul>
      ${metcon.target_score ? `<p class="metcon-target">Target: ${expandAcronyms(metcon.target_score)}</p>` : ''}
    </div>
  `;
}

function renderRationale(rationale, containerId = null) {
  const html = `
    <div class="rationale-item">
      <h4>Session Design</h4>
      <p>${expandAcronyms(rationale.session_why.text)}</p>
      <cite>— ${rationale.session_why.source}</cite>
    </div>
    <div class="rationale-item">
      <h4>Movement Selection</h4>
      <p>${expandAcronyms(rationale.movement_why.text)}</p>
      <cite>— ${rationale.movement_why.source}</cite>
    </div>
    <div class="rationale-item">
      <h4>Loading Rationale</h4>
      <p>${expandAcronyms(rationale.loading_why.text)}</p>
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
  // Setup logo click to go home
  const headerLogo = document.querySelector('.app-header .logo-header');
  if (headerLogo) {
    headerLogo.addEventListener('click', goHome);
  }
}

function goHome() {
  // Stop timer if running
  if (state.timerActive || state.timerRunning) {
    stopSession();
  }

  // Hide all views
  document.querySelectorAll('.view').forEach(v => v.classList.add('hidden'));
  document.getElementById('timer-overlay').classList.add('hidden');

  // Reset state (but preserve localStorage)
  state.currentProgram = null;
  state.currentProgramId = null;
  state.currentWod = null;
  state.currentCategory = null;

  // Show onboarding and hide header
  document.getElementById('view-onboarding').classList.remove('hidden');
  document.getElementById('app-header').classList.add('hidden');

  console.log('🏠 Returned to home');
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
  // Only attach listeners if buttons exist
  const btnStartSession = document.getElementById('btn-start-session');
  if (btnStartSession) btnStartSession.addEventListener('click', startSession);

  const btnStop = document.getElementById('btn-stop');
  if (btnStop) btnStop.addEventListener('click', stopSession);

  const btnPlay = document.getElementById('btn-play');
  if (btnPlay) btnPlay.addEventListener('click', playTimer);

  const btnPause = document.getElementById('btn-pause');
  if (btnPause) btnPause.addEventListener('click', pauseTimer);

  const btnReset = document.getElementById('btn-reset');
  if (btnReset) btnReset.addEventListener('click', resetTimer);

  const btnPrevBlock = document.getElementById('btn-prev-block');
  if (btnPrevBlock) btnPrevBlock.addEventListener('click', previousBlock);

  const btnNextBlock = document.getElementById('btn-next-block');
  if (btnNextBlock) btnNextBlock.addEventListener('click', nextBlock);
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
  // Initialize block navigation - display first block
  const blocksArray = getBlocksArray();
  if (blocksArray.length > 0) {
    state.currentBlockIndex = 0;
    displayBlock(0);
  } else {
    console.error('No blocks found for timer');
  }
}

function updateTimerDisplay() {
  const display = document.getElementById('timer-display');

  // For multi-round blocks, show time remaining in current round
  let displaySeconds = state.timerSeconds;
  if (state.totalRounds > 1 && state.roundDuration > 0) {
    displaySeconds = state.timerSeconds % state.roundDuration;
    if (displaySeconds === 0 && state.timerSeconds > 0) {
      displaySeconds = state.roundDuration;
    }
  }

  const mins = Math.floor(displaySeconds / 60);
  const secs = displaySeconds % 60;
  display.textContent = `${mins}:${secs.toString().padStart(2, '0')}`;

  // Update color based on remaining time in round
  display.classList.remove('warning', 'critical');
  if (displaySeconds <= 10 && displaySeconds > 0) {
    display.classList.add('critical');
  } else if (displaySeconds <= 20) {
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

    // Handle round transitions for multi-round blocks
    if (state.totalRounds > 1 && state.roundDuration > 0) {
      const secondsInCurrentRound = state.timerSeconds % state.roundDuration;

      // Check if we just completed a round
      if (secondsInCurrentRound === 0 && state.timerSeconds > 0) {
        state.currentRound++;
        const roundInfo = document.getElementById('timer-round-info');
        if (roundInfo && state.currentRound <= state.totalRounds) {
          const perRound = state.roundDuration / 60;
          roundInfo.textContent = `Round ${state.currentRound}/${state.totalRounds} • ${perRound}:00`;
          playBeep(); // Beep at round transition
        }
      }
    }

    // Update progress bar
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

// Helper function to get ordered blocks array
function getBlocksArray() {
  const blocks = state.currentProgram
    ? state.currentProgram.sessions[state.currentSessionIndex].blocks
    : state.currentWod?.blocks;

  if (!blocks) return [];

  const blockOrder = ['static_warmup', 'active_warmup', 'strength', 'metcon', 'cooldown'];
  return blockOrder.filter(key => blocks[key]).map(key => ({ key, block: blocks[key] }));
}

// Get the index of the currently displayed block
function getCurrentBlockIndex() {
  const blocksArray = getBlocksArray();
  const blocks = state.currentProgram
    ? state.currentProgram.sessions[state.currentSessionIndex].blocks
    : state.currentWod?.blocks;

  if (!blocks) return -1;

  // Find which block is currently shown
  const currentBlockKey = blocks.active_warmup ? 'active_warmup' : blocks.strength ? 'strength' : blocks.metcon ? 'metcon' : blocks.static_warmup ? 'static_warmup' : blocks.cooldown ? 'cooldown' : null;
  return blocksArray.findIndex(b => b.key === currentBlockKey);
}

// Display a specific block in the timer
function displayBlock(index) {
  const blocksArray = getBlocksArray();
  if (index < 0 || index >= blocksArray.length) return;

  const { key, block } = blocksArray[index];
  const blockNames = {
    static_warmup: 'Static Warmup',
    active_warmup: 'Active Warmup',
    strength: 'Strength',
    metcon: 'Metcon',
    cooldown: 'Cooldown'
  };

  // Update state to track current block
  state.currentBlockIndex = index;

  // Update block display
  const blockName = blockNames[key];
  const baseDuration = block.duration_minutes || 5;
  let roundInfo = `${baseDuration} minutes`;
  let totalDuration = baseDuration;
  let numRounds = 1;
  let perRound = baseDuration;

  // Calculate rounds for warmups/cooldowns
  if ((key === 'active_warmup' || key === 'static_warmup' || key === 'cooldown') && block.movements && block.movements.length > 0) {
    numRounds = Math.max(1, Math.floor(baseDuration / Math.max(1, block.movements.length * 0.5)));
    if (numRounds > 1) {
      perRound = Math.ceil(baseDuration / numRounds);
      totalDuration = numRounds * perRound;
    }
  } else if (key === 'metcon' && block.rounds_or_duration) {
    roundInfo = block.rounds_or_duration;
    // For metcon, try to extract number of rounds if format is "X rounds"
    const roundMatch = block.rounds_or_duration.match(/(\d+)\s*rounds?/i);
    if (roundMatch) {
      numRounds = parseInt(roundMatch[1]);
      perRound = Math.ceil(baseDuration / numRounds);
    }
  }

  // Store round info in state
  state.totalRounds = numRounds;
  state.currentRound = 1;
  state.roundDuration = perRound * 60; // Convert to seconds
  state.roundStartSeconds = state.roundDuration;

  // Update display with round info
  if (numRounds > 1) {
    roundInfo = `Round 1/${numRounds} • ${perRound}:00`;
  } else {
    roundInfo = `${baseDuration} minutes`;
  }

  document.getElementById('timer-block-name').textContent = blockName;
  document.getElementById('timer-round-info').textContent = roundInfo;

  if (block.movements) {
    const movementId = `movements-${state.currentBlockIndex}`;
    document.getElementById('timer-movements').innerHTML = block.movements
      .map((m, idx) => {
        let details = [];

        // Add reps/sets or duration
        if (m.reps_or_duration) {
          details.push(expandAcronyms(m.reps_or_duration));
        } else if (m.reps) {
          const sets = m.sets || 1;
          details.push(sets > 1 ? `${sets} × ${m.reps}` : m.reps);
        }

        // Add load if available
        if (m.load) {
          details.push(`@ ${expandAcronyms(m.load)}`);
        }

        // Add rest if available
        if (m.rest_seconds) {
          details.push(`Rest: ${m.rest_seconds}s`);
        } else if (m.rest) {
          details.push(`Rest: ${m.rest}`);
        }

        const detailsStr = details.length > 0 ? ` — ${details.join(' • ')}` : '';

        // Build full movement info with scaling if available
        let html = `<div class="timer-movement-item">
          <strong>${expandAcronyms(m.name)}</strong>${detailsStr}`;

        if (m.notes) {
          html += `<br><small class="timer-notes">${expandAcronyms(m.notes)}</small>`;
        }

        if (m.scaling) {
          const scalingId = `scaling-${state.currentBlockIndex}-${idx}`;
          html += `<button class="scaling-toggle" data-scaling-id="${scalingId}">
            <span>⚙️ Scaling Tips</span>
            <span class="toggle-icon">▼</span>
          </button>
          <div id="${scalingId}" class="scaling-tips hidden">
            ${expandAcronyms(m.scaling)}
          </div>`;
        }

        html += `</div>`;

        return html;
      })
      .join('');

    // Add event listeners to scaling toggles
    document.querySelectorAll('.scaling-toggle').forEach(btn => {
      btn.addEventListener('click', function(e) {
        e.preventDefault();
        const scalingId = this.getAttribute('data-scaling-id');
        const content = document.getElementById(scalingId);
        content.classList.toggle('hidden');
        this.classList.toggle('expanded');
      });
    });
  }

  // Update timer and reset
  state.timerSeconds = totalDuration * 60;
  state.timerRunning = false;
  updateTimerDisplay();
  document.getElementById('timer-progress-bar').style.width = '0%';

  // Update button states
  updateBlockNavButtons();
}

function updateBlockNavButtons() {
  const blocksArray = getBlocksArray();
  const currentIndex = state.currentBlockIndex !== undefined ? state.currentBlockIndex : getCurrentBlockIndex();

  const prevBtn = document.getElementById('btn-prev-block');
  const nextBtn = document.getElementById('btn-next-block');

  prevBtn.disabled = currentIndex <= 0;
  nextBtn.disabled = currentIndex >= blocksArray.length - 1;
}

function previousBlock() {
  const currentIndex = state.currentBlockIndex !== undefined ? state.currentBlockIndex : getCurrentBlockIndex();
  if (currentIndex > 0) {
    displayBlock(currentIndex - 1);
  }
}

function nextBlock() {
  const blocksArray = getBlocksArray();
  const currentIndex = state.currentBlockIndex !== undefined ? state.currentBlockIndex : getCurrentBlockIndex();
  if (currentIndex < blocksArray.length - 1) {
    displayBlock(currentIndex + 1);
  }
}

//=== WOD Mode ===
function setupWodMode() {
  console.log('🎯 setupWodMode() called');
  // Category filter buttons
  const filterBtns = document.querySelectorAll('.filter-btn');
  console.log('🎯 Setting up WOD mode with', filterBtns.length, 'filter buttons');
  filterBtns.forEach((btn, idx) => {
    console.log(`  Button ${idx}:`, btn.getAttribute('data-category'), btn);
  });

  filterBtns.forEach(btn => {
    btn.addEventListener('click', async function(e) {
      e.preventDefault();
      console.log('📌 Filter button clicked:', this.getAttribute('data-category'));

      // Update active state
      document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
      this.classList.add('active');

      const category = this.getAttribute('data-category');
      state.currentCategory = category;
      console.log('🔄 Loading WOD for category:', category);
      await loadRandomWod(category);
    });
  });
}

async function loadWodPool(category) {
  if (state.wodPools[category]) {
    console.log('💾 Using cached pool for:', category);
    return state.wodPools[category];
  }

  try {
    const url = `./data/wods/wods-${category}.json`;
    console.log('🌐 Fetching from:', url);
    const response = await fetch(url);

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const data = await response.json();
    console.log('✅ Loaded', data.wods?.length || 0, 'WODs from', url);
    state.wodPools[category] = data;
    return data;
  } catch (error) {
    console.error(`❌ Failed to load ${category} WODs:`, error);
    return null;
  }
}

async function loadRandomWod(category) {
  console.log('⏳ Loading WOD pool for:', category);
  const pool = await loadWodPool(category);
  console.log('📦 Pool loaded:', pool);

  if (!pool || !pool.wods || pool.wods.length === 0) {
    console.error('❌ No WODs in pool');
    document.getElementById('wod-display').innerHTML =
      '<p class="empty-state">No WODs available for this category yet</p>';
    return;
  }

  // Pick random WOD
  const randomIndex = Math.floor(Math.random() * pool.wods.length);
  const wod = pool.wods[randomIndex];
  state.currentWod = wod;
  console.log('✅ WOD loaded:', wod.title);

  // Render it
  renderWod(wod);
}

function renderWod(wod) {
  const container = document.getElementById('wod-display');
  const categorySelector = document.getElementById('wod-category-selector');

  // Hide category selector, show WOD display
  categorySelector.classList.add('hidden');
  container.classList.remove('hidden');

  let html = `
    <div class="wod-header-controls">
      <button id="btn-change-category" class="btn-back-category">← Change Category</button>
    </div>

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

  // Next WOD and Start buttons
  html += `
    <div class="session-actions">
      <button id="btn-next-wod" class="btn-next-wod">🎲 Next WOD</button>
      <button id="btn-start-wod" class="btn-primary btn-large">Start Session</button>
    </div>
  `;

  container.innerHTML = html;

  // Re-setup collapsibles for new content
  setupCollapsibles();

  // Setup buttons
  document.getElementById('btn-start-wod').addEventListener('click', startSession);
  document.getElementById('btn-next-wod').addEventListener('click', () => {
    loadRandomWod(state.currentCategory);
  });
  document.getElementById('btn-change-category').addEventListener('click', () => {
    const categorySelector = document.getElementById('wod-category-selector');
    const container = document.getElementById('wod-display');
    categorySelector.classList.remove('hidden');
    container.classList.add('hidden');
  });
}

window.woodieState = state;
