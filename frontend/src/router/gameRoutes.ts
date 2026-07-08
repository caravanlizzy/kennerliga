export default {
  path: 'games/', meta: { requiresAuth: true, requiresAdmin: true, label: 'Games', icon: 'sports_esports' }, children: [
    {
      path: '',
      name: 'games',
      component: () => import('pages/game/GamesListPage.vue'),
      meta: { icon: 'sports_esports', label: 'Games' }
    },
    {
      path: ':id',
      name: 'game-detail',
      component: () => import('pages/game/GameDetailPage.vue'),
        meta: { icon: 'info', label: 'Game Details'}
    },
    {
      path: 'create',
      name: 'game-create',
      component: () => import('pages/game/GameCreatePage.vue'),
      meta: { icon: 'add_circle', label: 'Create Game' }
    },
    {
      path: ':id/edit',
      name: 'game-edit',
      component: () => import('pages/game/EditGamePage.vue'),
      meta: { icon: 'edit', label: 'Edit Game' }
    },
  ]
};
