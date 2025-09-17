<template>
  <div class="q-pa-md">
    <div class="row q-col-gutter-md">
      <div class="col-12 col-sm-6">
        <q-input
          v-model="username"
          label="Username"
          outlined
          :rules="[(val) => !!val || 'Username is required']"
        />
      </div>
      <div class="col-12">
        <kenner-button
          color="positive"
          :loading="loading"
          :disabled="!username"
          @click="handleInvite"
        >
          Invite User
        </kenner-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { api } from 'src/boot/axios';
import { useQuasar } from 'quasar';
import KennerButton from 'components/base/KennerButton.vue';
import { useRouter } from 'vue-router';

const $q = useQuasar();
const username = ref('');
const loading = ref(false);
const router = useRouter();

const handleInvite = async () => {
  if (!username.value) return;

  loading.value = true;
  try {
    await api.post('/user/invitations/', {
      username: username.value,
    });

    await router.push({ name: 'list-invitations' });
    $q.notify({
      type: 'positive',
      message: `${username.value} can now register`,
    });
  } catch (error) {
    $q.notify({
      type: 'negative',
      message: 'Failed to invite user',
    });
    console.error('Invitation error:', error);
  } finally {
    loading.value = false;
  }
};
</script>
