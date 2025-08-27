import { api } from 'boot/axios';


export async function fetchLeagueDetails (leagueId: number) {
  return await api.get(`league/league-details/${leagueId}`);
}
