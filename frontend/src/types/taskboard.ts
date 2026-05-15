export enum TaskPriority {
  LOW = 'Low',
  MEDIUM = 'Medium',
  HIGH = 'High',
}

export enum TaskStatus {
  TODO = 'To Do',
  IN_PROGRESS = 'In Progress',
  DONE = 'Done',
  DECLINED = 'Declined',
}

export type TTaskDto = {
  id: number;
  title: string;
  description: string;
  priority: TaskPriority;
  status: TaskStatus;
  created_at: string;
  updated_at: string;
};

export type TaskCreate = {
  title: string;
  description?: string;
  priority: TaskPriority;
  status: TaskStatus;
};

export type TaskUpdate = Partial<TaskCreate>;
