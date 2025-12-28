export default {
  path: 'games/', meta: { requiresAuth: true, requiresAdmin: true }, children: [
    {
      path: '',
      name: 'games',
      component: () => import('pages/game/GamesListPage.vue'),
      meta: { icon: 'casino', label: 'Spiele' }
    },
    {
      path: ':id',
      name: 'game-detail',
      component: () => import('pages/game/GameDetailPage.vue'),
        meta: { icon: 'primary_i', label: 'Details'}
    },
    {
      path: 'create',
      name: 'game-create',
      component: () => import('pages/game/GameCreatePage.vue')
    },
    {
      path: ':id/edit',
      name: 'game-edit',
      component: () => import('pages/game/EditGamePage.vue')
    },
  ]
};
