import { api } from 'boot/axios';
import { TFeedbackDto } from 'src/types';

export async function postFeedback(message: string): Promise<void> {
  await api.post('/user/feedback/', { message });
}

export async function fetchFeedback(): Promise<TFeedbackDto[]> {
  const { data } = await api.get<TFeedbackDto[]>('/user/feedback/');
  return data;
}
