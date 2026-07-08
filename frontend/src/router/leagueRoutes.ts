export default {
  path: 'leagues/', meta: { requiresAuth: true, label: 'Leagues', icon: 'leaderboard' }, children: [
    {
      path: 'my',
      name: 'my-league',
      component: () => import('pages/league/MyLeaguePage.vue'),
      meta: { label: 'My League', icon: 'military_tech' }
    },
    {
      path: ':id/manage',
      name: 'league-manager',
      component: () => import('pages/league/ManageLeaguePage.vue'),
      meta: { requiresAdmin: true, label: 'Manage League', icon: 'settings' }
    }
  ]
};
