import {
  TBanDecisionDtoPayload,
  TFullGameDto,
  TGameOptionChoiceDto,
  TGameOptionDto,
  TSelectedGameDtoPayload,
  TPlatform,
} from 'src/types';
import { api } from 'boot/axios';
import {
  TGameOption,
  TGameOptionChoice,
  TResultConfig,
} from 'src/types';

import { useIDStorage } from 'src/composables/IDStorage';

const { addStorageItem, getStorageItem } = useIDStorage();

export async function banGame(banDecision: TBanDecisionDtoPayload) {
  const data: Record<string, string | number | boolean> = {
    player_banning: banDecision.profileId,
    league: banDecision.leagueId,
  };

  if (banDecision.skip) {
    data.skipped_ban = banDecision.skip;
  } else if (banDecision.selectedGameId) {
    data.selected_game_id = banDecision.selectedGameId;
  } else {
    console.log('Something went wrong, no decision was made.');
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

export async function createGame(
  name: string,
  platform: TPlatform,
  short_name?: string
): Promise<number> {
  try {
    const { data } = await api('game/games/', {
      method: 'POST',
      data: { name: name, platform: platform.id, short_name: short_name || name },
    });
    return data.id;
  } catch (e) {
    console.log('Error while creating a new game', e);
    throw new Error(
      'Could not create new game because of following error: ' + e
    );
  }
}

export async function addRestrictions(option: TGameOption): Promise<void> {
  if (option.onlyIfOption === undefined) {
    console.log('No restriction option given', { option });
    return;
  }

  const { only_if_option, only_if_choice, only_if_value } = option as unknown as { only_if_option: number; only_if_choice: number; only_if_value: boolean };
  const optionId = getStorageItem(only_if_option);

  if (optionId === undefined) {
    console.error(
      `Invalid option: ${onlyIfOption}. It does not exist in optionIDStorage.`
    );
    return;
  }

  const data: {
    only_if_option: number;
    only_if_choice?: number;
    only_if_value?: boolean;
  } = {
    only_if_option: optionId,
  };

  if (only_if_value !== undefined) {
    data.only_if_value = only_if_value;
  } else if (only_if_choice !== undefined) {
    const choiceValue = getStorageItem(only_if_choice);
    if (choiceValue !== undefined) {
      data.only_if_choice = choiceValue;
    } else {
      console.error(
        `Invalid choice: ${only_if_choice}. It does not exist in optionIDStorage.`
      );
      return;
    }
  } else {
    console.error(
      'Both only_if_value and only_if_choice are undefined. To set a restriction, at least one must be provided.'
    );
    return;
  }

  await api(`game/options/${optionId}/`, {
    method: 'PATCH',
    data,
  });
}

async function createOption(
  option: TGameOption,
  gameId: number
): Promise<TGameOptionDto> {
  try {
    const { data: newOption } = await api('game/options/', {
      method: 'POST',
      data: {
        name: option.title,
        has_choices: option.hasChoices,
        game: gameId,
      },
    });
    addStorageItem(option.id as number, newOption.id);
    return newOption;
  } catch (e) {
    // errorMessages.value.push('CreateGameOption');
    console.log('Error creating game options', e);
    throw new Error('Error creating game options: \n' + e);
  }
}

async function createOptionChoice(
  choice: TGameOptionChoice,
  optionId: number
): Promise<TGameOptionChoiceDto> {
  try {
    const { data: newChoice } = await api('game/option-choices/', {
      method: 'POST',
      data: {
        name: choice.name,
        option: optionId,
      },
    });
    addStorageItem(choice.id as number, newChoice.id);
    return newChoice;
  } catch (e) {
    console.log('Error creating game option choice', e);
    throw new Error('Error creating game option choice: \n' + e);
  }
}

async function createOptionChoices(option: TGameOption): Promise<void> {
  if (!option.hasChoices) return;
  for (const choice of option.choices) {
    const optionId = getStorageItem(option.id as number);
    await createOptionChoice(choice, optionId);
  }
}

export async function createOptions(
  gameId: number,
  gameOptions: TGameOption[]
): Promise<void> {
  for (const option of gameOptions) {
    await createOption(option, gameId);
  }
  for (const option of gameOptions) {
    await createOptionChoices(option);
    await addRestrictions(option);
  }
}

export async function createResultConfigData(
  gameId: number,
  resultConfig: TResultConfig
): Promise<void> {
  try {
    const { data: resultConfigData } = await api('game/result-configs/', {
      method: 'POST',
      data: {
        game: gameId,
        is_asymmetric: resultConfig?.isAsymmetric,
        has_starting_player_order: resultConfig?.hasStartingPlayerOrder,
        has_points: resultConfig?.hasPoints,
        starting_points_system: resultConfig?.startingPointSystem,
      },
    });
    await createFactions(gameId, resultConfig);
    await createTieBreakers(resultConfigData.id, resultConfig);
  } catch (e) {
    // errorMessages.value.push('CreateResultConfig');
    console.log('Error creating the result configuration', e);
    throw new Error('Error creating the result configuration: \n' + e);
  }
}

export async function createFactions(
  gameId: number,
  resultConfig: TResultConfig
): Promise<void> {
  if (resultConfig === undefined) return;
  if (resultConfig.factions === undefined) return;
  for (const faction of resultConfig.factions) {
    try {
      await api('game/factions/', {
        method: 'POST',
        data: {
          game: gameId,
          name: faction.name,
          level: faction.level
        },
      });
    } catch (e) {
      console.log('Error creating faction', e);
    }
  }
}

export async function createTieBreakers(resultConfigId: number, resultConfig: TResultConfig): Promise<void> {
  console.log(resultConfigId, resultConfig);
  if (resultConfig === undefined) return;
  if (resultConfig.tieBreakers === undefined) return;
  if (!resultConfig.hasTieBreaker) return;

  for (const [index, tieBreaker] of resultConfig.tieBreakers.entries()) {
    console.log(index, tieBreaker);
    try {
      await api('game/tie-breakers/', {
        method: 'POST',
        data: {
          result_config: resultConfigId,
          name: tieBreaker.name,
          order: index * 10,
          higher_wins: tieBreaker.higher_wins,
        },
      });
    } catch (e) {
      console.log('Error creating tieBreaker', e);
    }
  }
}


export async function createSelectedGame(
  selectedGame: TSelectedGameDtoPayload,
  manageOnly = false
) {
  const data = {
    game: selectedGame.game,
    selected_options: selectedGame.selected_options,
    league: selectedGame.league,
    profile: selectedGame.profile,
    manage_only: manageOnly,
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

export async function editSelectedGame(
  selectedGame: TSelectedGameDtoPayload & { id: number }
) {
  try {
    return await api(`/game/selected-games/${selectedGame.id}/`, {
      method: 'PATCH',
      data: {
        game: selectedGame.game,
        profile: selectedGame.profile,
        league: selectedGame.league,
        selected_options: selectedGame.selected_options,
      },
    });
  } catch (error) {
    throw new Error('Error editing selectedGame: ' + error);
  }
}

export async function fetchGameOptions(gameId: number): Promise<TGameOptionDto[]> {
  try {
    const { data } = await api.get<TGameOptionDto[]>(`/game/options/?game=${gameId}`);
    return data;
  } catch (error) {
    throw new Error(
      `Error retrieving game options for game with id: ${gameId} \n ${error}`
    );
  }
}

export async function fetchGameOptionChoices(optionId: number): Promise<TGameOptionChoiceDto[]> {
  try {
    const { data } = await api.get<TGameOptionChoiceDto[]>(`/game/option-choices/?option=${optionId}`);
    return data;
  } catch (error) {
    throw new Error(
      `Error retrieving game option choices for game with id: ${optionId} \n ${error}`
    );
  }
}

export async function fetchFullGame(gameId: number): Promise<TFullGameDto> {
  try {
    const { data } = await api(`game/games-full/${gameId}/`);
    return data;
  } catch (error) {
    throw new Error(`Error fetching full game with id ${gameId}: ${error}`);
  }
}

export async function updateResultConfigData(
  gameId: number,
  resultConfig: TResultConfig
): Promise<void> {
  try {
    // 1. Fetch existing result config to get its ID
    const { data: existingConfigs } = await api.get<TResultConfig[]>(
      `game/result-configs/?game=${gameId}`
    );

    let configId: number;

    if (existingConfigs.length > 0) {
      configId = existingConfigs[0].id;
      // 2. Update existing result config
      await api(`game/result-configs/${configId}/`, {
        method: 'PATCH',
        data: {
          is_asymmetric: resultConfig?.isAsymmetric,
          has_starting_player_order: resultConfig?.hasStartingPlayerOrder,
          has_points: resultConfig?.hasPoints,
          starting_points_system: resultConfig?.startingPointSystem,
        },
      });

      // 3. Delete existing factions and tie-breakers (simpler than selective update)
      const { data: existingFactions } = await api.get<any[]>(
        `game/factions/?game=${gameId}`
      );
      for (const f of existingFactions) {
        await api.delete(`game/factions/${f.id}/`);
      }

      const { data: existingTieBreakers } = await api.get<any[]>(
        `game/tie-breakers/?result_config=${configId}`
      );
      for (const tb of existingTieBreakers) {
        await api.delete(`game/tie-breakers/${tb.id}/`);
      }
    } else {
      // Create new if somehow missing
      const { data: newConfig } = await api('game/result-configs/', {
        method: 'POST',
        data: {
          game: gameId,
          is_asymmetric: resultConfig?.isAsymmetric,
          has_starting_player_order: resultConfig?.hasStartingPlayerOrder,
          has_points: resultConfig?.hasPoints,
          starting_points_system: resultConfig?.startingPointSystem,
        },
      });
      configId = newConfig.id;
    }

    // 4. Create new factions and tie-breakers
    await createFactions(gameId, resultConfig);
    await createTieBreakers(configId, resultConfig);
  } catch (e) {
    console.log('Error updating the result configuration', e);
    throw new Error('Error updating the result configuration: \n' + e);
  }
}
