<template>
  <q-page class="q-pa-md">
    <div class="text-h4 q-mb-lg">Manage Announcements</div>

    <LoadingSpinner v-if="loading" />

    <template v-else>
      <!-- Current Announcements -->
      <q-card flat bordered class="q-mb-lg">
        <q-card-section>
          <div class="text-h6 q-mb-md">Current Announcements</div>

          <div v-if="announcements.length === 0" class="text-center text-grey q-pa-lg">
            No announcements yet
          </div>

          <div v-else class="q-gutter-md">
            <q-banner
              v-for="announcement in announcements"
              :key="announcement.id"
              :class="bannerClasses[announcement.type]"
              rounded
            >
              <template #avatar>
                <q-icon
                  :name="announcementIcons[announcement.type]"
                  size="md"
                />
              </template>

              <template #action>
                <q-btn
                  flat
                  round
                  dense
                  icon="close"
                  @click="requestDelete(announcement.id)"
                />
              </template>

              <div class="text-subtitle1 text-weight-bold">
                {{ announcement.title }}
              </div>

              <div v-if="announcement.content" class="q-mt-xs">
                {{ announcement.content }}
              </div>

              <div class="text-caption q-mt-sm text-grey-4">
                {{ announcement.visible_from }} - {{ announcement.visible_until }}
              </div>
            </q-banner>
          </div>
        </q-card-section>
      </q-card>

      <!-- New Announcement Form -->
      <q-card flat bordered>
        <q-card-section>
          <div class="text-h6 q-mb-md">Add New Announcement</div>

          <q-form @submit.prevent="submitAnnouncement" class="q-gutter-md">
            <q-select
              v-model="newAnnouncement.type"
              :options="announcementTypes"
              label="Type"
              outlined
              emit-value
              map-options
            />

            <q-input
              v-model="newAnnouncement.title"
              label="Title"
              outlined
              :rules="[(val) => !!val || 'Title is required']"
            />

            <q-input
              v-model="newAnnouncement.content"
              label="Content (optional)"
              outlined
              type="textarea"
              autogrow
            />

            <div class="row q-gutter-md">
              <q-input
                v-model="newAnnouncement.visible_from"
                label="Visible From"
                outlined
                type="date"
                class="col"
                :rules="[(val) => !!val || 'Start date is required']"
              />

              <q-input
                v-model="newAnnouncement.visible_until"
                label="Visible Until"
                outlined
                type="date"
                class="col"
                :rules="[(val) => !!val || 'End date is required']"
              />
            </div>

            <div class="row justify-end">
              <KennerButton icon="add" type="submit">
                Add Announcement
              </KennerButton>
            </div>
          </q-form>
        </q-card-section>
      </q-card>
    </template>

    <!-- Delete confirmation dialog -->
    <q-dialog v-model="deleteDialogOpen" persistent>
      <q-card>
        <q-card-section class="row items-center q-gutter-sm">
          <q-icon name="warning" color="negative" size="md" />
          <div class="text-h6">Delete announcement?</div>
        </q-card-section>

        <q-card-section>
          Do you want to remove this announcement?
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Cancel" color="primary" v-close-popup />
          <q-btn
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
import { useAnnouncementStore } from 'stores/announcementStore';
import LoadingSpinner from 'components/base/LoadingSpinner.vue';
import KennerButton from 'components/base/KennerButton.vue';
import { AnnouncementType, type AnnouncementCreate } from 'src/models/announcementModel';

const announcementStore = useAnnouncementStore();
const { announcements, loading } = storeToRefs(announcementStore);
const { addAnnouncement, removeAnnouncement, bannerClasses, announcementIcons } = announcementStore;

const announcementTypes = [
  { label: 'Info', value: AnnouncementType.INFO },
  { label: 'Winner', value: AnnouncementType.WINNER },
  { label: 'Register', value: AnnouncementType.REGISTER },
  { label: 'Warning', value: AnnouncementType.WARNING },
  { label: 'Neutral', value: AnnouncementType.NEUTRAL },
];

const newAnnouncement = reactive<AnnouncementCreate>({
  type: AnnouncementType.INFO,
  title: '',
  content: '',
  visible_from: '',
  visible_until: '',
});

// dialog state
const deleteDialogOpen = ref(false);
const pendingDeleteId = ref<number | null>(null);

function resetForm() {
  newAnnouncement.type = AnnouncementType.INFO;
  newAnnouncement.title = '';
  newAnnouncement.content = '';
  newAnnouncement.visible_from = '';
  newAnnouncement.visible_until = '';
}

async function submitAnnouncement() {
  await addAnnouncement({ ...newAnnouncement });
  resetForm();
}

function requestDelete(id: number) {
  pendingDeleteId.value = id;
  deleteDialogOpen.value = true;
}

async function confirmDelete() {
  if (pendingDeleteId.value != null) {
    await removeAnnouncement(pendingDeleteId.value);
  }
  pendingDeleteId.value = null;
  deleteDialogOpen.value = false;
}
</script>
