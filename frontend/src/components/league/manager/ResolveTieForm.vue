<template>
  <div class="q-pa-md">
    <div v-if="loadingReasons" class="flex flex-center q-pa-md">
      <q-spinner size="30px" color="primary" />
    </div>
    <q-form v-else @submit="submit">
      <div class="text-subtitle2 q-mb-sm">Players in Tie Group (Order determines rank)</div>
      <q-list bordered separator class="rounded-borders q-mb-md bg-white">
        <q-item v-for="(member, index) in sortedMembers" :key="member.profile">
          <q-item-section avatar>
            <q-badge color="primary" text-color="white" :label="index + 1" />
          </q-item-section>
          <q-item-section>
            <q-item-label>{{ member.profile_name }}</q-item-label>
          </q-item-section>
          <q-item-section side>
            <div class="row q-gutter-xs">
              <q-btn
                flat
                round
                dense
                icon="arrow_upward"
                :disable="index === 0"
                @click="move(index, -1)"
              />
              <q-btn
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
        :rules="[val => !!val || 'Reason is required']"
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
        <q-btn label="Cancel" flat color="grey-7" v-close-popup />
        <q-btn
          label="Resolve Tie"
          color="primary"
          type="submit"
          :loading="submitting"
        />
      </div>
    </q-form>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { api } from 'boot/axios';
import { useQuasar } from 'quasar';
import type { TSeasonParticipantDto } from 'src/types';

const props = defineProps<{
  leagueId: number;
  groupKey: string;
  members: TSeasonParticipantDto[];
}>();

const emit = defineEmits(['onSuccess']);

const $q = useQuasar();
const sortedMembers = ref<TSeasonParticipantDto[]>([...props.members]);
const reason = ref<string | null>(null);
const note = ref('');
const reasons = ref<{ value: string; label: string }[]>([]);
const loadingReasons = ref(false);
const submitting = ref(false);

const fetchReasons = async () => {
  loadingReasons.value = true;
  try {
    const { data } = await api.get(`league/leagues/${props.leagueId}/tie-resolution-reasons/`);
    reasons.value = data;
    if (reasons.value.length > 0) {
      reason.value = reasons.value[0].value;
    }
  } catch (e) {
    console.error('Error fetching reasons:', e);
    $q.notify({ type: 'negative', message: 'Failed to load tie resolution reasons' });
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
    await api.post(`league/leagues/${props.leagueId}/resolve-tie/`, {
      group_key: props.groupKey,
      reason: reason.value,
      player_order: sortedMembers.value.map(m => m.profile),
      note: note.value
    });
    $q.notify({ type: 'positive', message: 'Tie group resolved successfully' });
    emit('onSuccess');
  } catch (e: unknown) {
    console.error('Error resolving tie:', e);
    let detail = 'Failed to resolve tie group';
    if (e && typeof e === 'object' && 'response' in e) {
      const resp = (e as any).response;
      if (resp?.data?.detail) detail = resp.data.detail;
    }
    $q.notify({ type: 'negative', message: detail });
  } finally {
    submitting.value = false;
  }
};

onMounted(fetchReasons);
</script>
