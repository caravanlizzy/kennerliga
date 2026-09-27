import { boot } from 'quasar/wrappers';
import { useThemeStore } from 'stores/themeStore';

export default boot(() => {
  const themeStore = useThemeStore();
  themeStore.initTheme();
});
