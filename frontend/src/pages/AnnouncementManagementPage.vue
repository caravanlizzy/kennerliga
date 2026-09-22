<template>
  <q-page class="q-py-md flex justify-center">
    <div style="max-width: var(--kenner-max-width-text); width: 100%" class="q-px-sm">
      <!-- Header -->
      <div class="management-hero-card q-pa-lg q-mb-lg row items-center justify-between">
        <div class="column">
          <div class="row items-center q-gutter-x-sm q-mb-xs">
            <q-icon name="campaign" color="primary" size="32px" />
            <div class="text-h5 text-weight-bold text-dark tracking-tight">
              Manage Announcements
            </div>
          </div>
          <div class="text-caption text-grey-7">
            Publish system banners, winner announcements, and registration notices.
          </div>
        </div>
      </div>

      <LoadingSpinner v-if="loading" />

      <template v-else>
        <!-- Current Announcements -->
        <q-card flat class="management-card q-mb-lg">
          <q-card-section class="q-pa-lg">
            <div class="text-subtitle1 text-weight-bold q-mb-md text-dark row items-center justify-between">
              <div class="row items-center q-gutter-x-xs">
                <q-icon name="notifications" color="primary" size="20px" />
                <span>Active Announcements</span>
              </div>
              <q-badge color="primary" rounded class="q-px-sm">
                {{ announcements.length }}
              </q-badge>
            </div>

            <div v-if="announcements.length === 0" class="text-center text-grey-6 q-pa-xl column items-center">
              <q-icon name="campaign" size="48px" class="opacity-30 q-mb-sm" />
              <span>No announcements currently published</span>
            </div>

            <div v-else class="column q-gutter-y-sm">
              <q-banner
                v-for="announcement in announcements"
                :key="announcement.id"
                :class="bannerClasses[announcement.type]"
                rounded
                class="shadow-1"
              >
                <template #avatar>
                  <q-icon
                    :name="announcementIcons[announcement.type]"
                    size="md"
                  />
                </template>

                <template #action>
                  <KennerButton
                    flat
                    round
                    dense
                    icon="delete"
                    color="negative"
                    @click="requestDelete(announcement.id)"
                  />
                </template>

                <div class="text-subtitle1 text-weight-bold">
                  {{ announcement.title }}
                </div>

                <div v-if="announcement.content" class="q-mt-xs text-body2">
                  {{ announcement.content }}
                </div>

                <div class="text-caption q-mt-sm opacity-80">
                  Visible: {{ announcement.visible_from }} - {{ announcement.visible_until }}
                </div>
              </q-banner>
            </div>
          </q-card-section>
        </q-card>

        <!-- New Announcement Form -->
        <q-card flat class="management-card">
          <q-card-section class="q-pa-lg">
            <div class="text-subtitle1 text-weight-bold q-mb-md text-dark row items-center q-gutter-x-xs">
              <q-icon name="add_circle" color="positive" size="20px" />
              <span>Add New Announcement</span>
            </div>

            <q-form @submit.prevent="submitAnnouncement" class="q-gutter-y-md">
              <KennerSelect
                v-model="newAnnouncement.type"
                :options="announcementTypes"
                label="Type"
                emit-value
                map-options
              />

              <KennerInput
                v-model="newAnnouncement.title"
                label="Title"
                :rules="[(val) => !!val || 'Title is required']"
              />

              <KennerInput
                v-model="newAnnouncement.content"
                label="Content (optional)"
                type="textarea"
                autogrow
              />

              <div class="row q-col-gutter-md">
                <div class="col-12 col-sm-6">
                  <KennerInput
                    v-model="newAnnouncement.visible_from"
                    label="Visible From"
                    type="date"
                    :rules="[(val) => !!val || 'Start date is required']"
                  />
                </div>

                <div class="col-12 col-sm-6">
                  <KennerInput
                    v-model="newAnnouncement.visible_until"
                    label="Visible Until"
                    type="date"
                    :rules="[(val) => !!val || 'End date is required']"
                  />
                </div>
              </div>

              <div class="row justify-end q-mt-md">
                <KennerButton icon="add" type="submit" color="primary">
                  Publish Announcement
                </KennerButton>
              </div>
            </q-form>
          </q-card-section>
        </q-card>
      </template>

      <!-- Delete confirmation dialog -->
      <q-dialog v-model="deleteDialogOpen" persistent>
        <q-card class="dialog-card">
          <q-card-section class="row items-center q-gutter-sm">
            <q-icon name="warning" color="negative" size="md" />
            <div class="text-h6 text-weight-bold">Delete announcement?</div>
          </q-card-section>

          <q-card-section class="text-body2 text-grey-8">
            Do you want to remove this announcement permanently?
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
import { useAnnouncementStore } from 'stores/announcementStore';
import LoadingSpinner from 'components/base/LoadingSpinner.vue';
import KennerButton from 'components/base/KennerButton.vue';
import KennerSelect from 'components/base/KennerSelect.vue';
import KennerInput from 'components/base/KennerInput.vue';
import { useDeleteConfirm } from 'src/composables/crudDialogs';
import { AnnouncementType, type AnnouncementCreate } from 'src/types';

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

const defaultAnnouncement: AnnouncementCreate = {
  type: AnnouncementType.INFO,
  title: '',
  content: '',
  visible_from: '',
  visible_until: '',
};

const newAnnouncement = reactive<AnnouncementCreate>({ ...defaultAnnouncement });

function resetForm() {
  Object.assign(newAnnouncement, defaultAnnouncement);
}

async function submitAnnouncement() {
  await addAnnouncement({ ...newAnnouncement });
  resetForm();
}

const { deleteDialogOpen, requestDelete, confirmDelete } = useDeleteConfirm(
  (id) => removeAnnouncement(id)
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

.dialog-card {
  min-width: 320px;
  max-width: 440px;
  border-radius: var(--kenner-card-radius, 16px);
  border: 1px solid var(--kenner-border-color, rgba(0, 0, 0, 0.08));
}
</style>
