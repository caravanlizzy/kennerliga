import { defineStore } from "pinia";
import { ref, Ref } from "vue";
import { api } from "boot/axios";

type TAnnouncement = {
  title: string;
  content: string;
  type: string;
}

export const useAnnouncementStore = defineStore('announcementStore', () => {
  const announcements: Ref<TAnnouncement[]> = ref([]);

  async function getAnnouncements(): Promise<void> {
    const { data } = await api('organisation/announcements', {
      method: 'GET'
    })
    for(const announcement of data) {
      announcements.value.push(announcement);
    }
  }

  function addAnnouncement(announcement: TAnnouncement): void {
    announcements.value.push(announcement);
  }

  function removeAnnouncement(announcement: TAnnouncement): void {
    announcements.value.splice(announcements.value.indexOf(announcement), 1);
  }

  return { announcements, addAnnouncement, removeAnnouncement, getAnnouncements }
})
