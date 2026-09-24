import { api } from 'boot/axios';
import {
  AvatarShape,
  TPlayerProfileDto,
  TUserDto,
  TUserInviteDto,
  TUserStatistics,
} from 'src/types';
import { unwrapList } from 'src/services/httpTypes';

export type UserListParams = Record<
  string,
  string | number | boolean | (string | number)[]
>;

/**
 * Fetches user rows, optionally filtered (see `UserViewSet.get_queryset`).
 * Throws on failure so callers can tell "no users" apart from "request failed".
 */
export async function fetchUsers(params?: UserListParams): Promise<TUserDto[]> {
  const { data } = await api.get('/user/users/', { params });
  return unwrapList<TUserDto>(data);
}

/** Years that have season data, newest first. */
export async function fetchAvailableYears(): Promise<number[]> {
  const { data } = await api.get<number[]>('/user/users/available-years/');
  return data;
}

/** A single user, addressed by username (the API also accepts an id). */
export async function fetchUser(username: string): Promise<TUserDto> {
  const { data } = await api.get<TUserDto>(
    `user/users/${encodeURIComponent(username)}/`
  );
  return data;
}

/**
 * Aggregated per-player statistics. `year` narrows the result to one season
 * year; the payload shape is defined by `UserViewSet.user_statistics`.
 */
export async function fetchUserStatistics(
  userId: number,
  params?: { year?: number }
): Promise<TUserStatistics> {
  const { data } = await api.get<TUserStatistics>(
    `user/users/${userId}/statistics/`,
    { params }
  );
  return data;
}

/** Player profiles. `unlinkedOnly` returns those not yet tied to a user. */
export async function fetchProfiles(
  { unlinkedOnly = false } = {}
): Promise<TPlayerProfileDto[]> {
  const { data } = await api.get('/user/profiles/', {
    params: unlinkedOnly ? { user__isnull: true } : undefined,
  });
  return unwrapList<TPlayerProfileDto>(data);
}

export async function fetchInvitations(): Promise<TUserInviteDto[]> {
  const { data } = await api.get('user/invitations/');
  return unwrapList<TUserInviteDto>(data);
}

export async function createInvitation(payload: {
  label: string;
  player_profile?: number | null;
}): Promise<TUserInviteDto> {
  const { data } = await api.post<TUserInviteDto>('/user/invitations/', payload);
  return data;
}

/**
 * Signs a new account up against an invite key.
 *
 * The endpoint answers `{ detail }` rather than the created user, and throws
 * (via Axios) on the 400s it uses for an expired or unknown invite.
 */
export async function registerUser(payload: {
  username: string;
  password: string;
  invite_key: string;
}): Promise<{ detail: string }> {
  const { data } = await api.post<{ detail: string }>('/user/register/', payload);
  return data;
}

/**
 * Requests a password reset link for a given username.
 */
export async function requestPasswordReset(payload: {
  username: string;
}): Promise<{ detail: string }> {
  const { data } = await api.post<{ detail: string }>(
    '/user/password-reset/',
    payload
  );
  return data;
}

/**
 * Confirms a new password using the one-time reset key.
 */
export async function confirmPasswordReset(payload: {
  key: string;
  password: string;
}): Promise<{ detail: string }> {
  const { data } = await api.post<{ detail: string }>(
    '/user/password-reset/confirm/',
    payload
  );
  return data;
}

/** Updates the authenticated user's avatar shape. */
export async function updateAvatarShape(shape: AvatarShape): Promise<TUserDto> {
  const { data } = await api.patch<TUserDto>('/user/users/avatar-shape/', {
    avatar_shape: shape,
  });
  return data;
}

/** Updates the authenticated user's avatar color (hex code or empty string for auto). */
export async function updateAvatarColor(color: string): Promise<TUserDto> {
  const { data } = await api.patch<TUserDto>('/user/users/avatar-color/', {
    avatar_color: color,
  });
  return data;
}
