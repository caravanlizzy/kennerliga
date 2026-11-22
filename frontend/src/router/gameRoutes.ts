export default {
  path: 'games/',
  meta: {
    requiresAuth: true,
    label: 'Games',
    icon: 'sports_esports',
  },
  children: [
    {
      path: '',
      name: 'games',
      component: () => import('pages/game/GamesListPage.vue'),
      meta: {
        requiresAuth: true,
        icon: 'sports_esports',
        label: 'Game Catalog',
      },
    },
    {
      path: 'create',
      name: 'game-create',
      component: () => import('pages/game/GameCreatePage.vue'),
      meta: { requiresAdmin: true, icon: 'add_circle', label: 'Create Game' },
    },
    {
      path: ':id',
      name: 'game-detail',
      component: () => import('pages/game/GameDetailPage.vue'),
      meta: {
        requiresAuth: true,
        icon: 'sports_esports',
        label: 'Game Details',
      },
    },
    {
      path: ':id/config',
      name: 'game-config',
      component: () => import('pages/game/GameConfigPage.vue'),
      meta: {
        requiresAdmin: true,
        icon: 'settings',
        label: 'Game Configuration',
      },
    },
    {
      path: ':id/edit',
      name: 'game-edit',
      component: () => import('pages/game/EditGamePage.vue'),
      meta: { requiresAdmin: true, icon: 'edit', label: 'Edit Game' },
    },
  ],
};
