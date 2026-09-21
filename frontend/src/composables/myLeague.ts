import { useLeagueStore } from 'stores/leagueStore';
import { useUserStore } from 'stores/userStore';

/**
 * Returns the pinia store instance for the current user's league.
 * Centralizes the slightly awkward `useLeagueStore(id)()` invocation so
 * that components in the MyLeague page tree can share the same store.
 */
export function useMyLeagueStore() {
  const userStore = useUserStore();
  // Falls back to id 0 when the user isn't in a league. `useLeagueStore`
  // registers one Pinia store definition per id, so this deliberately reuses
  // a single `league-0` placeholder rather than minting new ones; callers
  // should check `leagueId` before triggering a fetch.
  const leagueId = userStore.user?.myCurrentLeagueId ?? 0;
  return useLeagueStore(leagueId)();
}
