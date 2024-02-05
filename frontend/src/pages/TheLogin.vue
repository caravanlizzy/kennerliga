<template>
  <div class="full-height q-ma-xs ">
    <q-card style="max-width: 400px; height: 400px;" :class="['q-ma-auto shadow-20 bg-login q-pt-md', isMobile? 'q-px-md':'q-px-xl']">
      <q-card-section class="">
        <span class="text-h4 text-primary">
          Login
        </span>
      </q-card-section>
      <q-card-section>
        <kenner-input :dark="false" rules="" label="Email" />
        <kenner-input :dark="false" rules="" label="Passwort" type="password" class="q-pt-md"/>
      </q-card-section>
      <q-card-section>
        <kenner-button size="lg" class="full-width q-mt-md" label="Anmelden" color="positive" @click="login" />
      </q-card-section>
    </q-card>
  </div>
</template>

<script setup lang="ts">
import KennerInput from 'components/inputs/KennerInput.vue';
import KennerButton from 'components/KennerButton.vue';
import { useUserStore } from 'stores/userStore';
import { useResponsive } from 'src/composables/reponsive';
const { login } = useUserStore();
const { isMobile } = useResponsive();
</script>

<style scoped>
.ma {
  margin: auto;
}

.bg-login {
  background-color: #f6f7ff;
}
</style>
