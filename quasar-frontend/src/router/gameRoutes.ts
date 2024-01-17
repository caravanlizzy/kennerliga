export default {
  path: 'games/', children: [
    { path: '', name: 'games', component: () => import('pages/game/GamesList.vue') },
    { path: ':id', name: 'gameDetail', component: () => import('pages/game/GamesList.vue') },
    // { path: 'new', name: 'gameCreate', component: () => import('pages/GamesList.vue') },
  ]
 }
