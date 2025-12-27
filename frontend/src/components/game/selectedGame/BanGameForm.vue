<template>
  <div class="q-pa-md">
    <div class="text-subtitle1 q-mb-md">
      Select a game to ban from the games picked by other players:
    </div>

    <div v-if="availableToBan.length === 0" class="text-center q-pa-lg">
      <q-icon name="info" size="md" color="grey-5" />
      <div class="text-grey-7">No games available to ban.</div>
    </div>

    <div v-else class="row q-col-gutter-md">
      <div
        v-for="game in availableToBan"
        :key="game.id"
        class="col-12 col-sm-6"
      >
        <q-card
          flat
          bordered
          class="cursor-pointer hover-shadow transition-base"
          :class="selectedGameId === game.id ? 'bg-red-1 border-red' : ''"
          @click="selectedGameId = game.id"
        >
          <q-card-section class="row items-center no-wrap">
            <div class="col">
              <div class="text-weight-bold">{{ game.game_name }}</div>
              <div class="text-caption text-grey-7">
                Picked by {{ game.owner_name }}
              </div>
            </div>
            <q-radio v-model="selectedGameId" :val="game.id" color="red-7" />
          </q-card-section>
        </q-card>
      </div>
    </div>

    <div class="row justify-end q-mt-xl q-gutter-sm">
      <q-btn
        flat
        label="Skip Ban"
        color="grey-7"
        :loading="submitting"
        @click="submit(true)"
      />
      <q-btn
        label="Confirm Ban"
        color="red-7"
        :disable="!selectedGameId"
        :loading="submitting"
        @click="submit(false)"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { banGame } from 'src/services/gameService'; // Adjust path if necessary
import { useQuasar } from 'quasar';
import { TLeagueDto, TLeagueMemberDto } from 'src/types';
import { TSelectedGameDto } from 'src/types/game';

const props = defineProps<{
  league: TLeagueDto;
  member: TLeagueMemberDto;
}>();

const emit = defineEmits(['onSuccess']);
const $q = useQuasar();

const selectedGameId = ref<number | null>(null);
const submitting = ref(false);

interface AvailableGame extends TSelectedGameDto {
  owner_name: string;
}

const availableToBan = computed(() => {
  const games: AvailableGame[] = [];
  props.league.members.forEach((m: TLeagueMemberDto) => {
    // Players usually can't ban their own picks
    if (m.id === props.member.id) return;

    (m.selected_games || []).forEach((sg: TSelectedGameDto) => {
      games.push({
        ...sg,
        owner_name: m.profile_name,
      });
    });
  });
  return games;
});

async function submit(skip = false) {
  submitting.value = true;
  console.log(props.member.profile);
  try {
    await banGame({
      profileId: props.member.profile,
      leagueId: props.league.id,
      selectedGameId: skip ? undefined : (selectedGameId.value as number),
      skip: skip,
    });

    $q.notify({
      type: 'positive',
      message: skip ? 'Ban skipped' : 'Game banned successfully',
    });
    emit('onSuccess');
  } catch (e: unknown) {
    const error = e as Error & { message?: string };
    $q.notify({
      type: 'negative',
      message: error.message || 'Failed to process ban',
    });
  } finally {
    submitting.value = false;
  }
}
</script>

<style scoped>
.border-red {
  border: 1px solid var(--q-red-7);
}
.hover-shadow:hover {
  box-shadow: 0 1px 5px rgba(0, 0, 0, 0.1);
}
.transition-base {
  transition: all 0.3s ease;
}
</style>
