export default {
  path: 'players/',
  meta: { requiresAuth: true, requiresAdmin: false, label: 'Players', icon: 'people_alt' },
  children: [
    {
      path: '',
      name: 'players',
      component: () => import('pages/user/UsersListPage.vue'),
      meta: { icon: 'people_alt', label: 'Players' },
    },
    {
      path: ':username',
      name: 'user-detail',
      component: () => import('pages/user/UserDetailPage.vue'),
      meta: { label: 'Player Details', icon: 'person' },
    },
    {
      path: 'invite',
      name: 'invite-user',
      component: () => import('pages/user/UserInvitePage.vue'),
      meta: { label: 'Invite Player', icon: 'person_add' },
    },
    {
      path: 'invitations',
      name: 'invitations',
      component: () => import('pages/user/InvitationListPage.vue'),
      meta: { label: 'Invitations', icon: 'mark_email_unread' },
    },
  ],
};
