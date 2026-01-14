import { defineStore } from 'pinia';
import { ref, shallowRef, type Ref } from 'vue';

export interface NavSection {
  id: string;
  title: string;
  icon: string;
  color: string;
  isActive?: boolean | Ref<boolean>;
  onClick?: () => void;
}

export const useUiStore = defineStore('ui', () => {
  const isDev = ref(false);
  const navSections = shallowRef<NavSection[]>([]);
  const chatDrawerOpen = ref(false);

  function toggleChat() {
    chatDrawerOpen.value = !chatDrawerOpen.value;
  }

  function registerSection(section: NavSection) {
    if (!navSections.value.find((s: NavSection) => s.id === section.id)) {
      navSections.value = [...navSections.value, section];
    }
  }

  function unregisterSection(id: string) {
    navSections.value = navSections.value.filter(s => s.id !== id);
  }

  function clearSections() {
    navSections.value = [];
  }

  return {
    isDev,
    navSections,
    registerSection,
    unregisterSection,
    clearSections,
    chatDrawerOpen,
    toggleChat
  };
});
