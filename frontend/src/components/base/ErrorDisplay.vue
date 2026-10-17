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

      <div class="text-caption q-mt-sm">
        If this keeps happening, please write into the chat.
      </div>

      <template v-slot:action>
        <div class="row items-center q-gutter-xs q-mt-xs">
          <KennerButton
            flat
            dense
            no-caps
            size="sm"
            color="negative"
            :icon="copied ? 'check' : 'content_copy'"
            :label="copied ? 'Copied' : 'Copy Details'"
            aria-label="Copy error details to clipboard"
            @click="copyDetails"
          />
          <KennerButton
            v-if="retryable || $attrs.onRetry"
            outline
            dense
            no-caps
            size="sm"
            color="negative"
            icon="refresh"
            label="Retry"
            aria-label="Retry operation"
            @click="$emit('retry')"
          />
        </div>
      </template>
    </q-banner>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { copyToClipboard, useQuasar } from 'quasar';
import KennerButton from 'components/base/KennerButton.vue';

const props = withDefaults(
  defineProps<{
    error: string | Error | Record<string, unknown> | unknown;
    retryable?: boolean;
  }>(),
  {
    retryable: false,
  }
);

defineEmits<{
  (e: 'retry'): void;
}>();

const $q = useQuasar();
const copied = ref(false);

const errorDetails = computed(() => {
  if (typeof props.error === 'string') return props.error;
  if (props.error instanceof Error) {
    return `${props.error.name}: ${props.error.message}${
      props.error.stack ? `\n${props.error.stack}` : ''
    }`;
  }
  try {
    return JSON.stringify(props.error, null, 2);
  } catch {
    return String(props.error);
  }
});

async function copyDetails() {
  try {
    await copyToClipboard(errorDetails.value);
    copied.value = true;
    $q.notify({
      type: 'positive',
      message: 'Error details copied to clipboard',
    });
    setTimeout(() => {
      copied.value = false;
    }, 2000);
  } catch {
    $q.notify({
      type: 'negative',
      message: 'Failed to copy error details',
    });
  }
}
</script>

<style scoped>
.error-display {
  max-width: 600px;
  margin: 0 auto;
}

.body--dark .error-display .q-banner,
.body--dark .error-display :deep(.text-negative) {
  color: var(--kenner-danger-text) !important;
}
</style>
