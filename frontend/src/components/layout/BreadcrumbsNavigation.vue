<template>
  <div v-if="show" class="breadcrumbs-wrapper">
    <div class="breadcrumbs-container q-px-md">
      <div class="breadcrumbs-content row items-center q-gutter-x-sm no-wrap">
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

  // We skip the first matched record if it's just the root/layout
  // and we only include those with meta labels
  route.matched.forEach((record) => {
    if (record.meta && record.meta.label && record.path !== '/') {
      // Avoid duplicate labels if parent and child have same label
      if (result.length > 0 && result[result.length - 1].label === record.meta.label) {
        return;
      }

      // Handle dynamic segments in path if any (though route.path might be better)
      let path = record.path;
      if (path.includes(':')) {
         // If it's the current route, use the actual path
         if (record.name === route.name) {
             path = route.path;
         } else {
             // Try to resolve params for parent routes if possible
             // This is simplified; usually you'd need more logic here
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
.breadcrumbs-wrapper {
  padding-top: 12px;
  margin-bottom: 8px;
}

.breadcrumbs-container {
  max-width: 1300px;
  width: 100%;
  margin: 0 auto;
}

.breadcrumbs-content {
  background: rgba(255, 255, 255, 0.4);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid rgba(0, 0, 0, 0.05);
  border-radius: 12px;
  padding: 6px 12px;
  display: inline-flex;
  min-width: 200px;
}


:deep(.q-breadcrumbs__el) {
  white-space: nowrap;
}

:deep(.q-breadcrumbs__el-icon) {
  font-size: 18px;
}
</style>
