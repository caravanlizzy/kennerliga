<template>
  <ContentSection
    title="Leagues"
    icon="groups"
    color="accent"
    :bordered="false"
  >
    <template #header-extra>
      <KennerButton
        v-if="isAdmin"
        outline
        no-caps
        size="sm"
        color="accent"
        icon="add"
        label="Add League"
        class="q-ml-md"
        @click="$emit('open-add-league')"
      />
    </template>

    <div
      v-if="leagues.length === 0"
      class="text-grey-7 q-pa-md bg-grey-1 rounded-borders text-center column items-center q-gutter-y-sm"
    >
      <div>No leagues found for this season.</div>
      <KennerButton
        v-if="isAdmin"
        no-caps
        size="sm"
        color="accent"
        icon="add"
        label="Add League"
        @click="$emit('open-add-league')"
      />
    </div>
    <q-list v-else separator class="league-list-container">
      <LeagueList
        v-for="league in leagues"
        :key="league.id"
        :league="league"
        @delete="$emit('delete-league', league)"
      />
    </q-list>
  </ContentSection>
</template>

<script setup lang="ts">
import ContentSection from 'components/base/ContentSection.vue';
import KennerButton from 'components/base/KennerButton.vue';
import LeagueList from 'components/season/LeagueList.vue';
import type { TLeagueDto } from 'src/types';

defineProps<{
  leagues: TLeagueDto[];
  isAdmin: boolean;
}>();

defineEmits<{
  (e: 'open-add-league'): void;
  (e: 'delete-league', league: TLeagueDto): void;
}>();
</script>
