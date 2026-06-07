<template>
  <div class="row items-center no-wrap">
    <KennerButton
      :to="{ name: 'home' }"
      unelevated
      flat
      color="dark"
      :class="[isMobile ? 'q-px-xs' : 'q-px-md', 'text-weight-bold']"
      style="height: 44px; min-width: 44px;"
    >
      <div class="row items-center no-wrap brand-wrap">
        <q-icon
          name="img:icons/favicon.svg"
          class="brand-k-icon"
          :class="{ 'brand-k-icon--mobile': isMobile }"
        />
        <span
          v-if="!isMobile"
          class="text-h5 text-weight-bold tracking-tight brand-text"
        ><span class="text-primary">enner</span><span class="text-accent">Liga</span></span>
      </div>
    </KennerButton>

  </div>
</template>
<script setup lang="ts">
import { useResponsive } from 'src/composables/responsive';
import KennerButton from 'components/base/KennerButton.vue';

const { isMobile } = useResponsive();

</script>

<style scoped lang="scss">
.brand-wrap {
  line-height: 1;
}

.brand-k-icon {
  font-size: 1.6rem;
  height: 1.6rem;
  width: 1.6rem;
  margin-right: -2px;
  position: relative;
  top: 1px;
}

.brand-k-icon--mobile {
  margin-right: 0;
}

.brand-text {
  letter-spacing: -0.5px;
  line-height: 1;
}
</style>
