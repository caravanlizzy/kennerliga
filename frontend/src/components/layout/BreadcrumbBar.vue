<template>
  <div v-if="show" class="breadcrumb-bar">
    <div class="breadcrumb-bar__inner q-mx-auto q-px-md">
      <q-breadcrumbs gutter="xs" class="text-grey-6 text-weight-medium">
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
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useRoute } from 'vue-router';
import { useResponsive } from 'src/composables/responsive';

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
// A slim, full-bleed strip directly under the navbar rather than another
// bordered card -- the breadcrumb trail is secondary navigation, so it
// stays visually quiet (small text, no border/shadow of its own).
.breadcrumb-bar {
  width: 100%;
  background: var(--kenner-bg-page-accent, #f1f5f9);
  border-bottom: 1px solid var(--kenner-border-color);
}

.breadcrumb-bar__inner {
  max-width: var(--kenner-max-width);
  padding-top: 6px;
  padding-bottom: 6px;
  font-size: 11px;
}

:deep(.q-breadcrumbs__el) {
  white-space: nowrap;
}

:deep(.q-breadcrumbs__el-icon) {
  font-size: 14px;
}
</style>
