<template>
  <q-page padding>
    <!-- Header -->
    <div class="row items-center q-mb-lg">
      <div class="col-grow">
        <div class="text-h5 text-weight-bold">
          Manage L{{ league?.level }}
          <q-badge class="q-ml-sm" outline>League</q-badge>
        </div>
        <div class="text-subtitle2 text-grey-7">
          Season: <q-chip dense square>{{ season?.name }}</q-chip>
        </div>
      </div>
      <div class="col-auto">
        <q-btn flat icon="refresh" round @click="load" :loading="loading" />
      </div>
    </div>

    <!-- Loading -->
    <q-linear-progress v-if="loading" indeterminate class="q-mb-md" />

    <!-- Error -->
    <q-banner
      v-if="error"
      dense
      class="q-mb-md bg-red-1 text-negative"
      rounded
      inline-actions
    >
      <template #avatar>
        <q-icon name="error" />
      </template>
      {{ error }}
      <template #action>
        <q-btn flat color="negative" label="Retry" @click="reload" />
      </template>
    </q-banner>

    <!-- Empty state -->
    <q-card
      v-if="
        !loading && !error && (!league?.members || league.members.length === 0)
      "
      flat
      bordered
      class="q-pa-xl flex items-center justify-center"
    >
      <div class="column items-center">
        <q-icon name="group_off" size="48px" class="q-mb-sm" />
        <div class="text-subtitle1">No members yet</div>
        <div class="text-caption text-grey-7 q-mt-xs">
          Add members to start selecting games.
        </div>
      </div>
    </q-card>

    <!-- Members grid -->
    <div v-else class="row q-col-gutter-md">
      <div
        v-for="member in league?.members"
        :key="member.id"
        class="col-12 col-sm-6 col-md-4"
      >
        <q-card flat bordered class="fit">
          <q-item>
            <q-item-section avatar>
              <q-avatar rounded>
                <q-icon name="person" />
              </q-avatar>
            </q-item-section>
            <q-item-section>
              <q-item-label class="text-weight-medium">
                {{ member.username }}
              </q-item-label>
              <q-item-label caption> Member ID: {{ member.id }} </q-item-label>
            </q-item-section>
            <q-item-section side>
              <q-badge
                v-if="member.selected_game"
                color="positive"
                outline
                class="text-uppercase"
                >Selected</q-badge
              >
              <q-badge
                v-else
                color="grey-5"
                text-color="dark"
                outline
                class="text-uppercase"
                >No game yet</q-badge
              >
            </q-item-section>
          </q-item>

          <q-separator />

          <q-card-section>
            <div class="text-caption text-grey-7 q-mb-xs">Selected Game</div>
            <div class="row items-center">
              <div class="col-auto">
                <q-chip
                  v-if="member.selected_game?.game_name"
                  icon="sports_esports"
                  dense
                  square
                >
                  {{ member.selected_game.game_name }}
                </q-chip>
                <span v-else class="text-grey-6">No game yet</span>
              </div>
              <div class="col">
                <q-space />
              </div>
            </div>
          </q-card-section>

          <!-- Optional raw data toggle (dev aid) -->
          <q-expansion-item
            dense
            icon="info"
            label="Details"
            expand-icon="expand_more"
            class="q-mx-sm q-mb-sm"
          >
            <q-card-section class="bg-grey-1">
              <pre class="q-ma-none text-body2">{{ member }}</pre>
            </q-card-section>
          </q-expansion-item>

          <q-separator />

          <q-card-actions align="right">
            <q-btn
              :label="member.selected_game ? 'Edit Game' : 'Select Game'"
              :icon="member.selected_game ? 'edit' : 'add'"
              color="primary"
              @click="handleSelectOrEdit(member)"
            />
          </q-card-actions>
        </q-card>
      </div>
    </div>
  </q-page>
</template>

<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router';
import { onMounted, ref } from 'vue';
import { fetchLeagueDetails } from 'src/services/leagueService';
import { fetchSeason } from 'src/services/seasonService';
import { TLeague, TMember, TSeason } from 'src/types';

const route = useRoute();
const router = useRouter();

const league = ref<TLeague | null>(null);
const season = ref<TSeason | null>(null);

const loading = ref(false);
const error = ref<string | null>(null);

async function load() {
  loading.value = true;
  error.value = null;
  try {
    const leagueId = Number(route.params.id);
    league.value = await fetchLeagueDetails(leagueId);
    if(!league.value) throw new Error('Failed to load league data.')
    season.value = await fetchSeason(league.value.season);
  } catch (e: string) {
    error.value = e?.message || 'Failed to load league/season data.';
  } finally {
    loading.value = false;
  }
}

function handleSelectOrEdit(member: TMember) {
  // Adjust navigation to your routes; example targets:
  // - "/leagues/:leagueId/members/:memberId/select-game"
  // - or open a dialog instead
  // const leagueId = league.value?.id;
  // if (!leagueId) return;
  // const target = member.selected_game
  //   ? {
  //       name: 'EditMemberGame',
  //       params: {
  //         leagueId,
  //         memberId: member.id,
  //         selectedGameId: member.selected_game.id,
  //       },
  //     }
  //   : { name: 'SelectMemberGame', params: { leagueId, memberId: member.id } };
  //
  // // If you don’t have routes yet, replace with your dialog logic
  // router.push(target as any);
}

onMounted(load);
</script>
