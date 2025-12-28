export type TLiveEventType = 'PICK' | 'BAN' | 'GAME_FINISHED' | 'LEAGUE_FINISHED' | 'SEASON_FINISHED';

export interface TLiveEvent {
  id: string;
  type: TLiveEventType;
  timestamp: string;
  leagueLevel?: number | string;
  leagueId: number;
  data: {
    playerName?: string;
    gameName?: string;
    summary?: string; // For GAME_FINISHED (standings summary)
    winners?: string[]; // For LEAGUE_FINISHED/SEASON_FINISHED
    seasonWinner?: string; // For SEASON_FINISHED
  };
}
