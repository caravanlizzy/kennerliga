<template>
  <q-page class="q-pa-md flex justify-center">
    <div style="max-width: 1000px; width: 100%">
      <div class="text-h4 text-weight-bold q-mb-lg text-primary row items-center">
        <q-icon name="info" class="q-mr-md" />
        About KennerLiga
      </div>

      <div class="row q-col-gutter-lg">
        <div class="col-12">
          <q-card flat class="glass-effect-subtle border-subtle">
            <q-card-section>
              <PurposeSection />
            </q-card-section>
          </q-card>
        </div>

        <div class="col-12">
          <q-card flat class="glass-effect-subtle border-subtle">
            <q-card-section>
              <div class="text-h6 text-weight-bold q-mb-sm">What's new</div>
              <ReleaseNotesSection />
            </q-card-section>
          </q-card>
        </div>
      </div>
    </div>
  </q-page>
</template>

<script setup lang="ts">
defineOptions({ name: 'AboutPage' });
import PurposeSection from 'components/home/PurposeSection.vue';
import ReleaseNotesSection from 'components/home/ReleaseNotesSection.vue';
</script>

<style scoped lang="scss">
.border-subtle {
  border: 1px solid rgba(0, 0, 0, 0.05);
}

.glass-effect-subtle {
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(4px);
}
</style>
