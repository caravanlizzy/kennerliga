<!-- PlannedFeatures.vue -->
<template>
  <section class="q-pa-sm">
    <div class="text-subtitle1 text-weight-medium text-dark q-mb-sm">
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
          <q-avatar color="dark" text-color="white" size="32px">
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
  { title: 'TAnnouncement Display', desc: 'League news and updates.', icon: 'campaign' },
  { title: 'Automated leage management', desc: 'I.e. open registraion, create leagues etc.', icon: 'auto-awesome' },
  { title: 'Profile Details', desc: 'Player profile & stats.', icon: 'person' }
]
</script>
