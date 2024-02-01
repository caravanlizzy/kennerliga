export default {
  path: 'users/', children: [
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
    // { path: 'new', name: 'gameCreate', component: () => import('pages/GamesList.vue') },
  ]
};
