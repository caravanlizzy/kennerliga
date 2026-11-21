const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const ts = require('typescript');
const { ref } = require('vue');

function createStore(fetchProfiles) {
  const source = fs.readFileSync('src/stores/eloStore.ts', 'utf8');
  const code = ts.transpile(source, { module: ts.ModuleKind.CommonJS });
  const exports = {};
  const subscriptions = {};
  vm.runInNewContext(code, {
    exports,
    console,
    require(name) {
      if (name === 'pinia') {
        return { defineStore: (_name, setup, options) => () => ({ ...setup(), options }) };
      }
      if (name === 'vue') return { ref };
      if (name === 'src/services/userService') return { fetchProfiles };
      if (name === 'src/stores/updateStore') {
        return { useUpdateStore: () => ({ subscribe: (topic, fn) => { subscriptions[topic] = fn; } }) };
      }
      throw new Error(`Unexpected import: ${name}`);
    },
  });
  return { store: exports.useEloStore(), subscriptions };
}

test('restored ratings are refreshed in a new session', () => {
  const { store } = createStore(async () => []);
  const restored = { initialized: true };
  store.options.persist.afterRestore({ store: restored });
  assert.equal(restored.initialized, false);
});

test('an update during a fetch triggers a subsequent refresh', async () => {
  let resolveFirst;
  let calls = 0;
  const { store, subscriptions } = createStore(() => {
    calls++;
    if (calls === 1) return new Promise((resolve) => { resolveFirst = resolve; });
    return Promise.resolve([{ username: 'alice', elo_rating: 1600, elo_rank: 1 }]);
  });
  store.initUpdateSubscription();
  const first = store.fetchProfiles();
  const refresh = subscriptions['/result/']();
  resolveFirst([{ username: 'alice', elo_rating: 1500, elo_rank: 2 }]);
  await first;
  await refresh;
  assert.equal(calls, 2);
  assert.equal(store.getElo('alice').eloRating, 1600);
});

test('username takes precedence over another profile display name', async () => {
  const { store } = createStore(async () => [
    { username: 'other', profile_name: 'Alice', elo_rating: 1400 },
    { username: 'alice', profile_name: 'Ally', elo_rating: 1600 },
  ]);
  await store.fetchProfiles();
  assert.equal(store.getElo('Alice', 'alice').eloRating, 1600);
});