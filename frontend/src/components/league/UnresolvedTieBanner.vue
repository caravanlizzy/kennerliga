<template>
  <div class="unresolved-tie-notice" :class="{ 'is-compact': compact }">
    <div class="unresolved-tie-notice__header">
      <div class="unresolved-tie-notice__title-wrap">
        <div class="unresolved-tie-notice__icon-badge">
          <q-icon name="balance" size="16px" />
        </div>
        <div class="unresolved-tie-notice__heading">
          <span class="unresolved-tie-notice__title">Unresolved Tie</span>
          <span
            v-if="unresolvedGroups.length > 1"
            class="unresolved-tie-notice__count"
          >
            {{ unresolvedGroups.length }}
          </span>
        </div>
      </div>

      <KennerButton
        v-if="adminMode"
        label="Resolve"
        size="xs"
        color="warning"
        outline
        no-caps
        class="unresolved-tie-notice__action"
        @click="emit('resolve-tie', unresolvedGroups[0])"
      />
    </div>

    <div class="unresolved-tie-notice__body">
      <div
        v-for="grp in unresolvedGroups"
        :key="grp.group_key"
        class="unresolved-tie-notice__group"
      >
        <div class="unresolved-tie-notice__matchup">
          <template v-for="(m, idx) in grp.members" :key="m.player_profile_id">
            <span class="unresolved-tie-notice__player">{{
              m.profile_name
            }}</span>
            <span
              v-if="idx < grp.members.length - 1"
              class="unresolved-tie-notice__vs"
              >vs</span
            >
          </template>
        </div>
      </div>
    </div>

    <div class="unresolved-tie-notice__hint">Awaiting tie-break decision.</div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import type { TTieGroup } from 'src/types';
import KennerButton from 'components/base/KennerButton.vue';

const props = withDefaults(
  defineProps<{
    tieGroups: TTieGroup[];
    adminMode?: boolean;
    compact?: boolean;
  }>(),
  {
    adminMode: false,
    compact: false,
  }
);

const emit = defineEmits<{
  (e: 'resolve-tie', group?: TTieGroup): void;
}>();

const unresolvedGroups = computed(() =>
  props.tieGroups.filter((g) => g.unresolved)
);
</script>

<style scoped lang="scss">
.unresolved-tie-notice {
  position: relative;
  border-radius: var(--kenner-card-radius, 12px);
  padding: 12px 16px;
  background: var(--kenner-warning-bg, rgba(245, 158, 11, 0.08));
  border: 1px solid var(--kenner-border-subtle, rgba(0, 0, 0, 0.08));
  border-left: 4px solid var(--kenner-warning-text, #b45309);
  transition: all 0.2s ease;

  &.is-compact {
    padding: 10px 12px;
    border-radius: 10px;
  }

  &__header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 8px;
    margin-bottom: 8px;
  }

  &__title-wrap {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  &__icon-badge {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 24px;
    height: 24px;
    border-radius: 6px;
    background: rgba(245, 158, 11, 0.15);
    color: var(--kenner-warning-text, #b45309);
    flex-shrink: 0;
  }

  &__heading {
    display: flex;
    align-items: center;
    gap: 6px;
  }

  &__title {
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.6px;
    color: var(--kenner-warning-text, #b45309);
  }

  &__count {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 0.65rem;
    font-weight: 700;
    padding: 1px 6px;
    border-radius: 10px;
    background: rgba(245, 158, 11, 0.2);
    color: var(--kenner-warning-text, #b45309);
  }

  &__action {
    flex-shrink: 0;
  }

  &__body {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  }

  &__group {
    display: flex;
    align-items: center;
  }

  &__matchup {
    display: inline-flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 6px;
    padding: 4px 10px;
    background: var(--kenner-card-bg, #ffffff);
    border: 1px solid var(--kenner-border-subtle, rgba(0, 0, 0, 0.08));
    border-radius: 8px;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.02);
  }

  &__player {
    font-size: 0.8rem;
    font-weight: 600;
    color: var(--kenner-text-strong, #0f172a);
  }

  &__vs {
    font-size: 0.65rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: var(--kenner-warning-text, #b45309);
    opacity: 0.8;
  }

  &__hint {
    margin-top: 6px;
    font-size: 0.7rem;
    color: var(--kenner-text-muted, #64748b);
    font-style: italic;
  }
}
</style>
