import { api } from 'boot/axios';
import { TTaskDto, TaskCreate, TaskUpdate } from 'src/types';

const BASE_URL = 'taskboard/tasks/';

export async function fetchTasks(): Promise<TTaskDto[]> {
  const { data } = await api.get<TTaskDto[]>(BASE_URL);
  return data;
}

export async function createTask(task: TaskCreate): Promise<TTaskDto> {
  const { data } = await api.post<TTaskDto>(BASE_URL, task);
  return data;
}

export async function updateTask(id: number, task: TaskUpdate): Promise<TTaskDto> {
  const { data } = await api.patch<TTaskDto>(`${BASE_URL}${id}/`, task);
  return data;
}

export async function deleteTask(id: number): Promise<void> {
  await api.delete(`${BASE_URL}${id}/`);
}
