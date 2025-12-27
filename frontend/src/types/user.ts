export type TProfileDto = {
  id: number;
  name: string;
};

export type TUserDto = {
  id: number;
  username: string;
  email: string;
  is_superuser: boolean;
  is_staff: boolean;
  is_active: boolean;
  date_joined: string;
  last_login: string | null;
  profile?: TProfileDto;
  token?: string;
  admin?: boolean;
  myCurrentLeagueId?: number | null;
};
