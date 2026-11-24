<template>
  <q-page class="q-py-md flex justify-center">
    <div
      style="max-width: var(--kenner-max-width-text); width: 100%"
      class="q-px-sm"
    >
      <!-- Header / Hero -->
      <div
        class="about-hero-card row items-center justify-between"
        :class="isMobile ? 'q-pa-md q-mb-sm' : 'q-pa-lg q-mb-lg'"
      >
        <div class="column">
          <div class="row items-center q-gutter-x-sm q-mb-xs">
            <BrandLogo icon-size="32px" word-size="1.5rem" />
          </div>
          <div class="text-caption text-grey-7">
            The competitive board game league platform.
          </div>
        </div>
        <div class="row items-center q-gutter-x-xs">
          <q-chip
            outline
            :color="updateAvailable ? 'warning' : 'primary'"
            :icon="updateAvailable ? 'system_update' : 'verified'"
            class="text-weight-bold cursor-pointer"
            @click="onCheckUpdates"
          >
            v{{ appVersion }}
            <KennerTooltip>
              {{
                updateAvailable
                  ? 'Update available! Click to apply.'
                  : 'Click to check for updates'
              }}
            </KennerTooltip>
          </q-chip>
          <KennerButton
            flat
            round
            dense
            :icon="updateAvailable ? 'system_update' : 'refresh'"
            :color="updateAvailable ? 'warning' : 'primary'"
            :loading="isCheckingForUpdates"
            @click="onCheckUpdates"
          >
            <KennerTooltip>
              {{
                updateAvailable
                  ? 'Update available! Click to apply.'
                  : 'Check for updates'
              }}
            </KennerTooltip>
          </KennerButton>
        </div>
      </div>

      <div class="row q-col-gutter-md">
        <div class="col-12">
          <q-card flat class="about-section-card q-pa-md">
            <q-card-section>
              <PurposeSection />
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
import KennerButton from 'components/base/KennerButton.vue';
import KennerTooltip from 'components/base/KennerTooltip.vue';
import { useResponsive } from 'src/composables/responsive';
import {
  appVersion,
  updateAvailable,
  isCheckingForUpdates,
  checkForUpdates,
  showUpdatePrompt,
} from 'src/services/appUpdateService';

defineOptions({ name: 'AboutPage' });

const { isMobile } = useResponsive();

async function onCheckUpdates(): Promise<void> {
  if (updateAvailable.value) {
    showUpdatePrompt(null, true);
    return;
  }
  await checkForUpdates(true);
}
</script>

<style scoped lang="scss">
.about-hero-card {
  background: var(--kenner-surface-overlay);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  border: 1px solid var(--kenner-border-color);
  border-radius: var(--kenner-card-radius, 16px);
}

.about-section-card {
  background: var(--kenner-surface-overlay);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  border: 1px solid var(--kenner-border-color);
  border-radius: var(--kenner-card-radius, 16px);
}
</style>
