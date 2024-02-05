import { defineStore } from 'pinia';
import { ref, Ref } from 'vue';
import { useAxios } from '@vueuse/integrations/useAxios';
import { api } from 'boot/axios';

type User = {
  email: string;
  bga: string;
}
export const useUserStore = defineStore('userStore', () => {
  const user: Ref<User | null> = ref(null);
  const loggedIn: Ref<boolean> = ref(false);
   async function login(email: string, password: string):Promise<void> {
    const response = await useAxios('login/', { method: 'POST', data: { email, password } }, api);
    console.log({ response });
  };
  return { user, loggedIn, login };
});
