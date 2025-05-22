import { api } from 'boot/axios';
import { BanDecisionDtoPayload } from 'src/models/gameModels';

export async function banGame(banDecision: BanDecisionDtoPayload) {
  console.log(banDecision);
  const data: Record<string, any> = {
    username: banDecision.username,
    game: banDecision.gameId,
    league: banDecision.leagueId,
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
