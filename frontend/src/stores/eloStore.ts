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

      const matched = profiles.value.find((p) => {
        const pUser = p.username?.trim().toLowerCase();
        const pName = p.profile_name?.trim().toLowerCase();
        return (
          (u && (pUser === u || pName === u)) ||
          (n && (pUser === n || pName === n))
        );
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
      if (inFlight) return inFlight;

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
      updateStore.subscribe('/result/', () => {
        void fetchProfilesList(true);
      });
      updateStore.subscribe('/user/', () => {
        void fetchProfilesList(true);
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
    },
  }
);
