export type TSeasonDto = {
  id: number;
  year: number;
  month: number;
  name?: string;
  status?: string;
  is_completed?: boolean;
};

/** Mirrors `SeasonViewSet.league_winners`. */
export type TSeasonLeagueWinners = {
  season: { id: number; name: string; status: string };
  winners: Array<{
    league: { id: number; level: number };
    winner: {
      profile_id: number;
      profile_name: string;
      username: string | null;
    } | null;
    league_points: string | number | null;
  }>;
};

/** Mirrors `SeasonViewSet.current_champion`. */
export type TCurrentChampion = {
  username: string;
  season_id: number;
  season_name: string;
  profile_id: number;
  profile_name: string;
  league_points: string | number;
};
