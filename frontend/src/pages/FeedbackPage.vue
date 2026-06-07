<template>
  <div class="q-pa-md q-gutter-y-lg page-container">
    <!-- Page Header -->
    <div class="page-header">
      <div class="row items-center q-gutter-x-md no-wrap">
        <div class="header-icon-wrap">
          <q-icon name="forum" size="28px" class="text-white" />
        </div>
        <div class="column">
          <div class="text-h5 text-weight-bolder page-title">Feedback</div>
          <div class="text-caption page-subtitle">
            Share ideas, report issues, or tell us what you love.
          </div>
        </div>
      </div>
    </div>

    <!-- Feedback Submission Form -->
    <div class="feedback-form-container">
      <q-card flat class="feedback-card">
        <q-card-section class="feedback-card-header">
          <div class="row items-center q-gutter-x-sm">
            <q-icon name="edit_note" color="primary" size="22px" />
            <div class="text-subtitle1 text-weight-bold feedback-header-text">
              Submit Feedback
            </div>
          </div>
          <div class="text-caption feedback-subtle-text q-mt-xs">
            We value your thoughts! Let us know how we can improve.
          </div>
        </q-card-section>

        <q-separator class="feedback-separator" />

        <q-card-section class="q-pa-lg">
          <q-form @submit="onSubmit" class="q-gutter-md">
            <q-input
              v-model="feedback"
              label="Your Message"
              placeholder="Tell us what's on your mind..."
              type="textarea"
              autogrow
              rows="4"
              outlined
              counter
              maxlength="2000"
              class="feedback-input"
              :rules="[(val) => !!val || 'Feedback is required']"
            />

            <div class="row items-center justify-between q-gutter-sm submit-row">
              <div class="row items-center text-caption feedback-subtle-text q-gutter-x-xs">
                <q-icon name="lock" size="14px" />
                <span>Your feedback is sent privately to the admins.</span>
              </div>
              <KennerButton
                label="Send Feedback"
                type="submit"
                color="primary"
                icon-right="send"
                class="q-px-lg send-btn"
                :loading="submitting"
                :disable="!feedback.trim()"
              />
            </div>
          </q-form>
        </q-card-section>
      </q-card>
    </div>

    <!-- Feedback Display for Admins -->
    <div v-if="isAdmin" class="feedback-list">
      <div class="row items-center justify-between q-mb-md admin-header">
        <div class="row items-center q-gutter-x-sm">
          <q-icon name="admin_panel_settings" color="primary" size="22px" />
          <div class="text-subtitle1 text-weight-bold feedback-header-text">
            Manage User Feedback
          </div>
        </div>
        <q-chip
          v-if="!loadingFeedback && feedbacks.length > 0"
          dense
          color="primary"
          text-color="white"
          class="count-chip"
        >
          {{ feedbacks.length }} {{ feedbacks.length === 1 ? 'entry' : 'entries' }}
        </q-chip>
      </div>

      <q-card flat class="feedback-card">
        <q-table
          :rows="feedbacks"
          :columns="columns"
          row-key="id"
          flat
          :loading="loadingFeedback"
          :pagination="pagination"
          class="feedback-table"
          no-data-label="No feedback yet."
        >
          <template v-slot:body-cell-username="props">
            <q-td :props="props">
              <div class="row items-center no-wrap">
                <q-avatar size="28px" color="primary" text-color="white" class="q-mr-sm user-avatar">
                  {{ (props.row.username || 'A')[0].toUpperCase() }}
                </q-avatar>
                <div class="text-weight-medium">{{ props.row.username || 'Anonymous' }}</div>
              </div>
            </q-td>
          </template>

          <template v-slot:body-cell-datetime="props">
            <q-td :props="props" class="feedback-subtle-text">
              <div class="row items-center q-gutter-x-xs no-wrap">
                <q-icon name="schedule" size="14px" />
                <span>{{ formatDate(props.row.datetime) }}</span>
              </div>
            </q-td>
          </template>

          <template v-slot:body-cell-message="props">
            <q-td :props="props" class="message-cell">
              <div class="message-text truncate-2-lines">
                {{ props.row.message }}
              </div>
              <q-tooltip
                anchor="top middle"
                self="bottom middle"
                :offset="[0, 8]"
                class="bg-dark text-white shadow-2"
              >
                <div class="q-pa-xs max-width-300 whitespace-pre-line">
                  {{ props.row.message }}
                </div>
              </q-tooltip>
            </q-td>
          </template>

          <template v-slot:no-data>
            <div class="full-width column items-center q-pa-xl feedback-subtle-text">
              <q-icon name="inbox" size="48px" class="q-mb-sm opacity-20" />
              <div class="text-subtitle1 text-weight-bold">No Feedback Yet</div>
              <div class="text-caption">User feedback will appear here once submitted.</div>
            </div>
          </template>
        </q-table>
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
    align: 'left' as const,
    field: 'username',
    sortable: true,
  },
  {
    name: 'datetime',
    label: 'Date',
    align: 'left' as const,
    field: 'datetime',
    sortable: true,
  },
  {
    name: 'message',
    label: 'Feedback Message',
    align: 'left' as const,
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

/* ---------- Page header ---------- */
.page-header {
  padding: 8px 4px 0;
}

.header-icon-wrap {
  width: 52px;
  height: 52px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, var(--q-primary) 0%, #6366f1 100%);
  box-shadow: 0 6px 18px rgba(99, 102, 241, 0.25);
  flex-shrink: 0;
}

.page-title {
  color: var(--feedback-title, #1a1a1a);
  line-height: 1.2;
}

.page-subtitle {
  color: var(--feedback-subtle-text, #6b7280);
}

/* ---------- Cards (glass) ---------- */
.feedback-card {
  background: var(--feedback-bg, rgba(255, 255, 255, 0.6));
  backdrop-filter: blur(8px);
  border: 1px solid var(--feedback-border, rgba(54, 64, 88, 0.08));
  border-radius: 16px;
  overflow: hidden;
}

.feedback-card-header {
  padding: 16px 20px;
  background: var(--feedback-header-bg, rgba(248, 249, 250, 0.5));
}

.feedback-separator {
  background: var(--feedback-border, rgba(54, 64, 88, 0.08));
}

.feedback-header-text {
  color: var(--feedback-header-text, #374151);
}

.feedback-subtle-text {
  color: var(--feedback-subtle-text, #6b7280);
}

/* ---------- Form ---------- */
.feedback-input {
  :deep(.q-field__control) {
    border-radius: 12px;
    transition: all 0.2s ease;
  }

  :deep(.q-field__native),
  :deep(.q-field__label) {
    font-size: 0.95rem;
  }
}

.submit-row {
  flex-wrap: wrap;
}

.send-btn {
  border-radius: 10px;
}

/* ---------- Admin section ---------- */
.admin-header {
  padding: 0 4px;
}

.count-chip {
  font-weight: 600;
  font-size: 11px;
}

.user-avatar {
  font-weight: 700;
  font-size: 12px;
}

.feedback-table {
  background: transparent;

  :deep(.q-table__card),
  :deep(.q-table__container) {
    box-shadow: none;
    background: transparent;
  }

  :deep(thead tr th) {
    font-weight: 700;
    text-transform: uppercase;
    font-size: 0.7rem;
    letter-spacing: 0.06em;
    color: var(--feedback-subtle-text, #607d8b);
    background: var(--feedback-header-bg, rgba(248, 249, 250, 0.5));
    border-bottom: 1.5px solid var(--feedback-border, rgba(54, 64, 88, 0.12));
  }

  :deep(tbody tr) {
    transition: background-color 0.15s ease;
  }

  :deep(tbody tr:hover) {
    background-color: var(--feedback-row-hover, rgba(248, 250, 252, 1)) !important;
  }

  :deep(tbody td) {
    border-bottom: 1px solid var(--feedback-row-border, rgba(0, 0, 0, 0.04));
  }
}

.message-cell {
  position: relative;
}

.message-text {
  max-width: 450px;
  line-height: 1.5;
  color: var(--feedback-text, #212121);
}

.truncate-2-lines {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
}

.max-width-300 {
  max-width: 300px;
}

.whitespace-pre-line {
  white-space: pre-line;
}

/* ---------- Dark mode ---------- */
:global(.body--dark) {
  .feedback-card {
    --feedback-bg: rgba(30, 30, 30, 0.8);
    --feedback-border: rgba(255, 255, 255, 0.1);
    --feedback-header-bg: rgba(40, 40, 40, 0.5);
    --feedback-header-text: #ececec;
    --feedback-subtle-text: #9e9e9e;
    --feedback-text: #ececec;
    --feedback-row-hover: #262626;
    --feedback-row-border: rgba(255, 255, 255, 0.05);
  }

  .page-title {
    color: #ececec;
  }

  .page-subtitle {
    color: #9e9e9e;
  }
}

/* ---------- Responsive ---------- */
@media (max-width: 600px) {
  .message-text {
    max-width: 200px;
  }

  .submit-row .send-btn {
    width: 100%;
  }

  .header-icon-wrap {
    width: 44px;
    height: 44px;
    border-radius: 12px;
  }
}
</style>
