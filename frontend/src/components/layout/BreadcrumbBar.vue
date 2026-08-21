<template>
  <div v-if="show" class="breadcrumb-bar">
    <div class="breadcrumb-bar__inner q-mx-auto q-px-md row items-center no-wrap">
      <div class="row items-center no-wrap history-nav">
        <KennerButton
          flat
          icon="arrow_back"
          shape="circle"
          color="grey-7"
          size="sm"
          @click="router.back()"
        >
          <KennerTooltip>Back</KennerTooltip>
        </KennerButton>
        <KennerButton
          flat
          icon="arrow_forward"
          shape="circle"
          color="grey-7"
          size="sm"
          @click="router.forward()"
        >
          <KennerTooltip>Forward</KennerTooltip>
        </KennerButton>
      </div>
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
import { useRoute, useRouter } from 'vue-router';
import { useResponsive } from 'src/composables/responsive';
import KennerButton from 'components/base/KennerButton.vue';
import KennerTooltip from 'components/base/KennerTooltip.vue';

const route = useRoute();
const router = useRouter();
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
  // Neutral warm-grey tint, not the app's slate/blue page-accent token --
  // keeps the strip visually quiet without leaning into any hue.
  background: rgba(0, 0, 0, 0.035);
  border-bottom: 1px solid var(--kenner-border-color);
}

.breadcrumb-bar__inner {
  max-width: var(--kenner-max-width);
  padding-top: 6px;
  padding-bottom: 6px;
  font-size: 11px;
  gap: 2px;
}

.history-nav {
  gap: 2px;
  margin-right: 4px;

  :deep(.q-btn) {
    width: 22px;
    height: 22px;
    min-height: 22px;
    margin: 0;
  }

  :deep(.q-icon) {
    font-size: 16px;
  }
}

:deep(.q-breadcrumbs__el) {
  white-space: nowrap;
}

:deep(.q-breadcrumbs__el-icon) {
  font-size: 14px;
}
</style>
