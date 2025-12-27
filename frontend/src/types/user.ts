export type TProfile = {
  id: number;
  name: string;
};

export type TUser = {
  id: number;
  username: string;
  email: string;
  is_superuser: boolean;
  is_staff: boolean;
  is_active: boolean;
  date_joined: string;
  last_login: string | null;
  profile?: TProfile;
  token?: string;
  admin?: boolean;
  myCurrentLeagueId?: number | null;
};
