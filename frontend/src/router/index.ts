import { route } from 'quasar/wrappers';
import {
  createMemoryHistory,
  createRouter,
  createWebHashHistory,
  createWebHistory
} from 'vue-router';

import routes from './routes';
import { useUserStore } from 'stores/userStore';
import { useUiStore } from 'stores/uiStore';

/*
 * If not building with SSR mode, you can
 * directly export the Router instantiation;
 *
 * The function below can be async too; either use
 * async/await or return a Promise which resolves
 * with the Router instance.
 */

export default route(async function(/* { store, ssrContext } */) {
  const createHistory = process.env.SERVER
    ? createMemoryHistory
    : (process.env.VUE_ROUTER_MODE === 'history' ? createWebHistory : createWebHashHistory);

  const Router = createRouter({
    scrollBehavior: () => ({ left: 0, top: 0 }),
    routes,

    // Leave this as is and make changes in quasar.conf.js instead!
    // quasar.conf.js -> build -> vueRouterMode
    // quasar.conf.js -> build -> publicPath
    history: createHistory(process.env.VUE_ROUTER_BASE)
  });
  Router.beforeEach(function(to, from, next) {
    const uiStore = useUiStore();
    uiStore.clearSections();

    const isMobile =
      !process.env.SERVER &&
      typeof window !== 'undefined' &&
      window.matchMedia('(max-width: 599px)').matches;

    if (to.name === 'home' && isMobile) {
      return next({ name: 'season-standings' });
    }

    // `requiresAuth` / `requiresAdmin` are declared on parent routes as well
    // as leaves, so resolve them across the whole matched chain. The record
    // closest to the leaf wins, which lets a child opt out of a section-wide
    // flag (e.g. `requiresAdmin: false` under an admin parent).
    const resolveMeta = (key: 'requiresAuth' | 'requiresAdmin'): boolean => {
      for (let i = to.matched.length - 1; i >= 0; i--) {
        const value = to.matched[i].meta[key];
        if (value !== undefined) return Boolean(value);
      }
      return false;
    };

    const requiresAuth = resolveMeta('requiresAuth');
    const requiresAdmin = resolveMeta('requiresAdmin');

    if (!requiresAuth && !requiresAdmin) return next();

    const userStore = useUserStore();
    const { user } = userStore;
    if (!user) return next({ name: 'login' });

    // Admin pages are still enforced by the API, but without this check a
    // non-admin can open them and see a broken, half-empty screen.
    if (requiresAdmin && !userStore.isAdmin) return next({ name: 'home' });

    return next();
  });
  return Router;
});
