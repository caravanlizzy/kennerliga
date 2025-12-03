<template>
  <div class="q-pa-md">
    <div class="row q-col-gutter-md">
      <div class="col-12 col-sm-6">
        <q-input
          v-model="note"
          label="Internal note (remember who you invited)"
          outlined
        />
      </div>
      <div class="col-12">
        <kenner-button
          color="positive"
          :loading="loading"
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
const note = ref('');
const loading = ref(false);
const router = useRouter();

const handleInvite = async () => {
  loading.value = true;
  try {
    await api.post('/user/invitations/', {
      label: note.value,
    });

    await router.push({ name: 'invitations' });
    $q.notify({
      type: 'positive',
      message: `User can now register. Internal note: ${note.value}`,
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
