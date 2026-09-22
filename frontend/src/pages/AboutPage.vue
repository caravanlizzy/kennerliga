<template>
  <q-page class="q-py-md flex justify-center">
    <div style="max-width: var(--kenner-max-width-text); width: 100%" class="q-px-sm">
      <!-- Header / Hero -->
      <div class="about-hero-card q-pa-lg q-mb-lg row items-center justify-between">
        <div class="column">
          <div class="row items-center q-gutter-x-sm q-mb-xs">
            <BrandLogo icon-size="32px" word-size="1.5rem" />
          </div>
          <div class="text-caption text-grey-7">
            The competitive board game league platform.
          </div>
        </div>
        <q-chip outline color="primary" icon="verified" class="text-weight-bold">
          v{{ appVersion }}
        </q-chip>
      </div>

      <div class="row q-col-gutter-md">
        <div class="col-12">
          <q-card flat class="about-section-card q-pa-md">
            <q-card-section>
              <PurposeSection />
            </q-card-section>
          </q-card>
        </div>

        <div class="col-12">
          <q-card flat class="about-section-card q-pa-md">
            <q-card-section>
              <div class="text-h6 text-weight-bold q-mb-sm text-dark row items-center q-gutter-x-sm">
                <q-icon name="campaign" color="primary" size="24px" />
                <span>What's New</span>
              </div>
              <ReleaseNotesSection />
            </q-card-section>
          </q-card>
        </div>
      </div>
    </div>
  </q-page>
</template>

<script setup lang="ts">
import BrandLogo from 'components/base/BrandLogo.vue';
import PurposeSection from 'components/home/PurposeSection.vue';
import ReleaseNotesSection from 'components/home/ReleaseNotesSection.vue';

defineOptions({ name: 'AboutPage' });

const appVersion = '1.0.0';
</script>

<style scoped lang="scss">
.about-hero-card {
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  border: 1px solid var(--kenner-border-color, rgba(0, 0, 0, 0.08));
  border-radius: var(--kenner-card-radius, 16px);
}

.about-section-card {
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  border: 1px solid var(--kenner-border-color, rgba(0, 0, 0, 0.08));
  border-radius: var(--kenner-card-radius, 16px);
}
</style>
