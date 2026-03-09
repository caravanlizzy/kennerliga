<template>
  <div class="q-pa-md q-gutter-y-lg page-container">
    <!-- Feedback Display for Admins -->
    <div v-if="isAdmin" class="feedback-list">
      <div class="row items-center q-mb-md">
        <q-icon name="analytics" color="primary" size="sm" class="q-mr-sm" />
        <div class="text-h6 text-weight-bold">Manage User Feedback</div>
      </div>

      <q-table
        :rows="feedbacks"
        :columns="columns"
        row-key="id"
        flat
        bordered
        :loading="loadingFeedback"
        :pagination="pagination"
        class="feedback-table shadow-1"
        no-data-label="No feedback yet."
      >
        <template v-slot:body-cell-username="props">
          <q-td :props="props">
            <div class="row items-center no-wrap">
              <q-avatar size="24px" color="primary" text-color="white" class="q-mr-sm">
                {{ (props.row.username || 'A')[0].toUpperCase() }}
              </q-avatar>
              <div class="text-weight-medium">{{ props.row.username || 'Anonymous' }}</div>
            </div>
          </q-td>
        </template>

        <template v-slot:body-cell-datetime="props">
          <q-td :props="props" class="text-grey-7">
            {{ formatDate(props.row.datetime) }}
          </q-td>
        </template>

        <template v-slot:body-cell-message="props">
          <q-td :props="props" class="message-cell">
            <div class="message-text truncate-2-lines">
              {{ props.row.message }}
            </div>
            <q-tooltip anchor="top middle" self="bottom middle" :offset="[0, 8]" class="bg-dark text-white shadow-2">
              <div class="q-pa-xs max-width-300 whitespace-pre-line">
                {{ props.row.message }}
              </div>
            </q-tooltip>
          </q-td>
        </template>
      </q-table>
    </div>

    <!-- Feedback Submission Form -->
    <div class="feedback-form-container q-mt-xl">
      <q-card flat bordered class="feedback-card shadow-1">
        <q-card-section class="bg-grey-1 q-py-md">
          <div class="row items-center">
            <q-icon name="feedback" color="orange-8" size="sm" class="q-mr-sm" />
            <div class="text-h6 text-weight-bold">Submit Feedback</div>
          </div>
          <div class="text-caption text-grey-7">
            We value your thoughts! Let us know how we can improve.
          </div>
        </q-card-section>

        <q-separator />

        <q-card-section class="q-pa-lg">
          <q-form @submit="onSubmit" class="q-gutter-md">
            <q-input
              v-model="feedback"
              label="Your Message"
              placeholder="Tell us what's on your mind..."
              type="textarea"
              autogrow
              rows="4"
              filled
              class="feedback-input"
              :rules="[(val) => !!val || 'Feedback is required']"
            />

            <div class="row justify-end">
              <KennerButton
                label="Send Feedback"
                type="submit"
                color="primary"
                icon-right="send"
                class="q-px-lg"
                :loading="submitting"
              />
            </div>
          </q-form>
        </q-card-section>
      </q-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useQuasar } from 'quasar';
import { useRouter } from 'vue-router';
import { storeToRefs } from 'pinia';
import { useUserStore } from 'stores/userStore';
import KennerButton from 'components/base/KennerButton.vue';
import { postFeedback, fetchFeedback } from 'src/services/feedbackService';
import type { TFeedbackDto } from 'src/types';

const $q = useQuasar();
const router = useRouter();
const { isAdmin } = storeToRefs(useUserStore());

const feedback = ref('');
const feedbacks = ref<TFeedbackDto[]>([]);
const loadingFeedback = ref(false);
const submitting = ref(false);

const columns = [
  {
    name: 'username',
    label: 'User',
    align: 'left',
    field: 'username',
    sortable: true,
  },
  {
    name: 'datetime',
    label: 'Date',
    align: 'left',
    field: 'datetime',
    sortable: true,
  },
  {
    name: 'message',
    label: 'Feedback Message',
    align: 'left',
    field: 'message',
    style: 'max-width: 500px',
  },
];

const pagination = {
  rowsPerPage: 10,
  sortBy: 'datetime',
  descending: true,
};

async function onSubmit() {
  submitting.value = true;
  try {
    await postFeedback(feedback.value);
    $q.notify({
      title: 'Feedback Sent',
      message: 'Thank you for your feedback!',
      color: 'positive',
      icon: 'check_circle',
    });
    if (!isAdmin.value) {
      router.push({ name: 'home' });
    } else {
      feedback.value = '';
      await loadFeedback();
    }
  } catch (error) {
    $q.notify({
      type: 'negative',
      message: 'Failed to send feedback',
    });
  } finally {
    submitting.value = false;
  }
}

async function loadFeedback() {
  if (!isAdmin.value) return;
  loadingFeedback.value = true;
  try {
    feedbacks.value = await fetchFeedback();
  } catch (error) {
    console.error('Failed to load feedback:', error);
  } finally {
    loadingFeedback.value = false;
  }
}

function formatDate(dateStr: string) {
  const date = new Date(dateStr);
  return date.toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

onMounted(() => {
  loadFeedback();
});
</script>

<style scoped lang="scss">
.page-container {
  max-width: 1000px;
  margin: 0 auto;
}

.feedback-table {
  background: white;
  border-radius: 12px;
  overflow: hidden;

  :deep(.q-table__card) {
    box-shadow: none;
  }

  :deep(thead tr th) {
    font-weight: 700;
    text-transform: uppercase;
    font-size: 0.75rem;
    letter-spacing: 0.05em;
    color: #607d8b;
    background: #f8f9fa;
  }
}

.message-cell {
  position: relative;
}

.message-text {
  max-width: 450px;
  line-height: 1.5;
}

.truncate-2-lines {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
}

.feedback-card {
  border-radius: 16px;
  overflow: hidden;
  max-width: 800px;
  margin: 0 auto;
}

.feedback-input {
  :deep(.q-field__control) {
    border-radius: 12px;
    background: rgba(0, 0, 0, 0.03);
    transition: all 0.3s ease;

    &:before {
      display: none;
    }

    &:hover {
      background: rgba(0, 0, 0, 0.05);
    }
  }

  &.q-field--focused {
    :deep(.q-field__control) {
      background: white;
      box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
      border: 1px solid rgba(0, 0, 0, 0.1);
    }
  }

  :deep(.q-field__native) {
    padding-top: 24px;
    font-size: 1rem;
    line-height: 1.5;
  }

  :deep(.q-field__label) {
    top: 16px;
    font-weight: 500;
  }
}

.max-width-300 {
  max-width: 300px;
}

.whitespace-pre-line {
  white-space: pre-line;
}

@media (max-width: 600px) {
  .message-text {
    max-width: 200px;
  }
}
</style>
