import { RouteRecordRaw } from 'vue-router';
import gameRoutes from 'src/router/gameRoutes';
import userRoutes from 'src/router/userRoutes';
// This can be directly added to any of your `.ts` files like `router.ts`
// It can also be added to a `.d.ts` file. Make sure it's included in
// project's tsconfig.json "files"
import 'vue-router';
import seasonRoutes from 'src/router/seasonRoutes';
import ResponsivePage from 'src/components/layout/ResponsivePage.vue';

const LiveMobile = () => import('src/pages/mobile/LiveActionMobilePage.vue');
// Chat feature temporarily disabled
// const ChatMobile = () => import('src/pages/mobile/ChatMobilePage.vue');
const LeaderboardMobile = () => import('src/pages/mobile/LeaderboardMobilePage.vue');

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
    path: '/announcements',
    component: () => import('layouts/MainLayout.vue'),
    meta: { requiresAuth: true, requiresAdmin: true },
    children: [
      {
        path: '',
        name: 'announcements',
        component: () => import('pages/AnnouncementManagementPage.vue'),
        meta: { label: 'Announcements', icon: 'campaign' },
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
        meta: { label: 'Feedback', icon: 'forum' },
      },
    ],
  },
  {
    path: '/release-notes',
    component: () => import('layouts/MainLayout.vue'),
    meta: { requiresAuth: true, requiresAdmin: true },
    children: [
      {
        path: '',
        name: 'release-notes',
        component: () => import('pages/ReleaseNoteManagementPage.vue'),
        meta: { label: 'Release Notes', icon: 'history' },
      },
    ],
  },
  {
    path: '/taskboard',
    component: () => import('layouts/MainLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'taskboard',
        component: () => import('pages/TaskBoardPage.vue'),
        meta: { label: 'Task Board', icon: 'view_kanban' },
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
      {
        path: 'my',
        name: 'my-league',
        component: () => import('pages/league/MyLeaguePage.vue'),
        meta: { label: 'My League', icon: 'military_tech' }
      },
      {
        path: 'rules',
        name: 'rules',
        component: () => import('pages/RulesPage.vue'),
        meta: { icon: 'gavel', label: 'Rules' }
      },
      {
        path: 'about',
        name: 'about',
        component: () => import('pages/AboutPage.vue'),
        meta: { icon: 'info', label: 'About' }
      },
      {
        path: 'live',
        name: 'live',
        component: ResponsivePage,
        props: { desktop: LiveMobile, mobile: LiveMobile },
        meta: { icon: 'bolt', label: 'Live', requiresAuth: true },
      },
      // Chat feature temporarily disabled
      // {
      //   path: 'chat',
      //   name: 'chat',
      //   component: ResponsivePage,
      //   props: { desktop: ChatMobile, mobile: ChatMobile },
      //   meta: { icon: 'chat', label: 'Chat', requiresAuth: true },
      // },
      {
        path: 'leaderboard',
        name: 'leaderboard',
        component: ResponsivePage,
        props: { desktop: LeaderboardMobile, mobile: LeaderboardMobile },
        meta: { icon: 'stars', label: 'Leaderboard', requiresAuth: true },
      },
      {
        path: 'm/:rest(.*)*',
        redirect: (to) => '/' + ((to.params.rest as string[]) ?? []).join('/'),
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
