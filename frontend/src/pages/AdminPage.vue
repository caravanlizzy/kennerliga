<template>
  <q-page class="q-pa-md">
    <div class="text-h5 text-weight-bold q-mb-lg">Admin</div>

    <div v-for="group in groups" :key="group.title" class="q-mb-lg">
      <div class="text-h6 q-mb-md">{{ group.title }}</div>
      <div class="row q-col-gutter-md">
        <div
          v-for="item in group.items"
          :key="item.label"
          class="col-12 col-sm-6 col-md-4"
        >
          <q-card
            flat
            bordered
            clickable
            v-ripple
            class="admin-card full-height"
            :class="{ 'admin-card--disabled': item.disabled }"
            @click="!item.disabled && go(item)"
          >
            <q-card-section class="row items-center no-wrap">
              <q-icon :name="item.icon" size="32px" color="primary" class="q-mr-md" />
              <div>
                <div class="text-subtitle1 text-weight-medium">{{ item.label }}</div>
                <div class="text-caption text-grey-7">{{ item.description }}</div>
              </div>
            </q-card-section>
          </q-card>
        </div>
      </div>
    </div>
  </q-page>
</template>

<script setup lang="ts">
defineOptions({ name: 'AdminPage' });
import { computed, onMounted } from 'vue';
import { storeToRefs } from 'pinia';
import { useRouter } from 'vue-router';
import { useHomeSeasonStore } from 'stores/homeSeasonStore';

type AdminLink = {
  label: string;
  description: string;
  icon: string;
  name: string;
  params?: Record<string, unknown>;
  disabled?: boolean;
};

type AdminGroup = {
  title: string;
  items: AdminLink[];
};

const router = useRouter();
const homeSeasonStore = useHomeSeasonStore();
const { currentSeasonId } = storeToRefs(homeSeasonStore);

// The current season is required to reach the season/league management screens,
// so those cards are disabled until it is known.
const groups = computed<AdminGroup[]>(() => [
  {
    title: 'Seasons & Leagues',
    items: [
      {
        label: 'Manage Current Season',
        description: 'Edit the running season and its leagues.',
        icon: 'settings_applications',
        name: 'season-manage',
        params: currentSeasonId.value ? { id: currentSeasonId.value } : undefined,
        disabled: !currentSeasonId.value,
      },
      {
        label: 'Create Season',
        description: 'Start a new season.',
        icon: 'add_circle',
        name: 'season-create',
      },
      {
        label: 'All Seasons',
        description: 'Browse and open past seasons.',
        icon: 'event',
        name: 'seasons',
      },
      {
        label: 'Invitations',
        description: 'Invite players to the league.',
        icon: 'mark_email_unread',
        name: 'invitations',
      },
    ],
  },
  {
    title: 'Games',
    items: [
      {
        label: 'Games',
        description: 'Manage the game catalog.',
        icon: 'sports_esports',
        name: 'games',
      },
    ],
  },
  {
    title: 'Content',
    items: [
      {
        label: 'Announcements',
        description: 'Publish and remove announcements.',
        icon: 'campaign',
        name: 'announcements',
      },
      {
        label: 'Release Notes',
        description: "Manage the app's changelog.",
        icon: 'history',
        name: 'release-notes',
      },
    ],
  },
  {
    title: 'Settings',
    items: [
      {
        label: 'Configuration',
        description: 'App-wide settings and their history.',
        icon: 'settings',
        name: 'configuration',
      },
    ],
  },
]);

function go(item: AdminLink): void {
  void router.push({ name: item.name, params: item.params });
}

onMounted(() => {
  void homeSeasonStore.init();
});
</script>

<style scoped lang="scss">
.admin-card {
  // Instant (no-transition) hover affordance so users can tell the card is
  // clickable, without reintroducing the removed lift/shadow animation.
  &:not(.admin-card--disabled):hover {
    border-color: var(--q-primary);
    background-color: rgba(0, 0, 0, 0.03);
    cursor: pointer;
  }

  &--disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
}
</style>
