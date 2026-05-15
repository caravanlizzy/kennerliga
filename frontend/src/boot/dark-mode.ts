import { boot } from 'quasar/wrappers';
import { Dark } from 'quasar';

export const DARK_MODE_STORAGE_KEY = 'kenner.darkMode';

export default boot(() => {
  try {
    const stored = localStorage.getItem(DARK_MODE_STORAGE_KEY);
    if (stored === 'true' || stored === 'false') {
      Dark.set(stored === 'true');
    } else if (stored === 'auto') {
      Dark.set('auto');
    }
  } catch (e) {
    // localStorage unavailable (private mode, SSR, etc.) — ignore
  }
});
