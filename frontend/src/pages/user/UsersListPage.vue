<template>
  <div class="q-mb-md filter-toolbar">
    <div class="filter-controls row items-center q-col-gutter-md">
      <!-- Player Count Filter -->
      <div class="filter-item row items-center q-gutter-x-sm">
        <div class="row items-center text-caption text-weight-bold text-grey-8 filter-label">
          <q-icon name="groups" size="18px" class="q-mr-xs text-primary" />
          <span>Players:</span>
        </div>
        <div class="row q-gutter-xs items-center">
          <q-chip
            clickable
            dense
            :outline="!isAllPlayerCountsSelected"
            :color="isAllPlayerCountsSelected ? 'primary' : 'grey-7'"
            text-color="white"
            size="sm"
            class="text-weight-bold"
            style="border-radius: 4px"
            @click="toggleAllPlayerCounts"
          >
            All
          </q-chip>
          <q-chip
            v-for="pc in availablePlayerCounts"
            :key="pc"
            clickable
            dense
            :outline="!selectedPlayerCounts.includes(pc)"
            :color="selectedPlayerCounts.includes(pc) ? 'primary' : 'grey-7'"
            text-color="white"
            size="sm"
            class="text-weight-bold"
            style="border-radius: 4px"
            @click="togglePlayerCount(pc)"
          >
            {{ pc.toUpperCase() }}
          </q-chip>
        </div>
      </div>

      <!-- Years Multi-select Filter -->
      <div class="filter-item row items-center q-gutter-x-sm">
        <div class="row items-center text-caption text-weight-bold text-grey-8 filter-label">
          <q-icon name="calendar_today" size="16px" class="q-mr-xs text-primary" />
          <span>Years:</span>
        </div>
        <q-select
          v-model="selectedYears"
          :options="availableYears"
          multiple
          clearable
          dense
          outlined
          options-dense
          placeholder="All Years"
          :display-value="!selectedYears || selectedYears.length === 0 ? 'All Years' : selectedYears.slice().sort((a, b) => b - a).join(', ')"
          class="bg-white rounded-borders years-select"
        >
          <template v-slot:prepend>
            <q-icon name="event" size="xs" color="grey-6" />
          </template>
        </q-select>
      </div>
    </div>
  </div>

  <KennerTable
    :create-button="createButton"
    flat
    @row-click="onRowClick"
    :rows="users"
    :columns="columns"
    :loading="loading"
  >
    <template v-slot:body-cell-user="props">
      <q-td :props="props">
        <div class="row items-center no-wrap q-gutter-x-sm cursor-pointer">
          <UserAvatar
            :display-username="props.row.username"
            :shape="props.row.avatar_shape"
            :color="props.row.avatar_color"
            :elo-rating="props.row.elo_rating ?? props.row.profile?.elo_rating"
            size="28px"
          />
          <span class="text-weight-medium">{{ props.row.username }}</span>
        </div>
      </q-td>
    </template>
    <template v-slot:body-cell-elo_rating="props">
      <q-td :props="props">
        <div class="row items-center justify-end no-wrap q-gutter-x-xs">
          <span class="text-weight-bold">{{ props.value }}</span>
          <q-badge
            v-if="isBestElo(props.row)"
            color="amber-9"
            text-color="white"
            class="text-weight-bolder"
            style="font-size: 0.65rem; padding: 2px 5px; border-radius: 4px;"
            label="best"
          />
        </div>
      </q-td>
    </template>
    <template v-slot:body-cell-win_rate="props">
      <q-td :props="props">
        <div class="row items-center justify-end no-wrap q-gutter-x-xs">
          <span>{{ props.value }}</span>
          <q-badge
            v-if="isBestWinRate(props.row)"
            color="positive"
            text-color="white"
            class="text-weight-bolder"
            style="font-size: 0.65rem; padding: 2px 5px; border-radius: 4px;"
            label="best"
          />
        </div>
      </q-td>
    </template>
    <template v-slot:body-cell-avg_position="props">
      <q-td :props="props">
        <div class="row items-center justify-end no-wrap q-gutter-x-xs">
          <span>{{ props.value }}</span>
          <q-badge
            v-if="isBestAvgPosition(props.row)"
            color="primary"
            text-color="white"
            class="text-weight-bolder"
            style="font-size: 0.65rem; padding: 2px 5px; border-radius: 4px;"
            label="best"
          />
        </div>
      </q-td>
    </template>
    <template v-slot:body-cell-most_participated_league_level="props">
      <q-td :props="props">
        <LeagueLevel
          v-if="props.row.most_participated_league_level"
          badge
          :level="props.row.most_participated_league_level"
        />
        <span v-else class="text-grey-5">-</span>
      </q-td>
    </template>
    <template v-if="isAdmin" v-slot:body-cell-actions="props">
      <q-td :props="props" auto-width>
        <KennerButton
          flat
          round
          dense
          icon="lock_reset"
          color="primary"
          @click.stop="openResetDialog(props.row)"
        >
          <q-tooltip>Reset Password</q-tooltip>
        </KennerButton>
      </q-td>
    </template>
  </KennerTable>

  <q-dialog v-model="showResetDialog" @hide="onResetDialogHide">
    <q-card style="min-width: 320px; max-width: 480px; width: 100%; border-radius: 16px" class="q-pa-md">
      <q-card-section>
        <div class="text-h6 text-weight-bold">Reset Password</div>
        <div class="text-caption text-grey-7 q-mt-xs">
          Generate a one-time password reset link for <span class="text-weight-bold text-dark">{{ targetUser?.username }}</span>.
        </div>
      </q-card-section>

      <q-card-section v-if="!generatedResetUrl" class="q-pt-none">
        <KennerInput
          v-model="resetLabel"
          label="Label / Note (optional)"
          placeholder="e.g. Password reset for user"
          :disable="isGeneratingReset"
        />
      </q-card-section>

      <q-card-section v-else class="q-pt-none column q-gutter-y-sm">
        <div class="row items-center text-positive text-caption text-weight-medium">
          <q-icon name="check_circle" size="18px" class="q-mr-xs" />
          <span>Reset link created successfully.</span>
        </div>
        <KennerInput
          :model-value="generatedResetUrl"
          readonly
          label="Password Reset Link"
        >
          <template v-slot:append>
            <q-btn
              flat
              round
              dense
              icon="content_copy"
              color="primary"
              @click="copyGeneratedLink"
            >
              <q-tooltip>Copy link</q-tooltip>
            </q-btn>
          </template>
        </KennerInput>
      </q-card-section>

      <q-card-actions align="right" class="q-pt-sm">
        <template v-if="!generatedResetUrl">
          <KennerButton
            flat
            label="Cancel"
            color="grey-7"
            v-close-popup
            :disable="isGeneratingReset"
          />
          <KennerButton
            label="Generate Link"
            color="primary"
            icon="lock_reset"
            :loading="isGeneratingReset"
            :disable="isGeneratingReset"
            @click="doGenerateResetLink"
          />
        </template>
        <template v-else>
          <KennerButton
            flat
            label="Close"
            color="grey-7"
            v-close-popup
          />
          <KennerButton
            label="Copy Link"
            color="primary"
            icon="content_copy"
            @click="copyGeneratedLink"
          />
        </template>
      </q-card-actions>
    </q-card>
  </q-dialog>
</template>

<script setup lang="ts">
import KennerTable from 'components/tables/KennerTable.vue';
import KennerButton from 'components/base/KennerButton.vue';
import KennerInput from 'components/base/KennerInput.vue';
import LeagueLevel from 'components/season/LeagueLevel.vue';
import UserAvatar from 'components/ui/UserAvatar.vue';
import { useRouter } from 'vue-router';
import { TKennerButton, TUserDto } from 'src/types';
import { computed, onMounted, ref, watch } from 'vue';
import { useUserStore } from 'stores/userStore';
import { storeToRefs } from 'pinia';
import { copyToClipboard, useQuasar } from 'quasar';
import axios from 'axios';
import { createPasswordResetLink } from 'src/services/userService';

const $q = useQuasar();
const userStore = useUserStore();
const { listUsers, getAvailableYears } = userStore;
const { isAdmin } = storeToRefs(userStore);

const users = ref<TUserDto[]>([]);
const availablePlayerCounts = ['2p', '3p', '4p'];
const selectedPlayerCounts = ref<string[]>(['4p']);
const isAllPlayerCountsSelected = computed(
  () => selectedPlayerCounts.value.length === 0
);
const selectedYears = ref<number[]>([]);
const availableYears = ref<number[]>([]);
const loading = ref(false);

const showResetDialog = ref(false);
const targetUser = ref<TUserDto | null>(null);
const resetLabel = ref('');
const generatedResetUrl = ref('');
const isGeneratingReset = ref(false);

function openResetDialog(user: TUserDto) {
  targetUser.value = user;
  resetLabel.value = `Password reset for ${user.username}`;
  generatedResetUrl.value = '';
  showResetDialog.value = true;
}

function onResetDialogHide() {
  targetUser.value = null;
  resetLabel.value = '';
  generatedResetUrl.value = '';
  isGeneratingReset.value = false;
}

async function doGenerateResetLink() {
  if (!targetUser.value || targetUser.value.id === undefined) return;

  isGeneratingReset.value = true;
  try {
    const invite = await createPasswordResetLink({
      user: targetUser.value.id,
      label: resetLabel.value.trim() || undefined,
    });
    generatedResetUrl.value = invite.invite_url;
    $q.notify({
      type: 'positive',
      message: 'Password reset link generated.',
    });
  } catch (err: unknown) {
    let message = 'Failed to generate password reset link.';
    if (axios.isAxiosError(err)) {
      message = (err.response?.data as { detail?: string })?.detail || err.message || message;
    } else if (err instanceof Error) {
      message = err.message;
    }
    $q.notify({
      type: 'negative',
      message,
    });
  } finally {
    isGeneratingReset.value = false;
  }
}

function copyGeneratedLink() {
  if (!generatedResetUrl.value) return;
  copyToClipboard(generatedResetUrl.value)
    .then(() => $q.notify({ type: 'positive', message: 'Link copied to clipboard!' }))
    .catch(() => $q.notify({ type: 'negative', message: 'Failed to copy link.' }));
}

const bestWinRate = computed(() => {
  const validUsers = users.value.filter(
    (u) => (u.total_games ?? 0) > 0 && u.win_rate !== null && u.win_rate !== undefined
  );
  if (validUsers.length === 0) return null;
  const max = Math.max(...validUsers.map((u) => u.win_rate as number));
  return max > 0 ? max : null;
});

const bestAvgPosition = computed(() => {
  const validUsers = users.value.filter(
    (u) => (u.total_games ?? 0) > 0 && u.avg_position !== null && u.avg_position !== undefined
  );
  if (validUsers.length === 0) return null;
  return Math.min(...validUsers.map((u) => u.avg_position as number));
});

const bestElo = computed(() => {
  const validUsers = users.value.filter(
    (u) => (u.elo_rating ?? u.profile?.elo_rating) !== null && (u.elo_rating ?? u.profile?.elo_rating) !== undefined
  );
  if (validUsers.length === 0) return null;
  const max = Math.max(
    ...validUsers.map((u) => Math.round((u.elo_rating ?? u.profile?.elo_rating) as number))
  );
  return max > 1500 ? max : null;
});

function isBestWinRate(row: TUserDto) {
  return (
    bestWinRate.value !== null &&
    (row.total_games ?? 0) > 0 &&
    row.win_rate === bestWinRate.value
  );
}

function isBestAvgPosition(row: TUserDto) {
  return (
    bestAvgPosition.value !== null &&
    (row.total_games ?? 0) > 0 &&
    row.avg_position === bestAvgPosition.value
  );
}

function isBestElo(row: TUserDto) {
  const val = row.elo_rating ?? row.profile?.elo_rating;
  return (
    bestElo.value !== null &&
    val !== null &&
    val !== undefined &&
    Math.round(val) === bestElo.value
  );
}

function togglePlayerCount(val: string) {
  if (val === 'all') {
    selectedPlayerCounts.value = [];
    return;
  }
  const idx = selectedPlayerCounts.value.indexOf(val);
  if (idx >= 0) {
    selectedPlayerCounts.value.splice(idx, 1);
  } else {
    selectedPlayerCounts.value.push(val);
  }

  // If all individual player counts are selected, automatically switch to "All" (empty array)
  if (selectedPlayerCounts.value.length === availablePlayerCounts.length) {
    selectedPlayerCounts.value = [];
  }
}

function toggleAllPlayerCounts() {
  selectedPlayerCounts.value = [];
}

async function loadUsers() {
  loading.value = true;
  try {
    const params: Record<string, string> = {};
    if (selectedPlayerCounts.value.length > 0) {
      params.player_count = selectedPlayerCounts.value.join(',');
    }
    if (selectedYears.value && selectedYears.value.length > 0) {
      params.years = selectedYears.value.join(',');
    }
    users.value = (await listUsers(params)) ?? [];
  } finally {
    loading.value = false;
  }
}

watch([selectedPlayerCounts, selectedYears], () => {
  loadUsers();
}, { deep: true });

onMounted(async () => {
  const years = await getAvailableYears();
  if (years && years.length > 0) {
    availableYears.value = years;
  }
  loadUsers();
});

const router = useRouter();

const onRowClick = (_event: never, row: { username: never }) => {
  router.push({ name: 'user-detail', params: { username: row.username } });
};

const createButton: TKennerButton = {
  color: 'secondary',
  label: 'Invite',
  icon: 'add_circle',
  forwardName: 'invite-user',
};

const sortNullableLarge = (a: number | null | undefined, b: number | null | undefined) => {
  if (a === b) return 0;
  if (a === null || a === undefined) return 1;
  if (b === null || b === undefined) return -1;
  return a - b;
};

const sortNullableSmall = (a: number | null | undefined, b: number | null | undefined) => {
  if (a === b) return 0;
  if (a === null || a === undefined) return -1;
  if (b === null || b === undefined) return 1;
  return a - b;
};

const baseColumns = [
  {
    name: 'user',
    required: true,
    align: 'left' as const,
    label: 'Name',
    field: (x: TUserDto) => x.username,
    sortable: true,
  },
  {
    name: 'elo_rating',
    align: 'right' as const,
    label: 'Elo',
    field: (x: TUserDto) => x.elo_rating ?? x.profile?.elo_rating,
    format: (val: number | null | undefined) =>
      val !== null && val !== undefined ? `${Math.round(val)}` : '1500',
    sort: sortNullableSmall,
    sortable: true,
  },
  {
    name: 'total_games',
    align: 'right' as const,
    label: 'Games',
    field: (x: TUserDto) => x.total_games,
    format: (val: number | null | undefined) =>
      val !== null && val !== undefined ? `${val}` : '0',
    sortable: true,
  },
  {
    name: 'win_rate',
    align: 'right' as const,
    label: 'Win %',
    field: (x: TUserDto) => x.win_rate,
    format: (val: number | null | undefined) =>
      val !== null && val !== undefined ? `${val.toFixed(1)}%` : '-',
    sort: sortNullableSmall,
    sortable: true,
  },
  {
    name: 'avg_position',
    align: 'right' as const,
    label: 'Avg Pos',
    field: (x: TUserDto) => x.avg_position,
    format: (val: number | null | undefined) =>
      val !== null && val !== undefined ? val.toFixed(2) : '-',
    sort: sortNullableLarge,
    sortable: true,
  },
  {
    name: 'most_participated_league_level',
    align: 'right' as const,
    label: 'Home League',
    field: (x: TUserDto) => x.most_participated_league_level,
    format: (val: number | null | undefined) =>
      val !== null && val !== undefined ? `L${val}` : '-',
    sort: sortNullableLarge,
    sortable: true,
  },
];

const columns = computed(() => {
  if (isAdmin.value) {
    return [
      ...baseColumns,
      {
        name: 'actions',
        align: 'center' as const,
        label: 'Actions',
        field: () => '',
        sortable: false,
      },
    ];
  }
  return baseColumns;
});
</script>

<style scoped lang="scss">
.filter-toolbar {
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(54, 64, 88, 0.08);
  border-radius: 12px;
  padding: 10px 16px;
}

.filter-controls {
  width: 100%;
}

.filter-item {
  flex-shrink: 0;
}

.years-select {
  min-width: 170px;
}

@media (max-width: 599px) {
  .filter-toolbar {
    padding: 10px 12px;
  }

  .filter-controls {
    display: flex;
    flex-direction: column;
    align-items: stretch;
  }

  .filter-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    width: 100%;
  }

  .years-select {
    min-width: 140px;
    flex-grow: 1;
  }
}
</style>
