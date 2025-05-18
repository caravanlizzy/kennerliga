<template>
  <div
    class="q-pa-xl rounded-borders relative full-height"
    :style="{
      minHeight: '240px',
    }"
  >
    <!-- Header -->
    <div class="row items-center justify-between">
      <div class="text-subtitle1 text-weight-bold">
        {{ member.username }}
        <!-- Aktiv Badge -->
        <q-badge
          v-if="isActive"
          color="accent"
          text-color="white"
          class="q-mr-xs q-ml-md"
        >
          <q-icon name="play_arrow" size="15px" class="q-mr-xs" />
          <span v-if="isActive"> {{ statusVerb }} </span>
        </q-badge>
      </div>

      <div class="row q-gutter-xs items-center">

        <q-badge
          v-if="member.selected_game"
          color="secondary"
          text-color="white"
        >
          GAME
          <q-icon name="check"/>
        </q-badge>
        <q-badge
          v-if="member.banned_game"
          color="negative"
          text-color="white"
        >
          BAN
          <q-icon name="check"/>
        </q-badge>
      </div>
    </div>

    <!-- Game Info -->
    <div class="q-mt-xl">
      <div v-if="member.selected_game" class="q-mb-sm">
        <q-card flat bordered class="q-mb-md q-pa-sm shadow-1">
          <q-card-section class="row items-center justify-between">
            <div class="text-h6">{{ member.selected_game.game_name }}</div>

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
                <q-item v-for="option in member.selected_game.selected_options" :key="option.id">
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

      <div v-if="member.banned_game">
        <div class="text-caption text-weight-medium">Gebanntes Spiel:</div>
        <div class="text-body2 text-weight-bold text-negative">
          {{ member.banned_game }}
        </div>
      </div>

      <div
        v-if="!member.selected_game && !member.banned_game"
        class="text-caption text-grey-6"
      >
        Noch keine Auswahl oder Bann.
      </div>
    </div>
  </div>
</template>


<script setup lang="ts">
defineProps<{
  member: any;
  isActive: boolean;
  statusVerb: string;
}>();

import { ref } from 'vue';

const isExpanded = ref(false);
</script>
