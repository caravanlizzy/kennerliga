import { api } from 'boot/axios';
import { AxiosResponse } from 'axios';
import { TMessageDto } from 'src/types';

export async function fetchMessages(
  params?: {
    last_datetime?: string;
    before_datetime?: string;
    limit?: number;
  }
): Promise<AxiosResponse<TMessageDto[]>> {
  return await api.get<TMessageDto[]>('chat/messages/', { params });
}

export async function postMessage(messageText: string): Promise<AxiosResponse<TMessageDto>> {
  return await api.post<TMessageDto>('chat/messages/', { text: messageText });
}
