<template>
  <div class="bg-black">
    <q-separator color="info" />
    <div class="q-px-md q-my-xs q-gutter-sm ">
      <q-breadcrumbs separator="-->" class="text-secondary" active-color="secondary">
        <template v-slot:separator>
          <q-icon
            aize="1.2em"
            name="arrow_right"
            color="white"
          />
        </template>
        <q-breadcrumbs-el :to="{ name:crumb.forwardRouteName }" v-for="crumb in breadCrumbs" :key="crumb.label"
                          :label="crumb.label"
                          :icon="crumb.icon" />
      </q-breadcrumbs>
    </div>
    <q-separator color="info" />
  </div>
</template>

<script setup lang="ts">
import { useRoute, RouteLocationNormalizedLoaded, useRouter, RouteRecord } from 'vue-router';
import { BreadCrumb } from 'components/models';
import { ref, Ref, watch } from 'vue';

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
