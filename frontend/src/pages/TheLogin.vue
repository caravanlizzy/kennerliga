<template>
  <div class="column " :style="[isMobile? 'min-width: 280px; max-width:500px' : 'min-width: 450px']">
    <q-card :bordered="!isMobile" :flat="isMobile" :class="{'q-pa-xl':!isMobile}">
      <q-form @click="doLogin" @keyup.enter="doLogin">
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
          <kenner-button type="submit" size="lg" class="full-width q-mt-md" label="Anmelden" icon="pets" color="positive" />
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
  console.log('login');
  login(email.value, password.value);
}
</script>
