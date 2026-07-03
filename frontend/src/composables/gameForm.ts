import { ref, type Ref } from 'vue';
import type { TFullGameDto, TPlatform } from 'src/types';

// ---------------------------------------------------------------------------
// Shared UI-side types for the game form (create + edit).
// ---------------------------------------------------------------------------

export type ConditionKind = 'value' | 'choice';

export type UiChoice = {
  id?: number;
  ref: string;
  name: string;
  order: number;
};

export type UiCondition = {
  id: string; // client-side ID for list rendering
  depends_on_option_ref: string | null;
  kind: ConditionKind;
  expected_value: boolean | null;
  expected_choice_ref: string | null;
  negate: boolean;
};

export type UiGroup = {
  id: string; // client-side ID for list rendering
  conditions: UiCondition[];
};

export type UiOption = {
  id?: number;
  ref: string;
  name: string;
  order: number;
  has_choices: boolean;
  choices: UiChoice[];
  availability_groups: UiGroup[];
};

// ---------------------------------------------------------------------------
// Public composable
// ---------------------------------------------------------------------------

/**
 * Composable that centralises the shared state, mutators and validation
 * for the "game" form used by both GameCreatePage and EditGamePage.
 *
 * The two pages only differ in:
 *   - how they load their initial data (create starts empty, edit calls
 *     `loadFromDto`), and
 *   - how they submit (POST vs PUT). `buildPayload` returns the shared
 *     request body; callers add the id / send the request themselves.
 */
export function useGameForm() {
  // ---- Basic fields ----
  const name = ref('');
  const shortName = ref('');
  const selectable = ref(true);
  const minPlayers = ref(2);
  const maxPlayers = ref(4);
  const platforms = ref<TPlatform[]>([]);

  // In create mode the value is a full TPlatform object (matches KennerSelect
  // usage there); in edit mode it's the id (number). We keep the type wide
  // and let the caller narrow via a computed if needed.
  const platform = ref<TPlatform | number | null>(null);

  const gameOptions: Ref<UiOption[]> = ref<UiOption[]>([]);

  // ---- Helpers ----
  function newRef(): string {
    if (typeof crypto !== 'undefined' && 'randomUUID' in crypto) {
      // @ts-expect-error TS lib may not include randomUUID
      return crypto.randomUUID();
    }
    return `${Date.now()}-${Math.random().toString(16).slice(2)}`;
  }

  function resortOrders(): void {
    gameOptions.value.forEach((opt, idx) => {
      opt.order = (idx + 1) * 10;
      opt.choices.forEach((ch, cIdx) => {
        ch.order = (cIdx + 1) * 10;
      });
    });
  }

  // ---- Option manipulation ----
  function addEmptyOption(): void {
    const nextOrder = (gameOptions.value.length + 1) * 10;
    gameOptions.value.push({
      ref: newRef(),
      name: '',
      order: nextOrder,
      has_choices: false,
      choices: [],
      availability_groups: [],
    });
  }

  function moveOption(index: number, direction: 'up' | 'down'): void {
    const newIndex = direction === 'up' ? index - 1 : index + 1;
    if (newIndex < 0 || newIndex >= gameOptions.value.length) return;
    const tmp = gameOptions.value[index];
    gameOptions.value[index] = gameOptions.value[newIndex];
    gameOptions.value[newIndex] = tmp;
    resortOrders();
  }

  function removeOption(optionRef: string): void {
    gameOptions.value = gameOptions.value.filter((o) => o.ref !== optionRef);
  }

  // ---- Choice manipulation ----
  function addChoice(optionRef: string): void {
    const opt = gameOptions.value.find((o) => o.ref === optionRef);
    if (!opt) return;
    const nextOrder = (opt.choices.length + 1) * 10;
    opt.choices.push({
      ref: newRef(),
      name: '',
      order: nextOrder,
    });
  }

  function moveChoice(
    optionRef: string,
    choiceIndex: number,
    direction: 'up' | 'down'
  ): void {
    const opt = gameOptions.value.find((o) => o.ref === optionRef);
    if (!opt) return;
    const newIndex = direction === 'up' ? choiceIndex - 1 : choiceIndex + 1;
    if (newIndex < 0 || newIndex >= opt.choices.length) return;
    const tmp = opt.choices[choiceIndex];
    opt.choices[choiceIndex] = opt.choices[newIndex];
    opt.choices[newIndex] = tmp;
    resortOrders();
  }

  function removeChoice(optionRef: string, choiceRef: string): void {
    const opt = gameOptions.value.find((o) => o.ref === optionRef);
    if (!opt) return;
    opt.choices = opt.choices.filter((c) => c.ref !== choiceRef);

    // If any condition referenced that choice, clear it
    for (const grp of opt.availability_groups) {
      for (const cond of grp.conditions) {
        if (cond.expected_choice_ref === choiceRef) {
          cond.expected_choice_ref = null;
        }
      }
    }
  }

  // ---- Availability group / condition manipulation ----
  function addAvailabilityGroup(optionRef: string): void {
    const opt = gameOptions.value.find((o) => o.ref === optionRef);
    if (!opt) return;
    opt.availability_groups.push({
      id: newRef(),
      conditions: [],
    });
  }

  function removeAvailabilityGroup(optionRef: string, groupId: string): void {
    const opt = gameOptions.value.find((o) => o.ref === optionRef);
    if (!opt) return;
    opt.availability_groups = opt.availability_groups.filter(
      (g) => g.id !== groupId
    );
  }

  function addCondition(optionRef: string, groupId: string): void {
    const opt = gameOptions.value.find((o) => o.ref === optionRef);
    if (!opt) return;
    const grp = opt.availability_groups.find((g) => g.id === groupId);
    if (!grp) return;
    grp.conditions.push({
      id: newRef(),
      depends_on_option_ref: null,
      kind: 'value',
      expected_value: true,
      expected_choice_ref: null,
      negate: false,
    });
  }

  function removeCondition(
    optionRef: string,
    groupId: string,
    conditionId: string
  ): void {
    const opt = gameOptions.value.find((o) => o.ref === optionRef);
    if (!opt) return;
    const grp = opt.availability_groups.find((g) => g.id === groupId);
    if (!grp) return;
    grp.conditions = grp.conditions.filter((c) => c.id !== conditionId);
  }

  function onConditionKindChanged(cond: UiCondition): void {
    if (cond.kind === 'value') {
      cond.expected_choice_ref = null;
      if (cond.expected_value === null) cond.expected_value = true;
    } else {
      cond.expected_value = null;
      cond.expected_choice_ref = null;
    }
  }

  // ---- Ref-option helpers used by condition selects ----
  function optionRefOptions(currentOptionRef: string) {
    return gameOptions.value
      .filter((o) => o.ref !== currentOptionRef)
      .map((o) => ({
        label: o.name?.trim()
          ? o.name
          : `(Unnamed option ${String(o.ref).slice(0, 6)})`,
        value: o.ref,
      }));
  }

  function choiceRefOptions(dependsOnOptionRef: string | null) {
    if (!dependsOnOptionRef) return [];
    const opt = gameOptions.value.find((o) => o.ref === dependsOnOptionRef);
    if (!opt) return [];
    return opt.choices.map((c) => ({
      label: c.name?.trim()
        ? c.name
        : `(Unnamed choice ${String(c.ref).slice(0, 6)})`,
      value: c.ref,
    }));
  }

  // ---- Client-side validation ----
  function validateAvailabilityClientSide(): string[] {
    const errors: string[] = [];
    const optionRefs = new Set<string>();
    for (const opt of gameOptions.value) {
      if (optionRefs.has(opt.ref))
        errors.push(`Duplicate option ref: ${opt.ref}`);
      optionRefs.add(opt.ref);

      const choiceRefs = new Set<string>();
      for (const ch of opt.choices) {
        if (choiceRefs.has(ch.ref))
          errors.push(`Duplicate choice ref in option "${opt.name}": ${ch.ref}`);
        choiceRefs.add(ch.ref);
      }
    }

    for (const opt of gameOptions.value) {
      for (const grp of opt.availability_groups) {
        for (const cond of grp.conditions) {
          if (!cond.depends_on_option_ref) {
            errors.push(
              `Option "${opt.name || '(unnamed)'}" has a condition missing "Depends on option".`
            );
            continue;
          }
          if (!optionRefs.has(cond.depends_on_option_ref)) {
            errors.push(
              `Condition depends_on_option_ref "${cond.depends_on_option_ref}" does not exist.`
            );
            continue;
          }
          if (cond.kind === 'value') {
            if (cond.expected_value === null)
              errors.push('A boolean condition is missing expected_value.');
          } else {
            if (!cond.expected_choice_ref)
              errors.push('A choice condition is missing expected_choice_ref.');
          }
        }
      }
    }

    return errors;
  }

  // ---- DTO <-> UI mapping (edit mode) ----
  function loadFromDto(gameData: TFullGameDto): void {
    name.value = gameData.name;
    shortName.value = (gameData as any).short_name || '';
    selectable.value = (gameData as any).selectable ?? true;
    minPlayers.value = (gameData as any).min_players ?? 2;
    maxPlayers.value = (gameData as any).max_players ?? 4;
    platform.value = gameData.platform as any;

    const optionMap = new Map<number, string>();
    const choiceMap = new Map<number, string>();

    // Pass 1: build ref maps for existing options / choices
    gameData.options.forEach((opt) => {
      const oId = Number(opt.id);
      optionMap.set(oId, newRef());
      (opt.choices || []).forEach((ch) => {
        const cId = Number(ch.id);
        choiceMap.set(cId, newRef());
      });
    });

    // Pass 2: build UI structure using those refs
    gameOptions.value = gameData.options.map((opt) => {
      const oId = Number(opt.id);
      const optRef = optionMap.get(oId)!;

      return {
        id: oId,
        ref: optRef,
        name: opt.name,
        order: (opt as any).order || 0,
        has_choices: opt.has_choices,
        choices: (opt.choices || []).map((ch) => {
          const cId = Number(ch.id);
          return {
            id: cId,
            ref: choiceMap.get(cId)!,
            name: ch.name,
            order: (ch as any).order || 0,
          };
        }),
        availability_groups: ((opt as any).availability_groups || []).map(
          (grp: any) => ({
            id: newRef(),
            conditions: (grp.conditions || []).map((cond: any) => {
              const dependsOnId =
                cond.depends_on_option_id ||
                (typeof cond.depends_on_option === 'object'
                  ? cond.depends_on_option?.id
                  : cond.depends_on_option);
              const expectedChoiceId =
                cond.expected_choice_id ||
                (typeof cond.expected_choice === 'object'
                  ? cond.expected_choice?.id
                  : cond.expected_choice);

              const dependsOnRef = dependsOnId
                ? optionMap.get(Number(dependsOnId))
                : null;
              const expectedChoiceRef = expectedChoiceId
                ? choiceMap.get(Number(expectedChoiceId))
                : null;

              return {
                id: newRef(),
                depends_on_option_ref: dependsOnRef || null,
                kind: (expectedChoiceId ? 'choice' : 'value') as ConditionKind,
                expected_value: cond.expected_value as boolean | null,
                expected_choice_ref: expectedChoiceRef || null,
                negate: !!cond.negate,
              };
            }),
          })
        ),
      };
    });
  }

  /**
   * Builds the payload body shared by both `POST /game/games-full/` (create)
   * and `PUT /game/games-full/{id}/` (update). In edit mode option / choice
   * `id` fields are included, in create mode they are simply undefined.
   *
   * @param platformId numeric platform id resolved by the caller
   *   (create page holds a full TPlatform object, edit page holds the id).
   */
  function buildPayload(platformId: number) {
    const effectiveShortName =
      shortName.value.trim() !== '' ? shortName.value.trim() : name.value;

    return {
      name: name.value,
      short_name: effectiveShortName,
      platform: platformId,
      selectable: selectable.value,
      min_players: Number(minPlayers.value),
      max_players: Number(maxPlayers.value),
      options: gameOptions.value.map((opt) => ({
        id: opt.id,
        ref: opt.ref,
        name: opt.name,
        order: opt.order,
        has_choices: opt.has_choices,
        choices: opt.choices.map((ch) => ({
          id: ch.id,
          ref: ch.ref,
          name: ch.name,
          order: ch.order,
        })),
        availability_groups: opt.availability_groups.map((grp) => ({
          conditions: grp.conditions.map((cond) => ({
            depends_on_option_ref: cond.depends_on_option_ref,
            negate: !!cond.negate,
            expected_value: cond.kind === 'value' ? cond.expected_value : null,
            expected_choice_ref:
              cond.kind === 'choice' ? cond.expected_choice_ref : null,
          })),
        })),
      })),
    };
  }

  return {
    // state
    name,
    shortName,
    selectable,
    minPlayers,
    maxPlayers,
    platform,
    platforms,
    gameOptions,
    // helpers
    newRef,
    resortOrders,
    // options
    addEmptyOption,
    moveOption,
    removeOption,
    // choices
    addChoice,
    moveChoice,
    removeChoice,
    // availability groups / conditions
    addAvailabilityGroup,
    removeAvailabilityGroup,
    addCondition,
    removeCondition,
    onConditionKindChanged,
    optionRefOptions,
    choiceRefOptions,
    // validation
    validateAvailabilityClientSide,
    // DTO helpers
    loadFromDto,
    buildPayload,
  };
}
