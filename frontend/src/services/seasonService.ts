import { api } from "boot/axios";

export async function registerForCurrentSeason(): Promise<void> {
  try {
    const { data } = await api('/season/register/', { method: 'POST' });
  } catch (error) {
    console.error(error)
  }
}

export async function getCurrentSeasonId(): Promise<number> {
  const { data } = await api('/season/current/');
  return data.id;
}
