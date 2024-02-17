import { defineStore } from 'pinia';
import { ref, Ref } from 'vue';
import { useAxios } from '@vueuse/integrations/useAxios';
import { api } from 'boot/axios';
import { useRouter } from 'vue-router';

export type TUser = {
  email: string;
  username: string;
  bga?: string;
  token: string;
}


export const useUserStore = defineStore('userStore', () => {
  const router = useRouter();
  const user: Ref<TUser | null> = ref(null);
  const isAuthenticated: Ref<boolean> = ref(false);

  async function login(email: string, password: string): Promise<void> {
    const { data, error, isFinished } = await useAxios('login/', {
      method: 'POST',
      data: { username: email, password }
    }, api);
    if (isFinished.value && !error.value) {
      const userData = data.value.user;
      applyLogin(userData);
      await router.push({ name: 'home' });
    }

  }

  function storeToken():void {
    if(user.value){
      api.defaults.headers.common['Authorization'] = 'Token ' + user.value.token;
    }
  }
  function applyLogin(userData: TUser): void {
    isAuthenticated.value = true;
    user.value = userData;
    storeToken();
  }



  async function logout(): Promise<void> {
    user.value = null;
    isAuthenticated.value = false;
  }

  return { user, isAuthenticated, login, logout, storeToken };
}, { persist: { enabled: true }});
