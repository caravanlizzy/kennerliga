import { defineStore } from 'pinia';
import { ref } from 'vue';
import { api } from 'boot/axios';
import { TReleaseNoteDto, ReleaseNoteCreate } from 'src/types';

const BASE_URL = 'release-note/release-notes/';

export const useReleaseNoteStore = defineStore('releaseNote', () => {
  const releaseNotes = ref<TReleaseNoteDto[]>([]);
  const loading = ref(false);

  async function fetchReleaseNotes(): Promise<TReleaseNoteDto[]> {
    loading.value = true;
    try {
      const response = await api.get<TReleaseNoteDto[]>(BASE_URL);
      releaseNotes.value = response.data;
      return response.data;
    } finally {
      loading.value = false;
    }
  }

  async function addReleaseNote(
    note: ReleaseNoteCreate,
  ): Promise<TReleaseNoteDto> {
    loading.value = true;
    try {
      const response = await api.post<TReleaseNoteDto>(BASE_URL, note);
      releaseNotes.value.unshift(response.data);
      return response.data;
    } finally {
      loading.value = false;
    }
  }

  async function updateReleaseNote(
    id: number,
    note: ReleaseNoteCreate,
  ): Promise<TReleaseNoteDto> {
    loading.value = true;
    try {
      const response = await api.put<TReleaseNoteDto>(`${BASE_URL}${id}/`, note);
      const idx = releaseNotes.value.findIndex(n => n.id === id);
      if (idx !== -1) releaseNotes.value[idx] = response.data;
      return response.data;
    } finally {
      loading.value = false;
    }
  }

  async function removeReleaseNote(id: number): Promise<void> {
    loading.value = true;
    try {
      await api.delete(`${BASE_URL}${id}/`);
      releaseNotes.value = releaseNotes.value.filter(n => n.id !== id);
    } finally {
      loading.value = false;
    }
  }

  fetchReleaseNotes();

  return {
    releaseNotes,
    loading,
    fetchReleaseNotes,
    addReleaseNote,
    updateReleaseNote,
    removeReleaseNote,
  };
});
