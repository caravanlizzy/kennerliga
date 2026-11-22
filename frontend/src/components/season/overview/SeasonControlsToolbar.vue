<template>
  <div
    class="controls-toolbar row items-center justify-between q-gutter-y-sm"
    :class="isMobile ? 'q-px-md' : ''"
  >
    <!-- League Selector Dropdown -->
    <div
      class="league-select-container"
      :class="isMobile ? 'full-width' : ''"
    >
      <KennerSelect
        :model-value="selectedLeagueId"
        :options="leagueOptions"
        emit-value
        map-options
        dense
        label="League"
        class="full-width"
        @update:model-value="$emit('league-selected', $event)"
      >
        <template #selected-item="scope">
          <div class="row items-center q-gutter-x-xs no-wrap ellipsis">
            <LeagueLevel
              v-if="scope.opt.level !== undefined"
              :level="scope.opt.level"
              badge
              class="q-mr-xs"
            />
            <q-icon
              v-else
              name="grid_view"
              size="16px"
              color="primary"
              class="q-mr-xs"
            />
            <span class="ellipsis text-weight-bold">{{
              scope.opt.label
            }}</span>
          </div>
        </template>
        <template #option="scope">
          <q-item v-bind="scope.itemProps">
            <q-item-section avatar style="min-width: 32px">
              <LeagueLevel
                v-if="scope.opt.level !== undefined"
                :level="scope.opt.level"
                badge
              />
              <q-icon v-else name="grid_view" size="18px" color="primary" />
            </q-item-section>
            <q-item-section>
              <q-item-label class="row items-center q-gutter-x-xs">
                <span
                  :class="
                    scope.opt.isUser
                      ? 'text-weight-bold text-primary'
                      : 'text-weight-medium'
                  "
                >
                  {{ scope.opt.label }}
                </span>
                <span
                  v-if="scope.opt.isUser"
                  class="user-league-pill-sm row items-center no-wrap q-ml-xs"
                >
                  <q-icon name="person" size="11px" class="q-mr-xs" />
                  <span>You</span>
                </span>
              </q-item-label>
            </q-item-section>
            <q-item-section side>
              <span class="text-caption text-grey-6">
                {{
                  scope.opt.value === 'all'
                    ? `${scope.opt.memberCount} leagues`
                    : `${scope.opt.memberCount} players`
                }}
              </span>
            </q-item-section>
          </q-item>
        </template>
      </KennerSelect>
    </div>

    <!-- View Switcher Toggle -->
    <div
      class="view-toggle-container"
      :class="isMobile ? 'full-width' : ''"
    >
      <q-btn-toggle
        v-if="selectedLeagueId === 'all'"
        :model-value="activeAllView"
        no-caps
        rounded
        unelevated
        :spread="isMobile"
        class="season-view-toggle"
        toggle-color="primary"
        color="grey-2"
        text-color="grey-8"
        :options="allViewOptions"
        @update:model-value="$emit('update:activeAllView', $event); $emit('view-changed')"
      />
      <q-btn-toggle
        v-else
        :model-value="activeLeagueView"
        no-caps
        rounded
        unelevated
        :spread="isMobile"
        class="season-view-toggle"
        toggle-color="primary"
        color="grey-2"
        text-color="grey-8"
        :options="leagueViewOptions"
        @update:model-value="$emit('update:activeLeagueView', $event); $emit('view-changed')"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import KennerSelect from 'components/base/KennerSelect.vue';
import LeagueLevel from 'components/season/LeagueLevel.vue';

export interface LeagueOptionItem {
  label: string;
  value: number | 'all';
  level?: number;
  memberCount: number;
  isUser: boolean;
}

export interface ViewToggleOption {
  label: string;
  value: string;
  icon: string;
}

defineProps<{
  selectedLeagueId: number | 'all';
  leagueOptions: LeagueOptionItem[];
  activeAllView: string;
  activeLeagueView: string;
  allViewOptions: ViewToggleOption[];
  leagueViewOptions: ViewToggleOption[];
  isMobile: boolean;
}>();

defineEmits<{
  (e: 'league-selected', val: number | 'all'): void;
  (e: 'update:activeAllView', val: string): void;
  (e: 'update:activeLeagueView', val: string): void;
  (e: 'view-changed'): void;
}>();
</script>

<style scoped lang="scss">
.controls-toolbar {
  @media (min-width: 600px) {
    gap: 16px;
  }
}

.league-select-container {
  @media (min-width: 600px) {
    min-width: 220px;
    max-width: 320px;
  }
}

.view-toggle-container {
  @media (min-width: 600px) {
    flex-shrink: 0;
  }
}

.season-view-toggle {
  padding: 2px;
  max-width: 100%;

  @media (max-width: 599px) {
    width: 100%;

    :deep(.q-btn) {
      padding: 4px 6px;
      font-size: 0.75rem;

      .q-icon {
        font-size: 15px;
        margin-right: 4px;
      }
    }
  }
}

.user-league-pill-sm {
  font-size: 10px;
  font-weight: 700;
  color: var(--q-primary);
  background: rgba(var(--q-primary), 0.12);
  padding: 1px 6px;
  border-radius: 999px;
  text-transform: uppercase;
  letter-spacing: 0.3px;
}
</style>
