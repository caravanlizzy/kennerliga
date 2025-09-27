<template>
  <div class="column " :style="[isMobile? 'min-width: 280px; max-width:500px' : 'min-width: 450px']">
    <q-card :bordered="!isMobile" flat :class="{'q-pa-xl':!isMobile}">
      <q-form @submit="doLogin" @keyup.enter="doLogin">
        <q-card-section class="q-mb-md">
        <span class="text-h4 text-accent ">
          Login
        </span>
        </q-card-section>
        <q-card-section>
          <KennerInput v-model="username" :rules="[]" label="Nickname" />
          <KennerInput v-model="password" :rules="[]" label="Passwort" type="password" class="q-pt-md" />
        </q-card-section>
        <q-card-section>
          <KennerButton type="submit" size="lg" class="full-width q-mt-md" label="Anmelden" icon="pets" color="positive" />
        </q-card-section>
      </q-form>
    </q-card>
  </div>
</template>

<script setup lang="ts">
import KennerInput from 'components/base/KennerInput.vue';
import KennerButton from 'components/base/KennerButton.vue';
import { useUserStore } from 'stores/userStore';
import { useResponsive } from 'src/composables/reponsive';
import { ref } from 'vue';

const username = ref('');
const password = ref('');
const { login } = useUserStore();
const { isMobile } = useResponsive();

function doLogin(): void {
  login(username.value, password.value);
}
</script>
