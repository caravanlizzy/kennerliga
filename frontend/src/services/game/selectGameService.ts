import {GameDto} from 'pages/game/models';
import {api} from 'boot/axios';

export async function createSelectedGame(game: GameDto, options: object[], leagueId: number, playerId: number): Promise<void> {
  try {
    await api('/games/selected-games', {
      method: 'POST',
      data: {
        player: playerId,
        game: game.id,
        league: leagueId
      }
    })
    for (const [option, selection] of Object.entries(options)) {
      let data = null;
      if (hasChoices(selection)) {
        data = {value: selection};
      } else {
        data = {choice: selection.id}
      }
      await api('games/selected-game-options', {
        method: 'POST',
        data: data
      })
    }
  } catch (error) {
    console.log('error creating the selected game: ', game.name, error);
    throw new Error('Error creating the selected game: ' + error);
  }

  function hasChoices(option: object|boolean) {
    return typeof (option) !== 'boolean';
  }
}
