export default {
  path: 'statistics/',
  meta: { requiresAuth: true, requiresAdmin: false, label: 'Statistics', icon: 'query_stats' },
  children: [
    {
      path: '',
      name: 'statistics',
      component: () => import('pages/statistics/StatisticsPage.vue'),
      meta: { icon: 'query_stats', label: 'Statistics' },
    },
  ],
};
