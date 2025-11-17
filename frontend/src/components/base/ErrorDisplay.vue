<template>
  <div v-if="error" class="error-display q-pa-md">
    <q-banner rounded class="bg-red-1 text-negative">
      <template v-slot:avatar>
        <q-icon name="error" color="negative" />
      </template>
      <!-- If error is a string, display it directly -->
      <div v-if="typeof error === 'string'" class="text-body1">
        {{ error }}
      </div>
      <!-- If error is an Error object -->
      <template v-else-if="error instanceof Error">
        <div class="text-subtitle1 text-weight-bold">
          {{ error.name }}
        </div>
        <div class="text-body1">
          {{ error.message }}
        </div>
      </template>
      <!-- Fallback for other error types -->
      <div v-else class="text-body1">An unexpected error occurred</div>

      <!-- Support hint -->
      <div class="text-caption q-mt-sm">
        If this keeps happening, please write into the chat or use the <span class="text-teal cursor-pointer" @click="router.push({name: 'feedback'})">feedback form</span>.
      </div>
    </q-banner>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router';

defineProps({
  error: {
    type: [String, Error, Object],
    required: true,
  },
});

const router = useRouter();
</script>

<style scoped>
.error-display {
  max-width: 600px;
  margin: 0 auto;
}
</style>
