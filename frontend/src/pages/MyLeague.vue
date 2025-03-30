<template>
  <div class="q-pa-lg">
    <div class="gradient">
      <StatusBar> Status {{league?.status}} - active player: {{activePlayer?.username}} </StatusBar>
      <KennerButton @click="next"> Next</KennerButton>
      <div class="row q-gutter-md">

        <div v-for="member of members" :key="member" class="q-pa-sm"> {{member.username}}</div>
      </div>
    </div>
    <GameSelector v-if="isActive" class="q-mt-lg" />
  </div>
</template>

<script setup lang="ts">
import GameSelector from 'components/ui/GameSelector.vue';
import { computed, ref } from 'vue';
import StatusBar from 'components/StatusBar.vue';
import KennerButton from 'components/buttons/KennerButton.vue';
import { api } from 'boot/axios';

const league = ref();
const members = ref([]);
const activePlayer = computed(() => members.value.find(member => member.id === league.value.active_player));

const myleagueId = 1;

try {
  const data = await fetchLeague();
  await fetchLeagueMembers(data);
  console.log('League and members loaded');
} catch (err) {
  console.error('Error loading league/members:', err);
}


async function fetchLeague() {
  const { data } = await api.get(`league/leagues/${myleagueId}`);
  league.value = data;
  return data; // allows optional chaining
}

async function fetchLeagueMembers(leagueData: any) {
  const memberData = await Promise.all(
    leagueData.members.map(async (memberId: number) => {
      const { data } = await api.get(`user/users/${memberId}/`);
      return data;
    })
  );
  members.value = memberData;
  return memberData;
}

function next() {
  api({
    url: '/league/1/next-player/',
    method: 'POST',
  }).then(() => {
    fetchLeague();
  });
}

const isActive = ref(true);
</script>
