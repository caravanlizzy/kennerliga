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
          <q-icon name="img:icons/favicon.svg" size="64px" class="q-mb-md" />
          <div class="text-h4 text-weight-bolder text-dark tracking-tighter">Login</div>
          <div class="text-subtitle2 text-grey-6 q-mt-xs text-center">
            Welcome back to Kenner<span class="text-primary">Liga</span>
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

        <div class="column">
          <KennerButton
            type="submit"
            size="lg"
            class="full-width shadow-4"
            label="Login"
            icon="login"
            color="primary"
          />
        </div>
      </q-form>
    </q-card>
  </div>
</template>



<script setup lang="ts">
import KennerInput from 'components/base/KennerInput.vue';
import KennerButton from 'components/base/KennerButton.vue';
import { useUserStore } from 'stores/userStore';
import { useResponsive } from 'src/composables/responsive';
import { ref } from 'vue';
import { useRouter } from 'vue-router';

const { login } = useUserStore();
const router = useRouter();
const { isMobile } = useResponsive();

const username = ref('');
const password = ref('');
const errorMessage = ref('');

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
