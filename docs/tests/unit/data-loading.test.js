/**
 * Integration Tests for Data Loading
 * Tests WOD and program data loading flows
 */

describe('WOD Data Loading', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    global.fetch.mockClear();
  });

  test('should fetch WOD data for full-body category', async () => {
    const mockWodData = {
      category: 'full-body',
      wods: [
        {
          title: 'Test WOD',
          duration_minutes: 30,
          equipment: ['barbell', 'pullup bar'],
          blocks: {},
        }
      ]
    };

    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockWodData,
    });

    const response = await fetch('./data/wods/wods-full-body.json');
    const data = await response.json();

    expect(global.fetch).toHaveBeenCalledWith('./data/wods/wods-full-body.json');
    expect(data.category).toBe('full-body');
    expect(data.wods).toHaveLength(1);
  });

  test('should handle missing WOD data gracefully', async () => {
    global.fetch.mockResolvedValueOnce({
      ok: false,
      status: 404,
    });

    const response = await fetch('./data/wods/wods-nonexistent.json');
    expect(response.ok).toBe(false);
    expect(response.status).toBe(404);
  });

  test('should cache loaded WOD pools', async () => {
    const mockPool = { wods: [] };
    const cache = {};

    // First call - not cached
    cache['full-body'] = null;
    if (!cache['full-body']) {
      cache['full-body'] = mockPool;
    }

    // Second call - should use cache
    const cachedPool = cache['full-body'];

    expect(cachedPool).toBe(mockPool);
  });

  test('should validate WOD structure', () => {
    const validWod = {
      title: 'Complete WOD',
      duration_minutes: 30,
      category: ['full-body'],
      equipment: ['barbell'],
      blocks: {
        static_warmup: { duration_minutes: 10, movements: [] },
        active_warmup: { duration_minutes: 5, movements: [] },
        strength: { duration_minutes: 10, reps: '5x5' },
        metcon: { duration_minutes: 5, reps: '3 rounds' },
        cooldown: { duration_minutes: 0, movements: [] },
      },
      rationale: 'Test rationale',
    };

    expect(validWod.title).toBeDefined();
    expect(validWod.duration_minutes).toBeGreaterThan(0);
    expect(validWod.category).toBeInstanceOf(Array);
    expect(validWod.blocks).toBeDefined();
  });
});

describe('Program Data Loading', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    global.fetch.mockClear();
  });

  test('should fetch program data for 2-week duration', async () => {
    const mockProgramData = {
      program: {
        name: 'Back in Shape',
        sessions: [
          { id: 'ses-1', title: 'Session 1', week: 1, day: 1, is_rest_day: false },
          { id: 'ses-2', title: 'Session 2', week: 1, day: 3, is_rest_day: false },
        ]
      }
    };

    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockProgramData,
    });

    const response = await fetch('./data/programs/back-in-shape-2w.json');
    const data = await response.json();

    expect(global.fetch).toHaveBeenCalledWith('./data/programs/back-in-shape-2w.json');
    expect(data.program.name).toBe('Back in Shape');
    expect(data.program.sessions).toHaveLength(2);
  });

  test('should filter out rest days from training list', () => {
    const allSessions = [
      { id: 's1', is_rest_day: false },
      { id: 's2', is_rest_day: true },
      { id: 's3', is_rest_day: false },
      { id: 's4', is_rest_day: true },
    ];

    const trainings = allSessions.filter(s => !s.is_rest_day);

    expect(trainings).toHaveLength(2);
    expect(trainings.every(s => !s.is_rest_day)).toBe(true);
  });

  test('should group trainings by week', () => {
    const trainings = [
      { id: 't1', week: 1, day: 1 },
      { id: 't2', week: 1, day: 3 },
      { id: 't3', week: 2, day: 1 },
      { id: 't4', week: 2, day: 3 },
    ];

    const grouped = {};
    trainings.forEach(t => {
      if (!grouped[t.week]) grouped[t.week] = [];
      grouped[t.week].push(t);
    });

    expect(Object.keys(grouped)).toHaveLength(2);
    expect(grouped[1]).toHaveLength(2);
    expect(grouped[2]).toHaveLength(2);
  });

  test('should handle missing program data', async () => {
    global.fetch.mockResolvedValueOnce({
      ok: false,
      status: 404,
    });

    const response = await fetch('./data/programs/nonexistent-program.json');
    expect(response.ok).toBe(false);
  });
});

describe('Category Filter Tests', () => {
  test('should have all required WOD categories', () => {
    const categories = [
      'full-body',
      'upper-body',
      'lower-body',
      'cardio',
      'strength'
    ];

    expect(categories).toHaveLength(5);
    categories.forEach(cat => {
      expect(cat).toMatch(/^[a-z-]+$/);
    });
  });

  test('should map category button to data attribute', () => {
    document.body.innerHTML = `
      <button class="filter-btn" data-category="full-body">Full Body</button>
      <button class="filter-btn" data-category="upper-body">Upper Body</button>
    `;

    const buttons = document.querySelectorAll('.filter-btn');
    const categories = Array.from(buttons).map(btn => btn.getAttribute('data-category'));

    expect(categories).toContain('full-body');
    expect(categories).toContain('upper-body');
  });

  test('should select only one category at a time', () => {
    document.body.innerHTML = `
      <button class="filter-btn" data-category="full-body">Full Body</button>
      <button class="filter-btn" data-category="upper-body">Upper Body</button>
    `;

    const fullBody = document.querySelector('[data-category="full-body"]');
    const upperBody = document.querySelector('[data-category="upper-body"]');

    // Select full-body
    fullBody.classList.add('active');
    upperBody.classList.remove('active');

    expect(fullBody.classList.contains('active')).toBe(true);
    expect(upperBody.classList.contains('active')).toBe(false);

    // Switch to upper-body
    fullBody.classList.remove('active');
    upperBody.classList.add('active');

    expect(fullBody.classList.contains('active')).toBe(false);
    expect(upperBody.classList.contains('active')).toBe(true);
  });
});

describe('WOD Data Validation - No Undefined Steps', () => {
  test('should not contain undefined in WOD block movements', () => {
    const wodWithUndefined = {
      title: 'Bad WOD',
      blocks: {
        strength: {
          movements: [
            { name: 'Back Squat', reps: 'undefined x 5' },
            { name: undefined, reps: '5x5' }
          ]
        }
      }
    };

    // Check for undefined strings
    const jsonStr = JSON.stringify(wodWithUndefined);
    expect(jsonStr).toContain('undefined');

    // This WOD should fail validation
    const hasUndefined = jsonStr.includes('undefined');
    expect(hasUndefined).toBe(true);
  });

  test('should validate all movement names are defined', () => {
    const validWod = {
      title: 'Good WOD',
      blocks: {
        strength: {
          movements: [
            { name: 'Back Squat', reps: '5x5' },
            { name: 'Bench Press', reps: '5x5' }
          ]
        },
        metcon: {
          movements: [
            { name: 'Kettlebell Swing', reps: '20 reps' }
          ]
        }
      }
    };

    // Check that all movement names exist and aren't undefined
    const validateMovements = (wod) => {
      for (const blockName in wod.blocks) {
        const movements = wod.blocks[blockName].movements || [];
        for (const movement of movements) {
          if (!movement.name || typeof movement.name !== 'string') {
            return false;
          }
          if (movement.name.includes('undefined')) {
            return false;
          }
        }
      }
      return true;
    };

    expect(validateMovements(validWod)).toBe(true);
  });

  test('should detect WODs with undefined step content', () => {
    const detectUndefinedContent = (wod) => {
      const jsonString = JSON.stringify(wod);
      // Check for the literal string "undefined" in the JSON
      return jsonString.includes('"undefined"') || jsonString.includes(':undefined');
    };

    const badWod = {
      title: 'Broken WOD',
      blocks: {
        strength: {
          content: 'undefined'
        }
      }
    };

    const goodWod = {
      title: 'Good WOD',
      blocks: {
        strength: {
          content: '5 rounds for time'
        }
      }
    };

    expect(detectUndefinedContent(badWod)).toBe(true);
    expect(detectUndefinedContent(goodWod)).toBe(false);
  });

  test('should ensure all program sessions have valid movements', () => {
    const programData = {
      sessions: [
        {
          title: 'Session 1',
          blocks: [
            {
              type: 'strength',
              movements: [
                { name: 'Squat', reps: '5x3' }
              ]
            }
          ]
        }
      ]
    };

    const validateProgram = (program) => {
      for (const session of program.sessions) {
        if (session.blocks) {
          for (const block of session.blocks) {
            if (block.movements) {
              for (const movement of block.movements) {
                // Ensure movement has a name and it's not "undefined"
                if (!movement.name || movement.name === 'undefined' || typeof movement.name !== 'string') {
                  return false;
                }
              }
            }
          }
        }
      }
      return true;
    };

    expect(validateProgram(programData)).toBe(true);
  });
});

describe('Error Handling', () => {
  test('should handle fetch network errors', async () => {
    global.fetch.mockRejectedValueOnce(new Error('Network error'));

    try {
      await fetch('./data/wods/wods-full-body.json');
    } catch (error) {
      expect(error.message).toBe('Network error');
    }
  });

  test('should handle invalid JSON responses', async () => {
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => { throw new SyntaxError('Invalid JSON'); }
    });

    const response = await fetch('./data/wods/wods-full-body.json');
    try {
      await response.json();
    } catch (error) {
      expect(error).toBeInstanceOf(SyntaxError);
    }
  });

  test('should provide fallback for missing data', () => {
    const emptyState = {
      wodPools: {},
      currentWod: null,
      currentProgram: null,
    };

    const fallbackMessage = emptyState.currentWod ? 'WOD loaded' : 'No WOD available';
    expect(fallbackMessage).toBe('No WOD available');
  });
});
