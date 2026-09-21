import { api } from 'boot/axios';
import { TLeagueDto, TLeagueStatus } from 'src/types';
import { unwrapList } from 'src/services/httpTypes';

export async function fetchLeagueDetails(
  leagueId: number
): Promise<TLeagueDto> {
  try {
    const { data } = await api.get(`league/league-details/${leagueId}`);
    return data;
  } catch (error) {
    console.error('Error fetching league details:', error);
    throw new Error('Failed to fetch league details');
  }
}

export async function fetchMyCurrentLeagueInfo(): Promise<{ id: number; is_my_turn: boolean } | null> {
  try {
    const response = await api.get('user/me/current-league');
    return {
      id: response.data.id,
      is_my_turn: response.data.is_my_turn
    };
  } catch (error: unknown) {
    const err = error as { response?: { status?: number } };
    // Check if the error is a 404 (Not Found) which indicates no active league
    if (err.response?.status === 404) {
      return null;
    }
    // For other errors, log them and re-throw
    console.error('Error fetching league ID:', error);
    throw error;
  }
}

/**
 * All leagues of a season. Throws on failure so callers can distinguish a
 * season without leagues from a failed request.
 */
export async function fetchLeaguesForSeason(
  seasonId: number
): Promise<TLeagueDto[]> {
  const { data } = await api.get('league/leagues', {
    params: { season: seasonId },
  });
  return unwrapList<TLeagueDto>(data);
}

export type TTieResolutionReason = { value: string; label: string };

/**
 * The reasons an admin may pick when resolving a tie. The label for the
 * "decider game" reason is the game configured in the App Configuration,
 * so this must be fetched rather than hard-coded in the UI.
 */
export async function fetchTieResolutionReasons(
  leagueId: number
): Promise<TTieResolutionReason[]> {
  const { data } = await api.get(
    `league/leagues/${leagueId}/tie-resolution-reasons/`
  );
  return unwrapList<TTieResolutionReason>(data);
}

/** Records an admin's tie resolution; `playerOrder` is best-placed first. */
export async function resolveTie(
  leagueId: number,
  payload: {
    group_key: string;
    reason: string;
    player_order: number[];
    note?: string;
  }
): Promise<void> {
  await api.post(`league/leagues/${leagueId}/resolve-tie/`, payload);
}

/** Admin-only: force a league into a given `LeagueStatus`. */
export async function setLeagueStatus(
  leagueId: number,
  status: string
): Promise<{ id: number; status: TLeagueStatus }> {
  const { data } = await api.post(`league/leagues/${leagueId}/set-status/`, {
    status,
  });
  return data;
}

/** Admin-only: make the given profile the league's active player. */
export async function setLeagueActivePlayer(
  leagueId: number,
  profileId: number
): Promise<{ participant_id: number }> {
  const { data } = await api.post(
    `league/leagues/${leagueId}/set-active-player/`,
    { profile_id: profileId }
  );
  return data;
}
