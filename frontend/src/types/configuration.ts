export type TAppConfigurationDto = {
  id: number;
  max_same_game_per_year: number;
  tie_decider_game: number | null;
  tie_decider_game_name: string | null;
  created_at: string;
  created_by: number | null;
  created_by_username: string | null;
};

export type AppConfigurationCreate = {
  max_same_game_per_year: number;
  tie_decider_game: number | null;
};
