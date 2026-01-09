import { RouteRecordRaw } from 'vue-router';
import gameRoutes from 'src/router/gameRoutes';
import userRoutes from 'src/router/userRoutes';
// This can be directly added to any of your `.ts` files like `router.ts`
// It can also be added to a `.d.ts` file. Make sure it's included in
// project's tsconfig.json "files"
import 'vue-router';
import seasonRoutes from 'src/router/seasonRoutes';
import leagueRoutes from 'src/router/leagueRoutes';

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
        component: () => import('pages/account/LoginPage.vue'),
      },
    ],
  },
  {
    path: '/register',
    component: () => import('layouts/LoginLayout.vue'),
    children: [
      {
        path: '',
        name: 'register',
        component: () => import('pages/account/RegistrationPage.vue'),
      },
    ],
  },
  {
    path: '/feedback',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      {
        path: '',
        name: 'feedback',
        component: () => import('pages/FeedbackPage.vue'),
      },
    ],
  },
  {
    path: '/announcements',
    component: () => import('layouts/MainLayout.vue'),
    meta: { requiresAuth: true, requiresAdmin: true },
    children: [
      {
        path: '',
        name: 'announcements',
        component: () => import('pages/AnnouncementManagementPage.vue'),
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
      seasonRoutes,
      leagueRoutes,
      {
        path: 'm/seasons',
        name: 'mobile-seasons',
        component: () => import('src/pages/mobile/SeasonsMobilePage.vue'),
      },
      {
        path: 'm/live',
        name: 'mobile-live',
        component: () => import('src/pages/mobile/LiveActionMobilePage.vue'),
      },
      {
        path: 'm/chat',
        name: 'mobile-chat',
        component: () => import('src/pages/mobile/ChatMobilePage.vue'),
      },
      {
        path: 'm/leaderboard',
        name: 'mobile-leaderboard',
        component: () => import('src/pages/mobile/LeaderboardMobilePage.vue'),
      },
      {
        path: 'dev',
        name: 'dev',
        component: () => import('pages/DevPage.vue'),
      },
    ],
  },

  // Always leave this as the last one,
  // but you can also remove it
  {
    path: '/:catchAll(.*)*',
    component: () => import('pages/ErrorNotFoundPage.vue'),
  },
];

export default routes;
