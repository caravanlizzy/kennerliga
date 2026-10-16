<template>
  <q-page class="q-py-md flex justify-center">
    <div
      style="max-width: var(--kenner-max-width-text); width: 100%"
      class="q-px-sm"
    >
      <!-- Admin Hero Header -->
      <div
        class="admin-hero-card q-pa-lg q-mb-lg row items-center justify-between"
      >
        <div class="column">
          <div class="row items-center q-gutter-x-sm q-mb-xs">
            <q-icon name="admin_panel_settings" color="primary" size="32px" />
            <div class="text-h5 text-weight-bold text-dark tracking-tight">
              Admin Portal
            </div>
          </div>
          <div class="text-caption text-grey-7">
            Manage seasons, league assignments, games, announcements, and
            configuration.
          </div>
        </div>
      </div>

      <div v-for="group in groups" :key="group.title" class="q-mb-xl">
        <div
          class="text-subtitle1 text-weight-bold q-mb-sm text-dark row items-center q-gutter-x-xs"
        >
          <q-icon :name="group.icon" color="primary" size="18px" />
          <span>{{ group.title }}</span>
        </div>
        <div class="row q-col-gutter-md">
          <div
            v-for="item in group.items"
            :key="item.label"
            class="col-12 col-sm-6 col-md-4"
          >
            <q-card
              flat
              clickable
              v-ripple
              class="admin-card full-height"
              :class="{ 'admin-card--disabled': item.disabled }"
              @click="!item.disabled && go(item)"
            >
              <q-card-section class="row items-center no-wrap q-pa-md">
                <div
                  class="admin-icon-box q-mr-md flex flex-center"
                  :class="`bg-${item.color || 'primary'}-subtle`"
                >
                  <q-icon
                    :name="item.icon"
                    size="24px"
                    :color="item.color || 'primary'"
                  />
                </div>
                <div class="col">
                  <div class="text-subtitle2 text-weight-bold text-dark">
                    {{ item.label }}
                  </div>
                  <div class="text-caption text-grey-6 ellipsis-2-lines">
                    {{ item.description }}
                  </div>
                </div>
                <q-icon
                  name="chevron_right"
                  color="grey-5"
                  size="20px"
                  class="q-ml-xs"
                />
              </q-card-section>
            </q-card>
          </div>
        </div>
      </div>

      <!-- Platform Management Dialog -->
      <q-dialog v-model="platformDialogOpen" position="standard">
        <q-card style="width: 500px; max-width: 95vw" class="q-pa-sm">
          <q-card-section class="row items-center justify-between q-pb-none">
            <div class="row items-center q-gutter-x-sm">
              <q-icon name="devices" color="primary" size="24px" />
              <div class="text-h6 text-weight-bold">Manage Platforms</div>
            </div>
            <q-btn flat round dense icon="close" v-close-popup />
          </q-card-section>

          <q-card-section class="q-pt-sm">
            <div class="text-caption text-grey-7 q-mb-md">
              Add new gaming platforms (e.g. Board Game Arena, Steam) to use in game definitions.
            </div>

            <q-form @submit.prevent="handleAddPlatform" class="q-gutter-y-sm q-mb-lg">
              <div class="row q-col-gutter-sm items-center">
                <div class="col">
                  <KennerInput
                    v-model="newPlatformName"
                    label="Platform Name"
                    dense
                    :rules="[(val: string) => !!val?.trim() || 'Platform name is required']"
                  />
                </div>
                <div class="col-auto">
                  <KennerButton
                    type="submit"
                    color="primary"
                    icon="add"
                    label="Add"
                    :loading="submittingPlatform"
                  />
                </div>
              </div>
            </q-form>

            <q-separator class="q-my-md" />

            <div class="row items-center justify-between q-mb-sm">
              <div class="text-subtitle2 text-weight-bold text-dark">
                Existing Platforms
              </div>
              <q-badge color="primary" rounded class="q-px-sm">
                {{ platforms.length }}
              </q-badge>
            </div>

            <LoadingSpinner v-if="loadingPlatforms" />

            <div
              v-else-if="platforms.length === 0"
              class="text-caption text-grey-6 q-py-md text-center"
            >
              No platforms registered yet.
            </div>

            <div v-else class="row q-gutter-xs q-py-xs">
              <q-chip
                v-for="p in platforms"
                :key="p.id"
                outline
                color="primary"
                text-color="primary"
                icon="videogame_asset"
              >
                {{ p.name }}
              </q-chip>
            </div>
          </q-card-section>

          <q-card-actions align="right" class="q-pt-none">
            <KennerButton flat label="Close" v-close-popup />
          </q-card-actions>
        </q-card>
      </q-dialog>
    </div>
  </q-page>
</template>

<script setup lang="ts">
defineOptions({ name: 'AdminPage' });
import { computed, onMounted, ref } from 'vue';
import { storeToRefs } from 'pinia';
import { useRouter } from 'vue-router';
import { Notify } from 'quasar';
import { useHomeSeasonStore } from 'stores/homeSeasonStore';
import KennerButton from 'components/base/KennerButton.vue';
import KennerInput from 'components/base/KennerInput.vue';
import LoadingSpinner from 'components/base/LoadingSpinner.vue';
import { TPlatform } from 'src/types';
import { createPlatform, fetchPlatforms } from 'src/services/gameService';

type AdminLink = {
  label: string;
  description: string;
  icon: string;
  name?: string;
  color?: string;
  params?: Record<string, unknown>;
  disabled?: boolean;
  action?: () => void;
};

type AdminGroup = {
  title: string;
  icon: string;
  items: AdminLink[];
};

const router = useRouter();
const homeSeasonStore = useHomeSeasonStore();
const { currentSeasonId } = storeToRefs(homeSeasonStore);

const platformDialogOpen = ref(false);
const platforms = ref<TPlatform[]>([]);
const loadingPlatforms = ref(false);
const submittingPlatform = ref(false);
const newPlatformName = ref('');

async function loadPlatforms(): Promise<void> {
  loadingPlatforms.value = true;
  try {
    platforms.value = await fetchPlatforms();
  } catch {
    Notify.create({
      type: 'negative',
      message: 'Failed to load platforms',
    });
  } finally {
    loadingPlatforms.value = false;
  }
}

function openPlatformDialog(): void {
  platformDialogOpen.value = true;
  void loadPlatforms();
}

async function handleAddPlatform(): Promise<void> {
  const trimmed = newPlatformName.value.trim();
  if (!trimmed) return;

  submittingPlatform.value = true;
  try {
    await createPlatform(trimmed);
    Notify.create({
      type: 'positive',
      message: `Platform "${trimmed}" added successfully`,
    });
    newPlatformName.value = '';
    await loadPlatforms();
  } catch (error: unknown) {
    const err = error as {
      response?: { data?: { name?: string[]; detail?: string } };
      message?: string;
    };
    const errorMsg =
      err?.response?.data?.name?.[0] ||
      err?.response?.data?.detail ||
      err?.message ||
      'Failed to create platform';
    Notify.create({
      type: 'negative',
      message: errorMsg,
    });
  } finally {
    submittingPlatform.value = false;
  }
}

// The current season is required to reach the season/league management screens,
// so those cards are disabled until it is known.
const groups = computed<AdminGroup[]>(() => [
  {
    title: 'Seasons & Leagues',
    icon: 'military_tech',
    items: [
      {
        label: 'Manage Current Season',
        description: 'Edit the running season and its leagues.',
        icon: 'settings_applications',
        color: 'primary',
        name: 'season-manage',
        params: currentSeasonId.value
          ? { id: currentSeasonId.value }
          : undefined,
        disabled: !currentSeasonId.value,
      },
      {
        label: 'Create Season',
        description: 'Start a new season with automated assignments.',
        icon: 'add_circle',
        color: 'positive',
        name: 'season-create',
      },
      {
        label: 'All Seasons',
        description: 'Browse and inspect past seasons.',
        icon: 'event',
        color: 'secondary',
        name: 'seasons',
      },
      {
        label: 'Invitations',
        description: 'Invite new players to join the league.',
        icon: 'mark_email_unread',
        color: 'accent',
        name: 'invitations',
      },
    ],
  },
  {
    title: 'Games',
    icon: 'sports_esports',
    items: [
      {
        label: 'Game Catalog',
        description: 'Manage games, scoring configurations, and factions.',
        icon: 'sports_esports',
        color: 'primary',
        name: 'games',
      },
      {
        label: 'Platforms',
        description: 'Add and manage gaming platforms for games.',
        icon: 'devices',
        color: 'secondary',
        action: openPlatformDialog,
      },
    ],
  },
  {
    title: 'Content & Communication',
    icon: 'campaign',
    items: [
      {
        label: 'Announcements',
        description: 'Publish, schedule, and remove app announcements.',
        icon: 'campaign',
        color: 'warning',
        name: 'announcements',
      },
      {
        label: 'Release Notes',
        description: 'Manage app changelog and feature updates.',
        icon: 'history',
        color: 'info',
        name: 'release-notes',
      },
    ],
  },
  {
    title: 'Settings',
    icon: 'settings',
    items: [
      {
        label: 'App Configuration',
        description: 'Manage app-wide rules and tie-decider settings.',
        icon: 'settings',
        color: 'grey-8',
        name: 'configuration',
      },
    ],
  },
]);

function go(item: AdminLink): void {
  if (item.action) {
    item.action();
  } else if (item.name) {
    void router.push({ name: item.name, params: item.params });
  }
}

onMounted(() => {
  void homeSeasonStore.init();
});
</script>

<style scoped lang="scss">
.admin-hero-card {
  background: var(--kenner-surface-overlay);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  border: 1px solid var(--kenner-border-color);
  border-radius: var(--kenner-card-radius, 16px);
}

.admin-card {
  background: var(--kenner-surface-overlay);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  border: 1px solid var(--kenner-border-color);
  border-radius: var(--kenner-card-radius, 16px);
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);

  &:not(.admin-card--disabled):hover {
    border-color: var(--q-primary);
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
    cursor: pointer;
  }

  &--disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
}

.admin-icon-box {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  flex-shrink: 0;
}

.bg-primary-subtle {
  background: rgba(54, 64, 88, 0.08);
}
.bg-secondary-subtle {
  background: rgba(235, 126, 44, 0.12);
}
.bg-accent-subtle {
  background: rgba(144, 107, 79, 0.12);
}
.bg-positive-subtle {
  background: rgba(46, 125, 50, 0.12);
}
.bg-warning-subtle {
  background: rgba(245, 124, 0, 0.12);
}
.bg-info-subtle {
  background: rgba(2, 136, 209, 0.12);
}
.bg-grey-8-subtle {
  background: rgba(66, 66, 66, 0.08);
}

.body--dark {
  .bg-primary-subtle {
    background: rgba(255, 255, 255, 0.08);
  }
  .bg-secondary-subtle {
    background: rgba(235, 126, 44, 0.18);
  }
  .bg-accent-subtle {
    background: rgba(144, 107, 79, 0.22);
  }
  .bg-positive-subtle {
    background: rgba(46, 125, 50, 0.22);
  }
  .bg-warning-subtle {
    background: rgba(245, 124, 0, 0.18);
  }
  .bg-info-subtle {
    background: rgba(2, 136, 209, 0.2);
  }
  .bg-grey-8-subtle {
    background: rgba(255, 255, 255, 0.08);
  }
}
</style>
