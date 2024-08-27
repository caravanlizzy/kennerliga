import { api } from 'boot/axios';
import { AxiosPromise } from 'axios';

export type TMessage = {
  text: string;
  datetime: string;
  user: number;
  type: string;
}

export async function getMessages(lastDateTime: string|undefined): Promise<AxiosPromise> {
  let url = 'chat/messages/';
  if(lastDateTime) url += `?last_datetime=${lastDateTime}`;
  return await api(url);
}

export async function addMessage(messageText: string): Promise<void> {
  await api('chat/messages/', {
    method: 'POST',
    data: { text: messageText }
  });
}
