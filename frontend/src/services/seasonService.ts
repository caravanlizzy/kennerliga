import { api } from 'boot/axios';

export async function registerForCurrentSeason(): Promise<void> {
  try {
    const { data } = await api('/season/register/', { method: 'POST' });
  } catch (error) {
    console.error(error);
  }
}

export async function getCurrentSeasonId(): Promise<number | null> {
  const { data } = await api('/season/current/');
  return data.id ?? null;
}
/** Backend helpers */
// find-or-create season
export async function createSeason(targetYear: number, targetMonth: number) {
  const { data: seasons } = await api('/season/seasons/');
  let season = Array.isArray(seasons)
    ? seasons.find((s: any) => s.year === targetYear && s.month === targetMonth)
    : null;

  if (!season) {
    const res = await api('/season/seasons/', {
      method: 'POST',
      data: { year: targetYear, month: targetMonth },
    });
    season = res.data;
  }
  return season; // { id, year, month, ... }
}

async function getSeasonParticipants(seasonId: number) {
  // Season detail should include participants array
  console.log({seasonId});
  const { data } = await api(`/season/season-participants/?season=${seasonId}`);
  console.log('data in getSeasonParticipants: ', data);
  return data ? data : []
}

export async function getLeaguesBySeason(seasonId: number) {
  try {
    const { data } = await api(`/league/leagues/?season=${seasonId}`);
    return data;
  } catch (error) {
    console.error('Error fetching leagues by season:', error);
    throw error; // Re-throw the error to let the caller handle it
  }
}

export async function getLeageDetailsBySeason(seasonId: number) {
  try {
    const leagues = await getLeaguesBySeason(seasonId);
    const leagueDetails = await Promise.all(
      leagues.map((league) => api(`/league/league-details/${league.id}/`))
    );
    return leagueDetails.map((response) => response.data);
  } catch (error) {
    console.error('Error fetching league details by season:', error);
  }
}

type ProfileLike = { id: number } | number;

export async function ensureParticipants(
  seasonId: number,
  profiles: ProfileLike[]
) {
  // Normalize incoming profiles to a unique list of numeric IDs
  const incomingIds = Array.from(
    new Set(
      (profiles || [])
        .map((p) => (typeof p === 'number' ? p : p?.id))
        .filter((id): id is number => Number.isInteger(id))
    )
  );
  console.log('incomingIds:', incomingIds);

  // Fetch existing participants and index by profile id
  const existing = await getSeasonParticipants(seasonId);
  const byProfile: Record<number, any> = {};
  for (const sp of existing) {
    const pid = sp?.profile?.id ?? sp?.profile_id ?? sp?.profile;
    if (pid != null) byProfile[pid] = sp;
  }

  // Compute which incoming profiles are missing from this season
  const missing = incomingIds.filter((pid) => !byProfile[pid]);
  console.log({ missing });
  // Create SeasonParticipant for any missing profiles
  for (const pid of missing) {
    console.log('creating missing participant:', pid, 'for season:', seasonId);
    await api('/season/season-participants/', {
      method: 'POST',
      data: { season: seasonId, profile_id: pid },
    });
  }

  // Return the updated list
  return await getSeasonParticipants(seasonId);
}


export async function createLeagueForSeason(
  seasonId: number,
  level: number,
  seasonParticipants: any[],
  memberProfileIds: number[]
) {
  // map chosen PlayerProfile IDs -> SeasonParticipant IDs
  const spIds = seasonParticipants
    .filter((sp: any) =>
      memberProfileIds.includes(sp.profile_id)
    )
    .map((sp: any) => sp.id);

  console.log({ seasonParticipants, memberProfileIds, spIds });
  const { data } = await api('/league/leagues/', {
    method: 'POST',
    data: { season: seasonId, level, member_ids: spIds },
  });
  return data;
}
