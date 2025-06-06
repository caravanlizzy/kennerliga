import { api } from 'boot/axios';

interface LeagueDetails {
  id: number;
  status: 'PICKING' | 'BANNING' | 'PLAYING' | 'DONE';
  members: Array<{
    username: string;
    is_active_player: boolean;
  }>;
}


export async function getMyLeagueId(): Promise<number> {
  try {
    const response = await api.get<LeagueDetails>('user/me/current-league');
    return response.data.id;
  } catch (e) {
    console.error(e); // Using console.error for errors is more appropriate
    throw e; // Re-throw the error to handle it in the calling code
  }
}
