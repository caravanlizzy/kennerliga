import { api } from 'boot/axios';

export async function fetchLeagueDetails(leagueId: number) {
  try {
    const { data } = await api.get(`league/league-details/${leagueId}`);
    return data;
  } catch (error) {
    console.error('Error fetching league details:', error);
  }
}


export async function getMyLeagueId(): Promise<number | null> {
  try {
    const response = await api.get('user/me/current-league');
    return response.data.id;
  } catch (error: string) {
    // Check if the error is a 404 (Not Found) which indicates no active league
    if (error.response?.status === 404) {
      return null;
    }
    // For other errors, log them and re-throw
    console.error('Error fetching league ID:', error);
    throw error;
  }
}
