export default {
  path: 'leagues/', meta: { requiresAuth: true }, children: [
    {
      path: 'my',
      name: 'my-league',
      component: () => import('pages/league/MyLeaguePage.vue'),
    },
    {
      path: ':id',
      name: 'league-manager',
      component: () => import('pages/league/LeagueManager.vue'),
    }
  ]
};
