<template>
  <div class="q-pa-md column q-gutter-md">
    <div class="text-h5">Create Season &amp; Leagues</div>

    <div>Select year and month</div>
    <KennerInput v-model.number="year" type="number" label="Year (e.g. 2025)" />
    <KennerInput v-model.number="month" type="number" label="Month (1-12)" />

    <div>Select which members to include from all Player Profiles</div>
    <div class="row q-col-gutter-sm items-end">
      <div class="col">
        <KennerSelect
          v-model="memberList"
          :options="profileOptions"
          option-label="label"
          option-value="value"
          emit-value
          map-options
          multiple
          use-chips
          label="Pick players…"
          @update:model-value="onMemberListChange"
        />
      </div>
      <div class="col-auto">
        <KennerButton
          color="secondary"
          label="Reload Profiles"
          @click="loadMembers"
        />
      </div>
    </div>

    <!-- Selected Season Participants Order -->
    <div
      v-if="memberList.length > 0"
      class="column q-gutter-xs q-pa-md"
      style="border: 1px solid var(--kenner-border-strong); border-radius: 8px"
    >
      <div class="row items-center justify-between">
        <div>
          <div class="text-subtitle2 text-weight-bold">
            Season Participants ({{ memberList.length }} selected)
          </div>
          <div class="text-caption text-grey-7">
            Order defines participant rank and initial league seeding.
          </div>
        </div>
        <KennerButton
          outline
          color="primary"
          icon="tune"
          label="Distribute to Leagues"
          @click="distributePlayers"
        />
      </div>

      <div class="column q-gutter-xs q-mt-sm">
        <div
          v-for="(pid, pIdx) in memberList"
          :key="pid"
          class="row items-center q-py-xs q-px-sm bg-grey-2 text-dark rounded-borders"
        >
          <div class="text-weight-bold q-mr-sm" style="min-width: 28px">
            #{{ pIdx + 1 }}
          </div>
          <div class="col ellipsis">{{ getProfileName(pid) }}</div>
          <div class="row q-gutter-xs items-center">
            <KennerButton
              flat
              dense
              round
              size="sm"
              icon="arrow_upward"
              :disable="pIdx === 0"
              @click="moveParticipantUp(pIdx)"
            >
              <q-tooltip>Move Up</q-tooltip>
            </KennerButton>
            <KennerButton
              flat
              dense
              round
              size="sm"
              icon="arrow_downward"
              :disable="pIdx === memberList.length - 1"
              @click="moveParticipantDown(pIdx)"
            >
              <q-tooltip>Move Down</q-tooltip>
            </KennerButton>
            <KennerButton
              flat
              dense
              round
              size="sm"
              icon="close"
              color="negative"
              @click="removeParticipant(pIdx)"
            >
              <q-tooltip>Remove Participant</q-tooltip>
            </KennerButton>
          </div>
        </div>
      </div>
    </div>

    <div class="row items-center justify-between">
      <div>
        <div class="text-subtitle1 text-weight-bold">Leagues (Optional)</div>
        <div class="text-caption text-grey-7">
          Assign players to specific leagues and order their positions. You can
          also create the season without leagues and manage them later.
        </div>
      </div>
      <div v-if="memberList.length > 0" class="row q-gutter-sm items-center">
        <KennerButton
          flat
          color="primary"
          icon="tune"
          label="Distribute to Leagues"
          @click="distributePlayers"
        />
      </div>
    </div>

    <div
      v-for="(lg, idx) in preparedLeagues"
      :key="idx"
      class="q-pa-md q-mb-sm column q-gutter-sm"
      style="border: 1px solid var(--kenner-border-strong); border-radius: 8px"
    >
      <div class="row q-col-gutter-sm items-center">
        <div class="col-auto" style="min-width: 140px">
          <KennerInput
            v-model.number="lg.level"
            type="number"
            label="Level (1 = L1)"
          />
        </div>

        <div class="col">
          <KennerSelect
            :model-value="lg.memberProfileIds"
            :options="optionsForLeague(idx)"
            option-label="label"
            option-value="value"
            emit-value
            map-options
            multiple
            use-chips
            placeholder="Assign players to this league…"
            @update:model-value="(val) => onLeaguePickChange(idx, val)"
          />
        </div>

        <div class="col-auto">
          <KennerButton
            flat
            color="negative"
            label="Remove League"
            @click="removeLeague(idx)"
          />
        </div>
      </div>

      <!-- Player positions inside this league -->
      <div
        v-if="lg.memberProfileIds.length > 0"
        class="column q-gutter-xs q-mt-xs"
      >
        <div class="text-caption text-weight-medium text-grey-8">
          Player Order &amp; Positions:
        </div>
        <div
          v-for="(pid, mIdx) in lg.memberProfileIds"
          :key="pid"
          class="row items-center q-py-xs q-px-sm bg-grey-2 text-dark rounded-borders"
        >
          <div class="text-weight-bold q-mr-sm" style="min-width: 28px">
            #{{ mIdx + 1 }}
          </div>
          <div class="col ellipsis">{{ getProfileName(pid) }}</div>
          <div class="row q-gutter-xs items-center">
            <KennerButton
              flat
              dense
              round
              size="sm"
              icon="arrow_upward"
              :disable="mIdx === 0"
              @click="movePlayerUp(idx, mIdx)"
            >
              <q-tooltip>Move Up</q-tooltip>
            </KennerButton>
            <KennerButton
              flat
              dense
              round
              size="sm"
              icon="arrow_downward"
              :disable="mIdx === lg.memberProfileIds.length - 1"
              @click="movePlayerDown(idx, mIdx)"
            >
              <q-tooltip>Move Down</q-tooltip>
            </KennerButton>
            <KennerButton
              flat
              dense
              round
              size="sm"
              icon="close"
              color="negative"
              @click="removePlayerFromLeague(idx, mIdx)"
            >
              <q-tooltip>Remove from League</q-tooltip>
            </KennerButton>
          </div>
        </div>
      </div>
    </div>

    <div>
      <KennerButton flat color="primary" icon="add" label="Add League" @click="addLeague" />
    </div>

    <div class="row q-col-gutter-sm q-mt-md">
      <div class="col-auto">
        <KennerButton
          color="primary"
          :label="
            preparedLeagues.length > 0
              ? 'Create Season & Leagues'
              : 'Create Season'
          "
          :disable="!canSubmit"
          :loading="isSubmitting"
          @click="createAll"
        />
      </div>
      <div class="col-auto">
        <KennerButton flat color="grey-7" label="Clear" @click="resetForm" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import { fetchProfiles } from 'src/services/userService';
import KennerInput from 'components/base/KennerInput.vue';
import KennerButton from 'components/base/KennerButton.vue';
import KennerSelect from 'components/base/KennerSelect.vue';
import {
  createLeagueForSeason,
  createSeason,
  ensureParticipants,
} from 'src/services/seasonService';
import type { TSeasonParticipantDto } from 'src/types';

/* -------------------- State -------------------- */
const router = useRouter();
const year = ref<number | null>(null);
const month = ref<number | null>(null);
const memberList = ref<number[]>([]); // PlayerProfile IDs as numbers

type RawProfile = {
  id: number | string;
  profile_name?: string;
  username?: string;
};
const availableMembers = ref<RawProfile[]>([]);

type PreparedLeague = { level: number | null; memberProfileIds: number[] };
const preparedLeagues = ref<PreparedLeague[]>([]);
const isSubmitting = ref(false);

/* -------------------- Options (normalized) -------------------- */
const profileOptions = computed(() =>
  availableMembers.value.map((p) => {
    const idNum = Number(p.id);
    return {
      label: p.profile_name ?? p.username ?? `Profile ${idNum}`,
      value: idNum,
    };
  })
);

function getProfileName(pid: number): string {
  const p = availableMembers.value.find((m) => Number(m.id) === Number(pid));
  return p?.profile_name ?? p?.username ?? `Profile ${pid}`;
}

// Only allow assigning profiles chosen in the top select
const selectedProfileOptions = computed(() => {
  const allowed = new Set(memberList.value.map(Number));
  return profileOptions.value.filter((o) => allowed.has(Number(o.value)));
});

/* -------------------- Per-league options -------------------- */
function optionsForLeague(leagueIndex: number) {
  const otherAssigned = new Set<number>();
  preparedLeagues.value.forEach((lg, idx) => {
    if (idx === leagueIndex) return;
    lg.memberProfileIds.forEach((pid) => otherAssigned.add(Number(pid)));
  });

  const own = new Set(
    preparedLeagues.value[leagueIndex]?.memberProfileIds.map(Number) ?? []
  );
  return selectedProfileOptions.value.filter(
    (opt) => own.has(Number(opt.value)) || !otherAssigned.has(Number(opt.value))
  );
}

/* -------------------- Load members -------------------- */
onMounted(loadMembers);

async function loadMembers() {
  const profiles = await fetchProfiles();
  availableMembers.value = profiles.map((p) => ({ ...p, id: Number(p.id) }));
}

/* -------------------- Event-driven uniqueness -------------------- */

// When the top member list changes, drop any assignments that are no longer allowed.
function onMemberListChange(newList: any) {
  memberList.value = (newList ?? []).map((v: any) => Number(v));
  const allowed = new Set(memberList.value);

  preparedLeagues.value.forEach((lg) => {
    lg.memberProfileIds = lg.memberProfileIds
      .map(Number)
      .filter((pid) => allowed.has(pid));
  });

  dedupeAcrossLeagues();
}

// When a league's selection changes, preserve order and enforce cross-league uniqueness
function onLeaguePickChange(idx: number, newIds: any) {
  const normalized = (newIds ?? []).map((v: any) => Number(v));
  const newSet = new Set<number>(normalized);
  const current = preparedLeagues.value[idx].memberProfileIds.filter((pid) =>
    newSet.has(pid)
  );
  for (const id of normalized) {
    if (!current.includes(id)) {
      current.push(id);
    }
  }
  preparedLeagues.value[idx].memberProfileIds = current;

  // Remove any of these IDs from *other* leagues to keep uniqueness
  const chosen = new Set(current);
  preparedLeagues.value.forEach((lg, i) => {
    if (i === idx) return;
    lg.memberProfileIds = lg.memberProfileIds.filter(
      (pid) => !chosen.has(Number(pid))
    );
  });
}

function movePlayerUp(leagueIdx: number, playerIdx: number) {
  if (playerIdx <= 0) return;
  const list = preparedLeagues.value[leagueIdx].memberProfileIds;
  const temp = list[playerIdx];
  list[playerIdx] = list[playerIdx - 1];
  list[playerIdx - 1] = temp;
}

function movePlayerDown(leagueIdx: number, playerIdx: number) {
  const list = preparedLeagues.value[leagueIdx].memberProfileIds;
  if (playerIdx >= list.length - 1) return;
  const temp = list[playerIdx];
  list[playerIdx] = list[playerIdx + 1];
  list[playerIdx + 1] = temp;
}

function removePlayerFromLeague(leagueIdx: number, playerIdx: number) {
  preparedLeagues.value[leagueIdx].memberProfileIds.splice(playerIdx, 1);
}

/** Keep uniqueness across leagues by walking in order and dropping duplicates in later leagues. */
function dedupeAcrossLeagues() {
  const seen = new Set<number>();
  preparedLeagues.value.forEach((lg) => {
    lg.memberProfileIds = lg.memberProfileIds.map(Number).filter((pid) => {
      if (seen.has(pid)) return false;
      seen.add(pid);
      return true;
    });
  });
}

/* -------------------- Participant list actions -------------------- */
function moveParticipantUp(idx: number) {
  if (idx <= 0) return;
  const temp = memberList.value[idx];
  memberList.value[idx] = memberList.value[idx - 1];
  memberList.value[idx - 1] = temp;
}

function moveParticipantDown(idx: number) {
  if (idx >= memberList.value.length - 1) return;
  const temp = memberList.value[idx];
  memberList.value[idx] = memberList.value[idx + 1];
  memberList.value[idx + 1] = temp;
}

function removeParticipant(idx: number) {
  memberList.value.splice(idx, 1);
  onMemberListChange(memberList.value);
}

/* -------------------- Auto-distribute to leagues -------------------- */
function calculateLeagueSizes(count: number): number[] {
  if (count <= 0) return [];
  if (count === 1) return [1];
  const leagueCount = Math.floor(count / 4);
  const rest = count % 4;
  const players = Array(leagueCount).fill(4);
  if (rest === 1) {
    if (leagueCount > 0) {
      players[players.length - 1] = 3;
    }
    players.push(2);
  } else if (rest === 2) {
    players.push(2);
  } else if (rest === 3) {
    players.push(3);
  }
  return players;
}

function distributePlayers() {
  if (memberList.value.length === 0) return;
  const sizes = calculateLeagueSizes(memberList.value.length);
  let offset = 0;
  preparedLeagues.value = sizes.map((size, idx) => {
    const members = memberList.value.slice(offset, offset + size);
    offset += size;
    return {
      level: idx + 1,
      memberProfileIds: members,
    };
  });
}

/* -------------------- League list actions -------------------- */
function addLeague() {
  preparedLeagues.value.push({
    level: (preparedLeagues.value.length || 0) + 1,
    memberProfileIds: [],
  });
}

function removeLeague(idx: number) {
  preparedLeagues.value.splice(idx, 1);
  dedupeAcrossLeagues();
}

/* -------------------- Submit -------------------- */
const canSubmit = computed(() => {
  const okDate =
    year.value != null &&
    month.value != null &&
    year.value > 0 &&
    month.value >= 1 &&
    month.value <= 12;
  const okLeagues = preparedLeagues.value.every(
    (l) => l.level != null && Number(l.level) > 0
  );
  return okDate && okLeagues;
});

async function createAll() {
  if (!canSubmit.value || isSubmitting.value) return;

  isSubmitting.value = true;
  try {
    const s = await createSeason(year.value!, month.value!);
    const seasonId = s.id;

    // Order participants: all players in league 1 (in order), league 2 (in order), etc.
    // followed by any participants in memberList who were not assigned to any league.
    const orderedProfileIds: number[] = [];
    const addedSet = new Set<number>();

    const sortedLeagues = [...preparedLeagues.value].sort(
      (a, b) => (Number(a.level) || 0) - (Number(b.level) || 0)
    );

    for (const lg of sortedLeagues) {
      for (const pid of lg.memberProfileIds) {
        const numId = Number(pid);
        if (!addedSet.has(numId)) {
          orderedProfileIds.push(numId);
          addedSet.add(numId);
        }
      }
    }

    for (const pid of memberList.value) {
      const numId = Number(pid);
      if (!addedSet.has(numId)) {
        orderedProfileIds.push(numId);
        addedSet.add(numId);
      }
    }

    let seasonParticipants: TSeasonParticipantDto[] = [];
    if (orderedProfileIds.length > 0) {
      seasonParticipants = await ensureParticipants(
        seasonId,
        orderedProfileIds
      );
    }

    for (const lg of sortedLeagues) {
      if (lg.level == null) continue;
      await createLeagueForSeason(
        seasonId,
        Number(lg.level),
        seasonParticipants,
        lg.memberProfileIds.map(Number)
      );
    }

    resetForm();
    await router.push({ name: 'season-manage', params: { id: seasonId } });
  } catch (e) {
    console.error('Failed to create season & leagues:', e);
  } finally {
    isSubmitting.value = false;
  }
}

/* -------------------- Reset -------------------- */
function resetForm() {
  year.value = null;
  month.value = null;
  memberList.value = [];
  preparedLeagues.value = [];
}
</script>
