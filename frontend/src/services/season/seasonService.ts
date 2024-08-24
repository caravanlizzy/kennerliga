import { api } from "boot/axios";

export async function registerForCurrentSeason(): Promise<void> {
  try {
    const { data } = await api('/season/register/', { method: 'POST' });
    console.log(data);
  } catch (error) {
    console.error(error)
  }
}
