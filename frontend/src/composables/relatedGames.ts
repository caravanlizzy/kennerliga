import type { TGameDto, TPlatform } from 'src/types';

export type TRelatedGameOption = {
  id: number;
  label: string;
};

export type TRelatedGameDisplay = {
  items: TRelatedGameOption[];
  lookupFailed: boolean;
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

export function getRelatedGameDisplay(
  relatedGameIds: number[] | undefined,
  games: TGameDto[],
  platforms: TPlatform[],
  lookupFailed = false
): TRelatedGameDisplay {
  const ids = (relatedGameIds || []).map(Number);
  const optionsById = new Map(
    getRelatedGameOptions(games, platforms).map((option) => [option.id, option])
  );

  return {
    items: ids.map((id) =>
      optionsById.get(id) || { id, label: `Game ID ${id}` }
    ),
    lookupFailed: ids.length > 0 && lookupFailed,
  };
}