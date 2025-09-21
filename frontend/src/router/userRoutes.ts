export default {
  path: 'users/', meta:{requiresAuth:true, requiresAdmin: true },  children: [
    {
      path: '',
      name: 'users',
      component: () => import('pages/user/UsersListPage.vue'),
      meta: { icon: 'group', label: 'Players' }
    },
    {
      path: ':id',
      name: 'user-detail',
      component: () => import('pages/user/UserDetailPage.vue'),
    },
    {
      path: 'invite',
      name: 'user-invite',
      component: () => import('pages/user/UserInvitePage.vue'),
    },
    {
      path: 'invitations',
      name: 'list-invitations',
      component: () => import('pages/user/InvitationListPage.vue'),
    }
  ]
};
