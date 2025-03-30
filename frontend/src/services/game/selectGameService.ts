import { api } from 'boot/axios';
import {  SelectedGameDtoPayload } from 'src/models/gameModels';

export async function createSelectedGame(
  selectedGame: SelectedGameDtoPayload,
  leagueId: number | null = null
) {
  const data: Record<string, any> = {
    game: selectedGame.game,
    selected_options: selectedGame.selected_options
  };

  if (leagueId !== null) {
    data.leagueId = leagueId;
  }

  try {
    await api('/game/selected-games/', {
      method: 'POST',
      data
    });
  } catch (error) {
    throw new Error('Error creating selectedGame: ' + error);
  }
}


export async function fetchGameOptions(gameId: number) {
  try {
    return await api(`/game/options/?game=${gameId}`);
  } catch (error) {
    throw new Error(
      `Error retrieving game options for game with id: ${gameId} \n ${error}`
    );
  }
}

export async function fetchGameOptionChoices(optionId: number) {
  try {
    return await api(`/game/option-choices/?option=${optionId}`);
  } catch (error) {
    throw new Error(
      `Error retrieving game option choices for game with id: ${optionId} \n ${error}`
    );
  }
}
