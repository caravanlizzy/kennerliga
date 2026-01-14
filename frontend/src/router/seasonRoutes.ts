export default {
  path: 'seasons/', meta: { requiresAuth: true }, children: [
    {
      path: '',
      name: 'seasons',
      component: () => import('pages/season/SeasonListPage.vue'),
      meta: { icon: 'military_tech', label: 'Seasons' },
    },
    {
      path: 'create',
      name: 'season-create',
      component: () => import('pages/season/SeasonCreatePage.vue'),
      meta: { requiresAdmin: true }
    },
    {
      path: ':id/manage',
      name: 'season-manage',
      component: () => import('pages/season/SeasonManagePage.vue'),
    },
    {
      path: ':id/overview',
      name: 'season-overview',
      component: () => import('pages/season/SeasonOverviewPage.vue'),
    }
  ]
};
