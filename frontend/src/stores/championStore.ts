import { defineStore } from 'pinia';
import { computed, ref } from 'vue';
import {
  fetchCurrentChampion,
  type TCurrentChampionResponse,
} from 'src/services/seasonService';

export const useChampionStore = defineStore(
  'champion',
  () => {
    const champion = ref<TCurrentChampionResponse | null>(null);
    const loading = ref(false);
    const initialized = ref(false);
    let inFlight: Promise<TCurrentChampionResponse | null> | null = null;

    const championUsername = computed(
      () => champion.value?.username?.trim() ?? null
    );

    function isChampion(
      username?: string | null,
      navigationName?: string | null
    ): boolean {
      const current = championUsername.value;
      if (!current) return false;
      const target = current.toLowerCase();
      if (username && username.trim().toLowerCase() === target) return true;
      if (navigationName && navigationName.trim().toLowerCase() === target)
        return true;
      return false;
    }

    async function fetchChampion(
      force = false
    ): Promise<TCurrentChampionResponse | null> {
      if (!force && initialized.value && champion.value !== null) {
        return champion.value;
      }
      if (inFlight) return inFlight;

      loading.value = true;
      inFlight = (async () => {
        try {
          const data = await fetchCurrentChampion();
          champion.value = data || null;
          initialized.value = true;
          return champion.value;
        } catch (error) {
          console.error('Failed to load current champion:', error);
          return null;
        } finally {
          loading.value = false;
          inFlight = null;
        }
      })();

      return inFlight;
    }

    return {
      champion,
      loading,
      initialized,
      championUsername,
      isChampion,
      fetchChampion,
    };
  },
  {
    persist: {
      paths: ['champion', 'initialized'],
    },
  }
);
