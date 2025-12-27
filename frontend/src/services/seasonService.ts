import { AxiosResponse } from 'axios';
import { api } from 'boot/axios';
import { TSeasonDto, TSeasonParticipantDto, TLeagueDto } from 'src/types';

export async function registerForSeason(): Promise<AxiosResponse | undefined> {
  try {
    return await api.post('/season/register/');
  } catch (error) {
    console.error(error);
  }
}

export async function fetchIsRegisteredForSeason(): Promise<boolean> {
  try {
    const { data } = await api.get('/season/seasons/registration-status/');
    return data.registered;
  } catch (error) {
    console.log(error);
    return false;
  }
}

export async function fetchOpenSeasonParticipants(): Promise<TSeasonParticipantDto[]> {
  try {
    const { data } = await api.get('/season/season-participants/current/');
    return data;
  } catch (error) {
    console.error('Failed to fetch open season participants:', error);
    return []; // safe fallback
  }
}

export async function fetchSeason(seasonId: number): Promise<TSeasonDto | undefined> {
  try {
    const { data } = await api(`/season/seasons/${seasonId}/`);
    return data;
  } catch (error) {
    console.error('Error fetching season: ' + seasonId, error);
  }
}

export async function fetchCurrentSeasonId(): Promise<number | null> {
  try {
    const { data } = await api.get('/season/current/');
    return data.id ?? null;
  } catch (error) {
    console.error('Error fetching current season ID:', error);
    return null;
  }
}
/** Backend helpers */
// find-or-create season
export async function createSeason(targetYear: number, targetMonth: number): Promise<TSeasonDto> {
  const { data: seasons } = await api.get<TSeasonDto[]>('/season/seasons/');
  let season = Array.isArray(seasons)
    ? seasons.find((s: TSeasonDto) => s.year === targetYear && s.month === targetMonth)
    : null;

  if (!season) {
    const res = await api.post<TSeasonDto>('/season/seasons/', {
      year: targetYear,
      month: targetMonth,
      status: 'DONE',
    });
    season = res.data;
  }
  return season as TSeasonDto; // { id, year, month, ... }
}

async function fetchSeasonParticipants(seasonId: number): Promise<TSeasonParticipantDto[]> {
  // Season detail should include participants array
  console.log({ seasonId });
  const { data } = await api.get<TSeasonParticipantDto[]>(`/season/season-participants/?season=${seasonId}`);
  console.log('data in fetchSeasonParticipants: ', data);
  return data ? data : [];
}

export async function fetchLeaguesBySeason(seasonId: number): Promise<TLeagueDto[]> {
  try {
    const { data } = await api(`/league/leagues/?season=${seasonId}`);
    return data;
  } catch (error) {
    console.error('Error fetching leagues by season:', error);
    throw error; // Re-throw the error to let the caller handle it
  }
}

type ProfileLike = { id: number } | number;

export async function ensureParticipants(
  seasonId: number,
  profiles: ProfileLike[]
): Promise<TSeasonParticipantDto[]> {
  // Normalize incoming profiles to a unique list of numeric IDs, preserving order
  const incomingIds = Array.from(
    new Set(
      (profiles || [])
        .map((p) => (typeof p === 'number' ? p : p?.id))
        .filter((id): id is number => Number.isInteger(id))
    )
  );

  // Fetch existing participants and index by profile id
  const existing = await fetchSeasonParticipants(seasonId);
  const byProfile: Record<number, TSeasonParticipantDto> = {};
  for (const sp of existing) {
    const pid = sp.profile_id;
    if (pid != null) byProfile[pid] = sp;
  }

  // Compute which incoming profiles are missing from this season
  const missing = incomingIds.filter((pid) => !byProfile[pid]);

  // Create SeasonParticipant for any missing profiles with rank based on position
  for (const pid of missing) {
    const rank = incomingIds.indexOf(pid) + 1; // 1-based rank
    await api('/season/season-participants/', {
      method: 'POST',
      data: { season: seasonId, profile: pid, rank },
    });
  }

  // Return the updated list
  return await fetchSeasonParticipants(seasonId);
}

export async function createLeagueForSeason(
  seasonId: number,
  level: number,
  seasonParticipants: TSeasonParticipantDto[],
  memberProfileIds: number[]
): Promise<TLeagueDto> {
  // map chosen PlayerProfile IDs -> SeasonParticipant IDs
  const spIds = seasonParticipants
    .filter((sp: TSeasonParticipantDto) => memberProfileIds.includes(sp.profile_id))
    .map((sp: TSeasonParticipantDto) => sp.id);

  const { data } = await api('/league/leagues/', {
    method: 'POST',
    data: { season: seasonId, level, member_ids: spIds, status: 'DONE' },
  });
  return data;
}
