<template>
  <q-toolbar class="text-secondary breadcrumbs-container" >
    <div class="q-pa-xs row items-center justify-between " style="width: 100%">
      <KennerButton flat color="white" size="small" icon="arrow_back" @click="()=>router.go(-1)" />
      <div>
        <q-breadcrumbs separator="/" :class="`text-white`" :active-color="color">
<!--          <template v-slot:separator>-->
<!--            <q-icon-->
<!--              size="1.5em"-->
<!--              name=""-->
<!--              :color="color"-->
<!--            />-->
<!--          </template>-->
          <q-breadcrumbs-el :to="{ name:crumb.forwardRouteName }" v-for="crumb in breadCrumbs" :key="crumb.label"
                            :label="crumb.label"
                            :icon="crumb.icon"
                            class="q-pa-xs"
          />
        </q-breadcrumbs>
      </div>
      <KennerButton class="self-end" flat color="white" size="small" icon="arrow_forward" @click="()=>router.go(1)" />
    </div>
  </q-toolbar>
</template>

<script setup lang="ts">
import { useRoute, RouteLocationNormalizedLoaded, useRouter, RouteRecord } from 'vue-router';
import { BreadCrumb } from 'src/types';
import { ref, Ref, watch } from 'vue';
import KennerButton from 'components/buttons/KennerButton.vue';

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
    background-color: #5c5c5c;
  }
</style>
