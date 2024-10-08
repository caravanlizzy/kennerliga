export default {
  path: 'games/', meta: { requiresAuth: true, requiresAdmin: true }, children: [
    {
      path: '',
      name: 'games',
      component: () => import('pages/game/GamesList.vue'),
      meta: { icon: 'casino', label: 'Spiele' }
    },
    {
      path: ':id',
      name: 'game-detail',
      component: () => import('pages/game/gameDetail/GameDetail.vue'),
        meta: { icon: 'info_i', label: 'Details'}
    },
    {
      path: 'create',
      name: 'game-create',
      component: () => import('pages/game/GameCreate.vue')
    },
    {
      path: 'select',
      name: 'game-selection',
      component: () => import('pages/game/GameSelection.vue'),
      meta: { icon: 'sports_esports', label: 'Spielauswahl' }
    }
  ]
};
