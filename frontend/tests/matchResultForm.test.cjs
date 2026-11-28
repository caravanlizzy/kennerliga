const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const ts = require('typescript');
const { parse, compileScript } = require('@vue/compiler-sfc');
const vue = require('vue');

function mountForm(options = {}) {
  const source = fs.readFileSync('src/components/league/MatchResultForm.vue', 'utf8');
  const { descriptor } = parse(source, { filename: 'MatchResultForm.vue' });
  const compiled = compileScript(descriptor, { id: 'match-result-form' });
  const code = ts.transpile(compiled.content, {
    module: ts.ModuleKind.CommonJS,
  });
  const exports = {};
  const requests = [];
  const leagueStore = {
    members: vue.ref([
      { id: 1, profile: 101, profile_name: 'Alice' },
      { id: 2, profile: 102, profile_name: 'Bob' },
    ]),
    initialized: vue.ref(true),
    leagueData: { season: 7 },
    init() {},
  };

  vm.runInNewContext(code, {
    exports,
    require(name) {
      if (name === 'vue') return { ...vue, onMounted() {} };
      if (name === 'src/services/resultService') {
        return {
          fetchMatchResults: async (params) => {
            requests.push({ name: 'fetchMatchResults', params });
            return [];
          },
          fetchOrderedWinConditions: async () => [
            { id: 1, name: 'Points', condition_type: 'POINTS' },
          ],
          fetchSelectedGame: async (selectedGameId) => {
            requests.push({ name: 'fetchSelectedGame', selectedGameId });
            return { game: 20, game_link: options.gameLink ?? '' };
          },
          submitMatchResults: async (payload) => {
            requests.push({ name: 'submitMatchResults', payload });
            if (options.submitResponse) {
              return options.submitResponse(payload);
            }
            return { status: 200 };
          },
        };
      }
      if (name === 'src/services/gameService') {
        return {
          fetchFactionsForGame: async () => [],
          fetchResultConfigForGame: async () => ({ id: 30 }),
        };
      }
      if (name === 'quasar') return { useQuasar: () => ({ notify() {} }) };
      if (name === 'pinia') {
        return {
          storeToRefs: (store) => ({
            members: store.members,
            initialized: store.initialized,
          }),
        };
      }
      if (name === 'stores/leagueStore') {
        return { useLeagueStore: () => () => leagueStore };
      }
      if (name.endsWith('.vue')) return {};
      if (name === 'src/types') return {};
      throw new Error(`Unexpected import: ${name}`);
    },
    console,
    URL,
  });

  const setupResult = exports.default.setup(
    { selectedGameId: 5, leagueId: 12, league: { season: 7 } },
    { expose() {}, emit() {} }
  );

  return { requests, setupResult, leagueStore };
}

test('match result form runs its immediate watchers when mounted', async () => {
  const { requests } = mountForm();
  await new Promise((resolve) => setImmediate(resolve));

  assert.equal(
    requests.filter((request) => request.name === 'fetchSelectedGame').length,
    2
  );
  const resultRequest = requests.find(
    (request) => request.name === 'fetchMatchResults'
  );
  assert.ok(resultRequest);
  assert.equal(resultRequest.params.seasonId, 7);
  assert.equal(resultRequest.params.leagueId, 12);
  assert.equal(resultRequest.params.selectedGameId, 5);
});

test('match result form resets tie breaker fields when a 202 tie breaker is received', async () => {
  let submitCount = 0;
  const { requests, setupResult } = mountForm({
    gameLink: 'https://example.com/match/123',
    submitResponse: () => {
      submitCount++;
      if (submitCount === 1) {
        return {
          status: 202,
          data: {
            required_tie_breaker: { id: 1, name: 'First Tie Breaker' },
            tied_players: [101, 102],
          },
        };
      }
      return {
        status: 202,
        data: {
          required_tie_breaker: { id: 2, name: 'Second Tie Breaker' },
          tied_players: [101, 102],
        },
      };
    },
  });

  await new Promise((resolve) => setImmediate(resolve));

  // Initialize points for both players
  setupResult.formData.value.forEach((entry) => {
    entry.points = 100;
  });

  // First submit -> triggers tie breaker 1
  await setupResult.submitResults();

  assert.equal(
    requests.filter((request) => request.name === 'submitMatchResults')[0]
      .payload.game_link,
    'https://example.com/match/123'
  );
  assert.equal(setupResult.tieBreakerRequired.value, true);
  assert.equal(setupResult.requiredTieBreaker.value.id, 1);
  assert.equal(setupResult.formData.value[0].tie_breaker_value, null);
  assert.equal(setupResult.formData.value[1].tie_breaker_value, null);

  // User enters values for first tie breaker
  setupResult.formData.value[0].tie_breaker_value = 5;
  setupResult.formData.value[1].tie_breaker_value = 5;

  // Second submit -> triggers tie breaker 2 (still tied)
  await setupResult.submitResults();

  assert.equal(
    requests.filter((request) => request.name === 'submitMatchResults')[1]
      .payload.game_link,
    'https://example.com/match/123'
  );
  assert.equal(setupResult.tieBreakerRequired.value, true);
  assert.equal(setupResult.requiredTieBreaker.value.id, 2);
  // Values should be reset to null for the second tie breaker
  assert.equal(setupResult.formData.value[0].tie_breaker_value, null);
  assert.equal(setupResult.formData.value[1].tie_breaker_value, null);
});

test('match result form loads, submits, validates, and resets the game link', async () => {
  const { requests, setupResult } = mountForm({
    gameLink: 'https://example.com/match/123',
  });
  await new Promise((resolve) => setImmediate(resolve));

  assert.equal(setupResult.gameLink.value, 'https://example.com/match/123');
  setupResult.formData.value.forEach((entry, index) => {
    entry.points = index === 0 ? 10 : 8;
  });
  setupResult.gameLink.value = 'https://example.com/match/456';
  await setupResult.submitResults();

  const submission = requests.find(
    (request) => request.name === 'submitMatchResults'
  );
  assert.equal(submission.payload.game_link, 'https://example.com/match/456');

  setupResult.gameLink.value = 'javascript:alert(1)';
  await setupResult.submitResults();
  assert.equal(
    requests.filter((request) => request.name === 'submitMatchResults').length,
    1
  );

  setupResult.initFormData();
  assert.equal(setupResult.gameLink.value, 'https://example.com/match/123');
});