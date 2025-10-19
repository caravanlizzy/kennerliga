<!-- PlannedFeatures.vue -->
<template>
  <section class="q-pa-sm">
    <div class="text-subtitle1 text-weight-medium text-primary q-mb-sm">
      Planned Features
    </div>

    <q-list separator dense class="rounded-borders bg-grey-1">
      <q-item
        v-for="f in features"
        :key="f.title"
        clickable
        class="q-hoverable"
      >
        <q-item-section avatar>
          <q-avatar color="primary" text-color="white" size="32px">
            <q-icon :name="f.icon" />
          </q-avatar>
        </q-item-section>

        <q-item-section>
          <q-item-label class="text-weight-medium text-dark">
            {{ f.title }}
          </q-item-label>
          <q-item-label caption class="text-grey-7">
            {{ f.desc }}
          </q-item-label>
        </q-item-section>
      </q-item>
    </q-list>
  </section>
</template>

<script setup lang="ts">
const features = [
  { title: 'Upload Past Leagues', desc: 'Manage previous seasons.', icon: 'calendar_month' },
  { title: 'Announcement Display', desc: 'League news and updates.', icon: 'campaign' },
  { title: 'Register for Season', desc: 'Join upcoming seasons.', icon: 'how_to_reg' },
  { title: 'Feedback Options', desc: 'Share thoughts in chat.', icon: 'chat_bubble' },
  { title: 'Yearly Standings', desc: 'Ranks by year.', icon: 'leaderboard' },
  { title: 'Profile Details', desc: 'Player profile & stats.', icon: 'person' }
]
</script>
