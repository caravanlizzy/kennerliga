import { defineStore } from 'pinia';
import { ref, Ref, watch } from 'vue';
import { api } from 'boot/axios';
import { fetchMyCurrentLeagueInfo } from 'src/services/leagueService';
import { TUserDto } from 'src/types';

export const useUserStore = defineStore(
  'userStore',
  () => {
    const user: Ref<TUserDto | null> = ref(null);
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

    async function login(
      username: string,
      password: string,
      { ignorePermission = false } = {}
    ): Promise<boolean> {
      try {
        const { data } = await api('login/', {
          method: 'POST',
          data: { username, password },
        });
        const userData = data.user;
        applyLogin(userData, ignorePermission);
        await setMyCurrentLeagueId();
        return true;
      } catch (error) {
        console.log(error);
        return false;
      }
    }

    async function setMyCurrentLeagueId() {
      if( !user.value ) return;
      const info = await fetchMyCurrentLeagueInfo();
      if (info) {
        user.value.myCurrentLeagueId = info.id;
        user.value.isMyTurn = info.is_my_turn;
      } else {
        user.value.myCurrentLeagueId = null;
        user.value.isMyTurn = false;
      }
    }

    function loadDataFromLocalStorage(): void {
      const data = localStorage.getItem('userStore');
      if (data) {
        try {
          const parsedData = JSON.parse(data);
          user.value = parsedData.user;
          isAuthenticated.value = parsedData.isAuthenticated;
          isAdmin.value = parsedData.user?.admin ?? false;
          storeToken();
        } catch (e) {
          console.error('Failed to parse userStore from localStorage', e);
        }
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

    function applyLogin(userData: TUserDto, ignorePermission: boolean): void {
      isAuthenticated.value = true;
      user.value = userData;
      isAdmin.value = true;
      if( !ignorePermission ){
        isAdmin.value = userData.admin;
      }
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
      }
    }

    watch(
      () => [user.value, isAuthenticated.value],
      () => {
        localStorage.setItem(
          'userStore',
          JSON.stringify({
            user: user.value,
            isAuthenticated: isAuthenticated.value,
          })
        );
      },
      { deep: true }
    );

    loadDataFromLocalStorage();

    return { user, listUsers, isAuthenticated, isAdmin, isMe, login, logout, loadDataFromLocalStorage, setMyCurrentLeagueId };
  }
);
