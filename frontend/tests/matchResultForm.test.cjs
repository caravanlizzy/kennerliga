const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const ts = require('typescript');
const { parse, compileScript } = require('@vue/compiler-sfc');
const vue = require('vue');

function mountForm() {
  const source = fs.readFileSync('src/components/league/MatchResultForm.vue', 'utf8');
  const { descriptor } = parse(source, { filename: 'MatchResultForm.vue' });
  const compiled = compileScript(descriptor, { id: 'match-result-form' });
  const code = ts.transpile(compiled.content, {
    module: ts.ModuleKind.CommonJS,
  });
  const exports = {};
  const requests = [];
  const leagueStore = {
    members: vue.ref([{ id: 1, profile: 101, profile_name: 'Alice' }]),
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
          fetchOrderedWinConditions: async () => [],
          fetchSelectedGame: async (selectedGameId) => {
            requests.push({ name: 'fetchSelectedGame', selectedGameId });
            return { game: 20 };
          },
          submitMatchResults: async () => {},
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
  });

  exports.default.setup(
    { selectedGameId: 5, leagueId: 12, league: { season: 7 } },
    { expose() {}, emit() {} }
  );

  return requests;
}

test('match result form runs its immediate watchers when mounted', async () => {
  const requests = mountForm();
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