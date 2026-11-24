import { boot } from 'quasar/wrappers';
import { initAppUpdateListeners } from 'src/services/appUpdateService';

export default boot(({ router }) => {
  initAppUpdateListeners(router);
});
