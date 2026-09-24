<template>
  <div
    class="column items-center justify-center full-height"
    :style="[
      isMobile ? 'min-width: 280px; max-width:500px; width: 100%' : 'min-width: 450px',
    ]"
  >
    <q-card
      flat
      class="login-card shadow-2xl"
      :class="[isMobile ? 'q-pa-lg' : 'q-pa-xl']"
      style="border-radius: 20px; border: 1px solid rgba(54, 64, 88, 0.08)"
    >
      <q-form @submit="doLogin" @keyup.enter="doLogin" class="q-gutter-y-lg">
        <div class="column items-center q-mb-lg">
          <BrandLogo class="q-mb-md" icon-size="64px" word-size="2rem" />
          <div class="text-h4 text-weight-bolder text-dark tracking-tighter q-mt-md">Login</div>
          <div class="text-subtitle2 text-grey-6 q-mt-xs text-center">
            Welcome back
          </div>
        </div>

        <!-- Inline error message -->
        <div v-if="errorMessage" class="error-container q-pa-md rounded-borders bg-negative-soft text-negative text-center text-weight-bold border-negative-subtle">
          {{ errorMessage }}
        </div>

        <div class="column q-gutter-y-md">
          <KennerInput v-model="username" :rules="[]" label="Username" />
          <KennerInput
            v-model="password"
            :rules="[]"
            label="Password"
            type="password"
          />
        </div>

        <div class="column q-gutter-y-sm">
          <KennerButton
            type="submit"
            size="lg"
            class="full-width shadow-4"
            label="Login"
            icon="login"
            color="primary"
          />
          <KennerButton
            flat
            color="grey-7"
            label="Forgot password?"
            @click="showResetDialog = true"
            class="full-width q-mt-xs"
            size="sm"
            no-caps
          />
        </div>
      </q-form>
    </q-card>

    <q-dialog v-model="showResetDialog">
      <q-card style="min-width: 320px; max-width: 450px; width: 100%; border-radius: 16px" class="q-pa-md">
        <q-form ref="resetFormRef" @submit="doRequestReset">
          <q-card-section>
            <div class="text-h6 text-weight-bold">Restore Password</div>
            <div class="text-caption text-grey-7 q-mt-xs">
              Enter your username to request a one-time password reset link.
            </div>
          </q-card-section>

          <q-card-section class="q-pt-none">
            <KennerInput
              v-model="resetUsername"
              :rules="[rules.required]"
              label="Username"
              autocomplete="username"
              autofocus
            />
          </q-card-section>

          <q-card-actions align="right" class="q-pt-sm">
            <KennerButton
              flat
              label="Cancel"
              color="grey-7"
              v-close-popup
              :disable="isResetSubmitting"
            />
            <KennerButton
              type="submit"
              label="Request Reset"
              color="primary"
              icon="send"
              :loading="isResetSubmitting"
              :disable="isResetSubmitting"
            />
          </q-card-actions>
        </q-form>
      </q-card>
    </q-dialog>
  </div>
</template>



<script setup lang="ts">
import KennerInput from 'components/base/KennerInput.vue';
import KennerButton from 'components/base/KennerButton.vue';
import BrandLogo from 'components/base/BrandLogo.vue';
import { useUserStore } from 'stores/userStore';
import { useResponsive } from 'src/composables/responsive';
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useQuasar } from 'quasar';
import axios from 'axios';
import { requestPasswordReset } from 'src/services/userService';

const $q = useQuasar();
const { login } = useUserStore();
const router = useRouter();
const { isMobile } = useResponsive();

const username = ref('');
const password = ref('');
const errorMessage = ref('');

const showResetDialog = ref(false);
const resetUsername = ref('');
const resetFormRef = ref();
const isResetSubmitting = ref(false);

const rules = {
  required: (v: string) => !!v || 'This field is required',
};

async function doRequestReset(): Promise<void> {
  const valid = await resetFormRef.value?.validate?.();
  if (!valid) return;

  isResetSubmitting.value = true;
  try {
    const data = await requestPasswordReset({
      username: resetUsername.value.trim(),
    });

    $q.notify({
      type: 'positive',
      message: data?.detail || 'Password reset request sent.',
    });

    showResetDialog.value = false;
    resetUsername.value = '';
  } catch (err: unknown) {
    let message = 'Failed to request password reset.';
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
    isResetSubmitting.value = false;
  }
}

async function doLogin(): Promise<void> {
  errorMessage.value = ''; // clear old errors

  const success = await login(username.value, password.value);
  if (success) {
    await router.push({ name: 'home' });
  } else {
    errorMessage.value =
      'Login failed. Please check your username and password.';
  }
}
</script>

<style scoped lang="scss">
.login-card {
  background: rgba(255, 255, 255, 0.8) !important;
  backdrop-filter: blur(12px);
  max-width: 500px;
  width: 100%;
}

.bg-negative-soft {
  background: rgba(var(--q-negative), 0.05);
}

.border-negative-subtle {
  border: 1px solid rgba(var(--q-negative), 0.1);
}

.tracking-tighter {
  letter-spacing: -1.5px;
}
</style>
