<template>
  <div class="column q-px-xl" style="max-width: 450px">
    <q-card dark :bordered="!isMobile" :flat="isMobile" :class="['bg-primary', isMobile? '':'q-pa-xl']">
      <q-card-section class="q-mb-md">
        <span class="text-h4 text-accent ">
          Login
        </span>
      </q-card-section>
      <q-card-section>
        <kenner-input v-model="email" :dark="true" :rules="[]" label="Email" />
        <kenner-input v-model="password" :dark="true" :rules="[]" label="Passwort" type="password" class="q-pt-md" />
      </q-card-section>
      <q-card-section>
        <kenner-button size="lg" class="full-width q-mt-md" label="Anmelden" color="positive"
                       @click="login(email, password)" />
      </q-card-section>
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
</script>

<style scoped>
.bg-login {
  background-color: #f6f7ff;
}
</style>
