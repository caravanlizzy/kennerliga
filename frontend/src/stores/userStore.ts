import { defineStore } from 'pinia';
import { ref, Ref } from 'vue';
import { useAxios } from '@vueuse/integrations/useAxios';
import { api } from 'boot/axios';
import { useRouter } from 'vue-router';

type TUser = {
  email: string;
  username: string;
  bga?: string;
  token: string;
}
export const useUserStore = defineStore('userStore', () => {
  const router = useRouter();
  const user: Ref<TUser | null> = ref(null);
  const loggedIn: Ref<boolean> = ref(false);

  async function login(email: string, password: string): Promise<void> {
    const { data, error, isFinished } = await useAxios('login/', {
      method: 'POST',
      data: { username: email, password }
    }, api);
    if (isFinished.value && !error.value) {
      const userData = data.value.user;
      persistAuthentication(userData);
      applyLogin(userData);
      await router.push({ name: 'home' });
    }
  }

  function applyLogin(userData: TUser): void {
    loggedIn.value = true;
    user.value = userData;
  }

  function persistAuthentication(userData: TUser) {
    api.defaults.headers.common['Authorization'] = 'Token ' + userData.token;
    localStorage.setItem('user', JSON.stringify(userData));
  }

  async function logout(): Promise<void> {
    user.value = null;
    loggedIn.value = false;
  }

  return { user, loggedIn, login, logout, applyLogin };
});
