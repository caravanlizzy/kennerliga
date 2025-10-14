export default {
  path: 'admin/', meta: { requiresAuth: true, requiresAdmin: true }, children: [
    {
      path: '',
      name: 'admin-home',
      component: () => import('pages/admin/AdminPage.vue'),
      meta: { icon: 'build', label: 'Manage Kennerliga' },
    },
    {
      path: 'season-create',
      name: 'season-create',
      component: () => import('pages/admin/CreateSeasonPage.vue'),
    }
  ]
};
