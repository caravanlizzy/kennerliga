import { api } from 'boot/axios';
import { AxiosResponse } from 'axios';
import { TMessageDto } from 'src/types';

export async function fetchMessages(
  lastDateTime: string | undefined
): Promise<AxiosResponse<TMessageDto[]>> {
  let url = 'chat/messages/';
  if (lastDateTime) url += `?last_datetime=${lastDateTime}`;
  return await api.get<TMessageDto[]>(url);
}

export async function postMessage(messageText: string): Promise<void> {
  await api('chat/messages/', {
    method: 'POST',
    data: { text: messageText }
  });
}
