import { api } from 'boot/axios';

export async function fetchLeagueDetails(leagueId: number) {
  try {
    const { data } = await api.get(`league/league-details/${leagueId}`);
    return data;
  } catch (error) {
    console.error('Error fetching league details:', error);
  }
}
