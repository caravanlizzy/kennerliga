import { api } from 'boot/axios';

export async function registerForCurrentSeason(): Promise<void> {
  try {
    const { data } = await api('/season/register/', { method: 'POST' });
  } catch (error) {
    console.error(error)
  }
}

export async function getCurrentSeasonId(): Promise<number|null> {
  const { data } = await api('/season/current/');
  return data.id??null;
}
/** Backend helpers */
// find-or-create season
export async function createSeason(targetYear: number, targetMonth: number) {
  const { data: seasons } = await api('/seasons/');
  let season = Array.isArray(seasons)
    ? seasons.find((s: any) => s.year === targetYear && s.month === targetMonth)
    : null;

  if (!season) {
    const res = await api('/seasons/', {
      method: 'POST',
      data: { year: targetYear, month: targetMonth },
    });
    season = res.data;
  }
  return season; // { id, year, month, ... }
}

async function getSeasonParticipants(seasonId: number) {
  // Season detail should include participants array
  const { data } = await api(`/seasons/${seasonId}/`);
  return data?.participants ?? [];
}

export async function ensureParticipants(seasonId: number, profileIds: number[]) {
  const existing = await getSeasonParticipants(seasonId);
  const byProfile: Record<number, any> = {};
  for (const sp of existing) {
    const pid = sp.profile?.id ?? sp.profile_id ?? sp.profile;
    if (pid != null) byProfile[pid] = sp;
  }
  const missing = profileIds.filter((pid) => !byProfile[pid]);

  // create SeasonParticipant for any missing
  for (const pid of missing) {
    await api('/season-participants/', {
      method: 'POST',
      data: { season: seasonId, profile: pid },
    });
  }
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
      memberProfileIds.includes(sp.profile?.id ?? sp.profile_id ?? sp.profile)
    )
    .map((sp: any) => sp.id);

  const { data } = await api('/leagues/', {
    method: 'POST',
    data: { season: seasonId, level, members: spIds },
  });
  return data;
}
