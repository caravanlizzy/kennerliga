<template>
  <div class="q-pa-md q-gutter-y-lg">
    <!-- Feedback Display for Admins -->
    <div v-if="isAdmin" class="feedback-list">
      <div class="text-h6 q-mb-md">User Feedback</div>
      <q-card flat bordered v-if="loadingFeedback">
        <q-card-section class="flex flex-center">
          <q-spinner color="primary" size="3em" />
        </q-card-section>
      </q-card>
      <div v-else-if="feedbacks.length === 0" class="text-grey-7 text-center q-pa-lg">
        No feedback yet.
      </div>
      <div v-else class="row q-col-gutter-md">
        <div v-for="f in feedbacks" :key="f.id" class="col-12 col-sm-6 col-md-4">
          <q-card flat bordered class="h-full">
            <q-card-section>
              <div class="row items-center justify-between q-mb-sm">
                <div class="text-subtitle2 text-weight-bold">
                  {{ f.username || 'Anonymous' }}
                </div>
                <div class="text-caption text-grey-7">
                  {{ formatDate(f.datetime) }}
                </div>
              </div>
              <div class="text-body2 whitespace-pre-line">
                {{ f.message }}
              </div>
            </q-card-section>
          </q-card>
        </div>
      </div>
    </div>

    <!-- Feedback Submission Form -->
    <div class="feedback-form">
      <div class="text-h6 q-mb-md">Submit Feedback</div>
      <q-form @submit="onSubmit" class="q-gutter-md">
        <q-input
          v-model="feedback"
          label="Your Feedback"
          type="textarea"
          filled
          :rules="[(val) => !!val || 'Feedback is required']"
        />

        <KennerButton
          label="Submit"
          type="submit"
          color="primary"
          class="q-mt-md"
        />
      </q-form>
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

async function onSubmit() {
  try {
    await postFeedback(feedback.value);
    $q.notify({
      title: 'Feedback Sent',
      message: 'Thank you for your feedback!',
      color: 'positive',
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
  return new Date(dateStr).toLocaleString();
}

onMounted(() => {
  loadFeedback();
});
</script>

<style scoped>
.whitespace-pre-line {
  white-space: pre-line;
}
.h-full {
  height: 100%;
}
</style>
