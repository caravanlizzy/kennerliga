import { defineStore } from 'pinia';
import { ref, watch } from 'vue';
import { LocalStorage } from 'quasar';

export interface NavSection {
  id: string;
  title: string;
  icon: string;
  color: string;
  isActive?: boolean | import('vue').Ref<boolean>;
  onClick?: () => void;
}

export const useUiStore = defineStore('ui', () => {
  const isDev = ref(false);
  const navSections = ref<NavSection[]>([]);

  function showDev() {
    isDev.value = true;
  }
  function hideDev() {
    isDev.value = false;
  }
  function toggleDev() {
    isDev.value = !isDev.value;
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
    navSections,
    registerSection,
    unregisterSection
  };
});
