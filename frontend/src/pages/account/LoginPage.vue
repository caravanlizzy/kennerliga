<template>
  <div
    class="column"
    :style="[
      isMobile ? 'min-width: 280px; max-width:500px' : 'min-width: 450px',
    ]"
  >
    <q-card :bordered="!isMobile" flat :class="{ 'q-pa-xl': !isMobile }">
      <q-form @submit="doLogin" @keyup.enter="doLogin">
        <q-card-section class="q-mb-md">
          <span class="text-h4 text-dark"> Login </span>
        </q-card-section>

        <!-- Inline error message -->
        <q-card-section v-if="errorMessage" class="q-mb-sm">
          <div class="text-negative text-body2">
            {{ errorMessage }}
          </div>
        </q-card-section>

        <q-card-section>
          <KennerInput v-model="username" :rules="[]" label="Username" />
          <KennerInput
            v-model="password"
            :rules="[]"
            label="Password"
            type="password"
            class="q-pt-md"
          />
        </q-card-section>

        <q-card-section>
          <KennerButton
            type="submit"
            size="lg"
            class="full-width q-mt-md"
            label="Login"
            icon="pets"
            color="positive"
          />
        </q-card-section>
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
import { useQuasar } from 'quasar';

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
