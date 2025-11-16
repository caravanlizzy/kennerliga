import {
  BanDecisionDtoPayload,
  GameOptionChoiceDto,
  GameOptionDto,
  SelectedGameDtoPayload,
  TPlatform
} from 'src/models/gameModels';
import { api } from 'boot/axios';
import { TGameOption, TGameOptionChoice, TResultConfig } from 'src/types';

import { useIDStorage } from 'src/composables/IDStorage';

const { addStorageItem, getStorageItem } = useIDStorage();

export async function banGame(banDecision: BanDecisionDtoPayload) {
  const data: Record<string, string|number|boolean> = {
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

export async function createGame(name: string, platform: TPlatform): Promise<number> {
  try {
    const { data } = await api('game/games/', {
      method: 'POST',
      data: { name: name, platform: platform.id }
    });
    return data.id;
  } catch (e) {
    console.log('Error while creating a new game', e);
    throw new Error('Could not create new game because of following error: ' + e);
  }
}

export async function addRestrictions(option: TGameOption): Promise<void> {
  if (option.onlyIfOption === undefined) {
    console.log('No restriction option given', { option });
    return;
  }

  const { onlyIfOption, onlyIfChoice, onlyIfValue } = option;
  const optionId = getStorageItem(onlyIfOption);

  if (optionId === undefined) {
    console.error(`Invalid option: ${onlyIfOption}. It does not exist in optionIDStorage.`);
    return;
  }

  const data: { only_if_option: number; only_if_choice?: number; only_if_value?: boolean } = {
    only_if_option: optionId
  };

  if (onlyIfValue !== undefined) {
    data.only_if_value = onlyIfValue;
  } else if (onlyIfChoice !== undefined) {
    const choiceValue = getStorageItem(onlyIfChoice);
    if (choiceValue !== undefined) {
      data.only_if_choice = choiceValue;
    } else {
      console.error(`Invalid choice: ${onlyIfChoice}. It does not exist in optionIDStorage.`);
      return;
    }
  } else {
    console.error('Both onlyIfValue and onlyIfChoice are undefined. To set a restriction, at least one must be provided.');
    return;
  }

  await api(`game/options/${optionId}/`, {
    method: 'PATCH',
    data
  });
}

async function createOption(option: TGameOption, gameId: number): Promise<GameOptionDto> {
  try {
    const { data: newOption } = await api('game/options/', {
      method: 'POST',
      data: {
        name: option.title,
        has_choices: option.hasChoices,
        game: gameId
      }
    });
    addStorageItem(option.id, newOption.id);
    return newOption;
  } catch (e) {
    // errorMessages.value.push('CreateGameOption');
    console.log('Error creating game options', e);
    throw new Error('Error creating game options: \n' + e);
  }
}

async function createOptionChoice(choice: TGameOptionChoice, optionId: number): Promise<GameOptionChoiceDto> {
  try {
    const { data: newChoice } = await api('game/option-choices/', {
      method: 'POST',
      data: {
        name: choice.name,
        option: optionId
      }
    });
    addStorageItem(choice.id, newChoice.id);
    return newChoice;
  } catch (e) {
    console.log('Error creating game option choice', e);
    throw new Error('Error creating game option choice: \n' + e);
  }
}

async function createOptionChoices(option: TGameOption): Promise<void> {
  if (!option.hasChoices) return;
  for (const choice of option.choices) {
    const optionId = getStorageItem(option.id);
    await createOptionChoice(choice, optionId);
  }
}

export async function createOptions(gameId: number, gameOptions: TGameOption[]): Promise<void> {
  for (const option of gameOptions) {
    await createOption(option, gameId);
  }
  for (const option of gameOptions) {
    await createOptionChoices(option);
    await addRestrictions(option);
  }
}

export async function createResultConfigData(gameId: number, resultConfig: TResultConfig): Promise<void> {
  try {
    const { data: resultConfigData } = await api('game/result-configs/', {
      method: 'POST',
      data: {
        game: gameId,
        is_asymmetric: resultConfig?.isAsymmetric,
        has_starting_player_order: resultConfig?.hasStartingPlayerOrder,
        has_points: resultConfig?.hasPoints,
        starting_points_system: resultConfig?.startingPointSystem
      }
    });
    await createFactions(gameId, resultConfig);
    await createTieBreakers(resultConfigData.id, resultConfig);
  } catch (e) {
    // errorMessages.value.push('CreateResultConfig');
    console.log('Error creating the result configuration', e);
    throw new Error('Error creating the result configuration: \n' + e);
  }
}

export async function createFactions(gameId: number, resultConfig: TResultConfig): Promise<void> {
  if (resultConfig === undefined) return;
  if (resultConfig.factions === undefined) return;
  for (const faction of resultConfig.factions) {
    try {
      await api('game/factions/', {
        method: 'POST',
        data: {
          game: gameId,
          name: faction.name
        }
      });
    } catch (e) {
      console.log('Error creating faction', e);
    }
  }
}

export async function createTieBreakers(resultConfigId: number, resultConfig: TResultConfig): Promise<void> {
  if (resultConfig === undefined) return;
  if (resultConfig.tieBreakers === undefined) return;
  if (!resultConfig.hasTieBreaker) return;
  for (const [index, tieBreaker] of resultConfig.tieBreakers.entries()) {
    try {
      api('game/tie-breakers/', {
        method: 'POST',
        data: {
          result_config: resultConfigId,
          name: tieBreaker.name,
          order: index * 10
        }
      });
    } catch (e) {
      console.log('Error creating tieBreaker', e);
    }
  }
}
export async function createSelectedGame(
  selectedGame: SelectedGameDtoPayload,
  manageOnly = false
) {
  const data: Record<string, any> = {
    game: selectedGame.game,
    selected_options: selectedGame.selected_options,
    league_id: selectedGame.league,
    profile_id: selectedGame.profile,
    manage_only: manageOnly
  };

  try {
    return await api('/game/selected-games/', {
      method: 'POST',
      data,
    });
  } catch (error) {
    throw new Error('Error creating selectedGame: ' + error);
  }
}

export async function editSelectedGame(selectedGame: {
  id: number;
  game: number;
  selected_options: {
    selected_game: number;
    game_option_id: number;
    choice_id?: number;
    value?: boolean | null;
  }[];
  profile: number;
  league: number;
}) {
  const data: Record<string, any> = {
    // id is not needed in the payload, it is used in the URL
    game: selectedGame.game,
    selected_options: selectedGame.selected_options,
    league_id: selectedGame.league,
    profile_id: selectedGame.profile,
  };

  try {
    return await api(`/game/selected-games/${selectedGame.id}/`, {
      method: 'PATCH',
      data,
    });
  } catch (error) {
    throw new Error('Error editing selectedGame: ' + error);
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
