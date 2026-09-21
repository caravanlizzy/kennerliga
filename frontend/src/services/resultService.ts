import { AxiosResponse } from 'axios';
import { api } from 'boot/axios';
import {
  TMatchResult,
  TMatchResultSubmitPayload,
  TSelectedGameDto,
  TWinConditionDto,
} from 'src/types';
import { fetchWinConditionsForResultConfig } from 'src/services/gameService';
import { unwrapList } from 'src/services/httpTypes';

/**
 * Result-reporting endpoints (backend app: `result`, plus the game config it
 * needs). All of these throw on failure: reporting a match result is a write
 * flow where the caller has to surface the error, not silently show "no data".
 */

export async function fetchSelectedGame(
  selectedGameId: number
): Promise<TSelectedGameDto> {
  const { data } = await api.get<TSelectedGameDto>(
    `game/selected-games/${selectedGameId}/`
  );
  return data;
}

/**
 * Win conditions of a result config in the order the form should offer them.
 * Wraps `gameService.fetchWinConditionsForResultConfig` with the ordering the
 * result form depends on (the first entry becomes the default selection).
 */
export async function fetchOrderedWinConditions(
  resultConfigId: number
): Promise<TWinConditionDto[]> {
  const conditions = await fetchWinConditionsForResultConfig(resultConfigId);
  return conditions.slice().sort((a, b) => a.order - b.order);
}

export async function fetchMatchResults(params: {
  seasonId: number;
  leagueId: number;
  selectedGameId: number;
}): Promise<TMatchResult[]> {
  const { data } = await api.get('result/match-results/', {
    params: {
      season: params.seasonId,
      league: params.leagueId,
      selected_game: params.selectedGameId,
    },
  });
  return unwrapList<TMatchResult>(data);
}

/**
 * Submits a full match result set.
 *
 * The endpoint answers 201 on success and **202 when a tie-breaker is still
 * required**, so the raw response is returned rather than just its body —
 * callers have to branch on the status.
 */
export function submitMatchResults(
  payload: TMatchResultSubmitPayload
): Promise<AxiosResponse> {
  return api.post('/result/match-results/', payload);
}

/** Deletes every result of a selected game (admin only). */
export function deleteMatchResults(selectedGameId: number): Promise<AxiosResponse> {
  return api.delete(`result/match-results/${selectedGameId}/`);
}
