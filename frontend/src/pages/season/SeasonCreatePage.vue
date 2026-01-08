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
        <KennerButton color="secondary" label="Reload Profiles" @click="loadMembers" />
      </div>
    </div>

    <div>Then select which users to put in which league</div>

    <div
      v-for="(lg, idx) in preparedLeagues"
      :key="idx"
      class="q-pa-sm q-mb-sm"
      style="border: 1px solid #ddd; border-radius: 8px"
    >
      <div class="row q-col-gutter-sm items-center">
        <div class="col-auto">
          <KennerInput v-model.number="lg.level" type="number" label="Level (1 = L1)" />
        </div>

        <div class="col">
          <KennerSelect
            v-model="lg.memberProfileIds"
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
          <KennerButton flat color="negative" label="Remove" @click="removeLeague(idx)" />
        </div>
      </div>
    </div>

    <KennerButton flat color="dark" label="+ Add League" @click="addLeague" />

    <div class="row q-col-gutter-sm q-mt-md">
      <div class="col-auto">
        <KennerButton
          color="dark"
          label="Create Season & Leagues"
          :disable="!canSubmit"
          @click="createAll"
        />
      </div>
      <div class="col-auto">
        <KennerButton flat label="Clear" @click="resetForm" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { api } from 'boot/axios';
import KennerInput from 'components/base/KennerInput.vue';
import KennerButton from 'components/base/KennerButton.vue';
import KennerSelect from 'components/base/KennerSelect.vue';
import {
  createLeagueForSeason,
  createSeason,
  ensureParticipants,
} from 'src/services/seasonService';

/* -------------------- State -------------------- */
const year = ref<number | null>(null);
const month = ref<number | null>(null);
const memberList = ref<number[]>([]); // PlayerProfile IDs as numbers

type RawProfile = { id: number | string; profile_name?: string; username?: string };
const availableMembers = ref<RawProfile[]>([]);

type PreparedLeague = { level: number | null; memberProfileIds: number[] };
const preparedLeagues = ref<PreparedLeague[]>([{ level: 1, memberProfileIds: [] }]);

/* -------------------- Options (normalized) -------------------- */
const profileOptions = computed(() =>
  availableMembers.value.map((p) => {
    const idNum = Number(p.id);
    return {
      label: p.profile_name ?? p.username ?? `#${idNum}`,
      value: idNum,
    };
  })
);

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

  // Keep this league's own picks visible even if they appear in otherAssigned (shouldn't normally)
  const own = new Set(preparedLeagues.value[leagueIndex].memberProfileIds.map(Number));
  return selectedProfileOptions.value.filter(
    (opt) => own.has(Number(opt.value)) || !otherAssigned.has(Number(opt.value))
  );
}

/* -------------------- Load members -------------------- */
onMounted(loadMembers);

async function loadMembers() {
  const { data } = await api('/user/profiles/');
  const arr = Array.isArray(data) ? data : Array.isArray(data?.results) ? data.results : [];
  // Normalize ids to numbers immediately
  availableMembers.value = arr.map((p: any) => ({ ...p, id: Number(p.id) }));
}

/* -------------------- Event-driven uniqueness (no deep watchers) -------------------- */

// When the top member list changes, drop any assignments that are no longer allowed.
function onMemberListChange(newList: any) {
  // Quasar may emit arrays of numbers already; normalize just in case
  memberList.value = (newList ?? []).map((v: any) => Number(v));
  const allowed = new Set(memberList.value);

  preparedLeagues.value.forEach((lg) => {
    lg.memberProfileIds = lg.memberProfileIds.map(Number).filter((pid) => allowed.has(pid));
  });

  // Also remove duplicates across leagues (keep earlier leagues’ picks)
  dedupeAcrossLeagues();
}

// When a league's selection changes, normalize and enforce cross-league uniqueness
function onLeaguePickChange(idx: number, newIds: any) {
  const normalized = (newIds ?? []).map((v: any) => Number(v));
  preparedLeagues.value[idx].memberProfileIds = normalized;

  // Remove any of these IDs from *other* leagues to keep uniqueness
  const chosen = new Set(normalized);
  preparedLeagues.value.forEach((lg, i) => {
    if (i === idx) return;
    lg.memberProfileIds = lg.memberProfileIds.filter((pid) => !chosen.has(Number(pid)));
  });
}

/** Keep uniqueness across leagues by walking in order and dropping duplicates in later leagues. */
function dedupeAcrossLeagues() {
  const seen = new Set<number>();
  preparedLeagues.value.forEach((lg) => {
    lg.memberProfileIds = lg.memberProfileIds
      .map(Number)
      .filter((pid) => {
        if (seen.has(pid)) return false;
        seen.add(pid);
        return true;
      });
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
  // After removal, ensure there are no lingering duplicates (shouldn’t be, but cheap to ensure)
  dedupeAcrossLeagues();
}

/* -------------------- Submit -------------------- */
const canSubmit = computed(() => {
  const okDate = !!year.value && !!month.value;
  const okMembers = memberList.value.length > 0;
  const okLeagues =
    preparedLeagues.value.length > 0 &&
    preparedLeagues.value.every((l) => !!l.level && l.memberProfileIds.length > 0);
  return okDate && okMembers && okLeagues;
});

async function createAll() {
  if (!canSubmit.value) return;

  const s = await createSeason(year.value!, month.value!);
  const seasonId = s.id;
  const seasonParticipants = await ensureParticipants(seasonId, memberList.value.map(Number));

  for (const lg of preparedLeagues.value) {
    await createLeagueForSeason(
      seasonId,
      Number(lg.level),
      seasonParticipants,
      lg.memberProfileIds.map(Number)
    );
  }

  resetForm();
}

/* -------------------- Reset -------------------- */
function resetForm() {
  year.value = null;
  month.value = null;
  memberList.value = [];
  preparedLeagues.value = [{ level: 1, memberProfileIds: [] }];
}
</script>
