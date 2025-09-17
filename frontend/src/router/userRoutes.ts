export default {
  path: 'users/', meta:{requiresAuth:true, requiresAdmin: true },  children: [
    {
      path: '',
      name: 'users',
      component: () => import('pages/user/UsersList.vue'),
      meta: { icon: 'group', label: 'Players' }
    },
    {
      path: ':id',
      name: 'user-detail',
      component: () => import('pages/user/UserDetail.vue'),
    },
    {
      path: 'invite',
      name: 'user-invite',
      component: () => import('pages/user/UserInvite.vue'),
    },
    {
      path: 'invitations',
      name: 'list-invitations',
      component: () => import('pages/user/InvitationList.vue'),
    }
  ]
};
