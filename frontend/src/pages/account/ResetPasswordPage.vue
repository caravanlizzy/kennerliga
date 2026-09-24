<template>
  <div
    class="column items-center justify-center full-height"
    :style="[
      isMobile ? 'min-width: 280px; max-width: 500px; width: 100%' : 'min-width: 450px',
    ]"
  >
    <q-card
      flat
      class="reset-card shadow-2xl"
      :class="[isMobile ? 'q-pa-lg' : 'q-pa-xl']"
      style="border-radius: 20px; border: 1px solid rgba(54, 64, 88, 0.08)"
    >
      <q-form ref="formRef" @submit="doResetPassword" @keyup.enter="doResetPassword" class="q-gutter-y-lg">
        <div class="column items-center q-mb-lg">
          <BrandLogo class="q-mb-md" icon-size="64px" word-size="2rem" />
          <div class="text-h4 text-weight-bolder text-dark tracking-tighter q-mt-md">Set New Password</div>
          <div class="text-subtitle2 text-grey-6 q-mt-xs text-center">
            Enter your new password below
          </div>
        </div>

        <div class="column q-gutter-y-md">
          <KennerInput
            v-model="password"
            :rules="[rules.required]"
            label="New Password"
            type="password"
            autocomplete="new-password"
          />
          <KennerInput
            v-model="repeatPassword"
            :rules="[rules.required, rules.passwordMatch]"
            label="Repeat Password"
            type="password"
            autocomplete="new-password"
          />
        </div>

        <div class="column q-gutter-y-sm">
          <KennerButton
            type="submit"
            size="lg"
            class="full-width shadow-4"
            :label="isSubmitting ? 'Resetting Password…' : 'Set Password'"
            icon="lock_reset"
            color="primary"
            :loading="isSubmitting"
            :disable="isSubmitting"
          />
          <KennerButton
            flat
            color="grey-7"
            icon="login"
            label="Back to Login"
            @click="goToLogin"
            class="full-width"
            no-caps
          />
        </div>
      </q-form>
    </q-card>
  </div>
</template>

<script setup lang="ts">
import KennerInput from 'components/base/KennerInput.vue';
import KennerButton from 'components/base/KennerButton.vue';
import BrandLogo from 'components/base/BrandLogo.vue';
import { useResponsive } from 'src/composables/responsive';
import { ref, onMounted } from 'vue';
import { useQuasar } from 'quasar';
import { useRouter, useRoute } from 'vue-router';
import axios from 'axios';
import { confirmPasswordReset } from 'src/services/userService';

const { isMobile } = useResponsive();
const $q = useQuasar();
const router = useRouter();
const route = useRoute();

const formRef = ref();
const password = ref('');
const repeatPassword = ref('');
const resetKey = ref('');
const isSubmitting = ref(false);

const rules = {
  required: (v: string) => !!v || 'This field is required',
  passwordMatch: (v: string) =>
    v === password.value || 'Passwords do not match',
};

onMounted(() => {
  const key = route.query.key as string;
  if (!key) {
    $q.notify({
      type: 'negative',
      message: 'Invalid or missing password reset key.',
    });
    goToLogin();
    return;
  }
  resetKey.value = key;
});

async function doResetPassword(): Promise<void> {
  const valid = await formRef.value?.validate?.();
  if (!valid) return;

  if (!resetKey.value) {
    $q.notify({
      type: 'negative',
      message: 'Password reset key is missing.',
    });
    return;
  }

  isSubmitting.value = true;
  try {
    const data = await confirmPasswordReset({
      key: resetKey.value,
      password: password.value,
    });

    $q.notify({
      type: 'positive',
      message: data?.detail || 'Password has been reset successfully.',
    });

    goToLogin();
  } catch (err: unknown) {
    let message = 'Failed to reset password.';
    if (axios.isAxiosError(err)) {
      message = (err.response?.data as { detail?: string })?.detail || err.message || message;
    } else if (err instanceof Error) {
      message = err.message;
    }
    $q.notify({
      type: 'negative',
      message,
    });
  } finally {
    isSubmitting.value = false;
  }
}

function goToLogin(): void {
  router.push({ name: 'login' });
}
</script>

<style scoped lang="scss">
.reset-card {
  background: rgba(255, 255, 255, 0.8) !important;
  backdrop-filter: blur(12px);
  max-width: 500px;
  width: 100%;
}

.tracking-tighter {
  letter-spacing: -1.5px;
}
</style>
