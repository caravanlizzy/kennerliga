export default {
  path: 'statistics/',
  meta: {
    requiresAuth: true,
    requiresAdmin: false,
    label: 'Hall of Fame & Records',
    icon: 'stars',
  },
  children: [
    {
      path: '',
      name: 'statistics',
      component: () => import('pages/statistics/StatisticsPage.vue'),
      meta: { icon: 'stars', label: 'Hall of Fame & Records' },
    },
  ],
};
