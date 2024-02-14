<template>
  <div class="column q-px-xl" :style="[isMobile? 'max-width:400px' : 'max-width: 550px']">
    <q-card :bordered="!isMobile" :flat="isMobile" :class="['bg-primary', isMobile? '':'q-pa-xl']">
      <q-form @submit="doLogin" @keyup.enter="doLogin" class="q-pa-lg">
        <q-card-section class="q-mb-md">
        <span class="text-h4 text-accent ">
          Login
        </span>
        </q-card-section>
        <q-card-section>
          <kenner-input v-model="email" :rules="[]" label="Email" />
          <kenner-input v-model="password" :rules="[]" label="Passwort" type="password" class="q-pt-md" />
        </q-card-section>
        <q-card-section>
          <kenner-button type="submit" size="lg" class="full-width q-mt-md" label="Anmelden" color="positive" />
        </q-card-section>
      </q-form>
    </q-card>
  </div>
</template>

<script setup lang="ts">
import KennerInput from 'components/inputs/KennerInput.vue';
import KennerButton from 'components/buttons/KennerButton.vue';
import { useUserStore } from 'stores/userStore';
import { useResponsive } from 'src/composables/reponsive';
import { ref } from 'vue';

const email = ref('');
const password = ref('');
const { login } = useUserStore();
const { isMobile } = useResponsive();

function doLogin(): void {
  login(email.value, password.value);
}
</script>

<style scoped>
.bg-login {
  background-color: #f6f7ff;
}
</style>
