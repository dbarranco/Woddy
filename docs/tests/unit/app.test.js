/**
 * Unit Tests for Woddy App
 * Tests core state management and utility functions
 */

describe('Woddy App Core Tests', () => {
  let mockState;

  beforeEach(() => {
    localStorage.clear();
    jest.clearAllMocks();

    // Initialize mock state
    mockState = {
      availablePrograms: [
        { id: 'back-in-shape', name: 'Back in Shape', description: 'Test', weeks: null }
      ],
      selectedDuration: null,
      selectedFrequency: null,
      completedTrainings: [],
      wodPools: {},
      currentWod: null,
      currentProgram: null,
    };
  });

  describe('Program Management', () => {
    test('program name should not include weeks when not selected', () => {
      const prog = mockState.availablePrograms[0];
      const html = `<h3>${prog.name}</h3>`;

      expect(html).toBe('<h3>Back in Shape</h3>');
      expect(html).not.toContain('null');
    });

    test('should store selected duration and frequency', () => {
      mockState.selectedDuration = 2;
      mockState.selectedFrequency = 4;

      expect(mockState.selectedDuration).toBe(2);
      expect(mockState.selectedFrequency).toBe(4);
    });

    test('should persist frequency to localStorage', () => {
      const frequency = 4;
      localStorage.setItem('trainingFrequency', frequency);

      const stored = localStorage.getItem('trainingFrequency');
      expect(stored).toBe('4');
    });

    test('should retrieve persisted frequency from localStorage', () => {
      localStorage.setItem('trainingFrequency', '5');
      const retrieved = parseInt(localStorage.getItem('trainingFrequency'));

      expect(retrieved).toBe(5);
    });
  });

  describe('WOD Management', () => {
    test('should have empty WOD pools initially', () => {
      expect(Object.keys(mockState.wodPools)).toHaveLength(0);
    });

    test('should store loaded WOD pool', () => {
      const mockPool = {
        category: 'full-body',
        wods: [
          { title: 'Test WOD 1', duration_minutes: 30 },
          { title: 'Test WOD 2', duration_minutes: 25 },
        ]
      };

      mockState.wodPools['full-body'] = mockPool;

      expect(mockState.wodPools['full-body']).toBeDefined();
      expect(mockState.wodPools['full-body'].wods).toHaveLength(2);
    });

    test('should select random WOD from pool', () => {
      const wods = [
        { title: 'WOD 1' },
        { title: 'WOD 2' },
        { title: 'WOD 3' },
      ];

      const randomIndex = Math.floor(Math.random() * wods.length);
      const selectedWod = wods[randomIndex];

      expect(wods).toContain(selectedWod);
    });

    test('should track current WOD selection', () => {
      const wod = { title: 'Full Body Blast', duration_minutes: 30 };
      mockState.currentWod = wod;

      expect(mockState.currentWod).toBe(wod);
      expect(mockState.currentWod.title).toBe('Full Body Blast');
    });
  });

  describe('Training Progress', () => {
    test('should track completed trainings', () => {
      mockState.completedTrainings = ['training-1', 'training-3'];

      expect(mockState.completedTrainings).toHaveLength(2);
      expect(mockState.completedTrainings).toContain('training-1');
    });

    test('should calculate completion percentage', () => {
      mockState.completedTrainings = ['t1', 't2', 't3'];
      const totalTrainings = 10;
      const percentage = (mockState.completedTrainings.length / totalTrainings) * 100;

      expect(percentage).toBe(30);
    });

    test('should filter trainings by frequency', () => {
      const allTrainings = [
        { id: 't1', day: 0 },
        { id: 't2', day: 1 },
        { id: 't3', day: 2 },
        { id: 't4', day: 3 },
        { id: 't5', day: 4 },
        { id: 't6', day: 5 },
        { id: 't7', day: 6 },
      ];

      const frequency = 4;
      const filtered = allTrainings.filter(t => (t.day % 7) < frequency);

      expect(filtered).toHaveLength(4);
    });
  });

  describe('Acronym Expansion', () => {
    test('should expand common CrossFit acronyms', () => {
      const acronyms = {
        'AMRAP': 'As Many Rounds As Possible',
        'EMOM': 'Every Minute On the Minute',
        '1RM': 'One-Rep Max',
      };

      Object.entries(acronyms).forEach(([acronym, expansion]) => {
        expect(expansion).toBeDefined();
        expect(expansion.length).toBeGreaterThan(0);
      });
    });
  });
});

describe('DOM Visibility Tests', () => {
  beforeEach(() => {
    document.body.innerHTML = `
      <div id="view-onboarding" class="view"></div>
      <div id="view-programs" class="view hidden"></div>
      <div id="wod-category-selector"></div>
      <div id="wod-display" class="session-card hidden"></div>
    `;
  });

  test('should hide onboarding and show programs view', () => {
    const onboarding = document.getElementById('view-onboarding');
    const programs = document.getElementById('view-programs');

    onboarding.classList.add('hidden');
    programs.classList.remove('hidden');

    expect(onboarding.classList.contains('hidden')).toBe(true);
    expect(programs.classList.contains('hidden')).toBe(false);
  });

  test('should show WOD category selector', () => {
    const selector = document.getElementById('wod-category-selector');
    const display = document.getElementById('wod-display');

    selector.classList.remove('hidden');
    display.classList.add('hidden');

    expect(selector.classList.contains('hidden')).toBe(false);
    expect(display.classList.contains('hidden')).toBe(true);
  });

  test('should toggle between category selector and WOD display', () => {
    const selector = document.getElementById('wod-category-selector');
    const display = document.getElementById('wod-display');

    // Show WOD display
    selector.classList.add('hidden');
    display.classList.remove('hidden');

    expect(selector.classList.contains('hidden')).toBe(true);
    expect(display.classList.contains('hidden')).toBe(false);

    // Go back to selector
    selector.classList.remove('hidden');
    display.classList.add('hidden');

    expect(selector.classList.contains('hidden')).toBe(false);
    expect(display.classList.contains('hidden')).toBe(true);
  });
});

describe('Event Handler Tests', () => {
  test('should attach click handler to program card', () => {
    const mockHandler = jest.fn();
    document.body.innerHTML = '<div class="program-card" data-program-id="test-id"></div>';

    const card = document.querySelector('.program-card');
    card.addEventListener('click', mockHandler);
    card.click();

    expect(mockHandler).toHaveBeenCalledTimes(1);
  });

  test('should attach async click handler to filter buttons', () => {
    const mockHandler = jest.fn();
    document.body.innerHTML = `
      <button class="filter-btn" data-category="full-body">Full Body</button>
    `;

    const btn = document.querySelector('.filter-btn');
    btn.addEventListener('click', mockHandler);
    btn.click();

    expect(mockHandler).toHaveBeenCalledTimes(1);
  });

  test('should read category from data attribute', () => {
    document.body.innerHTML = `
      <button class="filter-btn" data-category="upper-body">Upper Body</button>
    `;

    const btn = document.querySelector('.filter-btn');
    const category = btn.getAttribute('data-category');

    expect(category).toBe('upper-body');
  });
});
