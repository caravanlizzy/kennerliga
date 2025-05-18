<template>
  <div class="q-mt-xl">
    <!-- Selected Game -->
    <div v-if="member.selected_game" class="q-mb-sm">
      <q-card
        :flat="status !== 'BANNING'"
        bordered
        class="q-mb-md q-pa-sm shadow-1 hover-card"
        :class="{ 'cursor-pointer ': isUserBanning }"
        @click="$emit('select-for-ban')"
      >
        <q-card-section class="row items-center justify-between">
          <div class="text-h6">
            {{ member.selected_game.game_name }}
            <q-badge
              v-if="isUserBanning"
              color="accent"
              text-color="white"
              class="cursor-pointer q-ml-sm q-py-xs q-px-sm"
              @click="$emit('select-for-ban')"
            >
              Bannen
            </q-badge>
          </div>

          <q-btn
            flat
            dense
            round
            icon="expand_more"
            class="material-symbols-outlined"
            :class="{ 'rotate-180': isExpanded }"
            @click="isExpanded = !isExpanded"
            color="primary"
          />
        </q-card-section>

        <q-slide-transition>
          <div v-show="isExpanded">
            <q-separator spaced />

            <q-list dense>
              <q-item
                v-for="option in member.selected_game.selected_options"
                :key="option.id"
              >
                <q-item-section>{{ option.game_option.name }}</q-item-section>

                <q-item-section side class="text-right">
                  <span v-if="option.choice" class="text-secondary">
                    {{ option.choice.name }}
                  </span>

                  <q-icon
                    v-else-if="option.value === true"
                    name="check_circle"
                    class="material-symbols-outlined"
                    color="positive"
                  />
                  <q-icon
                    v-else-if="option.value === false"
                    name="cancel"
                    class="material-symbols-outlined"
                    color="negative"
                  />
                  <q-icon
                    v-else
                    name="help"
                    class="material-symbols-outlined"
                    color="grey"
                  />
                </q-item-section>
              </q-item>
            </q-list>
          </div>
        </q-slide-transition>
      </q-card>
    </div>

    <!-- Banned Game -->
    <div v-if="member.banned_game">
      <div class="text-caption text-weight-medium">Gebanntes Spiel:</div>
      <div class="text-body2 text-weight-bold text-negative">
        {{ member.banned_game }}
      </div>
    </div>

    <!-- Nothing Selected -->
    <div
      v-if="!member.selected_game && !member.banned_game"
      class="text-caption text-grey-6"
    >
      Noch keine Auswahl oder Bann.
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue';

const isUserBanning = computed(() => {
  return props.status !== 'BANNING' && props.isActive;
})

// Props
const props = defineProps<{
  member: {
    selected_game?: {
      game_name: string;
      selected_options: {
        id: number;
        game_option: { name: string };
        choice?: { name: string };
        value?: boolean | null;
      }[];
    };
    banned_game?: string;
  };
  status: string;
  isActive: boolean;
}>();

const isExpanded = ref(false);
const emit = defineEmits<{
  (e: 'select-for-ban'): void;
}>();
</script>

<style scoped>
.rotate-180 {
  transform: rotate(180deg);
  transition: transform 0.3s ease;
}

.hover-card {
  transition: box-shadow 0.3s ease, transform 0.3s ease;
}

.hover-card:hover {
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.12);
  transform: translateY(-2px);
}
</style>
