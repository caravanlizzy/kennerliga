import { api } from 'boot/axios';
import { TFullStandings, TSeasonFullStandings } from 'src/types';

/**
 * Full standings matrix for a single league.
 * Throws on failure so callers can render a distinct error state.
 */
export async function fetchLeagueFullStandings(
  leagueId: number
): Promise<TFullStandings> {
  const { data } = await api.get<TFullStandings>(
    `league/leagues/${leagueId}/full-standings/`
  );
  return data;
}

/**
 * Full standings for every league of a season in one round-trip
 * (backed by `SeasonViewSet.full_standings`). Prefer this over calling
 * `fetchLeagueFullStandings` per league.
 */
export async function fetchSeasonFullStandings(
  seasonId: number
): Promise<TSeasonFullStandings> {
  const { data } = await api.get<TSeasonFullStandings>(
    `season/seasons/${seasonId}/full-standings/`
  );
  return data;
}
