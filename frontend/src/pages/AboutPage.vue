<template>
  <q-page class="q-py-md flex justify-center">
    <div style="max-width: var(--kenner-max-width-text); width: 100%">
      <div class="text-h5 text-weight-bold q-mb-lg text-dark tracking-tight">
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
