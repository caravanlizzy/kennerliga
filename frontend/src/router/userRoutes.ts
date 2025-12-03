export default {
  path: 'users/',
  meta: { requiresAuth: true, requiresAdmin: false },
  children: [
    {
      path: '',
      name: 'users',
      component: () => import('pages/user/UsersListPage.vue'),
      meta: { icon: 'group', label: 'Users' },
    },
    {
      path: ':username',
      name: 'user-detail',
      component: () => import('pages/user/UserDetailPage.vue'),
    },
    {
      path: 'invite',
      name: 'invite-user',
      component: () => import('pages/user/UserInvitePage.vue'),
    },
    {
      path: 'invitations',
      name: 'invitations',
      component: () => import('pages/user/InvitationListPage.vue'),
    },
  ],
};
