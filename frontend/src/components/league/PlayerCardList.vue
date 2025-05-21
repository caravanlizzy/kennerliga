<template>
  <div :class="containerClass">
    <div
      v-for="member in members"
      :key="member.id"
      class="player-card"
      :class="{
        'is-active-border-accent': member.is_active_player,
        // optionally swap to secondary based on context
        // 'is-active-border-secondary': someOtherCondition
      }"
    >
      <PlayerCard
        :status="status"
        :member="member"
        :isActive="member.is_active_player"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { useResponsive } from 'src/composables/reponsive';
import { computed } from 'vue';
import PlayerCard from 'components/league/PlayerCard.vue';


const props = defineProps<{
  members: any[]
  status: string
}>()

const { isMobile } = useResponsive()

const containerClass = computed(() =>
  isMobile ? 'column-reverse' : 'player-grid'
)
</script>

<style lang="scss" scoped>
.player-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(420px, 1fr));
  gap: 0;
}

.column-reverse {
  display: flex;
  flex-direction: column-reverse;
  gap: 16px;
}

.player-card {
  border: 1px solid #e0e0e0;
  border-radius: 2px;
  padding: 12px;
  box-shadow: 0 1px 6px rgba(0, 0, 0, 0.04);
  transition: box-shadow 0.3s ease;
  background: white;
}

.player-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.is-active-border-accent {
  border: 2px solid rgba($accent, 0.4);
}

.is-active-border-secondary {
  border: 2px solid rgba($secondary, 0.4);
}
</style>
