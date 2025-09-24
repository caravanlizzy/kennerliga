import { defineStore } from 'pinia';
import { ref, Ref } from 'vue';
import { api } from 'boot/axios';
import { useRouter } from 'vue-router';

export type TUser = {
  username: string;
  token: string;
  admin: boolean;
  platform_players: { name: string }[];
};

export const useUserStore = defineStore(
  'userStore',
  () => {
    const router = useRouter();
    const user: Ref<TUser | null> = ref(null);
    const isAdmin: Ref<boolean> = ref(false);
    const isAuthenticated: Ref<boolean> = ref(false);

    async function listUsers() {
      try {
        const { data: users } = await api.get('/user/users/');
        return users;
      } catch (e) {
        console.log(e);
      }
    }

    async function login(username: string, password: string): Promise<void> {
      try {
        const { data } = await api('login/', {
          method: 'POST',
          data: { username: username, password },
        });
        const userData = data.user;
        applyLogin(userData);
        await router.push({ name: 'home' });
      } catch (error) {
        console.log(error);
      }
    }

    function isMe(someUsername: string): boolean {
      return someUsername === user.value?.username;
    }

    function storeToken(): void {
      if (user.value) {
        api.defaults.headers.common['Authorization'] =
          'Token ' + user.value.token;
        api.defaults.headers['Authorization'] = 'Token ' + user.value.token;
      }
    }

    function applyLogin(userData: TUser): void {
      isAuthenticated.value = true;
      user.value = userData;
      isAdmin.value = userData.admin;
      storeToken();
    }

    async function logout(): Promise<void> {
      try {
        await api('logout/', {
          method: 'POST',
        });
      } catch (err) {
        console.error('An error occurred during logout:', err);
      } finally {
        // Clear the local user data
        user.value = null;
        isAuthenticated.value = false;

        // Remove token from Axios headers
        delete api.defaults.headers.common['Authorization'];
        delete api.defaults.headers['Authorization'];

        // Optional: Redirect to login or home
        await router.push({ name: 'login' });
      }
    }

    return { user, isAuthenticated, isAdmin, isMe, login, logout };
  },
  {
    persist: {
      enabled: true,
      strategies: [
        {
          key: 'userStore',
          storage: localStorage,
          paths: ['user', 'isAuthenticated'],
        },
      ],
    },
  }
);
