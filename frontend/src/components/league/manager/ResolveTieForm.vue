<template>
  <div class="q-pa-md">
    <div v-if="loadingReasons" class="flex flex-center q-pa-md">
      <q-spinner-puff size="30px" color="primary" />
    </div>
    <q-form v-else @submit="submit">
      <div class="text-subtitle2 q-mb-sm">
        Players in Tie Group (Order determines rank)
      </div>
      <q-list bordered separator class="rounded-borders q-mb-md bg-white">
        <q-item
          v-for="(member, index) in sortedMembers"
          :key="getProfileId(member)"
        >
          <q-item-section avatar>
            <q-badge color="primary" text-color="white" :label="index + 1" />
          </q-item-section>
          <q-item-section>
            <q-item-label>{{ member.profile_name }}</q-item-label>
          </q-item-section>
          <q-item-section side>
            <div class="row q-gutter-xs">
              <KennerButton
                flat
                round
                dense
                icon="arrow_upward"
                :disable="index === 0"
                @click="move(index, -1)"
              />
              <KennerButton
                flat
                round
                dense
                icon="arrow_downward"
                :disable="index === sortedMembers.length - 1"
                @click="move(index, 1)"
              />
            </div>
          </q-item-section>
        </q-item>
      </q-list>

      <q-select
        v-model="reason"
        :options="reasons"
        label="Resolution Reason"
        outlined
        emit-value
        map-options
        required
        class="q-mb-md"
        :rules="[(val) => !!val || 'Reason is required']"
      />

      <q-input
        v-model="note"
        label="Note (Optional)"
        outlined
        type="textarea"
        rows="2"
        class="q-mb-lg"
      />

      <div class="row justify-end q-gutter-sm">
        <KennerButton label="Cancel" flat color="grey-7" v-close-popup />
        <KennerButton
          :label="resolutionId ? 'Save Changes' : 'Resolve Tie'"
          color="primary"
          type="submit"
          :loading="submitting"
        />
      </div>
    </q-form>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue';
import KennerButton from 'components/base/KennerButton.vue';
import {
  fetchTieResolutionReasons,
  resolveTie,
  updateTieResolution,
  type TTieResolutionReason,
} from 'src/services/leagueService';
import { useQuasar } from 'quasar';
import type { TSeasonParticipantDto, TTieGroupMember } from 'src/types';

export type TTieMemberLike =
  | TSeasonParticipantDto
  | TTieGroupMember
  | { profile?: number; player_profile_id?: number; profile_name: string };

const props = withDefaults(
  defineProps<{
    leagueId: number;
    groupKey: string;
    members: TTieMemberLike[];
    initialReason?: string | null;
    initialNote?: string | null;
    resolutionId?: number | null;
  }>(),
  {
    initialReason: null,
    initialNote: null,
    resolutionId: null,
  }
);

const emit = defineEmits(['onSuccess']);

const $q = useQuasar();

const getProfileId = (m: TTieMemberLike): number => {
  if ('profile' in m && typeof m.profile === 'number') {
    return m.profile;
  }
  if ('player_profile_id' in m && typeof m.player_profile_id === 'number') {
    return m.player_profile_id;
  }
  return 0;
};

const sortedMembers = ref<TTieMemberLike[]>([...props.members]);
watch(
  () => props.members,
  (newMembers) => {
    sortedMembers.value = [...(newMembers || [])];
  }
);

const reason = ref<string | null>(props.initialReason || null);
const note = ref(props.initialNote || '');
const reasons = ref<TTieResolutionReason[]>([]);
const loadingReasons = ref(false);
const submitting = ref(false);

const fetchReasons = async () => {
  loadingReasons.value = true;
  try {
    reasons.value = await fetchTieResolutionReasons(props.leagueId);
    if (!reason.value && reasons.value.length > 0) {
      reason.value = reasons.value[0].value;
    }
  } catch (e) {
    console.error('Error fetching reasons:', e);
    $q.notify({
      type: 'negative',
      message: 'Failed to load tie resolution reasons',
    });
  } finally {
    loadingReasons.value = false;
  }
};

const move = (index: number, direction: number) => {
  const targetIndex = index + direction;
  if (targetIndex < 0 || targetIndex >= sortedMembers.value.length) return;
  const temp = sortedMembers.value[index];
  sortedMembers.value[index] = sortedMembers.value[targetIndex];
  sortedMembers.value[targetIndex] = temp;
};

const submit = async () => {
  if (!reason.value) return;
  submitting.value = true;
  try {
    const player_order = sortedMembers.value.map(getProfileId);
    if (props.resolutionId) {
      await updateTieResolution(props.resolutionId, {
        reason: reason.value,
        player_order,
        note: note.value,
      });
      $q.notify({
        type: 'positive',
        message: 'Tie resolution updated successfully',
      });
    } else {
      await resolveTie(props.leagueId, {
        group_key: props.groupKey,
        reason: reason.value,
        player_order,
        note: note.value,
      });
      $q.notify({
        type: 'positive',
        message: 'Tie group resolved successfully',
      });
    }
    emit('onSuccess');
  } catch (e: unknown) {
    console.error('Error resolving tie:', e);
    let detail = props.resolutionId
      ? 'Failed to update tie resolution'
      : 'Failed to resolve tie group';
    if (e && typeof e === 'object' && 'response' in e) {
      const resp = (e as { response?: { data?: { detail?: string } } }).response;
      if (resp?.data?.detail) detail = resp.data.detail;
    }
    $q.notify({ type: 'negative', message: detail });
  } finally {
    submitting.value = false;
  }
};

onMounted(fetchReasons);
</script>
