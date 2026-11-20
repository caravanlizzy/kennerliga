export default {
  path: 'match-results/',
  meta: { requiresAuth: true, label: 'Match Results', icon: 'emoji_events' },
  children: [
    {
      path: '',
      name: 'match-results',
      component: () => import('pages/result/MatchResultListPage.vue'),
      meta: { icon: 'emoji_events', label: 'Match Results' },
    },
    {
      path: ':id',
      name: 'match-result-detail',
      component: () => import('pages/result/MatchResultDetailPage.vue'),
      meta: { icon: 'emoji_events', label: 'Match Result' },
    },
  ],
};
