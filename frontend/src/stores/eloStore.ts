import { defineStore } from 'pinia';
import { ref } from 'vue';
import { fetchProfiles } from 'src/services/userService';
import type { TPlayerProfileDto } from 'src/types/user';
import { useUpdateStore } from 'src/stores/updateStore';

export interface PlayerEloInfo {
  eloRating: number | null;
  eloRank: number | null;
}

export const useEloStore = defineStore(
  'elo',
  () => {
    const profiles = ref<TPlayerProfileDto[]>([]);
    const loading = ref(false);
    const initialized = ref(false);
    let inFlight: Promise<TPlayerProfileDto[]> | null = null;
    let subscribed = false;

    function getElo(
      username?: string | null,
      navigationName?: string | null
    ): PlayerEloInfo | null {
      const u = username?.trim().toLowerCase();
      const n = navigationName?.trim().toLowerCase();
      if (!u && !n) return null;

      const matched =
        profiles.value.find((p) => p.username?.trim().toLowerCase() === n && n) ||
        profiles.value.find((p) => p.username?.trim().toLowerCase() === u && u) ||
        profiles.value.find((p) => {
          const name = p.profile_name?.trim().toLowerCase();
          return (u && name === u) || (n && name === n);
        });

      if (!matched) return null;

      return {
        eloRating: matched.elo_rating ?? null,
        eloRank: matched.elo_rank ?? null,
      };
    }

    async function fetchProfilesList(
      force = false
    ): Promise<TPlayerProfileDto[]> {
      if (!force && initialized.value && profiles.value.length > 0) {
        return profiles.value;
      }
      if (inFlight) {
        if (!force) return inFlight;
        await inFlight;
        return fetchProfilesList(true);
      }

      loading.value = true;
      inFlight = (async () => {
        try {
          const data = await fetchProfiles();
          profiles.value = data || [];
          initialized.value = true;
          return profiles.value;
        } catch (error) {
          console.error('Failed to load player profiles for elo:', error);
          return profiles.value;
        } finally {
          loading.value = false;
          inFlight = null;
        }
      })();

      return inFlight;
    }

    function initUpdateSubscription() {
      if (subscribed) return;
      subscribed = true;
      const updateStore = useUpdateStore();
      updateStore.subscribe('/result/', async () => {
        await fetchProfilesList(true);
      });
      updateStore.subscribe('/user/', async () => {
        await fetchProfilesList(true);
      });
    }

    return {
      profiles,
      loading,
      initialized,
      getElo,
      fetchProfiles: fetchProfilesList,
      initUpdateSubscription,
    };
  },
  {
    persist: {
      paths: ['profiles', 'initialized'],
      afterRestore: (ctx) => {
        ctx.store.initialized = false;
      },
    },
  }
);
