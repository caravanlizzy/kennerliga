import { defineStore } from 'pinia';
import { ref } from 'vue';
import { Dark } from 'quasar';

export type ThemeMode = 'auto' | 'dark' | 'light';

export const useThemeStore = defineStore(
  'themeStore',
  () => {
    const mode = ref<ThemeMode>('auto');
    const isDark = ref<boolean>(false);

    function syncQuasarDark(targetMode: ThemeMode) {
      if (targetMode === 'auto') {
        Dark.set('auto');
      } else {
        Dark.set(targetMode === 'dark');
      }
      isDark.value = Dark.isActive;
    }

    function setMode(newMode: ThemeMode) {
      mode.value = newMode;
      syncQuasarDark(newMode);
    }

    function toggleDark() {
      if (isDark.value) {
        setMode('light');
      } else {
        setMode('dark');
      }
    }

    function initTheme() {
      syncQuasarDark(mode.value);
    }

    return {
      mode,
      isDark,
      setMode,
      toggleDark,
      initTheme,
    };
  },
  {
    persist: {
      paths: ['mode'],
      afterRestore: (ctx) => {
        const store = ctx.store as unknown as {
          mode: ThemeMode;
          initTheme: () => void;
        };
        store.initTheme();
      },
    },
  }
);
