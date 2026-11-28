<template>
  <div>
    <KennerSelect
      v-model="selectedGameIds"
      :options="filteredOptions"
      label="Related games"
      option-label="label"
      option-value="id"
      multiple
      use-input
      use-chips
      hide-selected
      emit-value
      map-options
      clearable
      @filter="filterOptions"
    >
      <template #no-option>
        <q-item>
          <q-item-section class="text-grey">No games found</q-item-section>
        </q-item>
      </template>
    </KennerSelect>
    <div class="text-caption text-grey-7 q-mt-xs">
      ct pairs. Link every equivalent platform version; linking
      two games to a third does not link them to each other.
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue';
import KennerSelect from 'components/base/KennerSelect.vue';
import { getRelatedGameOptions } from 'src/composables/relatedGames';
import type { TGameDto, TPlatform } from 'src/types';

const selectedGameIds = defineModel<number[]>({ default: () => [] });

const props = defineProps<{
  games: TGameDto[];
  platforms: TPlatform[];
  currentGameId?: number;
}>();

const searchText = ref('');
const allOptions = computed(() =>
  getRelatedGameOptions(props.games, props.platforms, props.currentGameId)
);
const filteredOptions = computed(() => {
  const selectedIds = new Set(selectedGameIds.value);
  const selectedOptions = allOptions.value.filter((option) =>
    selectedIds.has(option.id)
  );
  const matchingOptions = getRelatedGameOptions(
    props.games,
    props.platforms,
    props.currentGameId,
    searchText.value
  );
  const optionsById = new Map(
    [...selectedOptions, ...matchingOptions].map((option) => [
      option.id,
      option,
    ])
  );

  return [...optionsById.values()];
});

function filterOptions(value: string, update: (callback: () => void) => void) {
  update(() => {
    searchText.value = value;
  });
}
</script>
