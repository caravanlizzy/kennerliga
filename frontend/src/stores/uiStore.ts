import { defineStore } from 'pinia';
import { ref, watch } from 'vue';
import { LocalStorage } from 'quasar';

export interface MinimizedItem {
  id: string;
  title: string;
  icon: string;
  color: string;
  type: 'section' | 'announcement';
}

export interface NavSection {
  id: string;
  title: string;
  icon: string;
  color: string;
  isActive?: boolean | import('vue').Ref<boolean>;
  onClick?: () => void;
}

const STORAGE_KEY = 'minimized_items';

export const useUiStore = defineStore('ui', () => {
  const isDev = ref(false);
  const minimizedItems = ref<MinimizedItem[]>(LocalStorage.getItem(STORAGE_KEY) || []);
  const navSections = ref<NavSection[]>([]);
  const activeTab = ref('seasons');

  watch(
    minimizedItems,
    (val) => {
      LocalStorage.set(STORAGE_KEY, val);
    },
    { deep: true }
  );

  function showDev() {
    isDev.value = true;
  }
  function hideDev() {
    isDev.value = false;
  }
  function toggleDev() {
    isDev.value = !isDev.value;
  }

  function minimize(item: MinimizedItem) {
    if (!minimizedItems.value.find(i => i.id === item.id)) {
      minimizedItems.value.push(item);
    }
  }

  function restore(id: string) {
    minimizedItems.value = minimizedItems.value.filter(i => i.id !== id);
  }

  function isMinimized(id: string) {
    return minimizedItems.value.some(i => i.id === id);
  }

  function registerSection(section: NavSection) {
    if (!navSections.value.find(s => s.id === section.id)) {
      navSections.value.push(section);
    }
  }

  function unregisterSection(id: string) {
    navSections.value = navSections.value.filter(s => s.id !== id);
  }

  return {
    isDev,
    showDev,
    hideDev,
    toggleDev,
    minimizedItems,
    navSections,
    activeTab,
    minimize,
    restore,
    isMinimized,
    registerSection,
    unregisterSection
  };
});
