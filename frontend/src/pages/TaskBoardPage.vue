<template>
  <q-page class="q-pa-md">
    <div class="row items-center q-mb-lg">
      <div class="text-h4">Task Board</div>
      <q-space />
      <KennerButton icon="add" color="primary" @click="openCreateDialog">
        New Task
      </KennerButton>
    </div>

    <LoadingSpinner v-if="loading && tasks.length === 0" />

    <div v-else class="row q-col-gutter-md">
      <!-- Kanban Board -->
      <div class="col-12 col-md-9">
        <div class="row q-col-gutter-md">
          <div
            v-for="status in statuses"
            :key="status"
            class="col-12 col-sm-6 col-md-3"
          >
            <q-card
              flat
              bordered
              :class="['kanban-column', statusColumnClasses[status]]"
            >
              <q-card-section class="q-pb-sm">
                <div class="row items-center q-gutter-sm">
                  <q-icon :name="statusIcons[status]" size="sm" />
                  <div class="text-subtitle1 text-weight-bold">{{ status }}</div>
                  <q-space />
                  <q-badge color="dark" :label="tasksByStatus[status].length" />
                </div>
              </q-card-section>

              <q-separator />

              <q-card-section class="q-gutter-sm column">
                <div
                  v-if="tasksByStatus[status].length === 0"
                  class="text-grey text-center q-py-md"
                >
                  No tasks
                </div>

                <q-card
                  v-for="task in tasksByStatus[status]"
                  :key="task.id"
                  flat
                  bordered
                  class="task-card cursor-pointer"
                  @click="openEditDialog(task)"
                >
                  <q-card-section class="q-pa-sm">
                    <div class="row items-center no-wrap">
                      <div class="text-weight-medium ellipsis col">
                        {{ task.title }}
                      </div>
                      <q-chip
                        dense
                        square
                        :class="priorityChipClasses[task.priority]"
                        :label="task.priority"
                      />
                    </div>
                    <div
                      v-if="task.description"
                      class="text-caption text-grey-7 q-mt-xs ellipsis-2-lines"
                    >
                      {{ task.description }}
                    </div>
                  </q-card-section>
                </q-card>
              </q-card-section>
            </q-card>
          </div>
        </div>
      </div>

      <!-- Recent Tasks Sidebar -->
      <div class="col-12 col-md-3">
        <q-card flat bordered>
          <q-card-section>
            <div class="text-subtitle1 text-weight-bold q-mb-sm">
              <q-icon name="history" size="sm" class="q-mr-xs" />
              Recent Tasks
            </div>
            <q-separator class="q-mb-sm" />

            <div
              v-if="recentTasks.length === 0"
              class="text-grey text-center q-py-md"
            >
              No tasks yet
            </div>

            <q-list v-else dense>
              <q-item
                v-for="task in recentTasks"
                :key="task.id"
                clickable
                @click="openEditDialog(task)"
              >
                <q-item-section avatar>
                  <q-icon :name="statusIcons[task.status]" size="xs" />
                </q-item-section>
                <q-item-section>
                  <q-item-label class="ellipsis">{{ task.title }}</q-item-label>
                  <q-item-label caption>{{ task.status }}</q-item-label>
                </q-item-section>
                <q-item-section side>
                  <q-chip
                    dense
                    square
                    size="xs"
                    :class="priorityChipClasses[task.priority]"
                    :label="task.priority"
                  />
                </q-item-section>
              </q-item>
            </q-list>
          </q-card-section>
        </q-card>
      </div>
    </div>

    <!-- Create / Edit Dialog -->
    <q-dialog v-model="formDialogOpen" persistent>
      <q-card style="min-width: 420px; max-width: 90vw;">
        <q-card-section class="row items-center q-gutter-sm">
          <q-icon
            :name="editingTaskId === null ? 'add_task' : 'edit'"
            color="primary"
            size="md"
          />
          <div class="text-h6">
            {{ editingTaskId === null ? 'New Task' : 'Edit Task' }}
          </div>
        </q-card-section>

        <q-card-section>
          <q-form @submit.prevent="submitTask" class="q-gutter-md">
            <KennerInput
              v-model="form.title"
              label="Title"
              :rules="[(val) => !!val || 'Title is required']"
              autofocus
            />

            <div class="description-field">
              <label class="description-field__label">Description</label>
              <textarea
                v-model="form.description"
                class="description-field__textarea"
                rows="4"
              />
            </div>

            <div class="row q-gutter-md">
              <KennerSelect
                v-model="form.priority"
                :options="priorityOptions"
                label="Priority"
                emit-value
                map-options
                class="col"
              />

              <KennerSelect
                v-model="form.status"
                :options="statusOptions"
                label="Status"
                emit-value
                map-options
                class="col"
              />
            </div>
          </q-form>
        </q-card-section>

        <q-card-actions align="right" class="q-pa-md">
          <KennerButton
            v-if="editingTaskId !== null"
            flat
            label="Delete"
            color="negative"
            icon="delete"
            @click="requestDelete"
          />
          <q-space />
          <KennerButton flat label="Cancel" color="dark" v-close-popup />
          <KennerButton
            color="primary"
            :icon="editingTaskId === null ? 'add' : 'save'"
            :label="editingTaskId === null ? 'Create' : 'Save'"
            @click="submitTask"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- Delete confirmation dialog -->
    <q-dialog v-model="deleteDialogOpen" persistent>
      <q-card>
        <q-card-section class="row items-center q-gutter-sm">
          <q-icon name="warning" color="negative" size="md" />
          <div class="text-h6">Delete task?</div>
        </q-card-section>

        <q-card-section>
          Do you want to remove this task? This action cannot be undone.
        </q-card-section>

        <q-card-actions align="right">
          <KennerButton flat label="Cancel" color="dark" v-close-popup />
          <KennerButton
            flat
            label="Delete"
            color="negative"
            @click="confirmDelete"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue';
import { storeToRefs } from 'pinia';
import { useTaskboardStore } from 'stores/taskboardStore';
import LoadingSpinner from 'components/base/LoadingSpinner.vue';
import KennerButton from 'components/base/KennerButton.vue';
import KennerSelect from 'components/base/KennerSelect.vue';
import KennerInput from 'components/base/KennerInput.vue';
import {
  TaskPriority,
  TaskStatus,
  type TaskCreate,
  type TTaskDto,
} from 'src/types';

const taskboardStore = useTaskboardStore();
const { tasks, loading, tasksByStatus, recentTasks } = storeToRefs(taskboardStore);
const {
  fetchTasks,
  addTask,
  editTask,
  removeTask,
  priorityChipClasses,
  statusColumnClasses,
  statusIcons,
} = taskboardStore;

const statuses: TaskStatus[] = [
  TaskStatus.TODO,
  TaskStatus.IN_PROGRESS,
  TaskStatus.DONE,
  TaskStatus.DECLINED,
];

const priorityOptions = [
  { label: 'High', value: TaskPriority.HIGH },
  { label: 'Medium', value: TaskPriority.MEDIUM },
  { label: 'Low', value: TaskPriority.LOW },
];

const statusOptions = [
  { label: 'To Do', value: TaskStatus.TODO },
  { label: 'In Progress', value: TaskStatus.IN_PROGRESS },
  { label: 'Done', value: TaskStatus.DONE },
  { label: 'Declined', value: TaskStatus.DECLINED },
];

const defaultForm: TaskCreate = {
  title: '',
  description: '',
  priority: TaskPriority.MEDIUM,
  status: TaskStatus.TODO,
};

const form = reactive<TaskCreate>({ ...defaultForm });
const editingTaskId = ref<number | null>(null);
const formDialogOpen = ref(false);

const deleteDialogOpen = ref(false);
const pendingDeleteId = ref<number | null>(null);

function resetForm(): void {
  form.title = defaultForm.title;
  form.description = defaultForm.description;
  form.priority = defaultForm.priority;
  form.status = defaultForm.status;
  editingTaskId.value = null;
}

function openCreateDialog(): void {
  resetForm();
  formDialogOpen.value = true;
}

function openEditDialog(task: TTaskDto): void {
  editingTaskId.value = task.id;
  form.title = task.title;
  form.description = task.description ?? '';
  form.priority = task.priority;
  form.status = task.status;
  formDialogOpen.value = true;
}

async function submitTask(): Promise<void> {
  if (!form.title.trim()) return;

  const payload: TaskCreate = {
    title: form.title.trim(),
    description: form.description ?? '',
    priority: form.priority,
    status: form.status,
  };

  if (editingTaskId.value === null) {
    await addTask(payload);
  } else {
    await editTask(editingTaskId.value, payload);
  }
  formDialogOpen.value = false;
  resetForm();
}

function requestDelete(): void {
  if (editingTaskId.value !== null) {
    pendingDeleteId.value = editingTaskId.value;
    deleteDialogOpen.value = true;
  }
}

async function confirmDelete(): Promise<void> {
  if (pendingDeleteId.value != null) {
    await removeTask(pendingDeleteId.value);
  }
  pendingDeleteId.value = null;
  deleteDialogOpen.value = false;
  formDialogOpen.value = false;
  resetForm();
}

onMounted(() => {
  fetchTasks();
});
</script>

<style lang="scss" scoped>
.kanban-column {
  min-height: 200px;
}

.task-card {
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}

.task-card:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.description-field {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.description-field__label {
  font-size: 12px;
  color: var(--q-dark, #757575);
  opacity: 0.7;
}

.description-field__textarea {
  width: 100%;
  min-height: 80px;
  max-height: 180px;
  resize: vertical;
  padding: 8px 10px;
  font: inherit;
  color: inherit;
  background: transparent;
  border: 1px solid rgba(0, 0, 0, 0.24);
  border-radius: 4px;
  outline: none;
  box-sizing: border-box;
  overflow-y: auto;
}

.description-field__textarea:focus {
  border-color: var(--q-primary);
  border-width: 2px;
  padding: 7px 9px;
}

.body--dark .description-field__textarea {
  border-color: rgba(255, 255, 255, 0.28);
  color: #fff;
}

.ellipsis-2-lines {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  word-break: break-word;
  overflow-wrap: anywhere;
}
</style>
