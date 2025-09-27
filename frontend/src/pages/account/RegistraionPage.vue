<template>
  <div
    class="column"
    :style="[isMobile ? 'min-width: 280px; max-width: 500px' : 'min-width: 450px']"
  >
    <q-card :bordered="!isMobile" flat :class="{'q-pa-xl': !isMobile}">
      <q-form ref="formRef" @submit="doRegister" @keyup.enter="doRegister">
        <q-card-section class="q-mb-md">
          <span class="text-h4 text-accent">
            Register
          </span>
        </q-card-section>

        <q-card-section>
          <KennerInput
            v-model="username"
            :rules="[rules.required, rules.usernameLen]"
            label="Username"
            autocomplete="username"
          />
          <KennerInput
            v-model="password"
            :rules="[rules.required, rules.passwordLen]"
            label="Password"
            type="password"
            class="q-pt-md"
            autocomplete="new-password"
          />
          <KennerInput
            v-model="otp"
            :rules="[rules.required]"
            label="One-Time Password (OTP)"
            class="q-pt-md"
            autocomplete="one-time-code"
          />
        </q-card-section>

        <q-card-section>
          <KennerButton
            type="submit"
            size="lg"
            class="full-width q-mt-md"
            :label="isSubmitting ? 'Creating Account…' : 'Register'"
            icon="person_add"
            color="positive"
            :loading="isSubmitting"
            :disable="isSubmitting"
          />
          <div class="q-mt-md text-center">
            <q-btn
              flat
              color="primary"
              icon="login"
              label="Already have an account? Login"
              @click="goToLogin"
            />
          </div>
        </q-card-section>
      </q-form>
    </q-card>
  </div>
</template>

<script setup lang="ts">
import KennerInput from 'components/base/KennerInput.vue';
import KennerButton from 'components/base/KennerButton.vue';
import { useResponsive } from 'src/composables/reponsive';
import { ref } from 'vue';
import { useQuasar } from 'quasar';
import { useRouter } from 'vue-router';

const { isMobile } = useResponsive();
const $q = useQuasar();
const router = useRouter();

const formRef = ref();
const username = ref('');
const password = ref('');
const otp = ref('');
const isSubmitting = ref(false);

const rules = {
  required: (v: string) => !!v || 'This field is required',
  usernameLen: (v: string) => (v?.length >= 3) || 'At least 3 characters required',
  passwordLen: (v: string) => (v?.length >= 6) || 'At least 6 characters required',
};

async function doRegister(): Promise<void> {
  const valid = await formRef.value?.validate?.();
  if (!valid) return;

  isSubmitting.value = true;
  try {
    const res = await fetch('/api/user/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        username: username.value,
        password: password.value,
        otp: otp.value,
      }),
    });

    const data = await res.json().catch(() => ({}));

    if (!res.ok) {
      throw new Error(data?.detail || 'Registration failed.');
    }

    $q.notify({
      type: 'positive',
      message: data?.detail || `User ${username.value} created successfully.`,
    });

    // Navigate to login page
    goToLogin();

    // Or auto-login if you prefer:
    // const { login } = useUserStore();
    // await login(username.value, password.value);
    // router.push({ name: 'home' });

  } catch (err: any) {
    $q.notify({
      type: 'negative',
      message: err?.message || 'Unknown error during registration.',
    });
  } finally {
    isSubmitting.value = false;
  }
}

function goToLogin(): void {
  router.push({ name: 'login' }); // adjust route if different
}
</script>
