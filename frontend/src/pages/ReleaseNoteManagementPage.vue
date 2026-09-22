<template>
  <q-page class="q-py-md flex justify-center">
    <div style="max-width: var(--kenner-max-width-text); width: 100%" class="q-px-sm">
      <!-- Header -->
      <div class="management-hero-card q-pa-lg q-mb-lg row items-center justify-between">
        <div class="column">
          <div class="row items-center q-gutter-x-sm q-mb-xs">
            <q-icon name="history" color="primary" size="32px" />
            <div class="text-h5 text-weight-bold text-dark tracking-tight">
              Manage Release Notes
            </div>
          </div>
          <div class="text-caption text-grey-7">
            Draft and publish product updates and release notes.
          </div>
        </div>
      </div>

      <LoadingSpinner v-if="loading" />

      <template v-else>
        <!-- New Release Note Form -->
        <q-card flat class="management-card q-mb-lg">
          <q-card-section class="q-pa-lg">
            <div class="text-subtitle1 text-weight-bold q-mb-md text-dark row items-center q-gutter-x-xs">
              <q-icon name="post_add" color="positive" size="20px" />
              <span>Add New Release Note</span>
            </div>

            <q-form @submit.prevent="submitReleaseNote" class="q-gutter-y-md">
              <KennerInput
                v-model="newNote.title"
                label="Title"
                :rules="[(val) => !!val || 'Title is required']"
              />

              <KennerInput
                v-model="newNote.text"
                label="Text"
                type="textarea"
                autogrow
                :rules="[(val) => !!val || 'Text is required']"
              />

              <div class="row justify-end q-mt-md">
                <KennerButton icon="add" type="submit" color="primary">
                  Add Release Note
                </KennerButton>
              </div>
            </q-form>
          </q-card-section>
        </q-card>

        <!-- Current Release Notes -->
        <q-card flat class="management-card">
          <q-card-section class="q-pa-lg">
            <div class="text-subtitle1 text-weight-bold q-mb-md text-dark row items-center justify-between">
              <div class="row items-center q-gutter-x-xs">
                <q-icon name="list_alt" color="primary" size="20px" />
                <span>Published Release Notes</span>
              </div>
              <q-badge color="primary" rounded class="q-px-sm">
                {{ releaseNotes.length }}
              </q-badge>
            </div>

            <div v-if="releaseNotes.length === 0" class="text-center text-grey-6 q-pa-xl column items-center">
              <q-icon name="history" size="48px" class="opacity-30 q-mb-sm" />
              <span>No release notes published yet</span>
            </div>

            <q-table
              v-else
              :rows="releaseNotes"
              :columns="columns"
              row-key="id"
              flat
              dense
              hide-bottom
              :pagination="{ rowsPerPage: 0 }"
              class="management-table rounded-borders"
            >
              <template #body-cell-text="props">
                <q-td :props="props">
                  <div class="release-note-text text-body2 text-grey-8">{{ props.row.text }}</div>
                </q-td>
              </template>
              <template #body-cell-actions="props">
                <q-td :props="props" auto-width>
                  <KennerButton
                    flat
                    round
                    dense
                    icon="delete"
                    color="negative"
                    @click="requestDelete(props.row.id)"
                  />
                </q-td>
              </template>
            </q-table>
          </q-card-section>
        </q-card>
      </template>

      <!-- Delete confirmation dialog -->
      <q-dialog v-model="deleteDialogOpen" persistent>
        <q-card class="dialog-card">
          <q-card-section class="row items-center q-gutter-sm">
            <q-icon name="warning" color="negative" size="md" />
            <div class="text-h6 text-weight-bold">Delete release note?</div>
          </q-card-section>

          <q-card-section class="text-body2 text-grey-8">
            Do you want to permanently remove this release note?
          </q-card-section>

          <q-card-actions align="right" class="q-pa-md">
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
    </div>
  </q-page>
</template>

<script setup lang="ts">
import { reactive } from 'vue';
import { storeToRefs } from 'pinia';
import { useReleaseNoteStore } from 'stores/releaseNoteStore';
import LoadingSpinner from 'components/base/LoadingSpinner.vue';
import KennerButton from 'components/base/KennerButton.vue';
import KennerInput from 'components/base/KennerInput.vue';
import { useDeleteConfirm } from 'src/composables/crudDialogs';
import type { ReleaseNoteCreate } from 'src/types';

const releaseNoteStore = useReleaseNoteStore();
const { releaseNotes, loading } = storeToRefs(releaseNoteStore);
const { addReleaseNote, removeReleaseNote } = releaseNoteStore;

const defaultNote: ReleaseNoteCreate = {
  title: '',
  text: '',
};

const newNote = reactive<ReleaseNoteCreate>({ ...defaultNote });

function formatDate(value: string): string {
  if (!value) return '';
  const d = new Date(value);
  if (Number.isNaN(d.getTime())) return value;
  return d.toLocaleDateString();
}

const columns = [
  { name: 'title', label: 'Title', field: 'title', align: 'left' as const, classes: 'text-weight-bold', style: 'min-width: 140px' },
  { name: 'created_at', label: 'Date', field: 'created_at', align: 'left' as const, format: (v: string) => formatDate(v), style: 'width: 110px' },
  { name: 'text', label: 'Text', field: 'text', align: 'left' as const },
  { name: 'actions', label: '', field: 'id', align: 'right' as const },
];

function resetForm() {
  Object.assign(newNote, defaultNote);
}

async function submitReleaseNote() {
  await addReleaseNote({ ...newNote });
  resetForm();
}

const { deleteDialogOpen, requestDelete, confirmDelete } = useDeleteConfirm(
  (id) => removeReleaseNote(id)
);
</script>

<style scoped lang="scss">
.management-hero-card {
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  border: 1px solid var(--kenner-border-color, rgba(0, 0, 0, 0.08));
  border-radius: var(--kenner-card-radius, 16px);
}

.management-card {
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  border: 1px solid var(--kenner-border-color, rgba(0, 0, 0, 0.08));
  border-radius: var(--kenner-card-radius, 16px);
}

.management-table {
  border: 1px solid rgba(0, 0, 0, 0.05);
}

.dialog-card {
  min-width: 320px;
  max-width: 440px;
  border-radius: var(--kenner-card-radius, 16px);
  border: 1px solid var(--kenner-border-color, rgba(0, 0, 0, 0.08));
}

.release-note-text {
  white-space: pre-wrap;
}
</style>
