const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const ts = require('typescript');
const vue = require('vue');

function loadTypeScriptModule(path) {
  const source = fs.readFileSync(path, 'utf8');
  const code = ts.transpile(source, { module: ts.ModuleKind.CommonJS });
  const exports = {};

  vm.runInNewContext(code, {
    exports,
    require(name) {
      if (name === 'vue') return vue;
      throw new Error(`Unexpected import: ${name}`);
    },
  });

  return exports;
}

test('game form maps related game ids between DTO and payload', () => {
  const { useGameForm } = loadTypeScriptModule('src/composables/gameForm.ts');
  const form = useGameForm();

  form.loadFromDto({
    id: 1,
    name: 'Gaia Project',
    short_name: 'Gaia',
    platform: 10,
    related_games: [2, 3],
    options: [],
  });

  assert.deepEqual(Array.from(form.buildPayload(10).related_games), [2, 3]);

  const newGameForm = useGameForm();
  assert.deepEqual(Array.from(newGameForm.buildPayload(10).related_games), []);
});

test('related game choices exclude the current game and show platform names', () => {
  const { getRelatedGameOptions } = loadTypeScriptModule(
    'src/composables/relatedGames.ts'
  );
  const games = [
    { id: 1, name: 'Gaia Project', platform: 10 },
    { id: 2, name: 'Gaia Project', platform: 11 },
    { id: 3, name: 'Terra Mystica', platform: 10 },
  ];
  const platforms = [
    { id: 10, name: 'Board Game Arena' },
    { id: 11, name: 'Steam' },
  ];

  assert.deepEqual(
    getRelatedGameOptions(games, platforms, 1).map((option) => option.label),
    ['Gaia Project (Steam)', 'Terra Mystica (Board Game Arena)']
  );
  assert.deepEqual(
    getRelatedGameOptions(games, platforms, 1, 'steam').map((option) => option.id),
    [2]
  );
});