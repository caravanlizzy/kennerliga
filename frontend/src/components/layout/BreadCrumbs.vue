<template>
  <q-toolbar class="breadcrumbs-container" >
    <div class="q-pa-xs row items-center justify-between no-wrap " style="width: 100%">
      <KennerButton flat color="primary" size="small" icon="arrow_back" @click="()=>router.go(-1)" />
      <div>
        <q-breadcrumbs separator=">" :class="`text-primary`" :active-color="color">
          <q-breadcrumbs-el :to="{ name:crumb.forwardRouteName }" v-for="crumb in breadCrumbs" :key="crumb.label"
                            :label="crumb.label"
                            :icon="crumb.icon"
                            class="q-pa-xs"
          />
        </q-breadcrumbs>
      </div>
      <KennerButton class="" flat color="primary" size="small" icon="arrow_forward" @click="()=>router.go(1)" />
    </div>
  </q-toolbar>
</template>

<script setup lang="ts">
import { useRoute, RouteLocationNormalizedLoaded, useRouter, RouteRecord } from 'vue-router';
import { BreadCrumb } from 'src/types';
import { ref, Ref, watch } from 'vue';
import KennerButton from 'components/base/KennerButton.vue';

defineProps<{ color: string }>();

const router = useRouter();
const routeSplitRoute = useRoute();

const allRoutes = router.getRoutes();
const breadCrumbs: Ref<BreadCrumb[]> = ref([]);

const getIcon = (routeString: string, routeObject: RouteRecord): string => {
  if (routeObject.meta.icon) return routeObject.meta.icon;
  else if (routeString === 'edit') return 'edit';
  else if (routeString === 'create') return 'add_circle';
  else return '';
};

const getLabel = (routeString: string, routeObject: RouteRecord): string => {
  if (routeObject.meta.label) return routeObject.meta.label;
  else if (routeString === 'edit') return 'bearbeiten';
  else if (routeString === 'create') return 'erstellen';
  else return '';
};

const createBreadCrumb = (routeString: string, routeObject: RouteRecord): BreadCrumb => {
  return <BreadCrumb>{
    label: getLabel(routeString, routeObject),
    icon: getIcon(routeString, routeObject),
    forwardRouteName: routeObject.name
  };
};

const getRouteObject = (allRoutes: RouteRecord[], currentRouteString: string): RouteRecord | undefined => {
  return allRoutes.find((r) => r.path.replaceAll('/', '') === currentRouteString);
};
const getBreadCrumbs = (routeSplitRoute: RouteLocationNormalizedLoaded): BreadCrumb[] => {
  const breadCrumbs = [{
    label: 'Home',
    icon: 'home',
    forwardRouteName: 'home'
  }];
  const routeStrings = routeSplitRoute.fullPath.split('/').filter((e) => e !== '');
  let route = '';
  for (let routeString of routeStrings) {
    route += routeString;
    const routeObject: RouteRecord | undefined = getRouteObject(allRoutes, route);
    if (routeObject) {
      breadCrumbs.push(createBreadCrumb(routeString, routeObject));
    }
  }
  return breadCrumbs;
};


watch(
  () => routeSplitRoute.fullPath,
  () => {
    breadCrumbs.value = getBreadCrumbs(routeSplitRoute);
  },
  { immediate: true }
);

</script>

<style scoped>
  .breadcrumbs-container {
    background-color: #fafafa;
  }
</style>
