import { api } from 'boot/axios';
import { GameOptionDto, SelectedGameDto } from 'src/models/gameModels';

export async function createSelectedGame(selectedGame: SelectedGameDto) {
  console.log({selectedGame})
  try {
    await api('/game/selected-games/', {
      method: 'POST',
      data: {
        selectedGame,
      },
    });
  } catch (error) {
    throw new Error('Error creating selectedGame' + error);
  }
}

export async function getGameOptions(gameId: number) {
  try {
    return await api(`/game/options/?game=${gameId}`);
  } catch (error) {
    throw new Error(
      `Error retrieving game options for game with id: ${gameId} \n ${error}`
    );
  }
}

export async function getGameOptionChoices(optionId: number) {
  try {
    return await api(`/game/option-choices/?option=${optionId}`);
  } catch (error) {
    throw new Error(
      `Error retrieving game option choices for game with id: ${optionId} \n ${error}`
    );
  }
}

// async function createSelectedGameOption(option) {
//   if(hasChoices())
// }

// export async function createSelections(
//   game: GameDto,
//   options: SelectedOptionsMap,
// ): Promise<void> {
//   try {
//     console.log({options});
//     console.log({ game });
//     await createSelectedGame(game.id);
//     for (const [_, selection] of Object.entries(options)) {
//       let data = null;
//       if (hasChoices(selection)) {
//         data = { value: selection };
//       } else {
//         data = { choice: selection.id };
//       }
//       await api('games/selected-game-options', {
//         method: 'POST',
//         data: data,
//       });
//     }
//   } catch (error) {
//     console.log('error creating the selected game: ', game.name, error);
//     throw new Error('Error creating the selected game: ' + error);
//   }
//
//   function hasChoices(option: object | boolean) {
//     return typeof option !== 'boolean';
//   }
// }
