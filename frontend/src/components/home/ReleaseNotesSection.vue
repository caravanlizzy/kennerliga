<template>
  <div v-if="releaseNotes.length > 0" class="release-notes-block">
    <div class="row items-center q-mb-xs">
      <q-icon name="campaign" size="16px" color="grey-6" class="q-mr-xs" />
      <div class="text-caption text-weight-medium text-grey-7 text-uppercase release-notes-block__title">What's new</div>
    </div>

    <div class="q-gutter-xs">
      <div
        v-for="note in releaseNotes"
        :key="note.id"
        class="release-note-item"
      >
        <div class="row items-center no-wrap">
          <q-icon name="new_releases" size="14px" class="text-grey-6 q-mr-xs" />
          <div class="text-caption text-weight-medium text-grey-8 col ellipsis">
            {{ note.title }}
          </div>
          <div class="text-caption text-grey-6">
            {{ formatDate(note.created_at) }}
          </div>
        </div>
        <div class="text-caption text-grey-7 release-note-text">
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
.release-notes-block__title {
  letter-spacing: 0.06em;
}

.release-note-item + .release-note-item {
  border-top: 1px solid rgba(54, 64, 88, 0.05);
  padding-top: 4px;
  margin-top: 4px;
}

.release-note-text {
  white-space: pre-wrap;
}
</style>
