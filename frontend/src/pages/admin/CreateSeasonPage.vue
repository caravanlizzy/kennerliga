<template>
  <div class="q-pa-md column q-gutter-md">
    <div class="text-h5">Create Season &amp; Leagues</div>

    <div>Select year and month</div>
    <KennerInput v-model.number="year" type="number" label="Year (e.g. 2025)" />
    <KennerInput v-model.number="month" type="number" label="Month (1-12)" />

    <div>Select which members to include from all Player Profiles</div>
    <div class="row q-col-gutter-sm items-end">
      <div class="col">
        <q-select
          v-model="memberList"
          :options="profileOptions"
          option-label="label"
          option-value="value"
          emit-value
          map-options
          multiple
          use-chips
          filled
          dense
          label="Pick players…"
        />
        <!-- quick debug (optional)
        <div style="opacity:.6">Options: {{ profileOptions.length }} | Selected: {{ memberList }}</div>
        -->
      </div>
      <div class="col-auto">
        <q-btn color="secondary" label="Reload Profiles" @click="loadMembers" />
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
          <KennerInput
            v-model.number="lg.level"
            type="number"
            label="Level (1 = L1)"
          />
        </div>

        <div class="col">
          <q-select
            v-model="lg.memberProfileIds"
            :options="getOptionsForLeague(idx)"
            option-label="label"
            option-value="value"
            emit-value
            map-options
            multiple
            use-chips
            filled
            dense
            placeholder="Assign players to this league…"
          />
        </div>

        <div class="col-auto">
          <q-btn
            flat
            color="negative"
            label="Remove"
            @click="removeLeague(idx)"
          />
        </div>
      </div>
    </div>

    <q-btn flat color="primary" label="+ Add League" @click="addLeague" />

    <div class="row q-col-gutter-sm q-mt-md">
      <div class="col-auto">
        <q-btn
          color="primary"
          label="Create Season & Leagues"
          :disable="!canSubmit"
          @click="createAll"
        />
      </div>
      <div class="col-auto">
        <q-btn flat label="Clear" @click="resetForm" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue';
import { api } from 'boot/axios';
import KennerInput from 'components/base/KennerInput.vue';
import {
  createLeagueForSeason,
  createSeason,
  ensureParticipants,
} from 'src/services/seasonService';

/** form state */
const year = ref<number | null>(null);
const month = ref<number | null>(null);
const memberList = ref<number[]>([]); // PlayerProfile IDs

/** profiles */
const availableMembers = ref<any[]>([]);
const profileOptions = computed(() =>
  availableMembers.value.map((p: any) => ({
    label: p.profile_name ?? p.username ?? `#${p.id}`,
    value: p.id,
  }))
);
// Only allow assigning profiles chosen in the top select
const selectedProfileOptions = computed(() =>
  profileOptions.value.filter((o) => memberList.value.includes(o.value))
);

/** leagues to create */
type PreparedLeague = { level: number | null; memberProfileIds: number[] };
const preparedLeagues = ref<PreparedLeague[]>([
  { level: 1, memberProfileIds: [] },
]);

function addLeague() {
  preparedLeagues.value.push({
    level: (preparedLeagues.value.length || 0) + 1,
    memberProfileIds: [],
  });
}
function removeLeague(idx: number) {
  preparedLeagues.value.splice(idx, 1);
  enforceUniqueness();
}

/** Load all player profiles (on mount + on click) */
onMounted(loadMembers);

async function loadMembers() {
  const { data } = await api('/user/profiles/');
  // handle both paginated and non-paginated responses
  availableMembers.value = Array.isArray(data)
    ? data
    : Array.isArray(data?.results)
    ? data.results
    : [];
}

/** Unique assignment logic */
// Ensure a profile is in at most one league.
// If duplicates exist, keep the earliest league and remove from later ones.
function enforceUniqueness() {
  const seen = new Set<number>();
  preparedLeagues.value.forEach((lg) => {
    lg.memberProfileIds = lg.memberProfileIds.filter((pid) => {
      if (seen.has(pid)) return false;
      seen.add(pid);
      return true;
    });
  });
}

// If top-level members change, drop any assignments that are no longer allowed.
watch(memberList, () => {
  preparedLeagues.value.forEach((lg) => {
    lg.memberProfileIds = lg.memberProfileIds.filter((pid) =>
      memberList.value.includes(pid)
    );
  });
  enforceUniqueness();
});

// Re-enforce uniqueness on deep changes
watch(preparedLeagues, enforceUniqueness, { deep: true });

/**
 * Per-league options: show selectedProfileOptions minus profiles already
 * assigned to any other league. Keep this league's own picks visible.
 */
function getOptionsForLeague(leagueIndex: number) {
  const otherAssigned = new Set<number>();
  preparedLeagues.value.forEach((lg, idx) => {
    if (idx === leagueIndex) return;
    for (const pid of lg.memberProfileIds) otherAssigned.add(pid);
  });
  return selectedProfileOptions.value.filter(
    (opt) => !otherAssigned.has(opt.value)
  );
}

/** Submit */
const canSubmit = computed(() => {
  const okDate = !!year.value && !!month.value;
  const okMembers = memberList.value.length > 0;
  const okLeagues =
    preparedLeagues.value.length > 0 &&
    preparedLeagues.value.every(
      (l) => !!l.level && l.memberProfileIds.length > 0
    );
  return okDate && okMembers && okLeagues;
});

async function createAll() {
  if (!canSubmit.value) return;
  const s = await createSeason(year.value!, month.value!);
  const seasonId = s.id;
  const seasonParticipants = await ensureParticipants(
    seasonId,
    memberList.value
  );

  for (const lg of preparedLeagues.value) {
    await createLeagueForSeason(
      seasonId,
      lg.level!,
      seasonParticipants,
      lg.memberProfileIds
    );
  }

  resetForm();
}

/** Reset */
function resetForm() {
  year.value = null;
  month.value = null;
  memberList.value = [];
  preparedLeagues.value = [{ level: 1, memberProfileIds: [] }];
}
</script>
