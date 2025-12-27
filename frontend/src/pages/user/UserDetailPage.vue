<!-- UserSeasons.vue -->
<template>
  <section class="q-pa-sm">
    <!-- User header -->
    <div class="row items-center justify-between q-mb-md">
      <div class="text-subtitle1 text-weight-medium">
        {{ user?.username || route.params.username }}
      </div>
      <q-btn dense flat icon="refresh" @click="reload" :disable="loading" />
    </div>

    <!-- Seasons box -->
    <q-card flat bordered class="rounded-borders">
      <q-card-section class="bg-grey-1 q-py-xs q-px-sm">
        <div class="text-subtitle2 text-weight-medium">
          Seasons Participated
        </div>
      </q-card-section>

      <q-separator />

      <q-card-section>
        <!-- Loading -->
        <div v-if="loading" class="row items-center q-gutter-sm">
          <q-spinner size="20px" />
          <span class="text-grey-7">Loading…</span>
        </div>

        <!-- Empty -->
        <q-banner
          v-else-if="!seasons.length"
          class="bg-grey-2 text-grey-8 q-ma-none q-pa-sm"
        >
          No seasons found.
        </q-banner>

        <!-- Season cards -->
        <div v-else class="row q-col-gutter-sm">
          <div
            v-for="s in seasons"
            :key="s.id"
            class="col-12 col-sm-6 col-md-4"
          >
            <q-card
              flat
              bordered
              clickable
              class="rounded-borders"
              @click="$emit('open:season', s.id)"
            >
              <q-card-section class="row items-center no-wrap">
                <q-avatar
                  icon="event"
                  color="dark"
                  text-color="white"
                  class="q-mr-md"
                />
                <div class="col">
                  <div class="text-subtitle2 text-weight-medium">
                    {{ s.name }}
                  </div>
                  <div class="text-caption text-grey-7">
                    <span v-if="s.year">Year: {{ s.year }}</span>
                    <span v-if="s.status"> · Status: {{ s.status }}</span>
                  </div>
                </div>
              </q-card-section>
            </q-card>
          </div>
        </div>
      </q-card-section>
    </q-card>
  </section>
</template>

<script setup lang="ts">
import { api } from 'boot/axios';
import { useRoute } from 'vue-router';
import { onMounted, ref } from 'vue';
import { TSeasonDto, TSeasonParticipantDto, TUserDto } from 'src/types';

defineEmits<{ (e: 'open:season', seasonId: number | string): void }>();

const user = ref<TUserDto>();
const userSeasonList = ref<TSeasonParticipantDto[]>([]);
const seasons = ref<TSeasonDto[]>([]);
const loading = ref(true);
const route = useRoute();

onMounted(async () => {
  await loadData();
});

async function loadData() {
  loading.value = true;
  try {
    await fetchUser();
    await fetchUserSeasons();
    await fetchSeasonDetails();
  } finally {
    loading.value = false;
  }
}

function reload() {
  loadData();
}

async function fetchUser(): Promise<void> {
  const { data } = await api(
    `user/users/${encodeURIComponent(String(route.params.username))}/`
  );
  user.value = data;
}

async function fetchUserSeasons(): Promise<void> {
  const username = route.params.username;
  if (!username) return;
  try {
    const { data } = await api.get('season/season-participants/', {
      params: { profile__profile_name: `${username}_profile` },
    });
    userSeasonList.value = Array.isArray(data) ? data : data.results || [];
  } catch (err: any) {
    console.error('Failed to fetch user seasons:', err);
    userSeasonList.value = [];
  }
}

async function fetchSeasonDetails(): Promise<void> {
  const details: any[] = [];
  for (const sp of userSeasonList.value) {
    try {
      // Assuming sp.id is the season id in your updated setup
      const { data } = await api.get(`season/seasons/${sp.id}/`);
      details.push(data);
    } catch (err) {
      console.error(`Failed to fetch season ${sp.id}:`, err);
    }
  }
  seasons.value = details;
}
</script>
