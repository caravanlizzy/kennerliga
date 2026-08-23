import { defineStore } from 'pinia';
import { ref } from 'vue';
import { api } from 'boot/axios';
import {
  TAppConfigurationDto,
  AppConfigurationCreate,
  TGameDto,
} from 'src/types';

const BASE_URL = 'configuration/app-configurations/';

export const useConfigurationStore = defineStore('configuration', () => {
  const current = ref<TAppConfigurationDto | null>(null);
  const history = ref<TAppConfigurationDto[]>([]);
  const games = ref<TGameDto[]>([]);
  const loading = ref(false);

  async function fetchCurrent(): Promise<TAppConfigurationDto | null> {
    const { data } = await api.get<TAppConfigurationDto | null>(`${BASE_URL}current/`);
    current.value = data;
    return data;
  }

  async function fetchHistory(): Promise<TAppConfigurationDto[]> {
    const { data } = await api.get<TAppConfigurationDto[]>(BASE_URL);
    history.value = data;
    return data;
  }

  // manage_only=true so admins can pick any game (incl. non-selectable ones
  // such as the tie-decider) as the tie-decider game.
  async function fetchGames(): Promise<TGameDto[]> {
    const { data } = await api.get<TGameDto[]>('game/games/?manage_only=true');
    games.value = data;
    return data;
  }

  // Saving always creates a new immutable configuration version on the
  // backend, keeping the full change history.
  async function saveConfiguration(
    payload: AppConfigurationCreate,
  ): Promise<TAppConfigurationDto> {
    loading.value = true;
    try {
      const { data } = await api.post<TAppConfigurationDto>(BASE_URL, payload);
      current.value = data;
      history.value.unshift(data);
      return data;
    } finally {
      loading.value = false;
    }
  }

  async function init(): Promise<void> {
    loading.value = true;
    try {
      await Promise.all([fetchCurrent(), fetchHistory(), fetchGames()]);
    } finally {
      loading.value = false;
    }
  }

  return {
    // state
    current,
    history,
    games,
    loading,

    // actions
    fetchCurrent,
    fetchHistory,
    fetchGames,
    saveConfiguration,
    init,
  };
});
