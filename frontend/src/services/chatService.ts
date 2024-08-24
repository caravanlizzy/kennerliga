import { api } from "boot/axios";
import { AxiosPromise } from "axios";

export async function getMessages(): Promise<AxiosPromise> {
  return await api('chat/messages/');
}

export async function addMessage(message: string): Promise<void> {
  await api('chat/messages/', {
    method: 'POST',
    data: { text: message }
  })
}
