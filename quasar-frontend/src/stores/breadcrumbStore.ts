import { defineStore } from 'pinia';
import { ref } from 'vue';
import type { Ref } from 'vue';

type Breadcrump = {
  label: string;
  icon: string;
  routeName: string;
}

// export const useCounterStore = defineStore('breadcrumbs', {
//   state: () => ({
//     home: { label: '', icon: 'home' },
//   }),
//   getters: {
//     doubleCount: (state) => state.counter * 2,
//   },
//   actions: {
//     increment() {
//       this.counter++;
//     },
//   },
// });

export const useBreadcrumbs = defineStore('breadcrumbs', () => {
  const routeTree: Ref<Breadcrump[]> = ref([{label:'', icon:'home', routeName: 'home'}]);
  const updateTree = ():void => {};
})
