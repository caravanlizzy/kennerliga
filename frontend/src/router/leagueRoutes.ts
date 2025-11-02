export default {
  path: 'leagues/', meta: { requiresAuth: true }, children: [
    {
      path: 'my',
      name: 'my-league',
      component: () => import('pages/league/MyLeaguePage.vue'),
    },
    {
      path: ':id',
      name: 'league-detail',
      component: () => import('pages/league/LeagueDetailPage.vue'),
    }
  ]
};
