<template>
  <div
    v-if="show"
    class="breadcrumb-bar"
    :class="{ 'border-bottom-none': hasAnnouncementBelow }"
  >
    <div
      class="breadcrumb-bar__inner q-mx-auto q-px-md row items-center no-wrap"
    >
      <q-breadcrumbs
        role="navigation"
        aria-label="Breadcrumb"
        gutter="sm"
        class="breadcrumb-trail text-weight-medium"
      >
        <template #separator>
          <q-icon name="chevron_right" size="18px" aria-hidden="true" />
        </template>
        <q-breadcrumbs-el label="Home" to="/" />
        <q-breadcrumbs-el
          v-for="(crumb, index) in crumbs"
          :key="crumb.path"
          :label="crumb.label"
          :to="index === crumbs.length - 1 ? undefined : crumb.path"
          :aria-current="index === crumbs.length - 1 ? 'page' : undefined"
          :class="{ 'breadcrumb-current': index === crumbs.length - 1 }"
        />
      </q-breadcrumbs>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useRoute } from 'vue-router';
import { useResponsive } from 'src/composables/responsive';
import { useUserStore } from 'stores/userStore';
import { useAnnouncementStore } from 'stores/announcementStore';
import { storeToRefs } from 'pinia';

const route = useRoute();
const { isMobile } = useResponsive();
const { isAuthenticated } = storeToRefs(useUserStore());
const { announcements } = storeToRefs(useAnnouncementStore());

const hasAnnouncementBelow = computed(() => {
  return (
    isMobile.value && isAuthenticated.value && announcements.value.length > 0
  );
});

const show = computed(() => {
  if (!route.name) return true;

  const alwaysExclude = ['home', 'login', 'register'];
  if (alwaysExclude.includes(route.name as string)) return false;

  // Mobile top-level navigation items
  const mobileTabs = ['season-standings', 'live', 'leaderboard', 'statistics'];
  if (isMobile.value && mobileTabs.includes(route.name as string)) return false;

  return true;
});

const crumbs = computed(() => {
  const result: { label: string; path: string }[] = [];

  route.matched.forEach((record) => {
    if (record.meta && record.meta.label && record.path !== '/') {
      if (
        result.length > 0 &&
        result[result.length - 1].label === record.meta.label
      ) {
        return;
      }

      let path = record.path;
      if (path.includes(':')) {
        if (record.name === route.name) {
          path = route.path;
        } else {
          Object.entries(route.params).forEach(([key, value]) => {
            path = path.replace(
              `:${key}`,
              Array.isArray(value) ? value[0] : value
            );
          });
        }
      }

      result.push({
        label: record.meta.label as string,
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
  // Sits in the fixed header over scrolling page content, so it needs an
  // opaque surface -- reuse the same near-solid "glass" white as the navbar
  // above it so content never bleeds through, with a faint grey overlay to
  // keep the strip subtly distinct from the navbar.
  background: linear-gradient(rgba(0, 0, 0, 0.02), rgba(0, 0, 0, 0.02)),
    var(--kenner-bg-glass, rgba(255, 255, 255, 0.98));
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  border-bottom: 1px solid var(--kenner-border-color);
}

.breadcrumb-bar__inner {
  max-width: var(--kenner-max-width);
  padding-top: 10px;
  padding-bottom: 10px;
  font-size: 13px;
}

.breadcrumb-trail {
  min-width: 0;
  overflow-x: auto;
  color: var(--kenner-text-muted, #718096);
}

:deep(.q-breadcrumbs__content) {
  flex-wrap: nowrap;
}

:deep(.q-breadcrumbs__el) {
  white-space: nowrap;
}

:deep(.breadcrumb-current) {
  color: var(--kenner-text-color, #333);
  font-weight: 600;
}
</style>
