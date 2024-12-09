import { RouteRecordRaw } from 'vue-router';
import gameRoutes from 'src/router/gameRoutes';
import userRoutes from 'src/router/userRoutes';
// This can be directly added to any of your `.ts` files like `router.ts`
// It can also be added to a `.d.ts` file. Make sure it's included in
// project's tsconfig.json "files"
import 'vue-router';

// To ensure it is treated as a module, add at least one `export` statement
export {};

declare module 'vue-router' {
  interface RouteMeta {
    // is optional
    label?: string;
    // must be declared by every route
    icon?: string;
  }
}

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    component: () => import('layouts/LoginLayout.vue'),
    children: [
      {
        path: '',
        name: 'login',
        component: () => import('pages/TheLogin.vue'),
      },
    ],
  },
  {
    path: '/',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      {
        path: '',
        name: 'home',
        component: () => import('pages/IndexPage.vue'),
        meta: { icon: 'home', label: 'Home' },
      },
      userRoutes,
      gameRoutes,
      {
        path: 'league',
        name: 'my-league',
        component: () => import('pages/MyLeague.vue'),
        meta: { icon: 'sports_esports', label: 'Meine Liga' },
      },
    ],
  },

  // Always leave this as last one,
  // but you can also remove it
  {
    path: '/:catchAll(.*)*',
    component: () => import('pages/ErrorNotFound.vue'),
  },
];

export default routes;
