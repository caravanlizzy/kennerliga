<template>
  <q-page class="q-pa-md q-gutter-y-lg page-container">
    <!-- Page Header -->
    <div class="page-header row items-center justify-between no-wrap q-gutter-x-md">
      <div class="row items-center q-gutter-x-md no-wrap">
        <div class="header-icon-wrap">
          <q-icon name="view_kanban" size="28px" class="text-white" />
        </div>
        <div class="column">
          <div class="text-h5 text-weight-bolder page-title">Task Board</div>
          <div class="text-caption page-subtitle">
            Plan, track, and manage tasks across the team.
          </div>
        </div>
      </div>
      <KennerButton
        v-if="isAdmin"
        icon="add"
        color="primary"
        class="new-task-btn"
        @click="openCreateDialog"
      >
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
              :class="['kanban-column glass-card', statusColumnClasses[status], `kanban-column--${statusKey(status)}`]"
            >
              <q-card-section class="kanban-column__header q-py-sm q-px-md">
                <div class="row items-center q-gutter-x-sm no-wrap">
                  <q-icon :name="statusIcons[status]" size="18px" class="kanban-column__icon" />
                  <div class="text-subtitle2 text-weight-bold kanban-column__title">{{ status }}</div>
                  <q-space />
                  <q-chip
                    dense
                    :label="tasksByStatus[status].length"
                    class="count-chip"
                  />
                </div>
              </q-card-section>

              <q-card-section class="q-gutter-y-sm column q-pa-md">
                <div
                  v-if="tasksByStatus[status].length === 0"
                  class="empty-column column items-center q-py-md text-caption"
                >
                  <q-icon name="inbox" size="28px" class="opacity-30 q-mb-xs" />
                  <span>No tasks</span>
                </div>

                <q-card
                  v-for="task in tasksByStatus[status]"
                  :key="task.id"
                  flat
                  :class="['task-card', { 'cursor-pointer': isAdmin }]"
                  @click="isAdmin ? openEditDialog(task) : undefined"
                >
                  <q-card-section class="q-pa-sm">
                    <div class="row items-center no-wrap q-gutter-xs">
                      <div class="text-weight-medium task-title col">
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
                      class="text-caption task-description q-mt-xs ellipsis-2-lines"
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
        <q-card flat class="glass-card recent-card">
          <q-card-section class="recent-card__header q-py-sm q-px-md">
            <div class="row items-center q-gutter-x-sm">
              <q-icon name="history" size="18px" color="primary" />
              <div class="text-subtitle2 text-weight-bold recent-card__title">Recent Tasks</div>
            </div>
          </q-card-section>

          <q-card-section class="q-pa-sm">
            <div
              v-if="recentTasks.length === 0"
              class="empty-column column items-center q-py-md text-caption"
            >
              <q-icon name="inbox" size="28px" class="opacity-30 q-mb-xs" />
              <span>No tasks yet</span>
            </div>

            <q-list v-else dense separator class="recent-list">
              <q-item
                v-for="task in recentTasks"
                :key="task.id"
                :clickable="isAdmin"
                class="recent-item"
                @click="isAdmin ? openEditDialog(task) : undefined"
              >
                <q-item-section avatar>
                  <q-icon :name="statusIcons[task.status]" size="18px" />
                </q-item-section>
                <q-item-section class="recent-task-section">
                  <q-item-label class="ellipsis text-weight-medium">{{ task.title }}</q-item-label>
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
import { onMounted } from 'vue';
import { storeToRefs } from 'pinia';
import { useTaskboardStore } from 'stores/taskboardStore';
import { useUserStore } from 'stores/userStore';
import LoadingSpinner from 'components/base/LoadingSpinner.vue';
import KennerButton from 'components/base/KennerButton.vue';
import KennerSelect from 'components/base/KennerSelect.vue';
import KennerInput from 'components/base/KennerInput.vue';
import { useCrudDialogs } from 'src/composables/crudDialogs';
import {
  TaskPriority,
  TaskStatus,
  type TaskCreate,
  type TTaskDto,
} from 'src/types';

const taskboardStore = useTaskboardStore();
const { tasks, loading, tasksByStatus, recentTasks } = storeToRefs(taskboardStore);
const { isAdmin } = storeToRefs(useUserStore());
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

function statusKey(status: TaskStatus): string {
  return String(status).toLowerCase().replace(/\s+/g, '-');
}

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

const {
  form,
  editingId: editingTaskId,
  formDialogOpen,
  deleteDialogOpen,
  openCreateDialog,
  openEditDialog,
  submit: submitTask,
  requestDelete,
  confirmDelete,
} = useCrudDialogs<TTaskDto, TaskCreate>({
  defaultForm,
  toForm: (task) => ({
    title: task.title,
    description: task.description ?? '',
    priority: task.priority,
    status: task.status,
  }),
  validate: (f) => !!f.title.trim(),
  create: (f) => addTask({
    title: f.title.trim(),
    description: f.description ?? '',
    priority: f.priority,
    status: f.status,
  }),
  update: (id, f) => editTask(id, {
    title: f.title.trim(),
    description: f.description ?? '',
    priority: f.priority,
    status: f.status,
  }),
  remove: (id) => removeTask(id),
});

onMounted(() => {
  fetchTasks();
});
</script>

<style lang="scss" scoped>
.page-container {
  max-width: 1400px;
  margin: 0 auto;
}

/* ---------- Page header ---------- */
.page-header {
  padding: 8px 4px 0;
}

.header-icon-wrap {
  width: 52px;
  height: 52px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, var(--q-primary) 0%, #6366f1 100%);
  flex-shrink: 0;
}

.page-title {
  color: var(--tb-title, #1a1a1a);
  line-height: 1.2;
}

.page-subtitle {
  color: var(--tb-subtle-text, #6b7280);
}

.new-task-btn {
  border-radius: 10px;
  flex-shrink: 0;
}

/* ---------- Glass cards ---------- */
.glass-card {
  background: var(--tb-bg, rgba(255, 255, 255, 0.6));
  backdrop-filter: blur(8px);
  border: 1px solid var(--tb-border, rgba(54, 64, 88, 0.08));
  border-radius: 16px;
  overflow: hidden;
}

.kanban-column {
  min-height: 220px;
  display: flex;
  flex-direction: column;
  position: relative;
}

.kanban-column::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: var(--column-accent, var(--q-primary));
  opacity: 0.85;
}

.kanban-column--todo { --column-accent: #6366f1; }
.kanban-column--in-progress { --column-accent: #f59e0b; }
.kanban-column--done { --column-accent: #10b981; }
.kanban-column--declined { --column-accent: #ef4444; }

.kanban-column__header {
  background: var(--tb-header-bg, rgba(248, 249, 250, 0.5));
  border-bottom: 1px solid var(--tb-border, rgba(54, 64, 88, 0.08));
}

.kanban-column__title {
  color: var(--tb-header-text, #374151);
  text-transform: uppercase;
  letter-spacing: 0.04em;
  font-size: 0.78rem;
}

.kanban-column__icon {
  color: var(--column-accent, var(--q-primary));
}

.count-chip {
  font-weight: 700;
  font-size: 11px;
  background: var(--column-accent, var(--q-primary)) !important;
  color: #fff !important;
  min-height: 20px;
  padding: 0 8px;
}

.empty-column {
  color: var(--tb-subtle-text, #9ca3af);
}

/* ---------- Task cards ---------- */
.task-card {
  background: var(--tb-task-bg, #ffffff);
  border: 1px solid var(--tb-task-border, rgba(54, 64, 88, 0.08));
  border-radius: 10px;
  transition: transform 0.15s ease, box-shadow 0.15s ease, border-color 0.15s ease;
}

.task-card.cursor-pointer:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.08);
  border-color: var(--column-accent, rgba(99, 102, 241, 0.4));
}

.task-title {
  color: var(--tb-title, #1f2937);
}

.task-description {
  color: var(--tb-subtle-text, #6b7280);
}

/* ---------- Recent sidebar ---------- */
.recent-card__header {
  background: var(--tb-header-bg, rgba(248, 249, 250, 0.5));
  border-bottom: 1px solid var(--tb-border, rgba(54, 64, 88, 0.08));
}

.recent-card__title {
  color: var(--tb-header-text, #374151);
  text-transform: uppercase;
  letter-spacing: 0.04em;
  font-size: 0.78rem;
}

.recent-list :deep(.q-item) {
  border-radius: 8px;
  transition: background-color 0.15s ease;
}

.recent-list :deep(.q-item:hover) {
  background-color: var(--tb-row-hover, rgba(99, 102, 241, 0.06));
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
  min-width: 0;
}

.task-title {
  word-break: break-word;
  overflow-wrap: anywhere;
  white-space: normal;
  min-width: 0;
}

.recent-task-section {
  min-width: 0;
}

.kanban-column,
.kanban-column :deep(.q-card__section) {
  min-width: 0;
}

/* ---------- Dark mode ---------- */
:global(.body--dark) {
  .glass-card {
    --tb-bg: rgba(30, 30, 30, 0.8);
    --tb-border: rgba(255, 255, 255, 0.1);
    --tb-header-bg: rgba(40, 40, 40, 0.5);
    --tb-header-text: #ececec;
    --tb-subtle-text: #9ca3af;
    --tb-title: #ececec;
    --tb-task-bg: #262626;
    --tb-task-border: rgba(255, 255, 255, 0.08);
    --tb-row-hover: rgba(255, 255, 255, 0.05);
  }

  .page-title { color: #ececec; }
  .page-subtitle { color: #9ca3af; }
}

/* ---------- Responsive ---------- */
@media (max-width: 600px) {
  .header-icon-wrap {
    width: 44px;
    height: 44px;
    border-radius: 12px;
  }

  .new-task-btn {
    width: auto;
  }
}
</style>
