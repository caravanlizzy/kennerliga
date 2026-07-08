export default {
  path: 'users/',
  meta: { requiresAuth: true, requiresAdmin: false, label: 'Users', icon: 'people_alt' },
  children: [
    {
      path: '',
      name: 'users',
      component: () => import('pages/user/UsersListPage.vue'),
      meta: { icon: 'people_alt', label: 'Users' },
    },
    {
      path: ':username',
      name: 'user-detail',
      component: () => import('pages/user/UserDetailPage.vue'),
      meta: { label: 'User Details', icon: 'person' },
    },
    {
      path: 'invite',
      name: 'invite-user',
      component: () => import('pages/user/UserInvitePage.vue'),
      meta: { label: 'Invite User', icon: 'person_add' },
    },
    {
      path: 'invitations',
      name: 'invitations',
      component: () => import('pages/user/InvitationListPage.vue'),
      meta: { label: 'Invitations', icon: 'mark_email_unread' },
    },
  ],
};
