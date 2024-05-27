import {api} from 'boot/axios';
import {TGameOption, TPlatform, TResultConfig} from 'pages/game/models';

export const optionIDStorage: { [key: string]: number } = {};


export function addStorageItemId(itemId: number, id: number): void {
  optionIDStorage[itemId.toString()] = id;
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
    console.log('No restriction option given');
    return;
  }

  const { onlyIfOption, onlyIfChoice, onlyIfValue } = option;
  const optionId = optionIDStorage[onlyIfOption];

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
    const choiceValue = optionIDStorage[onlyIfChoice];
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



export async function createOptions(gameId: number, gameOptions: TGameOption[]): Promise<void> {
  for (const option of gameOptions) {
    try {
      const { data: newOption } = await api('game/options/', {
        method: 'POST',
        data: {
          name: option.title,
          has_choices: option.hasChoices,
          game: gameId
        }
      });
      addStorageItemId(option.itemId, newOption.id);
      for (const choice of option.choices) {
        await api('game/option-choices/', {
          method: 'POST',
          data: {
            name: choice,
            option: newOption.id
          }
        });
        console.log({ itemIdMap: optionIDStorage });
        // currently not working since list logic has been outsourced
        // addItemId(choice.itemId, data.id);
      }
      await addRestrictions(option);
    } catch (e) {
      // errorMessages.value.push('CreateGameOption');
      console.log('Error creating game options', e);
      throw new Error('Error creating game options: \n' + e);
    }
  }
}


export async function createResultConfigData(gameId: number, resultConfig: TResultConfig): Promise<void> {
  try {
    const {data: resultConfigData} = await api('game/result-configs/', {
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

export async function createFactions(gameId: number, resultConfig:TResultConfig): Promise<void> {
  if(resultConfig === undefined) return;
  if(resultConfig.factions === undefined) return;
  for (const faction of resultConfig.factions){
    try {
      api('game/factions/', {
        method:'POST',
        data: {
          game: gameId,
          name: faction
        }
      })
    } catch(e) {
      console.log('Error creating faction', e)
    }
  }
}

export async function createTieBreakers(resultConfigId: number, resultConfig:TResultConfig): Promise<void> {
  if(resultConfig === undefined) return;
  if(resultConfig.tieBreakers === undefined) return;
  if(!resultConfig.hasTieBreaker) return;
  for (const [index, tieBreaker] of resultConfig.tieBreakers.entries()){
    try {
      api('game/tie-breakers/', {
        method:'POST',
        data: {
          result_config: resultConfigId,
          name: tieBreaker,
          order: index * 10
        }
      })
    } catch(e) {
      console.log('Error creating tieBreaker', e)
    }
  }
}
