import { api } from 'boot/axios';
import { TGameLeaderboard, TGameStatSummary, TStatisticsOverview } from 'src/types';

export type TStatisticsFilters = {
  years?: number[];
  playerCounts?: string[];
  minGames?: number;
  window?: number;
  topN?: number;
};

function toQueryParams(filters?: TStatisticsFilters): Record<string, string | number> {
  const params: Record<string, string | number> = {};
  if (filters?.years && filters.years.length > 0) {
    params.years = filters.years.join(',');
  }
  if (filters?.playerCounts && filters.playerCounts.length > 0) {
    params.player_count = filters.playerCounts.join(',');
  }
  if (filters?.minGames !== undefined) {
    params.min_games = filters.minGames;
  }
  if (filters?.window !== undefined) {
    params.window = filters.window;
  }
  if (filters?.topN !== undefined) {
    params.top_n = filters.topN;
  }
  return params;
}

export async function fetchStatisticsOverview(
  filters?: TStatisticsFilters
): Promise<TStatisticsOverview | null> {
  try {
    const { data } = await api.get<TStatisticsOverview>('statistics/overview/', {
      params: toQueryParams(filters),
    });
    return data;
  } catch (e) {
    console.log(e);
    return null;
  }
}

export async function fetchGameStatsList(
  years?: number[],
  playerCounts?: string[]
): Promise<TGameStatSummary[]> {
  try {
    const params: Record<string, string> = {};
    if (years && years.length > 0) {
      params.years = years.join(',');
    }
    if (playerCounts && playerCounts.length > 0) {
      params.player_count = playerCounts.join(',');
    }
    const { data } = await api.get<TGameStatSummary[]>('statistics/games/', { params });
    return data;
  } catch (e) {
    console.log(e);
    return [];
  }
}

export async function fetchGameLeaderboard(
  gameId: number,
  years?: number[],
  playerCounts?: string[],
  minGames?: number
): Promise<TGameLeaderboard | null> {
  try {
    const params: Record<string, string | number> = {};
    if (years && years.length > 0) {
      params.years = years.join(',');
    }
    if (playerCounts && playerCounts.length > 0) {
      params.player_count = playerCounts.join(',');
    }
    if (minGames !== undefined) {
      params.min_games = minGames;
    }
    const { data } = await api.get<TGameLeaderboard>(
      `statistics/games/${gameId}/leaderboard/`,
      { params }
    );
    return data;
  } catch (e) {
    console.log(e);
    return null;
  }
}
