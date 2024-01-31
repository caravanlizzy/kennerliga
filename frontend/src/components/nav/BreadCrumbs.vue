<template>
  <div class="bg-black">
    <q-separator color="info" />
    <div class="q-px-md q-my-xs q-gutter-sm ">
      <q-breadcrumbs separator="-->" class="text-secondary" active-color="secondary">
        <template v-slot:separator>
          <q-icon
            aize="1.2em"
            name="arrow_right"
            color="secondary"
          />
        </template>
        <q-breadcrumbs-el :to="crumb.forwardRoute" v-for="crumb in breadCrumbs" :key="crumb.label" :label="crumb.label" :icon="crumb.icon" />
      </q-breadcrumbs>
    </div>
    <q-separator color="info" />
  </div>
</template>

<script setup lang="ts">

import { useRoute } from 'vue-router';
import { Ref, ref, watch } from 'vue';
import { BreadCrumb } from 'components/models';
import BreadCrumbs from 'components/nav/BreadCrumbs.vue';

const route = useRoute();
const homeBread:BreadCrumb = {
  label: '',
  icon:'home',
  forwardRoute: { name: 'home'}
}
const breadCrumbs:Ref<BreadCrumb[]> = ref([homeBread]);
const getBreadcrumb = (part: string): BreadCrumb =>  {
  switch(part) {
    case 'games':
      return {
        label: 'Spiele',
        icon: 'sports_esports',
        forwardRoute: {name: 'games'}
      }
    default:
      return homeBread;
  }
}
watch(
  () => route.fullPath,
  () => {
    breadCrumbs.value = [homeBread];
    for (const part of route.fullPath.split('/')) {
      if(part !== ""){
        const crumb = getBreadcrumb(part)
        breadCrumbs.value.push(crumb);
      }
    }
  },
  {immediate: true}
)


</script>
