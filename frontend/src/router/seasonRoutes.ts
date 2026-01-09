export default {
  path: 'seasons/', meta: { requiresAuth: true, requiresAdmin: true }, children: [
    {
      path: '',
      name: 'seasons',
      component: () => import('pages/season/SeasonListPage.vue'),
      meta: { icon: 'build', label: 'Manage Seasons' },
    },
    {
      path: 'create',
      name: 'season-create',
      component: () => import('pages/season/SeasonCreatePage.vue'),
    },
    {
      path: ':id',
      name: 'season-detail',
      component: () => import('pages/season/SeasonManagePage.vue'),
    },
    {
      path: ':id/overview',
      name: 'season-overview',
      component: () => import('pages/season/SeasonOverviewPage.vue'),
    }
  ]
};
