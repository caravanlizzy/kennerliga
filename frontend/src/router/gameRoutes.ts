export default {
  path: 'games/', children: [
    { path: '', name: 'games', component: () => import('pages/game/GamesList.vue') },
    { path: ':id', name: 'game-detail', component: () => import('pages/game/GameDetail.vue') },
    { path: 'new', name: 'game-create', component: () => import('pages/game/GameCreate.vue') },
  ]
 }
