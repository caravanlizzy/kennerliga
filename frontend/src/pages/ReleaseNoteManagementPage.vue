<template>
  <q-page class="q-pa-md">
    <div class="text-h4 q-mb-lg">Manage Release Notes</div>

    <LoadingSpinner v-if="loading" />

    <template v-else>
      <!-- New Release Note Form (on top) -->
      <q-card flat bordered class="q-mb-lg">
        <q-card-section>
          <div class="text-h6 q-mb-md">Add New Release Note</div>

          <q-form @submit.prevent="submitReleaseNote" class="q-gutter-md">
            <KennerInput
              v-model="newNote.title"
              label="Title"
              :rules="[(val) => !!val || 'Title is required']"
            />

            <q-input
              v-model="newNote.text"
              label="Text"
              type="textarea"
              outlined
              autogrow
              :input-style="{ minHeight: '120px' }"
              :rules="[(val) => !!val || 'Text is required']"
            />

            <div class="row justify-end">
              <KennerButton icon="add" type="submit">
                Add Release Note
              </KennerButton>
            </div>
          </q-form>
        </q-card-section>
      </q-card>

      <!-- Current Release Notes (preview as table) -->
      <q-card flat bordered>
        <q-card-section>
          <div class="text-h6 q-mb-md">Current Release Notes</div>

          <div v-if="releaseNotes.length === 0" class="text-center text-grey q-pa-lg">
            No release notes yet
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
          >
            <template #body-cell-text="props">
              <q-td :props="props">
                <div class="release-note-text">{{ props.row.text }}</div>
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
      <q-card>
        <q-card-section class="row items-center q-gutter-sm">
          <q-icon name="warning" color="negative" size="md" />
          <div class="text-h6">Delete release note?</div>
        </q-card-section>

        <q-card-section>
          Do you want to remove this release note?
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
import { reactive, ref } from 'vue';
import { storeToRefs } from 'pinia';
import { useReleaseNoteStore } from 'stores/releaseNoteStore';
import LoadingSpinner from 'components/base/LoadingSpinner.vue';
import KennerButton from 'components/base/KennerButton.vue';
import KennerInput from 'components/base/KennerInput.vue';
import type { ReleaseNoteCreate } from 'src/types';

const releaseNoteStore = useReleaseNoteStore();
const { releaseNotes, loading } = storeToRefs(releaseNoteStore);
const { addReleaseNote, removeReleaseNote } = releaseNoteStore;

const newNote = reactive<ReleaseNoteCreate>({
  title: '',
  text: '',
});

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

// dialog state
const deleteDialogOpen = ref(false);
const pendingDeleteId = ref<number | null>(null);

function resetForm() {
  newNote.title = '';
  newNote.text = '';
}

async function submitReleaseNote() {
  await addReleaseNote({ ...newNote });
  resetForm();
}

function requestDelete(id: number) {
  pendingDeleteId.value = id;
  deleteDialogOpen.value = true;
}

async function confirmDelete() {
  if (pendingDeleteId.value != null) {
    await removeReleaseNote(pendingDeleteId.value);
  }
  pendingDeleteId.value = null;
  deleteDialogOpen.value = false;
}
</script>

<style scoped>
.release-note-text {
  white-space: pre-wrap;
}
</style>
