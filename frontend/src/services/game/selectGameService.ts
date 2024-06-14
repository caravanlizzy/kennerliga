import {GameDto} from 'pages/game/models';
import {api} from 'boot/axios';

export async function createSelectedGame(game: GameDto, options: {}, leagueId: number, playerId: number): Promise<void> {
  try {
    const {data: selectedGame} = await api('/games/selected-games', {
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
  }

  function hasChoices(option) {
    return typeof (option) !== 'boolean';
  }
}
