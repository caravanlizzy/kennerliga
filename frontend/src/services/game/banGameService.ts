import { api } from 'boot/axios';
import { BanDecisionDtoPayload } from 'src/models/gameModels';

export async function banGame(banDecision: BanDecisionDtoPayload) {
  const data: Record<string, any> = {
    username: banDecision.username,
    league: banDecision.leagueId,
  };
  if (banDecision.decline) {
    data.declined_ban = banDecision.decline;
  }
  if (banDecision.selectedGameId) {
    data.selected_game_id = banDecision.selectedGameId;
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
