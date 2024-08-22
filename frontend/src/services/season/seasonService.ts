import { api } from "boot/axios";

export async function registerForCurrentSeason(): Promise<void> {
  console.log({api});
  try {
    console.log('trying');
    const { data } = await api('/season/register/', { method: 'POST' });
    console.log(data);
  } catch (error) {
    console.log(error)
  }
}
