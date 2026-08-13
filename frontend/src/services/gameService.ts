import {
  TBanDecisionDtoPayload,
  TFullGameDto,
  TGameOptionChoiceDto,
  TGameOptionDto,
  TSelectedGameDtoPayload,
  TPlatform,
  TFactionDto,
  TResultConfigDto,
  TWinConditionDto,
} from 'src/types';
import { api } from 'boot/axios';
import {
  TGameOption,
  TGameOptionChoice,
  TResultConfig,
} from 'src/types';
import { unwrapList } from 'src/services/httpTypes';

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
    return await api.post('/game/ban-decisions/', data);
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
    const { data } = await api.post('/game/games/', {
      name: name,
      platform: platform.id,
      short_name: short_name || name,
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
      `Invalid option: ${only_if_option}. It does not exist in optionIDStorage.`
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

  await api.patch(`/game/options/${optionId}/`, data);
}

async function createOption(
  option: TGameOption,
  gameId: number
): Promise<TGameOptionDto> {
  try {
    const { data: newOption } = await api.post('/game/options/', {
      name: option.title,
      has_choices: option.hasChoices,
      game: gameId,
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
    const { data: newChoice } = await api.post('/game/option-choices/', {
      name: choice.name,
      option: optionId,
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
    const { data: resultConfigData } = await api.post('/game/result-configs/', {
      game: gameId,
      is_asymmetric: resultConfig?.isAsymmetric,
      has_starting_player_order: resultConfig?.hasStartingPlayerOrder,
      has_points: resultConfig?.hasPoints,
      starting_points_system: resultConfig?.startingPointSystem,
    });
    await createFactions(gameId, resultConfig);
    await createWinConditions(resultConfigData.id, resultConfig);
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
      await api.post('/game/factions/', {
        game: gameId,
        name: faction.name,
        level: faction.level,
      });
    } catch (e) {
      console.log('Error creating faction', e);
    }
  }
}

export async function createWinConditions(resultConfigId: number, resultConfig: TResultConfig): Promise<void> {
  if (!resultConfig?.winConditions?.length) return;

  for (const [wcIndex, winCondition] of resultConfig.winConditions.entries()) {
    let winConditionId: number;
    try {
      const { data: createdWc } = await api.post('/game/win-conditions/', {
        result_config: resultConfigId,
        name: winCondition.name,
        condition_type: winCondition.condition_type,
        order: wcIndex * 10,
      });
      winConditionId = createdWc.id;
    } catch (e) {
      console.log('Error creating winCondition', e);
      continue;
    }

    if (winCondition.condition_type === 'OPTION' && winCondition.options?.length) {
      for (const [optIndex, opt] of winCondition.options.entries()) {
        try {
          await api.post('/game/win-condition-options/', {
            win_condition: winConditionId,
            name: opt.name,
            order: optIndex * 10,
          });
        } catch (e) {
          console.log('Error creating winConditionOption', e);
        }
      }
    }

    if (winCondition.tieBreakers?.length) {
      const len = winCondition.tieBreakers.length;
      for (const [index, tieBreaker] of winCondition.tieBreakers.entries()) {
        try {
          await api.post('/game/tie-breakers/', {
            win_condition: winConditionId,
            name: tieBreaker.name,
            order: (len - index) * 10,
            higher_wins: tieBreaker.higher_wins,
          });
        } catch (e) {
          console.log('Error creating tieBreaker', e);
        }
      }
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
    return await api.post('/game/selected-games/', data);
  } catch (error) {
    throw new Error('Error creating selectedGame: ' + error);
  }
}

export async function editSelectedGame(
  selectedGame: TSelectedGameDtoPayload & { id: number }
) {
  try {
    return await api.patch(`/game/selected-games/${selectedGame.id}/`, {
      game: selectedGame.game,
      profile: selectedGame.profile,
      league: selectedGame.league,
      selected_options: selectedGame.selected_options,
    });
  } catch (error) {
    throw new Error('Error editing selectedGame: ' + error);
  }
}

export async function fetchGameOptions(gameId: number): Promise<TGameOptionDto[]> {
  try {
    const { data } = await api.get<TGameOptionDto[]>('/game/options/', {
      params: { game: gameId },
    });
    return unwrapList(data);
  } catch (error) {
    throw new Error(
      `Error retrieving game options for game with id: ${gameId} \n ${error}`
    );
  }
}

export async function fetchGameOptionChoices(optionId: number): Promise<TGameOptionChoiceDto[]> {
  try {
    const { data } = await api.get<TGameOptionChoiceDto[]>('/game/option-choices/', {
      params: { option: optionId },
    });
    return unwrapList(data);
  } catch (error) {
    throw new Error(
      `Error retrieving game option choices for game with id: ${optionId} \n ${error}`
    );
  }
}

export async function fetchPlatforms(): Promise<TPlatform[]> {
  const { data } = await api.get<TPlatform[]>('/game/platforms/');
  return unwrapList(data);
}

export async function fetchPlatform(platformId: number): Promise<TPlatform> {
  const { data } = await api.get<TPlatform>(`/game/platforms/${platformId}/`);
  return data;
}

export async function fetchFullGame(gameId: number): Promise<TFullGameDto> {
  try {
    const { data } = await api.get<TFullGameDto>(`/game/games-full/${gameId}/`, {
      params: { manage_only: true },
    });
    return data;
  } catch (error) {
    throw new Error(`Error fetching full game with id ${gameId}: ${error}`);
  }
}

export async function fetchResultConfigForGame(
  gameId: number
): Promise<TResultConfigDto | null> {
  const { data } = await api.get<TResultConfigDto[]>('/game/result-configs/', {
    params: { game: gameId },
  });
  const configs = unwrapList(data);
  return configs.length > 0 ? configs[0] : null;
}

export async function fetchWinConditionsForResultConfig(
  resultConfigId: number
): Promise<TWinConditionDto[]> {
  const { data } = await api.get<TWinConditionDto[]>('/game/win-conditions/', {
    params: { result_config: resultConfigId },
  });
  return unwrapList(data);
}

export async function fetchFactionsForGame(gameId: number): Promise<TFactionDto[]> {
  const { data } = await api.get<TFactionDto[]>('/game/factions/', {
    params: { game: gameId },
  });
  return unwrapList(data);
}

export async function updateGameFull(gameId: number, payload: unknown): Promise<void> {
  await api.put(`/game/games-full/${gameId}/`, payload);
}

export type TGameDetailBundle = {
  game: TFullGameDto;
  platform: TPlatform;
  resultConfig: TResultConfigDto;
  winConditions: TWinConditionDto[];
  factions: TFactionDto[];
};

/**
 * Loads everything GameDetailPage needs in one call, instead of the page
 * hitting the API client directly for five separate endpoints.
 */
export async function fetchGameDetailBundle(gameId: number): Promise<TGameDetailBundle> {
  const game = await fetchFullGame(gameId);
  const resultConfig = await fetchResultConfigForGame(gameId);
  if (!resultConfig) {
    throw new Error(`No result configuration found for game with id ${gameId}`);
  }
  const [winConditions, factions, platform] = await Promise.all([
    fetchWinConditionsForResultConfig(resultConfig.id),
    fetchFactionsForGame(gameId),
    fetchPlatform(game.platform),
  ]);
  return { game, platform, resultConfig, winConditions, factions };
}

export type TGameEditBundle = {
  platforms: TPlatform[];
  game: TFullGameDto;
  resultConfig: TResultConfigDto | null;
  winConditions: TWinConditionDto[];
  factions: TFactionDto[];
};

/**
 * Loads everything EditGamePage needs in one call, instead of the page
 * hitting the API client directly for platforms/result-config/win-conditions/factions.
 */
export async function fetchGameEditBundle(gameId: number): Promise<TGameEditBundle> {
  const [platforms, game, resultConfig] = await Promise.all([
    fetchPlatforms(),
    fetchFullGame(gameId),
    fetchResultConfigForGame(gameId),
  ]);

  let winConditions: TWinConditionDto[] = [];
  let factions: TFactionDto[] = [];
  if (resultConfig) {
    [winConditions, factions] = await Promise.all([
      fetchWinConditionsForResultConfig(resultConfig.id),
      fetchFactionsForGame(gameId),
    ]);
  }

  return { platforms, game, resultConfig, winConditions, factions };
}

export async function updateResultConfigData(
  gameId: number,
  resultConfig: TResultConfig
): Promise<void> {
  try {
    // 1. Fetch existing result config to get its ID
    const existingConfig = await fetchResultConfigForGame(gameId);

    let configId: number;

    if (existingConfig) {
      configId = existingConfig.id;
      // 2. Update existing result config
      await api.patch(`/game/result-configs/${configId}/`, {
        is_asymmetric: resultConfig?.isAsymmetric,
        has_starting_player_order: resultConfig?.hasStartingPlayerOrder,
        has_points: resultConfig?.hasPoints,
        starting_points_system: resultConfig?.startingPointSystem,
      });

      // 3. Delete existing factions and tie-breakers (simpler than selective update)
      const existingFactions = await fetchFactionsForGame(gameId);
      for (const f of existingFactions) {
        await api.delete(`/game/factions/${f.id}/`);
      }

      // Deleting win-conditions cascades to their options and tie-breakers.
      const existingWinConditions = await fetchWinConditionsForResultConfig(configId);
      for (const wc of existingWinConditions) {
        await api.delete(`/game/win-conditions/${wc.id}/`);
      }
    } else {
      // Create new if somehow missing
      const { data: newConfig } = await api.post('/game/result-configs/', {
        game: gameId,
        is_asymmetric: resultConfig?.isAsymmetric,
        has_starting_player_order: resultConfig?.hasStartingPlayerOrder,
        has_points: resultConfig?.hasPoints,
        starting_points_system: resultConfig?.startingPointSystem,
      });
      configId = newConfig.id;
    }

    // 4. Create new factions and win-conditions (with options and tie-breakers)
    await createFactions(gameId, resultConfig);
    await createWinConditions(configId, resultConfig);
  } catch (e) {
    console.log('Error updating the result configuration', e);
    throw new Error('Error updating the result configuration: \n' + e);
  }
}
