<template>
  <div v-if="releaseNotes.length > 0" class="release-notes-section q-mt-lg">
    <div class="row items-center q-mb-md">
      <q-icon name="campaign" size="md" class="text-primary q-mr-sm" />
      <div class="text-h5 text-weight-bold">What's new</div>
    </div>

    <div class="q-gutter-md">
      <q-card
        v-for="note in releaseNotes"
        :key="note.id"
        flat
        bordered
        class="release-note-card"
      >
        <q-card-section>
          <div class="row items-center no-wrap q-mb-xs">
            <q-icon name="new_releases" class="text-accent q-mr-sm" />
            <div class="text-subtitle1 text-weight-bold col">
              {{ note.title }}
            </div>
            <div class="text-caption text-grey-6">
              {{ formatDate(note.created_at) }}
            </div>
          </div>
          <div class="text-body2 text-grey-9 release-note-text">
            {{ note.text }}
          </div>
        </q-card-section>
      </q-card>
    </div>
  </div>
</template>

<script setup lang="ts">
defineOptions({ name: 'ReleaseNotesSection' });
import { storeToRefs } from 'pinia';
import { useReleaseNoteStore } from 'stores/releaseNoteStore';

const store = useReleaseNoteStore();
const { releaseNotes } = storeToRefs(store);

function formatDate(value: string): string {
  if (!value) return '';
  const d = new Date(value);
  if (Number.isNaN(d.getTime())) return value;
  return d.toLocaleDateString();
}
</script>

<style scoped>
.release-note-card {
  border-radius: 12px;
  border-left: 4px solid var(--q-primary);
  transition: box-shadow 0.2s ease;
}

.release-note-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.release-note-text {
  white-space: pre-wrap;
}
</style>
