import { api } from 'boot/axios';
import { BanDecisionDtoPayload } from 'src/models/gameModels';

export async function banGame(banDecision: BanDecisionDtoPayload) {
  const data: Record<string, any> = {
    username: banDecision.username,
    league: banDecision.leagueId,
  };
  if (banDecision.gameId) {
    data.game = banDecision.gameId;
  }

  try {
    return await api('/game/ban-decisions/', {
      method: 'POST',
      data,
    });
  } catch (error) {
    throw new Error('Error creating ban decision: ' + error);
  }
}
