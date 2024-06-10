import { GameDto } from 'pages/game/models';
import { api } from 'boot/axios';

export async function selectGame(selectedGame: GameDto, selectedOptions: {}):Promise<void> {
  const { data: selection } = api('selected-game')
}
