import { ref } from 'vue';
import { api } from 'boot/axios';

export function useGetData(url: string) {
  const data = ref();
  const get = async ():Promise<void> => {
    const response = await api({
      method: 'get',
      url: url,
    });
    data.value = response["data"];
  }
  return { data, get }
}
