import { defineStore } from 'pinia';
import { computed, ref } from 'vue';
import {
  TTaskDto,
  TaskCreate,
  TaskPriority,
  TaskStatus,
  TaskUpdate,
} from 'src/types';
import {
  createTask as apiCreateTask,
  deleteTask as apiDeleteTask,
  fetchTasks as apiFetchTasks,
  updateTask as apiUpdateTask,
} from 'src/services/taskboardService';

const priorityChipClasses: Record<TaskPriority, string> = {
  [TaskPriority.HIGH]: 'bg-red-6 text-white',
  [TaskPriority.MEDIUM]: 'bg-amber-7 text-white',
  [TaskPriority.LOW]: 'bg-blue-grey-5 text-white',
};

const statusColumnClasses: Record<TaskStatus, string> = {
  [TaskStatus.TODO]: 'bg-grey-3',
  [TaskStatus.IN_PROGRESS]: 'bg-indigo-1',
  [TaskStatus.DONE]: 'bg-green-1',
  [TaskStatus.DECLINED]: 'bg-red-1',
};

const statusIcons: Record<TaskStatus, string> = {
  [TaskStatus.TODO]: 'inbox',
  [TaskStatus.IN_PROGRESS]: 'pending_actions',
  [TaskStatus.DONE]: 'check_circle',
  [TaskStatus.DECLINED]: 'cancel',
};

export const useTaskboardStore = defineStore('taskboard', () => {
  const tasks = ref<TTaskDto[]>([]);
  const loading = ref(false);

  const tasksByStatus = computed<Record<TaskStatus, TTaskDto[]>>(() => {
    const grouped: Record<TaskStatus, TTaskDto[]> = {
      [TaskStatus.TODO]: [],
      [TaskStatus.IN_PROGRESS]: [],
      [TaskStatus.DONE]: [],
      [TaskStatus.DECLINED]: [],
    };
    for (const t of tasks.value) {
      if (grouped[t.status]) {
        grouped[t.status].push(t);
      }
    }
    return grouped;
  });

  const recentTasks = computed<TTaskDto[]>(() =>
    [...tasks.value]
      .sort((a, b) => (a.updated_at < b.updated_at ? 1 : -1))
      .slice(0, 10),
  );

  async function fetchTasks(): Promise<void> {
    loading.value = true;
    try {
      tasks.value = await apiFetchTasks();
    } finally {
      loading.value = false;
    }
  }

  async function addTask(task: TaskCreate): Promise<TTaskDto> {
    const created = await apiCreateTask(task);
    tasks.value.unshift(created);
    return created;
  }

  async function editTask(id: number, task: TaskUpdate): Promise<TTaskDto> {
    const updated = await apiUpdateTask(id, task);
    const idx = tasks.value.findIndex(t => t.id === id);
    if (idx !== -1) {
      tasks.value.splice(idx, 1, updated);
    }
    return updated;
  }

  async function removeTask(id: number): Promise<void> {
    await apiDeleteTask(id);
    tasks.value = tasks.value.filter(t => t.id !== id);
  }

  return {
    // state
    tasks,
    loading,

    // getters
    tasksByStatus,
    recentTasks,

    // style maps
    priorityChipClasses,
    statusColumnClasses,
    statusIcons,

    // actions
    fetchTasks,
    addTask,
    editTask,
    removeTask,
  };
});
