export default {
  path: 'users/', meta:{requiresAuth:true, requiresAdmin: true },  children: [
    {
      path: '',
      name: 'users',
      component: () => import('pages/user/UsersList.vue'),
      meta: { icon: 'group', label: 'SpielerInnen' }
    },
    {
      path: ':id',
      name: 'user-detail',
      component: () => import('pages/user/UserDetail.vue'),
    }
  ]
};
