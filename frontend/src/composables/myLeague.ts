import { useLeagueStore } from 'stores/leagueStore';
import { useUserStore } from 'stores/userStore';

/**
 * Returns the pinia store instance for the current user's league.
 * Centralizes the slightly awkward `useLeagueStore(id)()` invocation so
 * that components in the MyLeague page tree can share the same store.
 */
export function useMyLeagueStore() {
  const userStore = useUserStore();
  const leagueId = userStore.user?.myCurrentLeagueId ?? 0;
  return useLeagueStore(leagueId)();
}
