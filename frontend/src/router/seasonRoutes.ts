export default {
  path: 'seasons/', meta: { requiresAuth: true, label: 'Seasons', icon: 'event' }, children: [
    {
      path: '',
      name: 'seasons',
      component: () => import('pages/season/SeasonListPage.vue'),
      meta: { icon: 'event', label: 'Seasons' },
    },
    {
      path: 'standings',
      name: 'season-standings',
      component: () => import('pages/mobile/SeasonsMobilePage.vue'),
      meta: { icon: 'military_tech', label: 'Standings' },
    },
    {
      path: 'create',
      name: 'season-create',
      component: () => import('pages/season/SeasonCreatePage.vue'),
      meta: { requiresAdmin: true, label: 'Create Season', icon: 'add_circle' }
    },
    {
      path: ':id/manage',
      name: 'season-manage',
      component: () => import('pages/season/SeasonManagePage.vue'),
      meta: { label: 'Manage Season', icon: 'settings' }
    },
    {
      path: ':id/overview',
      name: 'season-overview',
      component: () => import('pages/season/SeasonOverviewPage.vue'),
      meta: { label: 'Season Overview', icon: 'visibility' }
    }
  ]
};
