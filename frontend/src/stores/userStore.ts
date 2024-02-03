import { defineStore } from 'pinia';
import { ref, Ref } from 'vue';

type User = {
  email: string;
  bga: string;
}
export const useUser = defineStore('userStore', () => {
  const user:Ref<User|null> = ref(null);
  const loggedIn: Ref<boolean> = ref(false);
})
