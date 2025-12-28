import { defineStore } from 'pinia';
import { ref } from 'vue';
import { api } from 'boot/axios';
import {
  TAnnouncementDto,
  AnnouncementCreate,
  AnnouncementType,
} from 'src/types';

const BASE_URL = 'announcement/announcements/';

// more saturated banner colors
const bannerClasses: Record<AnnouncementType, string> = {
  [AnnouncementType.INFO]: 'bg-blue-6 text-white',
  [AnnouncementType.WINNER]: 'bg-amber-6 text-black',
  [AnnouncementType.REGISTER]: 'bg-green-6 text-white',
  [AnnouncementType.WARNING]: 'bg-red-6 text-white',
  [AnnouncementType.NEUTRAL]: 'bg-grey-7 text-white',
};

const announcementIcons: Record<AnnouncementType, string> = {
  [AnnouncementType.INFO]: 'info',
  [AnnouncementType.WINNER]: 'emoji_events',
  [AnnouncementType.REGISTER]: 'how_to_reg',
  [AnnouncementType.WARNING]: 'warning',
  [AnnouncementType.NEUTRAL]: 'campaign',
};

export const useAnnouncementStore = defineStore('announcement', () => {
  const announcements = ref<TAnnouncementDto[]>([]);
  const loading = ref(false);

  async function fetchAnnouncements(): Promise<TAnnouncementDto[]> {
    loading.value = true;
    try {
      const response = await api.get<TAnnouncementDto[]>(BASE_URL);
      announcements.value = response.data;
      return response.data;
    } finally {
      loading.value = false;
    }
  }

  async function addAnnouncement(
    announcement: AnnouncementCreate,
  ): Promise<TAnnouncementDto> {
    loading.value = true;
    try {
      const response = await api.post<TAnnouncementDto>(BASE_URL, announcement);
      announcements.value.push(response.data);
      return response.data;
    } finally {
      loading.value = false;
    }
  }

  async function removeAnnouncement(id: number): Promise<void> {
    loading.value = true;
    try {
      await api.delete(`${BASE_URL}${id}/`);
      announcements.value = announcements.value.filter(a => a.id !== id);
    } finally {
      loading.value = false;
    }
  }

  fetchAnnouncements();

  return {
    // state
    announcements,
    loading,

    // style/icon maps
    bannerClasses,
    announcementIcons,

    // actions
    addAnnouncement,
    removeAnnouncement,
  };
});
