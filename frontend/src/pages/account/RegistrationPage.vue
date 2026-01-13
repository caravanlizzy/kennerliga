<template>
  <div
    class="column items-center justify-center full-height"
    :style="[
      isMobile ? 'min-width: 280px; max-width: 500px; width: 100%' : 'min-width: 450px',
    ]"
  >
    <q-card
      flat
      class="registration-card shadow-2xl"
      :class="[isMobile ? 'q-pa-lg' : 'q-pa-xl']"
      style="border-radius: 20px; border: 1px solid rgba(54, 64, 88, 0.08)"
    >
      <q-form ref="formRef" @submit="doRegister" @keyup.enter="doRegister" class="q-gutter-y-lg">
        <div class="column items-center q-mb-lg">
          <q-icon name="img:icons/favicon.svg" size="64px" class="q-mb-md" />
          <div class="text-h4 text-weight-bolder text-dark tracking-tighter">Sign Up</div>
          <div class="text-subtitle2 text-grey-6 q-mt-xs text-center">
            Join the Kenner<span class="text-accent">Liga</span> community
          </div>
        </div>

        <div class="column q-gutter-y-md">
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
            autocomplete="new-password"
          />
        </div>

        <div class="column q-gutter-y-sm">
          <KennerButton
            type="submit"
            size="lg"
            class="full-width shadow-4"
            :label="isSubmitting ? 'Signing Up…' : 'Sign Up'"
            icon="person_add"
            color="primary"
            :loading="isSubmitting"
            :disable="isSubmitting"
          />
          <KennerButton
            flat
            color="grey-7"
            icon="login"
            label="Already have an account? Login"
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
import { useResponsive } from 'src/composables/responsive';
import { ref, onMounted } from 'vue';
import { useQuasar } from 'quasar';
import { useRouter, useRoute } from 'vue-router';
import { api } from 'boot/axios';

const { isMobile } = useResponsive();
const $q = useQuasar();
const router = useRouter();
const route = useRoute();

const formRef = ref();
const username = ref('');
const password = ref('');
const inviteKey = ref('');
const isSubmitting = ref(false);

const rules = {
  required: (v: string) => !!v || 'This field is required',
  usernameLen: (v: string) =>
    v?.length >= 3 || 'At least 3 characters required',
  passwordLen: (v: string) =>
    v?.length >= 6 || 'At least 6 characters required',
};

onMounted(() => {
  // Extract the key from URL query parameters
  const key = route.query.key as string;
  if (!key) {
    $q.notify({
      type: 'negative',
      message: 'Invalid or missing invitation key.',
    });
    goToLogin();
    return;
  }
  inviteKey.value = key;
});

async function doRegister(): Promise<void> {
  const valid = await formRef.value?.validate?.();
  if (!valid) return;

  if (!inviteKey.value) {
    $q.notify({
      type: 'negative',
      message: 'Invitation key is missing.',
    });
    return;
  }

  isSubmitting.value = true;
  try {
    const res = await api.post('/user/register/', {
      username: username.value,
      password: password.value,
      invite_key: inviteKey.value,
    });

    // Axios automatically parses JSON and puts the response in .data
    const data = res.data;

    if (res.status >= 400) {
      throw new Error(data?.detail || 'Sign up failed.');
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
      message: err?.message || 'Unknown error during sign up.',
    });
  } finally {
    isSubmitting.value = false;
  }
}

function goToLogin(): void {
  router.push({ name: 'login' }); // adjust route if different
}
</script>

<style scoped lang="scss">
.registration-card {
  background: rgba(255, 255, 255, 0.8) !important;
  backdrop-filter: blur(12px);
  max-width: 500px;
  width: 100%;
}

.tracking-tighter {
  letter-spacing: -1.5px;
}
</style>
