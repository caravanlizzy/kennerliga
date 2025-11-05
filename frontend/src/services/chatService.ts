import { api } from 'boot/axios';
import { AxiosPromise } from 'axios';

export async function fetchMessages(
  lastDateTime: string | undefined
): Promise<AxiosPromise> {
  let url = 'chat/messages/';
  if (lastDateTime) url += `?last_datetime=${lastDateTime}`;
  return await api(url);
}

export async function postMessage(messageText: string): Promise<void> {
  await api('chat/messages/', {
    method: 'POST',
    data: { text: messageText }
  });
}
