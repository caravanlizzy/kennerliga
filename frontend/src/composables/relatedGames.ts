import type { TGameDto, TPlatform } from 'src/types';

export type TRelatedGameOption = {
  id: number;
  label: string;
};

export function getRelatedGameOptions(
  games: TGameDto[],
  platforms: TPlatform[],
  currentGameId?: number,
  searchText = ''
): TRelatedGameOption[] {
  const platformNames = new Map(
    platforms.map((platform) => [platform.id, platform.name])
  );
  const search = searchText.trim().toLocaleLowerCase();

  return games
    .filter((game) => game.id !== currentGameId)
    .map((game) => ({
      id: game.id,
      label: `${game.name} (${platformNames.get(game.platform) || 'Unknown platform'})`,
    }))
    .filter((option) => option.label.toLocaleLowerCase().includes(search));
}