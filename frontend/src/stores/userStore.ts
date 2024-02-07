import { defineStore } from 'pinia';
import { ref, Ref } from 'vue';
import { useAxios } from '@vueuse/integrations/useAxios';
import { api } from 'boot/axios';
import { useRouter } from 'vue-router';

type User = {
  id: string;
  email: string;
  username: string;
  bga?: string;
}
export const useUserStore = defineStore('userStore', () => {
  const router = useRouter();
  const user: Ref<User | null> = ref(null);
  const loggedIn: Ref<boolean> = ref(true);
   async function login(email: string, password: string):Promise<void> {
    const { data, error, isFinished  } = await useAxios('login/', { method: 'POST', data: {username: email, password } }, api);
    if(isFinished.value && !error.value) {
      loggedIn.value = true;
      user.value = data.value.user;
      router.push({ name: 'home' })
    }
  }
  return { user, loggedIn, login };
});
