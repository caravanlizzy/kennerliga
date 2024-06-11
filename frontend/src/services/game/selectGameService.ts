import {GameDto} from 'pages/game/models';
import {api} from 'boot/axios';

export async function createSelectedGame(game: GameDto, options: {}, leagueId: number, playerId: number): Promise<void> {
  try {
    const {data: selectedGame} = await api(`/games/selected-games`, {
      method: 'POST',
      data: {
        player: playerId,
        game: game.id,
        leage: leagueId
      }
    })
    for(const option of options){
      await
    }
  }
}
