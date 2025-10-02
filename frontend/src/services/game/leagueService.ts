import { api } from 'boot/axios';

interface LeagueDetails {
  id: number;
  status: 'PICKING' | 'BANNING' | 'PLAYING' | 'DONE';
  members: Array<{
    username: string;
    is_active_player: boolean;
  }>;
}

export async function getMyLeagueId(): Promise<number | null> {
  try {
    const response = await api.get<LeagueDetails>('user/me/current-league');
    return response.data.id;
  } catch (error: any) {
    // Check if the error is a 404 (Not Found) which indicates no active league
    if (error.response?.status === 404) {
      return null;
    }
    // For other errors, log them and re-throw
    console.error('Error fetching league ID:', error);
    throw error;
  }
}
