import { BanDecisionDtoPayload } from 'src/models/gameModels';
import { api } from 'boot/axios';

export async function banGame(
  playerId: number,
  gameId: number,
  leagueId: number,
) {
  const data: Record<string, any> = {
    player: playerId,
    game: gameId,
    league: leagueId,
  };

  try {
    return await api('/game/ban-decisions/', {
      method: 'POST',
      data,
    });
  } catch (error) {
    throw new Error('Error creating ban decision: ' + error);
  }
}
