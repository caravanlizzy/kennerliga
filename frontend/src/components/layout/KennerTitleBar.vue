<template>
  <div v-if="show" class="kenner-title-bar-wrapper">
    <div class="kenner-title-bar-container">
      <div
        class="kenner-title-bar-content items-center"
        :class="isMobile ? 'column q-py-sm q-gutter-y-sm' : 'row no-wrap'"
      >
        <!-- Left Section: Breadcrumbs -->
        <slot name="left">
          <div
            class="row items-center no-wrap q-gutter-x-sm left-section"
            :class="{ 'full-width justify-center': isMobile }"
          >
            <KennerButton
              flat
              icon="arrow_back"
              shape="circle"
              color="grey-7"
              size="sm"
              @click="$router.back()"
            >
              <KennerTooltip>Back</KennerTooltip>
            </KennerButton>
            <q-breadcrumbs gutter="sm" class="text-grey-7 text-weight-medium overflow-hidden">
              <q-breadcrumbs-el icon="home" to="/" />
              <q-breadcrumbs-el
                v-for="crumb in crumbs"
                :key="crumb.path"
                :label="crumb.label"
                :icon="crumb.icon"
                :to="crumb.path"
              />
            </q-breadcrumbs>
          </div>
        </slot>

        <q-space v-if="!isMobile" />

        <!-- Right Section: Actions/Other Content -->
        <slot name="right" />
      </div>

      <!-- Bottom Section (optional) -->
      <slot name="bottom" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useRoute } from 'vue-router';
import { useResponsive } from 'src/composables/responsive';
import KennerButton from 'components/base/KennerButton.vue';
import KennerTooltip from 'components/base/KennerTooltip.vue';

const route = useRoute();
const { isMobile } = useResponsive();

const show = computed(() => {
  if (!route.name) return true;

  const alwaysExclude = ['home', 'login', 'register'];
  if (alwaysExclude.includes(route.name as string)) return false;

  // Mobile top-level navigation items
  const mobileTabs = ['season-standings', 'live', 'leaderboard'];
  if (isMobile.value && mobileTabs.includes(route.name as string)) return false;

  return true;
});

const crumbs = computed(() => {
  const result: { label: string; icon?: string; path: string }[] = [];

  route.matched.forEach((record) => {
    if (record.meta && record.meta.label && record.path !== '/') {
      if (result.length > 0 && result[result.length - 1].label === record.meta.label) {
        return;
      }

      let path = record.path;
      if (path.includes(':')) {
         if (record.name === route.name) {
             path = route.path;
         } else {
             Object.entries(route.params).forEach(([key, value]) => {
               path = path.replace(`:${key}`, Array.isArray(value) ? value[0] : value);
             });
         }
      }

      result.push({
        label: record.meta.label as string,
        icon: record.meta.icon as string | undefined,
        path: path || '/',
      });
    }
  });
  return result;
});
</script>

<style scoped lang="scss">
.kenner-title-bar-wrapper {
  padding-top: 12px;
  margin-bottom: 8px;
}

.kenner-title-bar-container {
  max-width: var(--kenner-max-width);
  width: 100%;
  margin: 0 auto;
}

.kenner-title-bar-content {
  background: var(--kenner-bg-glass, rgba(255, 255, 255, 0.95));
  border: 1px solid var(--kenner-border-color);
  border-radius: var(--kenner-card-radius, 0px);
  padding: 6px 16px;
  display: flex;
  min-height: 48px;
}

::deep(.q-breadcrumbs__el) {
  white-space: nowrap;
}

::deep(.q-breadcrumbs__el-icon) {
  font-size: 18px;
}

.left-section {
  flex-shrink: 1;
  min-width: 0;
}

</style>
