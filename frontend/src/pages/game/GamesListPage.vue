<template>
  <div class="q-mb-md">
    <q-btn
      flat
      dense
      color="primary"
      :icon="showPopularGames ? 'expand_less' : 'leaderboard'"
      label="Picks & Bans"
      :aria-expanded="showPopularGames"
      @click="togglePopularGames"
    />

    <q-slide-transition>
      <div v-show="showPopularGames" class="q-mt-sm">
        <q-card flat bordered class="q-pa-md">
          <div
            class="row items-center q-col-gutter-sm q-mb-md"
            :class="isMobile ? 'justify-start' : 'justify-between'"
          >
            <div class="col-12 col-md-auto">
              <KennerPlayerCountFilter
                v-model="selectedPlayerCounts"
                :available-counts="availablePlayerCounts"
                label="Players:"
              />
            </div>
            <div class="col-12 col-md-auto">
              <q-select
                v-model="selectedYears"
                :options="availableYears"
                multiple
                clearable
                dense
                outlined
                options-dense
                placeholder="All Years"
                :display-value="
                  selectedYears.length === 0
                    ? 'All Years'
                    : selectedYears
                        .slice()
                        .sort((a, b) => b - a)
                        .join(', ')
                "
                label="Years"
                class="years-select"
              >
                <template #prepend>
                  <q-icon name="event" size="xs" color="grey-6" />
                </template>
              </q-select>
            </div>
          </div>

          <q-skeleton
            v-if="loadingYears || loadingPopular"
            type="rect"
            height="180px"
            class="rounded-borders"
          />
          <q-banner v-else-if="popularError" rounded dense>
            <template #avatar>
              <q-icon name="warning" color="negative" />
            </template>
            {{ popularError }}
            <template #action>
              <q-btn
                flat
                dense
                color="primary"
                label="Retry"
                @click="loadPopular"
              />
            </template>
          </q-banner>
          <PopularGamesCard
            v-else
            :popular="popular"
            @select="navigateToGame"
          />
        </q-card>
      </div>
    </q-slide-transition>
  </div>

  <KennerTable
    v-if="!loading && !error && data && Array.isArray(data)"
    :create-button="button"
    flat
    row-key="id"
    @row-click="onRowClick"
    :rows="data"
    :columns="columns"
  >
    <template v-slot:body-cell-actions="props">
      <q-td :props="props" class="q-gutter-x-xs">
        <q-btn
          flat
          round
          dense
          size="sm"
          icon="query_stats"
          color="primary"
          title="View Statistics"
          @click.stop="
            router.push({ name: 'game-detail', params: { id: props.row.id } })
          "
        />
        <q-btn
          v-if="isAdmin"
          flat
          round
          dense
          size="sm"
          icon="settings"
          color="secondary"
          title="View Configuration"
          @click.stop="
            router.push({ name: 'game-config', params: { id: props.row.id } })
          "
        />
        <q-btn
          v-if="isAdmin"
          flat
          round
          dense
          size="sm"
          icon="edit"
          color="grey-7"
          title="Edit Game"
          @click.stop="
            router.push({ name: 'game-edit', params: { id: props.row.id } })
          "
        />
      </q-td>
    </template>
  </KennerTable>

  <div v-else class="q-py-md">
    <q-banner v-if="error" rounded dense class="q-mb-sm">
      <template #avatar><q-icon name="warning" color="negative" /></template>
      {{ error }}
    </q-banner>
    <q-skeleton v-else height="180px" square />
  </div>
</template>

<script setup lang="ts">
import KennerTable from 'components/tables/KennerTable.vue';
import KennerPlayerCountFilter from 'components/base/KennerPlayerCountFilter.vue';
import PopularGamesCard from 'components/statistics/PopularGamesCard.vue';
import { useAsyncData } from 'src/composables/asyncData';
import { useResponsive } from 'src/composables/responsive';
import {
  fetchGamesForManagement,
  fetchPlatforms,
} from 'src/services/gameService';
import { fetchPopularGames } from 'src/services/statisticsService';
import { useRouter } from 'vue-router';
import { TGameDto, TKennerButton, TPlatform, TPopularGames } from 'src/types';
import { computed, ref, watch } from 'vue';
import { useUserStore } from 'stores/userStore';
import { storeToRefs } from 'pinia';

type GameRow = TGameDto;

const userStore = useUserStore();
const { isAdmin } = storeToRefs(userStore);
const { getAvailableYears } = userStore;
const { isMobile } = useResponsive();

const showPopularGames = ref(false);
const availablePlayerCounts = ['2p', '3p', '4p'];
const selectedPlayerCounts = ref<string[]>(['4p']);
const selectedYears = ref<number[]>([]);
const availableYears = ref<number[]>([]);
const yearsLoaded = ref(false);
const loadingYears = ref(false);
const loadingPopular = ref(false);
const popular = ref<TPopularGames | null>(null);
const popularError = ref<string | null>(null);
let popularRequestId = 0;

const playerCountsParam = computed(() =>
  selectedPlayerCounts.value.length > 0 ? selectedPlayerCounts.value : undefined
);

async function loadPopular() {
  const requestId = ++popularRequestId;
  loadingPopular.value = true;
  popular.value = null;
  popularError.value = null;
  try {
    const result = await fetchPopularGames(
      selectedYears.value.length > 0 ? selectedYears.value : undefined,
      playerCountsParam.value
    );
    if (requestId !== popularRequestId) return;
    if (result === null) {
      popularError.value = 'Unable to load Picks & Bans. Please try again.';
      return;
    }
    popular.value = result;
  } catch (error) {
    if (requestId !== popularRequestId) return;
    console.error('Failed to load popular games:', error);
    popularError.value = 'Unable to load Picks & Bans. Please try again.';
  } finally {
    if (requestId === popularRequestId) loadingPopular.value = false;
  }
}

async function togglePopularGames() {
  showPopularGames.value = !showPopularGames.value;
  if (!showPopularGames.value) return;

  if (!yearsLoaded.value && !loadingYears.value) {
    loadingYears.value = true;
    try {
      availableYears.value = await getAvailableYears();
    } catch (error) {
      console.error('Failed to load available years:', error);
      availableYears.value = [];
    } finally {
      yearsLoaded.value = true;
      loadingYears.value = false;
    }
    if (showPopularGames.value) await loadPopular();
  } else if (yearsLoaded.value && !popular.value && !loadingPopular.value) {
    await loadPopular();
  }
}

watch(
  [selectedYears, selectedPlayerCounts],
  () => {
    if (!yearsLoaded.value) return;
    if (showPopularGames.value) {
      void loadPopular();
    } else {
      popularRequestId++;
      popular.value = null;
      popularError.value = null;
      loadingPopular.value = false;
    }
  },
  { deep: true }
);

function navigateToGame(gameId: number) {
  router.push({ name: 'game-detail', params: { id: gameId } });
}

// Fetch games
const {
  data,
  isFinished,
  error: gamesError,
} = useAsyncData<GameRow[]>(fetchGamesForManagement, []);

// Fetch platforms
const {
  data: platformData,
  isFinished: isPlatformFinished,
  error: platformError,
} = useAsyncData<TPlatform[]>(fetchPlatforms, []);

// Unified loading/error
const loading = computed(() => !isFinished.value || !isPlatformFinished.value);
const error = computed(
  () => gamesError?.value?.message || platformError?.value?.message || null
);

// Build a map id->name from platformData (reactive, no manual watch needed)
const platformMap = computed<Record<string, string>>(() => {
  const arr = platformData.value;
  const map: Record<string, string> = {};
  for (const p of arr) {
    // coerce id to string to avoid 1 vs "1" mismatches
    map[String(p.id)] = p.name;
  }
  return map;
});

// Small helper to resolve platform label from a row
function lookupPlatform(row: GameRow) {
  return platformMap.value[String(row.platform)] ?? 'Unknown Platform';
}

// Router navigation
const router = useRouter();
function onRowClick(_evt: unknown, row: GameRow) {
  router.push({ name: 'game-detail', params: { id: row.id } });
}

// Create button
const button = computed<TKennerButton | undefined>(() => {
  if (!isAdmin.value) return undefined;
  return {
    color: 'secondary',
    label: 'Game',
    icon: 'add_circle',
    forwardName: 'game-create',
  };
});

// Reactive columns
const columns = computed(() => [
  {
    name: 'game',
    label: 'Game',
    field: (x: GameRow) => x.name,
    align: 'left',
    sortable: true,
  },
  {
    name: 'platform',
    label: 'Platform',
    field: (x: GameRow) => lookupPlatform(x),
    align: 'left',
    sortable: true,
  },
  {
    name: 'actions',
    label: 'Actions',
    field: () => '',
    align: 'right',
    sortable: false,
  },
]);
</script>

<style scoped lang="scss">
.years-select {
  min-width: 180px;
}

@media (max-width: 1023px) {
  .years-select {
    width: 100%;
  }
}
</style>
