export default {
  path: 'users/', children: [
    { path: '', name: 'users', component: () => import('pages/user/UsersList.vue') },
    { path: ':id', name: 'userDetail', component: () => import('pages/user/UsersList.vue') },
    // { path: 'new', name: 'gameCreate', component: () => import('pages/GamesList.vue') },
  ]
}
