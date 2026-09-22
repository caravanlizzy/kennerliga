import { defineStore } from 'pinia';
import { ref, Ref } from 'vue';
import { api, setAuthToken, setUnauthorizedHandler } from 'boot/axios';
import { clearCachedResources } from 'src/composables/cachedResource';
import { fetchMyCurrentLeagueInfo } from 'src/services/leagueService';
import {
  fetchAvailableYears,
  fetchUsers,
  updateAvatarColor,
  updateAvatarShape,
  type UserListParams,
} from 'src/services/userService';
import { AvatarShape, TUserDto } from 'src/types';
import { useUpdateStore } from 'stores/updateStore';

export const useUserStore = defineStore(
  'userStore',
  () => {
    const user: Ref<TUserDto | null> = ref(null);
    const isAdmin: Ref<boolean> = ref(false);
    const isAuthenticated: Ref<boolean> = ref(false);

    async function listUsers(params?: UserListParams): Promise<TUserDto[]> {
      try {
        return await fetchUsers(params);
      } catch (e) {
        console.error('Failed to list users:', e);
        return [];
      }
    }

    async function getAvailableYears(): Promise<number[]> {
      try {
        return await fetchAvailableYears();
      } catch (e) {
        console.error('Failed to load available years:', e);
        return [];
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
        // Anything cached for the previous identity must not leak into this
        // session (dev impersonation switches users without a reload).
        clearCachedResources();
        applyLogin(data.user, ignorePermission);
        await setMyCurrentLeagueId();
        return true;
      } catch (error) {
        console.error('Login failed:', error);
        return false;
      }
    }

    async function setMyCurrentLeagueId() {
      if (!user.value) return;
      const info = await fetchMyCurrentLeagueInfo();
      if (info) {
        user.value.myCurrentLeagueId = info.id;
        user.value.isMyTurn = info.is_my_turn;
      } else {
        user.value.myCurrentLeagueId = null;
        user.value.isMyTurn = false;
      }
    }

    function isMe(someUsername: string): boolean {
      return someUsername === user.value?.username;
    }

    function storeToken(): void {
      if (user.value) {
        setAuthToken(user.value.token);
      }
    }

    function applyLogin(userData: TUserDto, ignorePermission: boolean): void {
      isAuthenticated.value = true;
      user.value = userData;
      // `ignorePermission` is a dev-tools escape hatch: it shows the admin UI
      // for an impersonated account. The API still enforces the real one.
      isAdmin.value = ignorePermission ? true : Boolean(userData.admin);
      storeToken();
    }

    /** Drops all local session state. Does not call the API. */
    function clearSession(): void {
      user.value = null;
      isAuthenticated.value = false;
      isAdmin.value = false;
      setAuthToken(null);
      clearCachedResources();
    }

    async function logout(): Promise<void> {
      try {
        await api('logout/', {
          method: 'POST',
        });
      } catch (err) {
        console.error('An error occurred during logout:', err);
      } finally {
        clearSession();
      }
    }

    async function changeAvatarShape(shape: AvatarShape): Promise<boolean> {
      try {
        const updated = await updateAvatarShape(shape);
        if (user.value) {
          user.value.avatar_shape = updated.avatar_shape || shape;
        }
        clearCachedResources();
        const updateStore = useUpdateStore();
        updateStore.notify('/user/');
        updateStore.notify('/season/');
        updateStore.notify('/league/');
        return true;
      } catch (err) {
        console.error('Failed to update avatar shape:', err);
        return false;
      }
    }

    async function changeAvatarColor(color: string): Promise<boolean> {
      try {
        const updated = await updateAvatarColor(color);
        if (user.value) {
          user.value.avatar_color = updated.avatar_color ?? color;
        }
        clearCachedResources();
        const updateStore = useUpdateStore();
        updateStore.notify('/user/');
        updateStore.notify('/season/');
        updateStore.notify('/league/');
        return true;
      } catch (err) {
        console.error('Failed to update avatar color:', err);
        return false;
      }
    }

    // When the API rejects our token, drop the session instead of leaving the
    // app in a signed-in shell whose every request 401s.
    setUnauthorizedHandler(() => {
      if (isAuthenticated.value) clearSession();
    });

    return {
      user,
      listUsers,
      getAvailableYears,
      isAuthenticated,
      isAdmin,
      isMe,
      login,
      logout,
      clearSession,
      setMyCurrentLeagueId,
      changeAvatarShape,
      changeAvatarColor,
    };
  },
  {
    // Replaces the hand-rolled `watch` + localStorage pair. Same storage key
    // and same field names, so sessions saved by the old code still restore
    // (and `helpers.loadToken` keeps reading them).
    persist: {
      paths: ['user', 'isAuthenticated', 'isAdmin'],
      afterRestore: (ctx) => {
        const store = ctx.store as unknown as {
          user: TUserDto | null;
          isAdmin: boolean;
        };
        // Sessions written before `isAdmin` was persisted only carry
        // `user.admin`; derive it so those users aren't demoted on reload.
        if (store.user && !store.isAdmin) {
          store.isAdmin = Boolean(store.user.admin);
        }
        if (store.user?.token) setAuthToken(store.user.token);
      },
    },
  }
);
