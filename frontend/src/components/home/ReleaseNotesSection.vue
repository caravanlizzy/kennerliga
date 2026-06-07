<template>
  <div v-if="releaseNotes.length > 0" class="release-notes-block">
    <div class="row items-center q-mb-sm">
      <q-icon name="campaign" size="28px" color="primary" class="q-mr-sm" />
      <div class="text-h6 text-weight-bold">What's new</div>
    </div>

    <div class="q-gutter-sm">
      <div
        v-for="note in releaseNotes"
        :key="note.id"
        class="release-note-item"
      >
        <div class="row items-center no-wrap q-mb-xs">
          <q-icon name="new_releases" class="text-accent q-mr-sm" />
          <div class="text-subtitle2 text-weight-bold col">
            {{ note.title }}
          </div>
          <div class="text-caption text-grey-6">
            {{ formatDate(note.created_at) }}
          </div>
        </div>
        <div class="text-body2 text-grey-9 release-note-text">
          {{ note.text }}
        </div>
      </div>
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
.release-notes-card {
  border-radius: 12px;
  background: white;
}

.release-note-item + .release-note-item {
  border-top: 1px solid rgba(54, 64, 88, 0.08);
  padding-top: 8px;
}

.release-note-text {
  white-space: pre-wrap;
}
</style>
