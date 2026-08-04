<template>
  <div v-if="show" class="kenner-title-bar-wrapper">
    <div class="kenner-title-bar-container">
      <div
        class="kenner-title-bar-content"
        :class="[
          isMobile ? 'column items-start q-py-md q-gutter-y-sm' : 'row no-wrap items-center',
          { 'no-border-radius-mobile': isMobile }
        ]"
      >
        <!-- Left Section: Breadcrumbs and Title -->
        <slot name="left">
          <div
            class="row items-center no-wrap q-gutter-x-sm left-section"
            :class="{ 'full-width': isMobile }"
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
            
            <div class="column justify-center q-ml-xs">
              <div 
                v-if="pageTitle" 
                class="text-weight-bolder text-dark line-height-1"
                :class="isMobile ? 'text-subtitle1' : 'text-h6'"
              >
                {{ pageTitle }}
              </div>
              <q-breadcrumbs 
                gutter="xs" 
                class="text-grey-6 text-weight-medium overflow-hidden breadcrumbs-small"
              >
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

const pageTitle = computed(() => route.meta.label as string | undefined);

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
  margin-bottom: 12px;
  
  @media (max-width: 599px) {
    padding-top: 0;
    margin-bottom: 4px;
  }
}

.kenner-title-bar-container {
  max-width: var(--kenner-max-width);
  width: 100%;
  margin: 0 auto;
}

.kenner-title-bar-content {
  background: white;
  border: 1px solid var(--kenner-border-color);
  border-radius: var(--kenner-card-radius, 16px);
  padding: 8px 16px;
  display: flex;
  min-height: 56px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.03);
  
  @media (max-width: 599px) {
    min-height: 52px;
    border-left: none;
    border-right: none;
    border-top: none;
    background: white;
    box-shadow: none;
  }
}

.line-height-1 {
  line-height: 1.2;
}

.breadcrumbs-small {
  font-size: 11px;
}

::deep(.q-breadcrumbs__el) {
  white-space: nowrap;
}

::deep(.q-breadcrumbs__el-icon) {
  font-size: 14px;
}

.left-section {
  flex-shrink: 1;
  min-width: 0;
}

</style>
