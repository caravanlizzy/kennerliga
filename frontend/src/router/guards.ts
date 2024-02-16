import { TUser, useUserStore } from 'stores/userStore';
import { useAxios } from '@vueuse/integrations/useAxios';
import { api } from 'boot/axios';
import { Router } from 'vue-router';

function getLocalStorageUser(): string {
  const userString = localStorage.getItem('user');
  if (userString) return JSON.parse(userString);
  return '';
}

async function checkAuthentication(user: TUser|null) {
  if(!user) return false;
  const { response } = await useAxios('checkAuthentication', {
      headers: {
        'Authorization': 'Token ' + user.token
      }
    },
    api
  );
  console.log(response);
  return false;
}

export async function applyGuards(router: Router) {
  const userStore = useUserStore();
  const  { user } = userStore;
  const isAuthenticated = await checkAuthentication(user);
  router.beforeEach((to, from, next) => {
    if (to.meta.requiresAuth) {
      if (to.name !== 'Login' && !isAuthenticated) next({ name: 'login' })
      else next()
    }
  });
}
