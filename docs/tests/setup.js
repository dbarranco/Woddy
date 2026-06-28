// Jest setup file
global.localStorage = {
  data: {},
  getItem(key) {
    return this.data[key] || null;
  },
  setItem(key, value) {
    this.data[key] = value.toString();
  },
  removeItem(key) {
    delete this.data[key];
  },
  clear() {
    this.data = {};
  },
};

// Mock fetch for tests
global.fetch = jest.fn();

// Mock navigator.serviceWorker
Object.defineProperty(navigator, 'serviceWorker', {
  value: {
    register: jest.fn(() => Promise.resolve({})),
  },
  writable: true,
});
